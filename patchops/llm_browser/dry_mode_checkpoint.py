"""Commit and broad-validation checkpoint for llm-browser dry mode.

This module produces a passive operator checkpoint. It does not mutate the
repository and does not run broad pytest by itself. It reports:

- dry-mode release-gate status;
- git status summary;
- whether a commit is recommended;
- suggested commit command;
- suggested broad validation commands.

Safety:
- no browser starts;
- no Selenium driver starts;
- no download click occurs;
- no PatchOps command is run;
- no composer paste/send occurs;
- no git commit/push is performed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable, Sequence

from .dry_mode_release_gate import ReleaseGateReport, evaluate_dry_mode_release_gate


RunCommand = Callable[[Sequence[str], Path, int], tuple[int, str, str]]


DEFAULT_BROAD_VALIDATION_COMMANDS: tuple[str, ...] = (
    "py -m patchops.cli llm-browser release-gate --repo-root C:\\dev\\patchops --json",
    "py -m patchops.cli llm-browser doctor --browser none --json",
    "py -m pytest -q",
)

DEFAULT_COMMIT_MESSAGE = "D0.29 checkpoint browser runner dry mode"


@dataclass(frozen=True)
class GitCheckpoint:
    available: bool
    exit_code: int | None
    status_text: str
    stderr: str
    dirty: bool

    def to_payload(self) -> dict[str, object]:
        return {
            "available": self.available,
            "exit_code": self.exit_code,
            "dirty": self.dirty,
            "status_text": self.status_text,
            "stderr": self.stderr,
            "changed_line_count": len([line for line in self.status_text.splitlines() if line.strip()]),
        }


@dataclass(frozen=True)
class DryModeCheckpointReport:
    name: str
    ok: bool
    release_gate: ReleaseGateReport
    git: GitCheckpoint
    commit_recommended: bool
    commit_hint: str
    broad_validation_commands: tuple[str, ...]
    notes: tuple[str, ...]

    @property
    def status(self) -> str:
        return "PASS" if self.ok else "FAIL"

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "release_gate": self.release_gate.to_payload(),
            "git": self.git.to_payload(),
            "commit_recommended": self.commit_recommended,
            "commit_hint": self.commit_hint,
            "broad_validation_commands": list(self.broad_validation_commands),
            "notes": list(self.notes),
        }


def _default_run_command(args: Sequence[str], cwd: Path, timeout_seconds: int) -> tuple[int, str, str]:
    completed = subprocess.run(
        list(args),
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_seconds,
    )
    return completed.returncode, completed.stdout, completed.stderr


def read_git_checkpoint(
    repo_root: str | Path,
    *,
    run_command: RunCommand = _default_run_command,
    timeout_seconds: int = 120,
) -> GitCheckpoint:
    root = Path(repo_root)
    try:
        exit_code, stdout, stderr = run_command(("git", "status", "--short", "--branch"), root, timeout_seconds)
    except FileNotFoundError as exc:
        return GitCheckpoint(
            available=False,
            exit_code=None,
            status_text="",
            stderr=str(exc),
            dirty=False,
        )
    except Exception as exc:
        return GitCheckpoint(
            available=False,
            exit_code=None,
            status_text="",
            stderr=repr(exc),
            dirty=False,
        )

    changed_lines = [
        line
        for line in stdout.splitlines()
        if line.strip() and not line.startswith("##")
    ]

    return GitCheckpoint(
        available=exit_code == 0,
        exit_code=exit_code,
        status_text=stdout.strip(),
        stderr=stderr.strip(),
        dirty=bool(changed_lines),
    )


def build_commit_hint(
    *,
    commit_message: str = DEFAULT_COMMIT_MESSAGE,
) -> str:
    sanitized = commit_message.replace('"', "'").strip() or DEFAULT_COMMIT_MESSAGE
    return f'git add -A; git commit -m "{sanitized}"'


def evaluate_dry_mode_checkpoint(
    *,
    repo_root: str | Path | None = None,
    run_command: RunCommand = _default_run_command,
    broad_validation_commands: Sequence[str] = DEFAULT_BROAD_VALIDATION_COMMANDS,
    commit_message: str = DEFAULT_COMMIT_MESSAGE,
) -> DryModeCheckpointReport:
    root = Path.cwd() if repo_root is None else Path(repo_root)
    release_gate = evaluate_dry_mode_release_gate(repo_root=root)
    git = read_git_checkpoint(root, run_command=run_command)

    notes: list[str] = []
    if not git.available:
        notes.append("Git status could not be read; inspect the repository manually before committing.")
    elif git.dirty:
        notes.append("Repository has uncommitted changes; commit after broad validation passes.")
    else:
        notes.append("Repository appears clean; no commit is currently required.")

    notes.append("This checkpoint is passive and does not run git commit, git push, or broad pytest automatically.")

    ok = release_gate.ok and (git.available or git.exit_code is None)
    return DryModeCheckpointReport(
        name="llm_browser_commit_broad_validation_checkpoint",
        ok=ok,
        release_gate=release_gate,
        git=git,
        commit_recommended=bool(git.available and git.dirty),
        commit_hint=build_commit_hint(commit_message=commit_message),
        broad_validation_commands=tuple(broad_validation_commands),
        notes=tuple(notes),
    )


def render_checkpoint_report(report: DryModeCheckpointReport) -> str:
    lines: list[str] = []
    lines.append(f"Checkpoint: {report.name}")
    lines.append(f"Status    : {report.status}")
    lines.append(f"ExitCode  : {report.exit_code}")
    lines.append("")
    lines.append("Release gate:")
    lines.append(f"- Status: {report.release_gate.status}")
    for check in report.release_gate.checks:
        lines.append(f"- {check.status} {check.name}: {check.details}")
    lines.append("")
    lines.append("Git:")
    lines.append(f"- Available: {str(report.git.available).lower()}")
    lines.append(f"- Dirty    : {str(report.git.dirty).lower()}")
    if report.git.status_text:
        lines.append("- Status text:")
        for line in report.git.status_text.splitlines():
            lines.append(f"  {line}")
    if report.git.stderr:
        lines.append("- Stderr:")
        for line in report.git.stderr.splitlines():
            lines.append(f"  {line}")
    lines.append("")
    lines.append(f"Commit recommended: {str(report.commit_recommended).lower()}")
    lines.append(f"Commit hint        : {report.commit_hint}")
    lines.append("")
    lines.append("Broad validation commands:")
    for command in report.broad_validation_commands:
        lines.append(f"- {command}")
    lines.append("")
    lines.append("Notes:")
    for note in report.notes:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
