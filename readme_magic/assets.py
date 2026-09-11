"""Project-aware visual asset planning and image-provider integration.

The planner is deliberately useful without an image API: ``prompt_only``
produces reproducible prompts and an asset manifest that a user can complete
with any web image tool.  API generation is opt-in and never replaces runtime
evidence such as screenshots or CLI recordings.
"""

from dataclasses import asdict, dataclass, field
import base64
import json
import os
from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional
import urllib.error
import urllib.request

from .analyzer import ProjectMetadata


IMAGE_MODES = ("api", "prompt_only", "disabled")
DEFAULT_CONFIG = {
    "mode": "prompt_only",
    "provider": "openai",
    "model": "gpt-image-1",
    "api_key_env": "OPENAI_API_KEY",
    "base_url": "https://api.openai.com/v1",
    "output_dir": "assets/generated",
    "image_format": "png",
}


@dataclass
class ImageGenerationConfig:
    mode: str = "prompt_only"
    provider: str = "openai"
    model: str = "gpt-image-1"
    api_key_env: str = "OPENAI_API_KEY"
    base_url: str = "https://api.openai.com/v1"
    output_dir: str = "assets/generated"
    image_format: str = "png"

    def validate(self) -> "ImageGenerationConfig":
        if self.mode not in IMAGE_MODES:
            raise ValueError(f"image mode must be one of: {', '.join(IMAGE_MODES)}")
        if not self.provider.strip():
            raise ValueError("image provider cannot be empty")
        if not self.model.strip():
            raise ValueError("image model cannot be empty")
        if self.image_format.lower() not in ("png", "jpg", "jpeg", "webp"):
            raise ValueError("image format must be png, jpg, jpeg, or webp")
        return self

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class AssetSpec:
    key: str
    kind: str
    purpose: str
    section: str
    filename: str
    prompt: str
    required: bool = True
    source: str = "repository"
    status: str = "planned"
    path: str = ""
    error: str = ""


@dataclass
class AssetManifest:
    project: str
    mode: str
    provider: str
    model: str
    assets: List[AssetSpec] = field(default_factory=list)
    paper_sources: List[str] = field(default_factory=list)
    paper_context: Dict[str, str] = field(default_factory=dict)
    optional_skills: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["assets"] = [asdict(asset) for asset in self.assets]
        return payload


def _read_json(path: Path) -> Dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def load_image_config(
    project: Path,
    config_path: Optional[Path] = None,
    overrides: Optional[Dict[str, object]] = None,
) -> ImageGenerationConfig:
    """Load ``.readme-magic.json`` and apply explicit CLI overrides."""
    candidates = [config_path] if config_path else [project / ".readme-magic.json"]
    values: Dict[str, object] = dict(DEFAULT_CONFIG)
    for candidate in candidates:
        if candidate and candidate.is_file():
            loaded = _read_json(candidate)
            section = loaded.get("image_generation")
            values.update(section if isinstance(section, dict) else loaded)
            break
    for key, value in (overrides or {}).items():
        if value is not None:
            values[key] = value
    allowed = set(DEFAULT_CONFIG)
    config = ImageGenerationConfig(**{key: values[key] for key in allowed if key in values})
    return config.validate()


def discover_paper_sources(project: Path, limit: int = 8) -> List[str]:
    """Find local paper material and paper links without downloading anything."""
    sources: List[str] = []
    for path in sorted(project.rglob("*")):
        if not path.is_file() or any(part in {".git", "node_modules", "dist", "build"} for part in path.parts):
            continue
        if path.suffix.lower() in {".pdf", ".tex", ".bib", ".cff"}:
            relative = path.relative_to(project).as_posix()
            if any(token in relative.lower() for token in ("paper", "publication", "manuscript", "supplement", "citation")) or path.suffix.lower() in {".pdf", ".tex"}:
                sources.append(relative)
        if len(sources) >= limit:
            break
    readme = project / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8", errors="ignore")
        for url in re.findall(r"https?://(?:arxiv\.org|doi\.org)/[^)\s]+", text, re.I):
            if url not in sources:
                sources.append(url.rstrip(".,"))
    return sources[:limit]


def extract_paper_context(project: Path, sources: Iterable[str]) -> Dict[str, str]:
    """Extract safe, small context snippets from local LaTeX sources."""
    context: Dict[str, str] = {}
    for source in sources:
        if not source.endswith(".tex"):
            continue
        path = project / source
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        title = re.search(r"\\title\s*\{([^{}]+)\}", text, re.S)
        abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.S | re.I)
        captions = re.findall(r"\\caption\s*\{([^{}]+)\}", text, re.S)
        if title:
            context["title"] = " ".join(title.group(1).split())[:300]
        if abstract:
            context["abstract"] = " ".join(abstract.group(1).split())[:1000]
        if captions:
            context["figure_captions"] = " | ".join(" ".join(item.split()) for item in captions[:5])[:1200]
        if context:
            context["source"] = source
            break
    return context


def _prompt(
    metadata: ProjectMetadata,
    key: str,
    purpose: str,
    paper_sources: Iterable[str],
    paper_context: Optional[Dict[str, str]] = None,
) -> str:
    evidence = []
    for category in ("project_metadata", "installation_commands", "usage_commands", "architecture_assets", "benchmarks"):
        evidence.extend(item.value for item in metadata.evidence.get(category, [])[:3])
    paper = ", ".join(paper_sources) if paper_sources else "No paper source detected"
    paper_detail = " ".join(
        value for name, value in (paper_context or {}).items() if name != "source"
    )[:1800]
    return (
        f"Create a GitHub README visual for the project '{metadata.name}'.\n"
        f"Project type: {metadata.project_type}.\n"
        f"Project description: {metadata.description}\n"
        f"Visual purpose: {purpose}\n"
        f"Repository evidence to reflect faithfully: {'; '.join(evidence) or 'repository structure and documented workflow'}\n"
        f"Paper sources (use only as factual context): {paper}\n"
        f"Paper context: {paper_detail or 'No local LaTeX context extracted'}\n"
        "Style: clear technical editorial illustration, high contrast, generous whitespace,"
        " GitHub-friendly, no stock-photo look, no fake UI, no unsupported metrics.\n"
        "Do not invent features, numbers, logos, people, or product screens.\n"
        "Use only a short project title as visible text; avoid paragraphs and tiny labels."
    )


def plan_assets(metadata: ProjectMetadata, config: ImageGenerationConfig) -> AssetManifest:
    """Create mandatory visual plans plus capability-gated optional skills."""
    project = Path(metadata.path)
    paper_sources = discover_paper_sources(project)
    paper_context = extract_paper_context(project, paper_sources)
    raw_output_dir = config.output_dir.strip() or DEFAULT_CONFIG["output_dir"]
    output_path = Path(raw_output_dir)
    output_parts = output_path.parts
    if output_path.is_absolute() or ".." in output_parts:
        raise ValueError("image output_dir must be a relative path inside the project")
    output_dir = output_path.as_posix().lstrip("./")
    section_names = {
        "architecture": "Architecture / How It Works",
        "workflow": "Workflow / Quick Start",
        "introduction": "Overview",
    }
    purposes = {
        "architecture": "Explain the major modules and data flow as a repository-grounded architecture diagram.",
        "workflow": "Show the shortest user journey from input or setup to a useful result.",
        "introduction": "Communicate the project's identity, audience, and concrete value at a glance.",
    }
    assets = []
    for key in ("introduction", "architecture", "workflow"):
        assets.append(AssetSpec(
            key=key,
            kind="diagram" if key != "introduction" else "illustration",
            purpose=purposes[key],
            section=section_names[key],
            filename=f"{output_dir}/{key}.{config.image_format.lower()}",
            prompt=_prompt(metadata, key, purposes[key], paper_sources, paper_context),
            source="paper" if paper_sources else "repository",
        ))
    optional = {
        "cli-demo": metadata.project_type == "cli",
        "screenshot": metadata.project_type == "product" or bool(metadata.evidence.get("screenshots")),
        "paper-extractor": bool(paper_sources),
        "benchmark-visualizer": bool(metadata.evidence.get("benchmarks")),
    }
    return AssetManifest(
        metadata.name, config.mode, config.provider, config.model,
        assets, paper_sources, paper_context, optional,
    )


def _api_image(prompt: str, config: ImageGenerationConfig, destination: Path) -> None:
    key = os.environ.get(config.api_key_env, "").strip()
    if not key:
        raise RuntimeError(f"set {config.api_key_env} before using image mode 'api'")
    endpoint = config.base_url.rstrip("/") + "/images/generations"
    payload = json.dumps({
        "model": config.model,
        "prompt": prompt,
        "size": "1536x1024",
        "output_format": config.image_format.lower(),
    }).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
    }, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"image provider returned HTTP {exc.code}: {detail}") from exc
    items = data.get("data") or []
    if not items:
        raise RuntimeError("image provider returned no image data")
    item = items[0]
    if item.get("b64_json"):
        destination.write_bytes(base64.b64decode(item["b64_json"]))
        return
    if item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=60) as image_response:
            destination.write_bytes(image_response.read())
        return
    raise RuntimeError("image provider response had neither b64_json nor url")


def materialize_assets(
    project: Path,
    manifest: AssetManifest,
    config: ImageGenerationConfig,
    write_prompts: bool = True,
) -> AssetManifest:
    """Generate images or write prompts and a manifest; never fabricates evidence."""
    artifacts = project / "artifacts"
    prompt_dir = artifacts / "prompts"
    if write_prompts and config.mode == "prompt_only":
        prompt_dir.mkdir(parents=True, exist_ok=True)
    for asset in manifest.assets:
        if config.mode == "disabled":
            asset.status = "disabled"
            continue
        if config.mode == "prompt_only":
            if not write_prompts:
                asset.status = "prompt_ready"
                asset.path = asset.filename
                continue
            (prompt_dir / f"{asset.key}.prompt.md").write_text(asset.prompt + "\n", encoding="utf-8")
            asset.status = "prompt_ready"
            asset.path = asset.filename
            continue
        destination = project / asset.filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            _api_image(asset.prompt, config, destination)
            asset.status = "generated"
            asset.path = asset.filename
        except (RuntimeError, OSError) as exc:
            asset.status = "error"
            asset.error = str(exc)
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "asset-manifest.json").write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def asset_summary(manifest: AssetManifest) -> Dict[str, int]:
    summary: Dict[str, int] = {}
    for asset in manifest.assets:
        summary[asset.status] = summary.get(asset.status, 0) + 1
    return summary
