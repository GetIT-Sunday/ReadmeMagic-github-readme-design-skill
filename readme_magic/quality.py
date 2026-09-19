"""README presentation and content quality checks used by the CLI and skill."""

from dataclasses import asdict, dataclass
import re
from typing import Dict, List


# The score intentionally separates required documentation quality from optional
# showcase polish.  A project must be understandable and usable without having
# to ship a GIF, screenshot, or custom architecture illustration.
CORE_SCORE_MAX = 70
PRESENTATION_SCORE_MAX = 30


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
    strict_evidence_gate: bool = False

    def to_dict(self) -> Dict[str, object]:
        strict_gate = self.strict_evidence_gate
        core_score = self.dimensions.get("content", 0) + self.dimensions.get("onboarding", 0) + self.dimensions.get("trust", 0)
        presentation_score = self.dimensions.get("presentation", 0)
        # 80% of the required/core points is enough for a usable README. Visual
        # evidence remains visible as an enhancement score rather than a hard
        # prerequisite for basic documentation quality.
        core_quality_gate = core_score >= 56
        tier = "exceptional" if self.score >= 95 and strict_gate else (
            "excellent" if self.score >= 90 else
            "strong" if self.score >= 80 else
            "usable" if self.score >= 60 else "incomplete"
        )
        return {
            "score": self.score,
            "max_score": self.max_score,
            "dimensions": self.dimensions,
            "core_score": core_score,
            "core_max_score": CORE_SCORE_MAX,
            "presentation_score": presentation_score,
            "presentation_max_score": PRESENTATION_SCORE_MAX,
            "core_quality_gate": core_quality_gate,
            "findings": [asdict(item) for item in self.findings],
            "passed_checks": self.passed_checks,
            "strict_evidence_gate": strict_gate,
            "tier": tier,
            "score_kind": "automated_preflight",
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
    # A visual in a later Showcase section or footer must not make the first
    # screen look complete. Stop at the first major section heading.
    first_section = re.search(r"(?m)^##\s+", content)
    first_screen = content[:first_section.start()] if first_section else content[:2_500]
    sources = _image_sources(first_screen)
    ignored = (
        "img.shields.io", "badge", "contrib.rocks", "github-readme-stats",
        "star-history", "banner", "hero", "cover", "logo",
    )
    return any(not any(token in source.lower() for token in ignored) for source in sources)


def _has_visual_identity(content: str) -> bool:
    """Allow a logo/banner to establish identity, but not product proof."""
    sources = _image_sources(content[:3_500])
    ignored = ("img.shields.io", "badge", "contrib.rocks", "github-readme-stats", "star-history")
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
        if has_command:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            # Project commands can emit arbitrary text; a non-status line after
            # the prompt is still useful runtime evidence.
            if len(lines) >= 2 and any(
                not line.startswith(("$", ">", "[")) for line in lines[1:]
            ):
                return True
        if has_command and has_output:
            return True
    return False


def _has_verified_runtime_evidence(content: str, project_type: str) -> bool:
    """Require evidence that a command was actually run, not merely listed."""
    if project_type not in ("cli", "ai", "product"):
        return False
    verified_marker = re.compile(
        r"(?i)(verified\s+(?:runtime|command|output)|captured\s+output|exit\s+code|"
        r"valid\s+records\s*:|rendered\s+\d+\s+sample|success(?:fully)?\b)"
    )
    for language, block in _code_blocks(content):
        if language not in ("", "bash", "shell", "console", "terminal", "text"):
            continue
        if not re.search(r"(?m)^(?:\$|>)\s*\S+", block):
            continue
        if verified_marker.search(block) or re.search(r"(?i)\b(?:project|type|valid records|rendered)\s*:", block):
            return True
    # A GIF/video can be a direct runtime proof when its name is descriptive.
    return any(
        source.lower().endswith((".gif", ".mp4", ".webm"))
        and any(token in source.lower() for token in ("demo", "run", "terminal", "usage", "preview"))
        for source in _image_sources(content)
    )


def _has_architecture_visual(content: str, project_type: str) -> bool:
    """Mermaid is useful, but a polished architecture visual needs an image."""
    if project_type not in ("cli", "ai", "infrastructure", "product"):
        return True
    sources = _image_sources(content)
    return any(
        not any(token in source.lower() for token in ("badge", "star-history", "logo", "banner", "hero"))
        and any(token in source.lower() for token in ("architecture", "diagram", "workflow", "pipeline", "system"))
        for source in sources
    )


def _has_dynamic_demo(content: str, project_type: str) -> bool:
    """Dynamic evidence is expected for runnable or visual products."""
    if project_type not in ("cli", "ai", "product"):
        return True
    return any(source.lower().endswith((".gif", ".mp4", ".webm")) for source in _image_sources(content))


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
    # A missing optional showcase asset is reported by the presentation checks;
    # it is not an unfinished README placeholder. Only explicit authoring gaps
    # should fail the completeness check.
    gap_markers = ("发布前请",)
    explicit_publish_gap = bool(re.search(
        r"(?i)\b(?:add|define|resolve|provide)\b[^.\n]{0,140}\bbefore publishing\b",
        content,
    ))
    return placeholder or explicit_publish_gap or any(marker in content.lower() for marker in gap_markers)


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
        ("first_screen", "content", 12, _has_first_screen_story(content),
         "The first screen does not explain the project", "Lead with the project name, audience, and concrete value proposition."),
        ("features", "content", 8, _contains_heading(content, ["features", "highlights", "功能", "核心能力", "亮点", "特性"]),
         "Project highlights are hard to scan", "Present 3-6 differentiated capabilities in a compact grid or list."),
        ("type_structure", "content", 5, _has_type_structure(content, project_type),
         f"The README lacks expected {project_type} reference content", recommendations["structure"]),
        ("visual_story", "presentation", 6, _has_meaningful_visual(content),
         "The first screen has no meaningful project visual", "Place a real or native-generated hero visual in the first screen; badges and Star History do not count."),
        ("showcase_evidence", "presentation", 9,
         _has_showcase_evidence(content, project_type) and (
             project_type not in ("cli", "ai", "product") or _has_verified_runtime_evidence(content, project_type)
         ),
         f"The README does not demonstrate the {project_type} project with verified evidence",
         "Add a real runtime transcript, GIF, screenshot, output sample, benchmark, or runnable demo; descriptive prose alone does not count."),
        ("architecture_quality", "presentation", 6, _has_architecture_visual(content, project_type),
         "The architecture explanation is not presented as a polished visual",
         "Use a repository-grounded PNG/SVG architecture or workflow figure. Mermaid may supplement it but does not receive full credit by itself."),
        ("dynamic_demo", "presentation", 3, _has_dynamic_demo(content, project_type),
         "The README lacks dynamic demonstration evidence",
         "Add a short, real GIF or video for runnable/visual projects when the workflow can be captured; mark it unavailable when the project cannot be run."),
        ("visual_identity", "presentation", 3, _has_visual_identity(content),
         "The README has no coherent visual identity",
         "Add a project-owned logo, banner, or visual system without treating it as runtime evidence."),
        ("navigation", "presentation", 3, _has_navigation(content),
         "The README is difficult to scan", "Add a compact first-screen navigation row linking to the key sections."),
        ("installation", "onboarding", 8, _contains_heading(content, ["install", "setup", "安装", "部署"]),
         "Installation instructions are missing", "Add verified, copy-pasteable installation commands."),
        ("first_success", "onboarding", 10,
         _contains_heading(content, ["usage", "quick start", "getting started", "使用", "快速开始"]) and "```" in content,
         "Readers cannot reach first success quickly", "Show the shortest verified path from installation to a useful result."),
        ("documentation", "onboarding", 7, _contains_heading(content, ["docs", "documentation", "文档"]),
         "The path to deeper documentation is unclear", "Link to API docs, examples, guides, or the relevant documentation directory."),
        ("contributing", "trust", 5, _contains_heading(content, ["contribut", "贡献"]),
         "Contribution guidance is missing", "Explain how to report issues, validate changes, and submit a pull request."),
        ("license", "trust", 3, _contains_heading(content, ["license", "许可证", "许可"]),
         "License information is missing", "State the project license and link to the actual license file."),
        ("complete", "trust", 12,
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

    passed_set = set(passed)
    strict_gate = all(code in passed_set for code in ("visual_story", "showcase_evidence", "architecture_quality"))
    if project_type in ("cli", "ai", "product"):
        strict_gate = strict_gate and "dynamic_demo" in passed_set
    return ReadmeReport(
        score=score,
        max_score=100,
        dimensions=dimensions,
        findings=findings,
        passed_checks=passed,
        strict_evidence_gate=strict_gate,
    )
