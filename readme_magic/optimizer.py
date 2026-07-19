"""Safe, project-grounded README presentation and optimization."""

import html
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from .analyzer import ProjectMetadata, inspect_project
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


def _section(label: str, emoji: str, body: str) -> str:
    """Add a stable explicit anchor because GitHub slugs vary with emoji."""
    anchor = label.lower().replace(" ", "-")
    return f'<a name="{anchor}"></a>\n## {emoji} {label}\n\n{body}'


def _hero(metadata: ProjectMetadata, existing: str, labels: Dict[str, str]) -> str:
    visual = _primary_visual(metadata, existing)
    image = (
        f'  <img src="{html.escape(visual, quote=True)}" alt="{html.escape(metadata.name, quote=True)} preview" width="100%">\n'
        if visual else ""
    )
    return (
        '<div align="center">\n'
        f'{image}'
        f'  <h1>{html.escape(metadata.name)}</h1>\n'
        f'  <p><strong>{html.escape(metadata.description)}</strong></p>\n'
        f'  {_nav(labels)}\n'
        '</div>'
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
    return [path for path in metadata.visual_assets if path != primary][:4]


def _showcase_has_type_evidence(body: str, project_type: str) -> bool:
    lowered = body.lower()
    if project_type == "cli":
        return ".gif" in lowered or "terminal" in lowered or "console" in lowered
    if project_type == "product":
        return bool(re.search(r"<img\s|!\[[^]]*\]\([^)]+\)", body, re.I)) and "banner" not in lowered
    if project_type == "infrastructure":
        return "architecture" in lowered or "diagram" in lowered or "mermaid" in lowered
    return bool(re.search(r"<img\s|!\[[^]]*\]\([^)]+\)", body, re.I)) or "```" in body


def _showcase(metadata: ProjectMetadata, existing: str, sections: Dict[str, str], is_zh: bool) -> str:
    existing_showcase = sections.get("showcase", "")
    if existing_showcase and _showcase_has_type_evidence(existing_showcase, metadata.project_type):
        return existing_showcase
    primary = _primary_visual(metadata, existing)
    assets = _showcase_assets(metadata, primary)
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


def render_optimized_readme(metadata: ProjectMetadata, existing: str = "", lang: str = "auto") -> str:
    lang = _detect_language(existing, lang)
    sections = _extract_sections(existing)
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

    primary = _primary_visual(metadata, existing)
    features = _feature_cards(metadata, sections.get("features", ""), is_zh)
    showcase = _showcase(metadata, existing, sections, is_zh)
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
    preserved = _extract_unmanaged_sections(existing)

    header = "\n\n".join(part for part in (_hero(metadata, existing, labels), _badges(metadata)) if part)
    blocks = [
        header,
        _section(labels['features'], "✨", features),
        _section(labels['showcase'], "🖼️", showcase),
        _section(labels['installation'], "📦", install),
        _section(labels['usage'], "🚀", usage),
    ]
    if reference_body:
        blocks.append(_section("命令参考" if is_zh else "Command Reference", "🧭", reference_body))
    blocks.extend([
        _section(labels['documentation'], "📖", docs),
        _section(labels['structure'], "🗂️", structure),
    ])
    blocks.extend(
        _section(title, "📌", body) for title, body in preserved
    )
    blocks.extend([
        _section(labels['contributing'], "🤝", contributing),
        _section(labels['license'], "📄", license_body),
    ])
    if not primary:
        blocks.insert(1, "<!-- Add a real project banner, product screenshot, or architecture image to strengthen the first screen. -->")
    return "\n\n---\n\n".join(block.strip() for block in blocks if block.strip()) + "\n"


def optimize_project(
    project_path: Path,
    output: Optional[Path] = None,
    apply: bool = False,
    lang: str = "auto",
) -> Tuple[Path, ReadmeReport, ReadmeReport, ProjectMetadata]:
    metadata = inspect_project(project_path)
    project = Path(metadata.path)
    readme = Path(metadata.readme_path) if metadata.readme_path else project / "README.md"
    existing = readme.read_text(encoding="utf-8") if readme.exists() else ""
    before = analyze_readme(existing, metadata.project_type)
    candidate = render_optimized_readme(metadata, existing, lang)
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
