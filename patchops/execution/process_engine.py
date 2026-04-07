from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class ProcessExecutionResult:
    command: tuple[str, ...]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool


def run_process(
    command: list[str] | tuple[str, ...],
    *,
    cwd: str | Path,
    timeout_seconds: float | None = None,
    env_overrides: Mapping[str, str] | None = None,
) -> ProcessExecutionResult:
    normalized_command = tuple(str(part) for part in command)
    if len(normalized_command) == 0:
        raise ValueError("command must not be empty")

    working_directory = str(Path(cwd).resolve())
    env = os.environ.copy()
    if env_overrides:
        env.update({str(key): str(value) for key, value in env_overrides.items()})

    start = time.perf_counter()
    try:
        completed = subprocess.run(
            list(normalized_command),
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
            check=False,
        )
        duration = time.perf_counter() - start
        return ProcessExecutionResult(
            command=normalized_command,
            cwd=working_directory,
            exit_code=int(completed.returncode),
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_seconds=duration,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - start
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return ProcessExecutionResult(
            command=normalized_command,
            cwd=working_directory,
            exit_code=-1,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            timed_out=True,
        )
