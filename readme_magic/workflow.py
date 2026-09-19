"""Agent workflow state and artifact contract for ReadmeMagic."""

from dataclasses import asdict, dataclass, field
import importlib.util
import json
from pathlib import Path
from typing import Dict, List

STAGES = ("discover", "inspect", "score", "plan", "optimize", "preview", "review", "apply")
PREVIEW_STATUSES = ("not_generated", "generated_pending_open", "opened", "awaiting_user_review")

@dataclass
class WorkflowState:
    workflow: str = "readme-optimization"
    version: str = "1.0"
    stage: str = "discover"
    status: str = "ready"
    project_path: str = ""
    execution_mode: str = "agent_only"
    cli_available: bool = False
    completed_stages: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    findings: List[Dict[str, object]] = field(default_factory=list)
    scores: Dict[str, object] = field(default_factory=dict)
    target: str = ""
    next_actions: List[str] = field(default_factory=list)
    preview_status: str = "not_generated"

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)

def detect_cli() -> bool:
    return importlib.util.find_spec("readme_magic") is not None and importlib.util.find_spec("markdown_it") is not None

def create_state(project_path: Path, stage: str = "discover") -> WorkflowState:
    if stage not in STAGES:
        raise ValueError(f"Unknown workflow stage: {stage}. Choose one of: {', '.join(STAGES)}")
    cli_available = detect_cli()
    return WorkflowState(stage=stage, project_path=str(Path(project_path).resolve()), execution_mode="hybrid" if cli_available else "agent_only", cli_available=cli_available)

def save_state(state: WorkflowState, project_path: Path) -> Path:
    output = Path(project_path) / "artifacts" / "workflow-state.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def mark_preview_opened(project_path: Path) -> Path:
    """Mark the generated preview as opened by the host UI."""
    path = Path(project_path) / "artifacts" / "workflow-state.json"
    if not path.exists():
        raise FileNotFoundError(f"workflow state not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("preview_status") != "generated_pending_open" and payload.get("status") != "preview_pending_open":
        raise ValueError("preview cannot be marked opened before a preview is generated")
    payload["preview_status"] = "opened"
    # The optimize command exposes the user-facing pending state as
    # ``preview_pending_open`` while the lifecycle field remains
    # ``generated_pending_open``. Accept both so the host acknowledgement
    # actually reaches the workflow state.
    if payload.get("status") in {"generated_pending_open", "preview_pending_open"}:
        payload["status"] = "awaiting_user_review"
        payload["next_actions"] = ["apply", "revise", "keep_original"]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    card_path = path.parent / "interaction-card.json"
    if card_path.exists():
        card = json.loads(card_path.read_text(encoding="utf-8"))
        if card.get("status") == "preview_pending_open":
            card["status"] = "awaiting_user_review"
            card["next_actions"] = ["apply", "revise", "keep_original"]
            for event in card.get("events", []):
                if event.get("stage") == "review":
                    event["status"] = "awaiting_user_review"
                    event["label"] = "Waiting for user review"
                    event["actions"] = card["next_actions"]
        card["preview_status"] = "opened"
        card_path.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
