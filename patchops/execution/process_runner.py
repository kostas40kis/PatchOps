from __future__ import annotations

from pathlib import Path

from patchops.execution.process_engine import run_process
from patchops.execution.quoting import render_display_command
from patchops.execution.result_model import ExecutionResult
from patchops.models import CommandResult, CommandSpec


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

    process_result = run_process(
        [program, *args],
        cwd=working_directory,
    )
    return ExecutionResult(
        name=command.name,
        program=program,
        args=args,
        working_directory=working_directory,
        exit_code=process_result.exit_code,
        stdout=process_result.stdout,
        stderr=process_result.stderr,
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
