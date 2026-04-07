from __future__ import annotations

import subprocess
from pathlib import Path

from patchops.execution.result_model import (
    ExecutionResult,
    execution_result_as_dict,
    normalize_command_result,
    normalize_execution_result,
)
from patchops.models import CommandResult


def test_execution_result_from_completed_process_preserves_current_fields(tmp_path: Path) -> None:
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

    assert result == ExecutionResult(
        name="validation_case",
        program="py",
        args=["-m", "pytest"],
        working_directory=tmp_path,
        exit_code=3,
        stdout="hello",
        stderr="warn",
        display_command="py -m pytest",
        phase="validation",
    )


def test_execution_result_to_command_result_round_trips_current_shape(tmp_path: Path) -> None:
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

    assert isinstance(command_result, CommandResult)
    assert command_result.name == "smoke_case"
    assert command_result.program == "py"
    assert command_result.args == ["-m", "pytest", "-q"]
    assert command_result.working_directory == tmp_path
    assert command_result.exit_code == 0
    assert command_result.stdout == "ok"
    assert command_result.stderr == ""
    assert command_result.display_command == "py -m pytest -q"
    assert command_result.phase == "smoke"


def test_normalize_command_result_and_dict_helpers_preserve_current_contract(tmp_path: Path) -> None:
    command_result = CommandResult(
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

    normalized = normalize_command_result(command_result)

    assert normalized == ExecutionResult(
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

    assert normalize_execution_result(command_result) == normalized
    payload = execution_result_as_dict(command_result)
    assert payload["name"] == "audit_case"
    assert payload["program"] == "py"
    assert payload["args"] == ["-m", "pytest", "tests/test_example.py"]
    assert payload["working_directory"] == tmp_path
    assert payload["exit_code"] == 5
    assert payload["stdout"] == ""
    assert payload["stderr"] == "failed"
    assert payload["display_command"] == "py -m pytest tests/test_example.py"
    assert payload["phase"] == "audit"
