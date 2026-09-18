"""Agent workflow state and artifact contract for ReadmeMagic."""

from dataclasses import asdict, dataclass, field
import importlib.util
import json
from pathlib import Path
from typing import Dict, List

STAGES = ("discover", "inspect", "score", "plan", "optimize", "preview", "review", "apply")

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
    scores: Dict[str, int] = field(default_factory=dict)
    target: str = ""
    next_actions: List[str] = field(default_factory=list)

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
