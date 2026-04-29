"""PatchOps subprocess runner for the optional LLM browser runner.

This module is the narrow bridge from a prepared downloaded artifact to the
PatchOps CLI. It is deliberately explicit and fail-closed:
- importing it does not run PatchOps,
- tests inject fake process runners,
- JSON run-package output with ok:false is treated as failure even if the
  native process exit code is 0,
- JSON run-package output with inner_result:FAIL is treated as failure even if
  the native process exit code is 0,
- timeout handling does not rely on PowerShell.

A later orchestration patch wires this together with the download bridge,
processed store, and run lock.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Mapping, Sequence


ProcessRunner = Callable[[Sequence[str], Path, float, Mapping[str, str] | None], Any]


_WINDOWS_TXT_PATH_RE = re.compile(
    r"(?P<path>[A-Za-z]:\\[^\r\n\"<>|?*]+?\.txt)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PatchOpsRunCommand:
    command: tuple[str, ...]
    cwd: Path
    timeout_seconds: float
    artifact_path: Path
    wrapper_root: Path

    def to_payload(self) -> dict[str, object]:
        return {
            "command": list(self.command),
            "cwd": str(self.cwd),
            "timeout_seconds": self.timeout_seconds,
            "artifact_path": str(self.artifact_path),
            "wrapper_root": str(self.wrapper_root),
        }


@dataclass(frozen=True)
class PatchOpsRunResult:
    command: PatchOpsRunCommand
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool
    ok: bool
    reason: str
    report_path: str | None
    failure_category: str | None
    parsed_payload: dict[str, object] | None

    def to_payload(self) -> dict[str, object]:
        return {
            "command": self.command.to_payload(),
            "exit_code": self.exit_code,
            "stdout_length": len(self.stdout),
            "stderr_length": len(self.stderr),
            "timed_out": self.timed_out,
            "ok": self.ok,
            "reason": self.reason,
            "report_path": self.report_path,
            "failure_category": self.failure_category,
            "parsed_payload": self.parsed_payload,
        }


def resolve_patchops_python_command(wrapper_root: str | Path) -> tuple[str, ...]:
    root = Path(wrapper_root)
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return (str(venv_python),)
    return ("py", "-3")


def build_run_package_command(
    artifact_path: str | Path,
    *,
    wrapper_root: str | Path,
    timeout_seconds: float = 1800.0,
    python_command: Sequence[str] | None = None,
) -> PatchOpsRunCommand:
    artifact = Path(artifact_path)
    root = Path(wrapper_root)

    if not artifact.exists() or not artifact.is_file():
        raise FileNotFoundError(f"PatchOps artifact does not exist: {artifact}")
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"PatchOps wrapper root does not exist: {root}")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    launcher = tuple(python_command) if python_command is not None else resolve_patchops_python_command(root)
    if not launcher:
        raise ValueError("python_command must not be empty")

    command = launcher + (
        "-m",
        "patchops.cli",
        "run-package",
        str(artifact),
        "--wrapper-root",
        str(root),
    )

    return PatchOpsRunCommand(
        command=tuple(command),
        cwd=root,
        timeout_seconds=float(timeout_seconds),
        artifact_path=artifact,
        wrapper_root=root,
    )


def _default_process_runner(
    command: Sequence[str],
    cwd: Path,
    timeout_seconds: float,
    env: Mapping[str, str] | None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd),
        timeout=timeout_seconds,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=None if env is None else dict(env),
    )


def parse_run_package_payload(stdout: str) -> dict[str, object] | None:
    text = (stdout or "").strip()
    if not text:
        return None

    if text.startswith("{") and text.endswith("}"):
        try:
            payload = json.loads(text)
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            return None

    # Some wrappers may print banners before/after the JSON payload. Parse the
    # first complete-looking object as a best-effort fallback.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            payload = json.loads(text[start : end + 1])
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            return None

    return None


def extract_report_path(stdout: str, payload: Mapping[str, object] | None = None) -> str | None:
    if payload is not None:
        for key in ("outer_report_path", "OuterReportPath", "inner_report_path", "InnerReportPath", "report_path"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    text = stdout or ""
    matches = list(_WINDOWS_TXT_PATH_RE.finditer(text))
    if matches:
        return matches[-1].group("path").strip()

    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if stripped.lower().endswith(".txt"):
            return stripped

    return None


def _payload_failure_category(payload: Mapping[str, object] | None) -> str | None:
    if payload is None:
        return None
    for key in ("failure_category", "FailureCategory", "inner_failure_category"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def interpret_run_package_result(
    *,
    command: PatchOpsRunCommand,
    exit_code: int | None,
    stdout: str,
    stderr: str,
    timed_out: bool,
) -> PatchOpsRunResult:
    payload = parse_run_package_payload(stdout)
    report_path = extract_report_path(stdout, payload)
    failure_category = _payload_failure_category(payload)

    ok = False
    reason = "unknown"

    if timed_out:
        ok = False
        reason = "timeout"
    elif exit_code != 0:
        ok = False
        reason = "nonzero_exit_code"
    elif payload is not None:
        payload_ok = payload.get("ok")
        inner_result = str(payload.get("inner_result", "")).strip().upper()
        if payload_ok is False:
            ok = False
            reason = "patchops_payload_ok_false"
        elif inner_result == "FAIL":
            ok = False
            reason = "patchops_inner_result_fail"
        else:
            ok = True
            reason = "success"
    else:
        ok = True
        reason = "success_no_json_payload"

    return PatchOpsRunResult(
        command=command,
        exit_code=exit_code,
        stdout=stdout or "",
        stderr=stderr or "",
        timed_out=timed_out,
        ok=ok,
        reason=reason,
        report_path=report_path,
        failure_category=failure_category,
        parsed_payload=payload,
    )


def run_patchops_package(
    artifact_path: str | Path,
    *,
    wrapper_root: str | Path,
    timeout_seconds: float = 1800.0,
    python_command: Sequence[str] | None = None,
    env: Mapping[str, str] | None = None,
    process_runner: ProcessRunner = _default_process_runner,
) -> PatchOpsRunResult:
    command = build_run_package_command(
        artifact_path,
        wrapper_root=wrapper_root,
        timeout_seconds=timeout_seconds,
        python_command=python_command,
    )

    try:
        completed = process_runner(command.command, command.cwd, command.timeout_seconds, env)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return interpret_run_package_result(
            command=command,
            exit_code=None,
            stdout=stdout,
            stderr=stderr,
            timed_out=True,
        )

    exit_code = getattr(completed, "returncode", None)
    stdout = getattr(completed, "stdout", "") or ""
    stderr = getattr(completed, "stderr", "") or ""

    return interpret_run_package_result(
        command=command,
        exit_code=None if exit_code is None else int(exit_code),
        stdout=str(stdout),
        stderr=str(stderr),
        timed_out=False,
    )
