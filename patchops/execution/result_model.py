from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from patchops.models import CommandResult


@dataclass(frozen=True)
class ExecutionResult:
    name: str
    program: str
    args: list[str]
    working_directory: Path
    exit_code: int
    stdout: str
    stderr: str
    display_command: str
    phase: str

    @classmethod
    def from_completed_process(
        cls,
        *,
        name: str,
        program: str,
        args: list[str],
        working_directory: Path,
        completed: subprocess.CompletedProcess[str],
        display_command: str,
        phase: str,
    ) -> "ExecutionResult":
        return cls(
            name=name,
            program=program,
            args=list(args),
            working_directory=working_directory,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            display_command=display_command,
            phase=phase,
        )

    @classmethod
    def from_command_result(cls, result: CommandResult) -> "ExecutionResult":
        return cls(
            name=result.name,
            program=result.program,
            args=list(result.args),
            working_directory=result.working_directory,
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            display_command=result.display_command,
            phase=result.phase,
        )

    def to_command_result(self) -> CommandResult:
        return CommandResult(
            name=self.name,
            program=self.program,
            args=list(self.args),
            working_directory=self.working_directory,
            exit_code=self.exit_code,
            stdout=self.stdout,
            stderr=self.stderr,
            display_command=self.display_command,
            phase=self.phase,
        )


def normalize_command_result(result: CommandResult) -> ExecutionResult:
    return ExecutionResult.from_command_result(result)


__all__ = ["ExecutionResult", "normalize_command_result"]
