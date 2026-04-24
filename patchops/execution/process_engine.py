from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
from collections.abc import Mapping, Sequence


@dataclass
class ProcessResult:
    command: list[str]
    working_directory: Path
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False

    @property
    def cwd(self) -> str:
        return str(Path(self.working_directory).resolve())




class ProcessExecutionResult(ProcessResult):
    # Backward-compatible process result accepted by older runner tests.
    # Current process execution uses ProcessResult(working_directory=...).
    # Older tests used ProcessExecutionResult(cwd=..., duration_seconds=...).
    def __init__(
        self,
        *,
        command,
        cwd=None,
        working_directory=None,
        exit_code=0,
        stdout="",
        stderr="",
        duration_seconds=0.0,
        timed_out=False,
    ):
        resolved_working_directory = working_directory if working_directory is not None else cwd
        if resolved_working_directory is None:
            resolved_working_directory = Path.cwd()
        super().__init__(
            command=[str(part) for part in command],
            working_directory=Path(resolved_working_directory),
            exit_code=int(exit_code),
            stdout=str(stdout or ""),
            stderr=str(stderr or ""),
            timed_out=bool(timed_out),
        )
        self.duration_seconds = float(duration_seconds or 0.0)

def _coerce_timeout_seconds(value: object) -> float | None:
    if value is None:
        return None

    if isinstance(value, str):
        raw = value.strip()
        if raw == "":
            return None
    else:
        raw = value

    try:
        resolved = float(raw)
    except (TypeError, ValueError):
        return None

    if resolved <= 0:
        return None

    return resolved


def _resolve_effective_timeout_seconds(timeout_seconds: float | int | str | None) -> float | None:
    explicit = _coerce_timeout_seconds(timeout_seconds)
    if explicit is not None:
        return explicit

    if timeout_seconds is not None:
        return None

    return _coerce_timeout_seconds(os.environ.get("PATCHOPS_COMMAND_TIMEOUT_SECONDS"))


def _merge_env_overrides(env_overrides: Mapping[str, object] | None) -> dict[str, str]:
    env = os.environ.copy()
    if not env_overrides:
        return env

    for key, value in env_overrides.items():
        if value is None:
            env.pop(str(key), None)
        else:
            env[str(key)] = str(value)
    return env


def _decode_timeout_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return value.decode("utf-8", "replace")


def run_process(
    command: Sequence[str],
    *,
    cwd: str | Path,
    timeout_seconds: float | int | str | None = None,
    env_overrides: Mapping[str, object] | None = None,
) -> ProcessResult:
    command_list = [str(part) for part in command]
    working_directory = Path(cwd).resolve()
    effective_timeout = _resolve_effective_timeout_seconds(timeout_seconds)

    try:
        completed = subprocess.run(
            command_list,
            cwd=str(working_directory),
            env=_merge_env_overrides(env_overrides),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=effective_timeout,
            check=False,
        )
        return ProcessResult(
            command=command_list,
            working_directory=working_directory,
            exit_code=int(completed.returncode),
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _decode_timeout_output(exc.stdout)
        stderr = _decode_timeout_output(exc.stderr)
        timeout_text = effective_timeout if effective_timeout is not None else timeout_seconds
        timeout_message = f"Process timed out after {timeout_text} seconds."
        if stderr:
            stderr = stderr.rstrip() + "\n" + timeout_message
        else:
            stderr = timeout_message

        return ProcessResult(
            command=command_list,
            working_directory=working_directory,
            exit_code=-1,
            stdout=stdout,
            stderr=stderr,
            timed_out=True,
        )

__all__ = ["ProcessResult", "ProcessExecutionResult", "run_process"]
