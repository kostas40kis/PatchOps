from __future__ import annotations

import subprocess
from pathlib import Path

from patchops.execution.quoting import render_display_command
from patchops.execution.result_model import ExecutionResult
from patchops.models import CommandResult, CommandSpec


def run_command(
    command: CommandSpec,
    *,
    runtime_path: Path | None,
    working_directory_root: Path,
    phase: str,
) -> CommandResult:
    if command.use_profile_runtime:
        if runtime_path is None:
            raise RuntimeError(f"Command {command.name!r} requested profile runtime, but none was resolved.")
        program = str(runtime_path)
    else:
        if command.program is None:
            raise RuntimeError(f"Command {command.name!r} has no program configured.")
        program = command.program

    working_directory = (
        (working_directory_root / command.working_directory).resolve()
        if command.working_directory
        else working_directory_root.resolve()
    )
    args = list(command.args)
    display_command = render_display_command(program, args)

    completed = subprocess.run(
        [program, *args],
        cwd=str(working_directory),
        capture_output=True,
        text=True,
        check=False,
    )
    return ExecutionResult.from_completed_process(
        name=command.name,
        program=program,
        args=args,
        working_directory=working_directory,
        completed=completed,
        display_command=display_command,
        phase=phase,
    ).to_command_result()
