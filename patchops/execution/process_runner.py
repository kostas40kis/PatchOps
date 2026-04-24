from __future__ import annotations

import os
from pathlib import Path

from patchops.execution.process_engine import run_process
from patchops.execution.quoting import render_display_command
from patchops.execution.result_model import ExecutionResult
from patchops.models import CommandResult, CommandSpec


COMMAND_TIMEOUT_ENV_VAR = "PATCHOPS_COMMAND_TIMEOUT_SECONDS"
DEFAULT_COMMAND_TIMEOUT_SECONDS = 180.0
_TIMEOUT_DISABLED_VALUES = {"0", "none", "off", "false", "disabled", "disable"}


def _parse_timeout_seconds(value: object | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in _TIMEOUT_DISABLED_VALUES:
        return None
    try:
        seconds = float(text)
    except ValueError:
        return None
    if seconds <= 0:
        return None
    return seconds


def _command_timeout_seconds(command: CommandSpec) -> float | None:
    command_value = getattr(command, "timeout_seconds", None)
    parsed_command_value = _parse_timeout_seconds(command_value)
    if parsed_command_value is not None:
        return parsed_command_value

    env_value = os.environ.get(COMMAND_TIMEOUT_ENV_VAR)
    if env_value is not None:
        if env_value.strip().lower() in _TIMEOUT_DISABLED_VALUES:
            return None
        parsed_env_value = _parse_timeout_seconds(env_value)
        if parsed_env_value is not None:
            return parsed_env_value

    return DEFAULT_COMMAND_TIMEOUT_SECONDS


def _timeout_stderr(stderr: str, *, timeout_seconds: float | None) -> str:
    timeout_text = "unknown" if timeout_seconds is None else f"{timeout_seconds:g}"
    note = f"PatchOps command timed out after {timeout_text} seconds."
    if stderr:
        return stderr.rstrip() + "\n" + note
    return note


def _resolve_command_program(command: CommandSpec, runtime_path: Path | None) -> str:
    if command.use_profile_runtime:
        if runtime_path is None:
            raise RuntimeError(f"Command {command.name!r} requested profile runtime, but none was resolved.")
        return str(runtime_path)

    if command.program is None:
        raise RuntimeError(f"Command {command.name!r} has no program configured.")
    return command.program


def _resolve_working_directory(command: CommandSpec, working_directory_root: Path) -> Path:
    if command.working_directory:
        return (working_directory_root / command.working_directory).resolve()
    return working_directory_root.resolve()


def run_command_result(
    command: CommandSpec,
    *,
    runtime_path: Path | None,
    working_directory_root: Path,
    phase: str,
) -> ExecutionResult:
    program = _resolve_command_program(command, runtime_path)
    working_directory = _resolve_working_directory(command, working_directory_root)
    args = list(command.args)
    display_command = render_display_command(program, args)
    timeout_seconds = _command_timeout_seconds(command)

    process_result = run_process(
        [program, *args],
        cwd=working_directory,
        timeout_seconds=timeout_seconds,
    )

    stderr = process_result.stderr
    if process_result.timed_out:
        stderr = _timeout_stderr(stderr, timeout_seconds=timeout_seconds)

    return ExecutionResult(
        name=command.name,
        program=program,
        args=args,
        working_directory=working_directory,
        exit_code=process_result.exit_code,
        stdout=process_result.stdout,
        stderr=stderr,
        display_command=display_command,
        phase=phase,
    )


def run_command(
    command: CommandSpec,
    *,
    runtime_path: Path | None,
    working_directory_root: Path,
    phase: str,
) -> CommandResult:
    return run_command_result(
        command,
        runtime_path=runtime_path,
        working_directory_root=working_directory_root,
        phase=phase,
    ).to_command_result()
