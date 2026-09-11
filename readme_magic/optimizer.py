"""Safe, project-grounded README presentation and optimization."""

import html
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from .analyzer import ProjectMetadata, inspect_project
from .assets import ImageGenerationConfig, AssetManifest, load_image_config, materialize_assets, plan_assets
from .demo import capture_command
from .quality import ReadmeReport, analyze_readme


SECTION_KEYS = {
    "features": ("features", "feature", "highlights", "功能特性", "核心亮点", "功能", "特性"),
    "showcase": ("showcase", "demo", "screenshots", "preview", "展示", "演示", "截图", "效果"),
    "installation": ("installation", "install", "setup", "安装", "部署"),
    "usage": ("usage", "quick start", "getting started", "使用", "快速开始"),
    "documentation": ("documentation", "docs", "文档"),
    "structure": ("structure", "project structure", "architecture", "项目结构", "架构"),
    "commands": ("commands", "command reference", "options", "configuration", "命令", "参数", "配置"),
    "contributing": ("contributing", "contribute", "贡献"),
    "license": ("license", "许可证", "许可"),
}


def _extract_sections(content: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", content))
    for index, match in enumerate(matches):
        title = re.sub(r"[^\w\u4e00-\u9fff ]", "", match.group(1)).strip().lower()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        body = content[match.end():end].strip()
        body = re.sub(r'(?is)<div\s+align="right".*?</div>', "", body).strip()
        body = re.sub(r"(?:\n\s*---\s*)+$", "", body).strip()
        if not body:
            continue
        for key, aliases in SECTION_KEYS.items():
            if any(alias in title for alias in aliases):
                sections.setdefault(key, body)
                break
    return sections


def _extract_unmanaged_sections(content: str) -> List[Tuple[str, str]]:
    """Preserve valid sections that the optimizer does not own yet."""
    preserved: List[Tuple[str, str]] = []
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", content))
    managed_aliases = tuple(alias for aliases in SECTION_KEYS.values() for alias in aliases)
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        normalized = re.sub(r"[^\w\u4e00-\u9fff ]", "", title).strip().lower()
        if any(alias in normalized for alias in managed_aliases):
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        body = content[match.end():end].strip()
        body = re.sub(r'(?is)<div\s+align="right".*?</div>', "", body).strip()
        body = re.sub(r"(?:\n\s*---\s*)+$", "", body).strip()
        if body:
            preserved.append((title, body))
    return preserved


def _closing_star_history(content: str) -> str:
    """Return an existing Star History CTA/chart block for terminal placement."""
    match = re.search(
        r'(?is)\n*<p\s+align="center">\s*<sub>.*?giving it a .*?</sub>\s*</p>\s*'
        r'<p\s+align="center">\s*<a\s+href="https://star-history\.com/[^" ]+".*?</p>',
        content,
    )
    return match.group(0).strip() if match else ""


def _without_closing_star_history(content: str) -> str:
    if not _closing_star_history(content):
        return content
    return re.sub(
        r'(?is)\n*<p\s+align="center">\s*<sub>.*?giving it a .*?</sub>\s*</p>\s*'
        r'<p\s+align="center">\s*<a\s+href="https://star-history\.com/[^" ]+".*?</p>',
        "\n",
        content,
    )


def _detect_language(existing: str, requested: str) -> str:
    if requested in ("en", "zh"):
        return requested
    chinese = len(re.findall(r"[\u4e00-\u9fff]", existing))
    return "zh" if chinese >= max(20, len(existing) // 20) else "en"


def _code_block(commands: List[str]) -> str:
    return "```bash\n" + "\n".join(commands) + "\n```"


def _badge_items(metadata: ProjectMetadata) -> List[str]:
    badges = []
    if metadata.version != "Not specified":
        badges.append(
            f'<img src="https://img.shields.io/badge/version-{quote(metadata.version, safe="")}-4f46e5?style=flat-square" alt="Version">'
        )
    if metadata.license != "Not specified":
        badges.append(
            f'<img src="https://img.shields.io/badge/license-{quote(metadata.license, safe="")}-10b981?style=flat-square" alt="License">'
        )
    if metadata.language and metadata.language != "Other":
        badges.append(
            f'<img src="https://img.shields.io/badge/built%20with-{quote(metadata.language, safe="")}-0ea5e9?style=flat-square" alt="{metadata.language}">'
        )
    if metadata.repo:
        badges.append(
            f'<img src="https://img.shields.io/github/stars/{metadata.repo}?style=flat-square&color=f59e0b" alt="GitHub stars">'
        )
        badges.append(
            f'<img src="https://img.shields.io/github/last-commit/{metadata.repo}?style=flat-square&color=8b5cf6" alt="Last commit">'
        )
    return badges[:5]


def _badges(metadata: ProjectMetadata) -> str:
    badges = _badge_items(metadata)
    if not badges:
        return ""
    return '<p align="center">\n  ' + "\n  ".join(badges) + "\n</p>"


def _nav(labels: Dict[str, str]) -> str:
    keys = ("features", "showcase", "usage", "documentation", "contributing")
    links = [f'<a href="#{labels[key].lower().replace(" ", "-")}">{labels[key]}</a>' for key in keys]
    return '<p align="center">' + " · ".join(links) + "</p>"


def _language_switch(existing: str) -> str:
    """Preserve an existing English/Chinese switch from the source README."""
    header = existing.split("\n## ", 1)[0]
    match = re.search(
        r'(?is)<p\s+align="center">\s*<strong>English</strong>\s*\|\s*'
        r'<a\s+href="[^"]+">中文</a>\s*</p>',
        header,
    )
    return match.group(0) if match else ""


def _section(label: str, emoji: str, body: str) -> str:
    """Add a stable explicit anchor because GitHub slugs vary with emoji."""
    anchor = label.lower().replace(" ", "-")
    heading = f"{emoji} {label}".strip()
    return f'<a name="{anchor}"></a>\n## {heading}\n\n{body}'


def _hero(metadata: ProjectMetadata, existing: str, labels: Dict[str, str]) -> str:
    existing_header = existing.split("\n## ", 1)[0].strip()
    existing_header = re.sub(r"(?:\n\s*---\s*)+$", "", existing_header).strip()
    if _has_polished_header(existing):
        # A polished existing hero is project-owned design. Preserve it instead
        # of replacing brand copy, language switches, and navigation with a
        # generic metadata-derived header.
        return existing_header
    visual = _primary_visual(metadata, existing)
    image = (
        f'  <img src="{html.escape(visual, quote=True)}" alt="{html.escape(metadata.name, quote=True)} preview" width="100%">\n'
        if visual else ""
    )
    language_switch = _language_switch(existing)
    language_line = f"  {language_switch}\n" if language_switch else ""
    return (
        '<div align="center">\n'
        f'{image}'
        f'  <h1>{html.escape(metadata.name)}</h1>\n'
        f'  <p><strong>{html.escape(metadata.description)}</strong></p>\n'
        f'  {_nav(labels)}\n'
        f'{language_line}'
        '</div>'
    )


def _has_polished_header(existing: str) -> bool:
    header = existing.split("\n## ", 1)[0].strip()
    if not header or not re.search(r"(?i)(<h1\b|^#\s+)", header, re.M):
        return False
    return bool(
        re.search(
            r'(?is)<img\s+[^>]*src="(?!https://img\.shields\.io)([^"]+)"[^>]*>',
            header,
        )
        or re.search(r"(?m)^!\[[^]]*\]\(((?!https://img\.shields\.io)[^)]+)\)$", header)
    )


def _primary_visual(metadata: ProjectMetadata, existing: str) -> str:
    header = existing.split("\n## ", 1)[0]
    match = re.search(
        r'(?is)<img\s+[^>]*src="(?!https://img\.shields\.io)([^"]+)"[^>]*>',
        header,
    )
    if match:
        return match.group(1)
    match = re.search(r"(?m)^!\[[^]]*\]\(((?!https://img\.shields\.io)[^)]+)\)$", header)
    if match:
        return match.group(1)
    if metadata.visual_assets:
        ranked = [path for path in metadata.visual_assets if not any(token in path.lower() for token in ("logo", "icon"))]
        return (ranked or metadata.visual_assets)[0]
    return ""


def _showcase_assets(metadata: ProjectMetadata, primary: str) -> List[str]:
    return [
        path for path in metadata.visual_assets
        if path != primary and not any(
            token in path.lower() for token in ("star-history", "star_history", "growth-chart", "growth_chart")
        )
    ][:4]


def _showcase_has_type_evidence(body: str, project_type: str) -> bool:
    lowered = body.lower()
    if project_type == "cli":
        return ".gif" in lowered or "terminal" in lowered or "console" in lowered
    if project_type == "product":
        return bool(re.search(r"<img\s|!\[[^]]*\]\([^)]+\)", body, re.I)) and "banner" not in lowered
    if project_type == "infrastructure":
        return "architecture" in lowered or "diagram" in lowered or "mermaid" in lowered
    return bool(re.search(r"<img\s|!\[[^]]*\]\([^)]+\)", body, re.I)) or "```" in body


def _showcase(
    metadata: ProjectMetadata,
    existing: str,
    sections: Dict[str, str],
    is_zh: bool,
    runtime_demo: str = "",
) -> str:
    existing_showcase = sections.get("showcase", "")
    if existing_showcase and _showcase_has_type_evidence(existing_showcase, metadata.project_type) and not runtime_demo:
        return existing_showcase
    primary = _primary_visual(metadata, existing)
    assets = _showcase_assets(metadata, primary)
    if runtime_demo:
        demo_label = "真实运行记录" if is_zh else "Verified runtime transcript"
        runtime_block = f"**{demo_label}**\n\n{runtime_demo.strip()}"
        if metadata.project_type == "cli":
            return runtime_block
        if existing_showcase:
            return existing_showcase + "\n\n" + runtime_block
        return runtime_block
    if existing_showcase and assets:
        showcase_assets = assets[:2]
        visual = "\n\n".join(
            f'<p align="center"><img src="{html.escape(path, quote=True)}" '
            f'alt="{html.escape(metadata.name, quote=True)} project evidence" width="90%"></p>'
            for path in showcase_assets
        )
        return existing_showcase + "\n\n" + visual
    if existing_showcase:
        return existing_showcase
    if not assets:
        message = (
            "暂无项目截图。建议补充一张真实界面、运行结果或架构图，让读者无需阅读代码即可理解项目。"
            if is_zh
            else "No project screenshot is available yet. Add a real interface, output, or architecture image so readers can understand the project before reading the code."
        )
        return f"> {message}"
    if len(assets) == 1:
        return (
            f'<p align="center"><img src="{html.escape(assets[0], quote=True)}" '
            f'alt="{html.escape(metadata.name, quote=True)} showcase" width="90%"></p>'
        )
    cells = "".join(
        f'<td width="50%"><img src="{html.escape(path, quote=True)}" '
        f'alt="{html.escape(metadata.name, quote=True)} showcase {index + 1}" width="100%"></td>'
        for index, path in enumerate(assets[:2])
    )
    return f'<table><tr>{cells}</tr></table>'


def _feature_cards(metadata: ProjectMetadata, existing_body: str, is_zh: bool) -> str:
    if existing_body and ("<table" in existing_body or len(existing_body) > 500):
        return existing_body
    features = _feature_list(metadata, existing_body, is_zh)[:6]
    icons = ["⚡", "🎯", "🧩", "🛡️", "🌐", "🧪"]
    cells = []
    for index, feature in enumerate(features):
        text = re.sub(r"^[-*]\s*", "", feature).strip()
        text = html.escape(re.sub(r"[*_`]", "", text))
        if not text:
            continue
        cells.append(
            f'<td width="50%" valign="top"><h3>{icons[index % len(icons)]} {text}</h3></td>'
        )
    rows = []
    for index in range(0, len(cells), 2):
        rows.append("<tr>" + "".join(cells[index:index + 2]) + "</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def _feature_list(metadata: ProjectMetadata, existing_body: str, is_zh: bool) -> List[str]:
    if existing_body:
        items = re.findall(r"(?m)^[-*]\s+(.+)$", existing_body)
        if items:
            return items
    if not is_zh:
        return metadata.features
    translations = {
        "Includes an automated test suite": "包含自动化测试套件",
        "Includes project documentation": "包含项目文档",
        "Ships with runnable examples": "提供可运行示例",
        "Simple project setup and usage": "提供简洁的安装与使用流程",
    }
    localized = []
    for item in metadata.features:
        if item.startswith("Built with "):
            localized.append(f"使用 {item[len('Built with '):]} 构建")
        else:
            localized.append(translations.get(item, item))
    return localized


def _asset_section(manifest: Optional[AssetManifest], key: str, is_zh: bool) -> str:
    """Embed generated assets, or leave an explicit non-broken placeholder."""
    if not manifest:
        return ""
    asset = next((item for item in manifest.assets if item.key == key), None)
    if not asset:
        return ""
    title = {
        "architecture": "架构图" if is_zh else "Architecture",
        "workflow": "工作流程" if is_zh else "Workflow",
        "introduction": "项目介绍图" if is_zh else "Project Overview",
    }[key]
    if asset.status in ("generated", "available") and asset.path:
        return f'<p align="center"><img src="{html.escape(asset.path, quote=True)}" alt="{title}" width="100%"></p>'
    if asset.status == "prompt_ready":
        # Prompt-only is an authoring artifact, not README content. Showing it
        # in the published page makes the candidate look unfinished.
        return ""
    if asset.status == "disabled":
        return ""
    return ""


def _insert_before_section(content: str, block: str, section_key: str) -> str:
    """Insert a new H2 block without changing the surrounding section design."""
    aliases = SECTION_KEYS[section_key]
    for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", content):
        title = re.sub(r"[^\w\u4e00-\u9fff ]", "", match.group(1)).strip().lower()
        if any(alias in title for alias in aliases):
            return content[:match.start()] + block.rstrip() + "\n\n---\n\n" + content[match.start():]
    return content.rstrip() + "\n\n---\n\n" + block.rstrip() + "\n"


def _render_conservative_readme(
    metadata: ProjectMetadata,
    existing: str,
    labels: Dict[str, str],
    is_zh: bool,
    asset_manifest: Optional[AssetManifest],
    runtime_demo: str,
) -> str:
    """Surgically fill gaps in an already strong, project-owned README."""
    closing_visual = _closing_star_history(existing)
    content = _without_closing_star_history(existing).rstrip()
    sections = _extract_sections(content)

    existing_showcase = sections.get("showcase", "")
    improved_showcase = _showcase(
        metadata,
        content,
        sections,
        is_zh,
        runtime_demo=runtime_demo,
    )
    if existing_showcase and improved_showcase != existing_showcase:
        content = content.replace(existing_showcase, improved_showcase, 1)

    if metadata.project_type == "cli" and not sections.get("commands") and metadata.usage_commands:
        command_body = (
            "已验证的命令入口：\n\n" if is_zh else "Verified entry point:\n\n"
        ) + _code_block(metadata.usage_commands)
        command_section = _section(
            "命令参考" if is_zh else "Command Reference",
            "🧭",
            command_body,
        )
        content = _insert_before_section(content, command_section, "documentation")

    generated_sections = []
    for key, title, emoji in (
        ("introduction", "项目介绍" if is_zh else "Project Overview", "💡"),
        ("architecture", "架构" if is_zh else "Architecture", "🏗️"),
        ("workflow", "工作流程" if is_zh else "Workflow", "🔄"),
    ):
        body = _asset_section(asset_manifest, key, is_zh)
        if body and body not in content:
            generated_sections.append(_section(title, emoji, body))
    if generated_sections:
        content = _insert_before_section(content, "\n\n---\n\n".join(generated_sections), "documentation")

    if closing_visual:
        content = re.sub(r"(?:\n\s*---\s*)+$", "", content.rstrip())
        content = content.rstrip() + "\n\n---\n\n" + closing_visual
    return content.rstrip() + "\n"


def render_optimized_readme(
    metadata: ProjectMetadata,
    existing: str = "",
    lang: str = "auto",
    asset_manifest: Optional[AssetManifest] = None,
    runtime_demo: str = "",
) -> str:
    lang = _detect_language(existing, lang)
    closing_visual = _closing_star_history(existing)
    sections_source = _without_closing_star_history(existing)
    sections = _extract_sections(sections_source)
    is_zh = lang == "zh"
    labels = {
        "features": "核心亮点" if is_zh else "Highlights",
        "showcase": "项目展示" if is_zh else "Showcase",
        "installation": "安装" if is_zh else "Installation",
        "usage": "快速开始" if is_zh else "Quick Start",
        "documentation": "文档" if is_zh else "Documentation",
        "structure": "项目结构" if is_zh else "Project Structure",
        "contributing": "参与贡献" if is_zh else "Contributing",
        "license": "许可证" if is_zh else "License",
    }

    if existing and _has_polished_header(existing):
        current_report = analyze_readme(existing, metadata.project_type)
        if current_report.score >= 85:
            return _render_conservative_readme(
                metadata,
                existing,
                labels,
                is_zh,
                asset_manifest,
                runtime_demo,
            )

    primary = _primary_visual(metadata, existing)
    features = _feature_cards(metadata, sections.get("features", ""), is_zh)
    showcase = _showcase(metadata, existing, sections, is_zh, runtime_demo=runtime_demo)
    install = sections.get("installation") or _code_block(metadata.install_commands)
    usage = sections.get("usage") or _code_block(metadata.usage_commands)
    structure = sections.get("structure") or f"```text\n{metadata.structure}\n```"
    docs = sections.get("documentation") or (
        "详细文档请参阅项目中的 `docs/` 目录。" if is_zh and (Path(metadata.path) / "docs").is_dir()
        else "See the `docs/` directory for detailed documentation." if (Path(metadata.path) / "docs").is_dir()
        else "更多说明和示例请参阅本仓库。" if is_zh else "See this repository for additional guides and examples."
    )
    contributing = sections.get("contributing") or (
        "欢迎提交 Issue 和 Pull Request。提交代码前，请先运行项目测试。" if is_zh
        else "Issues and pull requests are welcome. Run the project tests before submitting changes."
    )
    if metadata.license == "Not specified":
        license_default = (
            "当前未检测到许可证文件。发布前请明确项目的使用和分发条款。" if is_zh
            else "No license file was detected. Define usage and distribution terms before publishing."
        )
    else:
        license_default = (
            f"本项目采用 {metadata.license} 许可证。详情见 `LICENSE` 文件。" if is_zh
            else f"This project is licensed under {metadata.license}. See `LICENSE` for details."
        )
    license_body = sections.get("license") or license_default

    reference_body = sections.get("commands", "")
    if not reference_body and metadata.project_type == "cli" and metadata.usage_commands:
        # A CLI needs a scannable command reference even when Quick Start exists.
        reference_body = (
            "Verified entry point:\n\n" + _code_block(metadata.usage_commands)
        )
    preserved = _extract_unmanaged_sections(sections_source)

    header_parts = [_hero(metadata, existing, labels)]
    if not _has_polished_header(existing):
        header_parts.append(_badges(metadata))
    header = "\n\n".join(part for part in header_parts if part)
    blocks = [
        header,
        _section(labels['features'], "✨", features),
        _section(labels['showcase'], "🖼️", showcase),
        _section(labels['installation'], "📦", install),
        _section(labels['usage'], "🚀", usage),
    ]
    overview = _asset_section(asset_manifest, "introduction", is_zh)
    architecture = _asset_section(asset_manifest, "architecture", is_zh)
    workflow = _asset_section(asset_manifest, "workflow", is_zh)
    if overview:
        blocks.append(_section("项目介绍" if is_zh else "Project Overview", "💡", overview))
    if architecture:
        blocks.append(_section("架构" if is_zh else "Architecture", "🏗️", architecture))
    if workflow:
        blocks.append(_section("工作流程" if is_zh else "Workflow", "🔄", workflow))
    if reference_body:
        blocks.append(_section("命令参考" if is_zh else "Command Reference", "🧭", reference_body))
    blocks.extend([
        _section(labels['documentation'], "📖", docs),
        _section(labels['structure'], "🗂️", structure),
    ])
    blocks.extend(
        _section(title, "", body) for title, body in preserved
    )
    blocks.extend([
        _section(labels['contributing'], "🤝", contributing),
        _section(labels['license'], "📄", license_body),
    ])
    if closing_visual:
        blocks.append(closing_visual)
    if not primary:
        blocks.insert(1, "<!-- Add a real project banner, product screenshot, or architecture image to strengthen the first screen. -->")
    return "\n\n---\n\n".join(block.strip() for block in blocks if block.strip()) + "\n"


def optimize_project(
    project_path: Path,
    output: Optional[Path] = None,
    apply: bool = False,
    lang: str = "auto",
    image_config: Optional[ImageGenerationConfig] = None,
    image_mode: Optional[str] = None,
    image_provider: Optional[str] = None,
    image_model: Optional[str] = None,
    image_config_path: Optional[Path] = None,
    demo_command: Optional[str] = None,
) -> Tuple[Path, ReadmeReport, ReadmeReport, ProjectMetadata]:
    metadata = inspect_project(project_path)
    project = Path(metadata.path)
    config = image_config or load_image_config(
        project,
        config_path=image_config_path,
        overrides={"mode": image_mode, "provider": image_provider, "model": image_model},
    )
    manifest = materialize_assets(project, plan_assets(metadata, config), config)
    runtime_demo = ""
    if demo_command:
        transcript_path = capture_command(project, demo_command)
        runtime_demo = transcript_path.read_text(encoding="utf-8")
    readme = Path(metadata.readme_path) if metadata.readme_path else project / "README.md"
    existing = readme.read_text(encoding="utf-8") if readme.exists() else ""
    before = analyze_readme(existing, metadata.project_type)
    candidate = render_optimized_readme(metadata, existing, lang, asset_manifest=manifest, runtime_demo=runtime_demo)
    after = analyze_readme(candidate, metadata.project_type)

    if apply:
        destination = readme
        if readme.exists():
            shutil.copy2(readme, readme.with_name(readme.name + ".bak"))
    else:
        destination = output or project / "README.optimized.md"
        if not destination.is_absolute():
            destination = project / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(candidate, encoding="utf-8")
    return destination, before, after, metadata
