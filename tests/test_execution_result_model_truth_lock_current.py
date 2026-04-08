from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.execution.result_model import (
    ExecutionResult,
    execution_result_as_dict,
    normalize_command_result,
    normalize_execution_result,
)
from patchops.models import CommandResult


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    tmp_path = Path.cwd()

    completed = subprocess.CompletedProcess(
        args=["py", "-m", "pytest"],
        returncode=3,
        stdout="hello",
        stderr="warn",
    )

    result = ExecutionResult.from_completed_process(
        name="validation_case",
        program="py",
        args=["-m", "pytest"],
        working_directory=tmp_path,
        completed=completed,
        display_command="py -m pytest",
        phase="validation",
    )

    _assert(result.name == "validation_case", f"name mismatch: {result.name!r}")
    _assert(result.program == "py", f"program mismatch: {result.program!r}")
    _assert(result.args == ["-m", "pytest"], f"args mismatch: {result.args!r}")
    _assert(result.working_directory == tmp_path, f"working_directory mismatch: {result.working_directory!r}")
    _assert(result.exit_code == 3, f"exit_code mismatch: {result.exit_code!r}")
    _assert(result.stdout == "hello", f"stdout mismatch: {result.stdout!r}")
    _assert(result.stderr == "warn", f"stderr mismatch: {result.stderr!r}")
    _assert(result.display_command == "py -m pytest", f"display_command mismatch: {result.display_command!r}")
    _assert(result.phase == "validation", f"phase mismatch: {result.phase!r}")

    execution_result = ExecutionResult(
        name="smoke_case",
        program="py",
        args=["-m", "pytest", "-q"],
        working_directory=tmp_path,
        exit_code=0,
        stdout="ok",
        stderr="",
        display_command="py -m pytest -q",
        phase="smoke",
    )

    command_result = execution_result.to_command_result()

    _assert(isinstance(command_result, CommandResult), "to_command_result did not return CommandResult")
    _assert(command_result.name == "smoke_case", f"round-trip name mismatch: {command_result.name!r}")
    _assert(command_result.program == "py", f"round-trip program mismatch: {command_result.program!r}")
    _assert(command_result.args == ["-m", "pytest", "-q"], f"round-trip args mismatch: {command_result.args!r}")
    _assert(command_result.working_directory == tmp_path, f"round-trip working_directory mismatch: {command_result.working_directory!r}")
    _assert(command_result.exit_code == 0, f"round-trip exit_code mismatch: {command_result.exit_code!r}")
    _assert(command_result.stdout == "ok", f"round-trip stdout mismatch: {command_result.stdout!r}")
    _assert(command_result.stderr == "", f"round-trip stderr mismatch: {command_result.stderr!r}")
    _assert(command_result.display_command == "py -m pytest -q", f"round-trip display_command mismatch: {command_result.display_command!r}")
    _assert(command_result.phase == "smoke", f"round-trip phase mismatch: {command_result.phase!r}")

    audit_result = CommandResult(
        name="audit_case",
        program="py",
        args=["-m", "pytest", "tests/test_example.py"],
        working_directory=tmp_path,
        exit_code=5,
        stdout="",
        stderr="failed",
        display_command="py -m pytest tests/test_example.py",
        phase="audit",
    )

    normalized = normalize_command_result(audit_result)

    _assert(
        normalized == ExecutionResult(
            name="audit_case",
            program="py",
            args=["-m", "pytest", "tests/test_example.py"],
            working_directory=tmp_path,
            exit_code=5,
            stdout="",
            stderr="failed",
            display_command="py -m pytest tests/test_example.py",
            phase="audit",
        ),
        f"normalize_command_result mismatch: {normalized!r}",
    )
    _assert(normalize_execution_result(audit_result) == normalized, "normalize_execution_result did not preserve normalized shape")
    _assert(normalize_execution_result(normalized) == normalized, "normalize_execution_result changed an ExecutionResult")

    payload = execution_result_as_dict(audit_result)
    _assert(payload["name"] == "audit_case", f"dict name mismatch: {payload!r}")
    _assert(payload["program"] == "py", f"dict program mismatch: {payload!r}")
    _assert(payload["args"] == ["-m", "pytest", "tests/test_example.py"], f"dict args mismatch: {payload!r}")
    _assert(payload["working_directory"] == tmp_path, f"dict working_directory mismatch: {payload!r}")
    _assert(payload["exit_code"] == 5, f"dict exit_code mismatch: {payload!r}")
    _assert(payload["stdout"] == "", f"dict stdout mismatch: {payload!r}")
    _assert(payload["stderr"] == "failed", f"dict stderr mismatch: {payload!r}")
    _assert(payload["display_command"] == "py -m pytest tests/test_example.py", f"dict display_command mismatch: {payload!r}")
    _assert(payload["phase"] == "audit", f"dict phase mismatch: {payload!r}")

    print("execution-result-model truth-lock validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
