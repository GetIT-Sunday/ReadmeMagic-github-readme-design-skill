"""README presentation and content quality checks used by the CLI and skill."""

from dataclasses import asdict, dataclass
import re
from typing import Dict, List


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    recommendation: str


@dataclass
class ReadmeReport:
    score: int
    max_score: int
    dimensions: Dict[str, int]
    findings: List[Finding]
    passed_checks: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "score": self.score,
            "max_score": self.max_score,
            "dimensions": self.dimensions,
            "findings": [asdict(item) for item in self.findings],
            "passed_checks": self.passed_checks,
        }


def _contains_heading(text: str, terms: List[str]) -> bool:
    headings = "\n".join(re.findall(r"(?m)^#{1,4}\s+(.+)$", text)).lower()
    return any(term.lower() in headings for term in terms)


def _has_first_screen_story(content: str) -> bool:
    first_screen = content[:2_000]
    has_title = bool(
        re.search(r"(?m)^#\s+\S+", first_screen)
        or re.search(r"<h1(?:\s[^>]*)?>\s*\S+.*?</h1>", first_screen, re.I | re.S)
    )
    plain = re.sub(r"<[^>]+>|[#*_`\[\]()]", " ", first_screen)
    sentences = [line.strip() for line in plain.splitlines() if len(line.strip()) >= 20]
    return has_title and bool(sentences)


def _has_meaningful_visual(content: str) -> bool:
    sources = _image_sources(content)
    ignored = ("img.shields.io", "badge", "contrib.rocks", "github-readme-stats")
    return any(not any(token in source.lower() for token in ignored) for source in sources)


def _image_sources(content: str) -> List[str]:
    sources = re.findall(r'<img\s+[^>]*src=["\']([^"\']+)', content, re.I)
    sources.extend(re.findall(r"!\[[^]]*\]\(([^)]+)\)", content))
    return sources


def _code_blocks(content: str) -> List[tuple]:
    """Parse fenced blocks without treating a closing fence as a new opener."""
    blocks = []
    language = None
    body = []
    for line in content.splitlines():
        stripped = line.strip()
        if language is None and stripped.startswith("```"):
            language = stripped[3:].strip().lower()
            body = []
        elif language is not None and stripped == "```":
            blocks.append((language, "\n".join(body)))
            language = None
        elif language is not None:
            body.append(line)
    return blocks


def _has_terminal_evidence(content: str) -> bool:
    sources = _image_sources(content)
    terminal_tokens = ("terminal", "cli", "command", "demo", "output", "usage", "screenshot")
    if any(source.lower().endswith(".gif") for source in sources):
        return True
    if any(any(token in source.lower() for token in terminal_tokens) for source in sources):
        return True
    output_tokens = ("project:", "type:", "score:", "evidence:", "usage:", "output:", "success")
    for language, block in _code_blocks(content):
        if language not in ("", "bash", "shell", "console", "terminal", "text"):
            continue
        lowered = block.lower()
        has_command = bool(re.search(r"(?m)^(?:\$|>)\s*\S+", block)) or "readme-magic " in lowered
        has_output = any(token in lowered for token in output_tokens)
        if has_command and has_output:
            return True
    return False


def _has_non_brand_visual(content: str) -> bool:
    ignored = (
        "img.shields.io", "badge", "contrib.rocks", "github-readme-stats",
        "banner", "hero", "cover", "logo", "star-history",
    )
    return any(
        not any(token in source.lower() for token in ignored)
        for source in _image_sources(content)
    )


def _has_showcase_evidence(content: str, project_type: str) -> bool:
    sources = _image_sources(content)
    evidence_tokens = ("screenshot", "demo", "preview", "architecture", "result", "output")
    if project_type == "cli":
        return _has_terminal_evidence(content)
    if project_type == "product":
        return _has_non_brand_visual(content)
    if project_type == "ai":
        return any(
            any(token in source.lower() for token in ("benchmark", "eval", "result", "demo", "output"))
            for source in sources
        ) or _has_terminal_evidence(content)
    if project_type == "library":
        return _has_non_brand_visual(content) or bool(
            re.search(r"```(?:python|javascript|typescript|rust|go)\s*\n", content, re.I)
        )
    if project_type == "infrastructure":
        return any(any(token in source.lower() for token in evidence_tokens) for source in sources) or bool(
            re.search(r"```mermaid\s*\n", content, re.I)
        )
    if project_type == "knowledge":
        return _has_navigation(content) and bool(re.search(r"(?m)^[-*]\s+\S+", content))
    if any(any(token in source.lower() for token in evidence_tokens) for source in sources):
        return True
    showcase = re.search(
        r"(?ims)^##\s+[^\n]*(?:showcase|demo|screenshots?|展示|演示|截图|效果)[^\n]*\n(.*?)(?=^##\s|\Z)",
        content,
    )
    if not showcase:
        return False
    body = showcase.group(1)
    return bool(re.search(r"<img\s|!\[[^]]*\]\([^)]+\)|```(?!mermaid)", body, re.I))


def _has_type_structure(content: str, project_type: str) -> bool:
    terms = {
        "cli": ["commands", "command reference", "options", "configuration", "examples", "命令", "参数", "配置", "示例"],
        "product": ["features", "highlights", "how it works", "功能", "亮点", "工作原理"],
        "ai": ["evaluation", "benchmark", "results", "method", "limitations", "评估", "结果", "方法", "局限"],
        "infrastructure": ["architecture", "deployment", "configuration", "架构", "部署", "配置"],
        "knowledge": ["contents", "categories", "index", "目录", "分类", "索引"],
        "library": ["documentation", "api", "examples", "文档", "接口", "示例"],
        "generic": ["structure", "architecture", "项目结构", "架构"],
    }
    return _contains_heading(content, terms.get(project_type, terms["generic"]))


def _type_recommendations(project_type: str) -> Dict[str, str]:
    showcase = {
        "cli": "Add a real terminal transcript or GIF showing a command and its useful output.",
        "product": "Add a real product screenshot or interactive demo; a banner alone is branding, not product evidence.",
        "ai": "Add a real result, evaluation figure, benchmark, or runnable model output.",
        "library": "Add a minimal code example and show the resulting output or behavior.",
        "infrastructure": "Add a real architecture, deployment flow, or operational output.",
        "knowledge": "Add a clear contents section and representative categorized entries.",
    }
    structure = {
        "cli": "Add a Commands, Options, Configuration, or Examples section for repeated CLI use.",
        "product": "Explain the differentiated capabilities or how the product works.",
        "ai": "Add evaluation, results, method, or limitations appropriate to the project.",
        "infrastructure": "Add architecture, deployment, or configuration guidance.",
        "knowledge": "Add a contents, categories, or index section.",
        "library": "Add API documentation or practical examples.",
    }
    return {
        "showcase": showcase.get(project_type, "Add a real screenshot, demo, output sample, benchmark figure, or architecture diagram."),
        "structure": structure.get(project_type, "Add a compact project map when it helps readers navigate the repository."),
    }


def _has_unresolved_gaps(content: str, prose: str) -> bool:
    placeholder = bool(re.search(r"\{\{[A-Z0-9_]+\}\}|\bTODO\b|<YOUR[_ -]", prose, re.I))
    gap_markers = (
        "before publishing",
        "no project screenshot is available yet",
        "add a real project banner",
        "发布前请",
        "暂无项目截图",
    )
    return placeholder or any(marker in content.lower() for marker in gap_markers)


def _has_navigation(content: str) -> bool:
    html_links = len(re.findall(r'<a\s+[^>]*href=["\']#[^"\']+', content, re.I))
    markdown_links = len(re.findall(r"\[[^]]+\]\(#[^)]+\)", content))
    return html_links + markdown_links >= 3


def analyze_readme(content: str, project_type: str = "generic") -> ReadmeReport:
    findings: List[Finding] = []
    passed: List[str] = []
    score = 0
    dimensions = {"content": 0, "presentation": 0, "onboarding": 0, "trust": 0}

    prose = re.sub(r"```.*?```", "", content, flags=re.S)
    prose = re.sub(r"`[^`]+`", "", prose)

    recommendations = _type_recommendations(project_type)
    checks = [
        ("first_screen", "content", 15, _has_first_screen_story(content),
         "The first screen does not explain the project", "Lead with the project name, audience, and concrete value proposition."),
        ("features", "content", 10, _contains_heading(content, ["features", "highlights", "功能", "亮点", "特性"]),
         "Project highlights are hard to scan", "Present 3-6 differentiated capabilities in a compact grid or list."),
        ("type_structure", "content", 5, _has_type_structure(content, project_type),
         f"The README lacks expected {project_type} reference content", recommendations["structure"]),
        ("visual_story", "presentation", 5, _has_meaningful_visual(content),
         "The README has no visual identity", "Add a useful banner, logo, product screenshot, output example, or architecture diagram."),
        ("showcase_evidence", "presentation", 10, _has_showcase_evidence(content, project_type),
         f"The README does not demonstrate the {project_type} project in use", recommendations["showcase"]),
        ("navigation", "presentation", 5, _has_navigation(content),
         "The README is difficult to scan", "Add a compact first-screen navigation row linking to the key sections."),
        ("installation", "onboarding", 10, _contains_heading(content, ["install", "setup", "安装", "部署"]),
         "Installation instructions are missing", "Add verified, copy-pasteable installation commands."),
        ("first_success", "onboarding", 15,
         _contains_heading(content, ["usage", "quick start", "getting started", "使用", "快速开始"]) and "```" in content,
         "Readers cannot reach first success quickly", "Show the shortest verified path from installation to a useful result."),
        ("documentation", "onboarding", 5, _contains_heading(content, ["docs", "documentation", "文档"]),
         "The path to deeper documentation is unclear", "Link to API docs, examples, guides, or the relevant documentation directory."),
        ("contributing", "trust", 5, _contains_heading(content, ["contribut", "贡献"]),
         "Contribution guidance is missing", "Explain how to report issues, validate changes, and submit a pull request."),
        ("license", "trust", 5, _contains_heading(content, ["license", "许可证", "许可"]),
         "License information is missing", "State the project license and link to the actual license file."),
        ("complete", "trust", 10,
         not _has_unresolved_gaps(content, prose),
         "README contains unfinished placeholders", "Resolve all placeholders and unsupported claims before publishing."),
    ]

    for code, dimension, weight, condition, message, recommendation in checks:
        if condition:
            score += weight
            dimensions[dimension] += weight
            passed.append(code)
        else:
            severity = "high" if weight >= 15 or code == "complete" else "medium"
            findings.append(Finding(code, severity, message, recommendation))

    return ReadmeReport(
        score=score,
        max_score=100,
        dimensions=dimensions,
        findings=findings,
        passed_checks=passed,
    )
