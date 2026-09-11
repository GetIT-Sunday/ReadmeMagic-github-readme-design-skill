"""Opt-in runtime evidence capture for README optimization."""

from pathlib import Path
import shlex
import subprocess
from typing import List


def capture_command(project: Path, command: str, timeout: int = 20) -> Path:
    """Run an explicit command in the project and save a readable transcript.

    The command is tokenized without a shell so shell metacharacters cannot
    expand into unrelated commands. It is intentionally opt-in.
    """
    if not command.strip():
        raise ValueError("demo command cannot be empty")
    if len(command) > 500:
        raise ValueError("demo command is too long")
    try:
        argv: List[str] = shlex.split(command)
    except ValueError as exc:
        raise ValueError(f"invalid demo command: {exc}") from exc
    if not argv:
        raise ValueError("demo command cannot be empty")
    try:
        completed = subprocess.run(
            argv,
            cwd=project,
            capture_output=True,
            text=True,
            timeout=max(1, min(timeout, 120)),
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        status = f"exit code: {completed.returncode}"
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + "\n[ReadmeMagic: command timed out]"
        status = "timeout"
    destination = project / "artifacts" / "runtime" / "cli-transcript.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        f"```console\n$ {command}\n{output.rstrip()}\n[{status}]\n```\n",
        encoding="utf-8",
    )
    return destination
