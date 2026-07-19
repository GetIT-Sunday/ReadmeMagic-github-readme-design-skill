"""Project inspection for grounded README generation."""

from dataclasses import asdict, dataclass, field
import json
import re
from pathlib import Path
from typing import Dict, List, Optional


IGNORED_ENTRIES = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "node_modules",
    "venv",
}


@dataclass
class EvidenceItem:
    """A README-relevant fact with a traceable repository source."""

    value: str
    source: str
    confidence: float = 1.0


@dataclass
class ProjectProfile:
    """The project archetype selected from repository signals."""

    project_type: str
    confidence: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class ProjectMetadata:
    path: str
    name: str
    description: str
    version: str
    license: str
    language: str
    language_version: str
    repo: str
    template: str
    install_commands: List[str]
    usage_commands: List[str]
    features: List[str]
    visual_assets: List[str]
    structure: str
    readme_path: Optional[str]
    project_type: str = "generic"
    type_confidence: float = 0.0
    type_reasons: List[str] = field(default_factory=list)
    evidence: Dict[str, List[EvidenceItem]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _read_text(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8")[:limit]
    except (OSError, UnicodeDecodeError):
        return ""


def _read_json(path: Path) -> Dict[str, object]:
    try:
        data = json.loads(_read_text(path))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def _toml_value(content: str, key: str, section: Optional[str] = None) -> str:
    scope = content
    if section:
        match = re.search(
            rf"(?ms)^\[{re.escape(section)}\]\s*$\n(.*?)(?=^\[|\Z)", content
        )
        scope = match.group(1) if match else ""
    match = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*["\']([^"\']+)["\']', scope)
    return match.group(1).strip() if match else ""


def _find_readme(project: Path) -> Optional[Path]:
    for name in ("README.md", "Readme.md", "readme.md", "README.MD"):
        candidate = project / name
        if candidate.is_file():
            return candidate
    return None


def _git_repo(project: Path) -> str:
    git_path = project / ".git"
    config_path = git_path / "config"
    if git_path.is_file():
        pointer = _read_text(git_path, 2_000)
        match = re.search(r"gitdir:\s*(.+)", pointer)
        if match:
            git_dir = Path(match.group(1).strip())
            if not git_dir.is_absolute():
                git_dir = project / git_dir
            config_path = git_dir / "config"
            if not config_path.exists():
                config_path = git_dir.parent.parent / "config"
    config = _read_text(config_path, 20_000)
    match = re.search(
        r"github\.com[/:]([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:\s|$)",
        config,
    )
    return f"{match.group(1)}/{match.group(2)}" if match else ""


def _detect_license(project: Path, declared: str) -> str:
    if declared:
        return declared
    for pattern in ("LICENSE*", "LICENCE*", "COPYING*"):
        for path in sorted(project.glob(pattern)):
            text = _read_text(path, 8_000).lower()
            if "mit license" in text:
                return "MIT"
            if "apache license" in text:
                return "Apache-2.0"
            if "mozilla public license" in text:
                return "MPL-2.0"
            if "gnu general public license" in text:
                return "GPL"
            if "bsd" in text:
                return "BSD"
            return path.name
    return "Not specified"


def _project_structure(project: Path, max_entries: int = 14) -> str:
    entries = [p for p in sorted(project.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
               if p.name not in IGNORED_ENTRIES and not p.name.startswith(".readme-magic")]
    visible = entries[:max_entries]
    lines = [f"{project.name}/"]
    for index, entry in enumerate(visible):
        connector = "`-- " if index == len(visible) - 1 and len(entries) <= max_entries else "|-- "
        suffix = "/" if entry.is_dir() else ""
        lines.append(f"{connector}{entry.name}{suffix}")
    if len(entries) > max_entries:
        lines.append(f"`-- ... ({len(entries) - max_entries} more)")
    return "\n".join(lines)


def _find_visual_assets(project: Path, limit: int = 12) -> List[str]:
    extensions = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
    roots = [project / name for name in ("assets", "docs", "images", "screenshots", ".github")]
    candidates = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            relative = path.relative_to(project).as_posix()
            lowered = relative.lower()
            if any(part in lowered for part in ("badge", "favicon", "social-preview")):
                continue
            priority = next(
                (index for index, token in enumerate(
                 ("screenshot", "demo", "preview", "hero", "banner", "cover", "architecture", "logo"))
                 if token in lowered),
                20,
            )
            candidates.append((priority, len(path.parts), relative))
    candidates.sort()
    return [relative for _, _, relative in candidates[:limit]]


def _asset_evidence(assets: List[str]) -> Dict[str, List[EvidenceItem]]:
    """Classify local visual assets without treating every image as a screenshot."""
    grouped: Dict[str, List[EvidenceItem]] = {
        "screenshots": [],
        "demos": [],
        "benchmarks": [],
        "architecture_assets": [],
        "brand_assets": [],
    }
    for relative in assets:
        lowered = relative.lower()
        if any(token in lowered for token in ("screenshot", "screen", "ui")):
            kind = "screenshots"
        elif any(token in lowered for token in ("demo", "preview", "output", "result")) or lowered.endswith(".gif"):
            kind = "demos"
        elif any(token in lowered for token in ("benchmark", "perf", "speed")):
            kind = "benchmarks"
        elif any(token in lowered for token in ("architecture", "diagram", "flow", "workflow")):
            kind = "architecture_assets"
        else:
            kind = "brand_assets"
        grouped[kind].append(EvidenceItem(relative, relative, 0.95))
    return grouped


def _relative_source(project: Path, path: Path) -> str:
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return path.as_posix()


def _classify_project(
    project: Path,
    pyproject: str,
    package: Dict[str, object],
    cargo: str,
    go_mod: str,
    readme_text: str,
) -> ProjectProfile:
    """Classify a repository using deterministic, explainable signals."""
    scores: Dict[str, float] = {}
    reasons: Dict[str, List[str]] = {}

    def signal(kind: str, weight: float, reason: str) -> None:
        scores[kind] = scores.get(kind, 0.0) + weight
        reasons.setdefault(kind, []).append(reason)

    # Manifest signals are more reliable than README prose, which may mention
    # unrelated ecosystems while documenting the project.
    config_text = " ".join((pyproject, json.dumps(package), cargo, go_mod)).lower()
    readme_lower = readme_text.lower()
    package_scripts = package.get("scripts") if isinstance(package, dict) else {}
    has_cli_entry = bool(
        re.search(r"(?ms)^\[project\.scripts\]", pyproject)
        or (isinstance(package, dict) and package.get("bin"))
        or any(token in config_text for token in ("click", "typer", "argparse", "commander", "oclif"))
    )
    has_ai_signal = any(
        token in config_text
        for token in (
            "pytorch", "torch", "tensorflow", "transformers", "scikit-learn",
            "langchain", "llama", "ollama", "diffusers", "huggingface",
            "openai-agents", "crewai", "autogen",
        )
    )
    has_web_signal = any(
        token in config_text
        for token in ("react", "next", "vue", "vite", "svelte", "angular", "fastapi", "django", "flask")
    ) or (isinstance(package_scripts, dict) and any(key in package_scripts for key in ("dev", "start")))
    has_infra_signal = any(
        (project / name).exists()
        for name in (
            "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml",
            "Dockerfile", "helm", "k8s", "terraform",
        )
    ) or any(token in config_text for token in ("kubernetes", "docker", "terraform", "helm"))
    has_knowledge_signal = any(
        token in f"{project.name.lower()} {readme_lower}"
        for token in ("awesome", "roadmap", "tutorial", "curriculum", "learning resources", "interview guide")
    )

    if has_cli_entry:
        signal("cli", 6.0, "Found a command-line entry point or CLI framework")
    if has_ai_signal:
        signal("ai", 5.0, "Found an AI/ML/model or agent dependency signal")
    if has_infra_signal:
        signal("infrastructure", 4.0, "Found deployment or infrastructure configuration")
    if has_web_signal:
        signal("product", 4.0, "Found web application or server framework signals")
    if has_knowledge_signal and not (pyproject or package or cargo or go_mod):
        signal("knowledge", 5.0, "Repository content resembles a curated guide or knowledge base")
    if (pyproject or package or cargo or go_mod) and not has_cli_entry and not has_web_signal:
        signal("library", 3.5, "Found a package manifest without a CLI or product entry point")
    if (project / "src").is_dir() and (project / "tests").is_dir():
        signal("library", 0.8, "Found src and tests directories")

    if not scores:
        return ProjectProfile("generic", 0.4, ["No strong project-type signal was found"])

    project_type = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = min(0.98, max(0.55, 0.5 + scores[project_type] / max(total, 1.0) * 0.48))
    ordered_scores = sorted(scores.values(), reverse=True)
    if len(ordered_scores) > 1 and ordered_scores[0] - ordered_scores[1] < 1.0:
        confidence = min(confidence, 0.68)
    return ProjectProfile(project_type, round(confidence, 2), reasons.get(project_type, []))


def _existing_description(readme: Optional[Path]) -> str:
    if not readme:
        return ""
    text = _read_text(readme, 30_000)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    for paragraph in re.split(r"\n\s*\n", text):
        cleaned = paragraph.strip()
        if not cleaned or cleaned.startswith(("#", "<", "![", "[![", "```")):
            continue
        cleaned = re.sub(r"[*_`>#]", "", cleaned).strip()
        if 20 <= len(cleaned) <= 300:
            return " ".join(cleaned.split())
    return ""


def _build_evidence(
    project: Path,
    pyproject: str,
    package: Dict[str, object],
    cargo: str,
    go_mod: str,
    readme: Optional[Path],
    metadata: ProjectMetadata,
) -> Dict[str, List[EvidenceItem]]:
    """Collect README facts while retaining where each fact came from."""
    evidence: Dict[str, List[EvidenceItem]] = {
        "project_metadata": [],
        "installation_commands": [],
        "usage_commands": [],
        "features": [],
        "screenshots": [],
        "demos": [],
        "benchmarks": [],
        "architecture_assets": [],
        "brand_assets": [],
        "documentation_links": [],
        "license": [],
        "contribution_guide": [],
        "security_policy": [],
    }
    config_sources = (
        ("pyproject.toml", pyproject),
        ("package.json", json.dumps(package) if package else ""),
        ("Cargo.toml", cargo),
        ("go.mod", go_mod),
    )
    for source, content in config_sources:
        if content:
            evidence["project_metadata"].append(EvidenceItem(source, source, 1.0))

    readme_text = _read_text(readme) if readme else ""
    description_source = _relative_source(project, readme) if readme and metadata.description in readme_text else "project manifest"
    evidence["project_metadata"].append(
        EvidenceItem(metadata.description, description_source, 0.85)
    )

    command_source = (
        "pyproject.toml" if pyproject else
        "package.json" if package else
        "Cargo.toml" if cargo else
        "go.mod" if go_mod else
        "repository"
    )
    evidence["installation_commands"].extend(
        EvidenceItem(command, command_source, 1.0)
        for command in metadata.install_commands
        if not command.startswith("Follow the project-specific")
    )
    evidence["usage_commands"].extend(
        EvidenceItem(command, command_source, 0.95)
        for command in metadata.usage_commands
        if not command.startswith("See the documentation")
    )

    for key, values in _asset_evidence(metadata.visual_assets).items():
        evidence[key].extend(values)
    for directory, label in (
        ("docs", "Project documentation"),
        ("examples", "Runnable examples"),
        ("tests", "Automated test suite"),
    ):
        path = project / directory
        if path.is_dir():
            evidence["features"].append(EvidenceItem(label, directory, 0.95))
    if (project / "docs").is_dir():
        evidence["documentation_links"].append(EvidenceItem("docs/", "docs", 1.0))

    for candidate in (project / "CONTRIBUTING.md", project / ".github" / "CONTRIBUTING.md"):
        if candidate.is_file():
            source = _relative_source(project, candidate)
            evidence["contribution_guide"].append(EvidenceItem(source, source, 1.0))
    for candidate in (project / "SECURITY.md", project / ".github" / "SECURITY.md"):
        if candidate.is_file():
            source = _relative_source(project, candidate)
            evidence["security_policy"].append(EvidenceItem(source, source, 1.0))
    license_candidates = (
        sorted(project.glob("LICENSE*"))
        + sorted(project.glob("LICENCE*"))
        + sorted(project.glob("COPYING*"))
    )
    if license_candidates:
        source = _relative_source(project, license_candidates[0])
        evidence["license"].append(EvidenceItem(metadata.license, source, 1.0))
    elif metadata.license != "Not specified":
        evidence["license"].append(EvidenceItem(metadata.license, "project manifest", 0.9))
    return evidence


def inspect_project(project_path: Path) -> ProjectMetadata:
    project = project_path.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"Project directory not found: {project}")

    pyproject = _read_text(project / "pyproject.toml")
    package = _read_json(project / "package.json")
    cargo = _read_text(project / "Cargo.toml")
    go_mod = _read_text(project / "go.mod")
    readme = _find_readme(project)
    readme_text = _read_text(readme, 80_000) if readme else ""

    name = str(package.get("name") or "")
    description = str(package.get("description") or "")
    version = str(package.get("version") or "")
    declared_license = str(package.get("license") or "")
    language = ""
    language_version = ""
    install_commands: List[str] = []
    usage_commands: List[str] = []
    template = "standard"

    if pyproject:
        name = _toml_value(pyproject, "name", "project") or name
        description = _toml_value(pyproject, "description", "project") or description
        version = _toml_value(pyproject, "version", "project") or version
        declared_license = _toml_value(pyproject, "license", "project") or declared_license
        language = "Python"
        language_version = _toml_value(pyproject, "requires-python", "project").lstrip(">=")
        install_commands = ["pip install -e ."]
        scripts_match = re.search(r"(?ms)^\[project\.scripts\]\s*$\n(.*?)(?=^\[|\Z)", pyproject)
        if scripts_match:
            command = re.search(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*=", scripts_match.group(1))
            if command:
                usage_commands = [f"{command.group(1)} --help"]
                template = "cli-tool"
    elif package:
        language = "JavaScript / TypeScript"
        engines = package.get("engines")
        if isinstance(engines, dict):
            language_version = str(engines.get("node") or "")
        package_manager = "npm"
        if (project / "pnpm-lock.yaml").exists():
            package_manager = "pnpm"
        elif (project / "yarn.lock").exists():
            package_manager = "yarn"
        install_commands = [f"{package_manager} install"]
        scripts = package.get("scripts")
        if isinstance(scripts, dict):
            preferred = next((s for s in ("dev", "start", "build") if s in scripts), "")
            if preferred:
                usage_commands = [f"{package_manager} run {preferred}"]
    elif cargo:
        name = _toml_value(cargo, "name", "package") or name
        description = _toml_value(cargo, "description", "package") or description
        version = _toml_value(cargo, "version", "package") or version
        declared_license = _toml_value(cargo, "license", "package") or declared_license
        language, install_commands, usage_commands = "Rust", ["cargo build --release"], ["cargo run"]
    elif go_mod:
        module = re.search(r"(?m)^module\s+(\S+)", go_mod)
        name = (module.group(1).rsplit("/", 1)[-1] if module else name)
        language, install_commands, usage_commands = "Go", ["go mod download"], ["go run ."]

    name = name or project.name
    description = description or _existing_description(readme) or f"{name} project."
    version = version or "Not specified"
    license_name = _detect_license(project, declared_license)
    repo = _git_repo(project)
    if not repo and package:
        repository = package.get("repository")
        repository_url = repository.get("url", "") if isinstance(repository, dict) else repository
        match = re.search(
            r"github\.com[/:]([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?$",
            str(repository_url or ""),
        )
        if match:
            repo = f"{match.group(1)}/{match.group(2)}"

    profile = _classify_project(project, pyproject, package, cargo, go_mod, readme_text)
    template_by_type = {
        "ai": "ai-project",
        "cli": "cli-tool",
        "library": "library",
        "personal": "personal",
    }
    template = template_by_type.get(profile.project_type, "standard")

    features = []
    if language:
        features.append(f"Built with {language}")
    if (project / "tests").is_dir() or any(project.glob("test_*.py")):
        features.append("Includes an automated test suite")
    if (project / "docs").is_dir():
        features.append("Includes project documentation")
    if (project / "examples").is_dir():
        features.append("Ships with runnable examples")
    if not features:
        features.append("Simple project setup and usage")

    metadata = ProjectMetadata(
        path=str(project),
        name=name,
        description=description,
        version=version,
        license=license_name,
        language=language or "Other",
        language_version=language_version,
        repo=repo,
        template=template,
        install_commands=install_commands or ["Follow the project-specific installation instructions."],
        usage_commands=usage_commands or ["See the documentation for usage examples."],
        features=features,
        visual_assets=_find_visual_assets(project),
        structure=_project_structure(project),
        readme_path=str(readme) if readme else None,
        project_type=profile.project_type,
        type_confidence=profile.confidence,
        type_reasons=profile.reasons,
    )
    metadata.evidence = _build_evidence(
        project, pyproject, package, cargo, go_mod, readme, metadata
    )
    return metadata
