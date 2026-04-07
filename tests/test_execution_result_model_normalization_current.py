from __future__ import annotations

from pathlib import Path

from patchops.execution.process_runner import run_command, run_command_result
from patchops.execution.result_model import (
    ExecutionResult,
    execution_result_as_dict,
    normalize_command_result,
    normalize_execution_result,
)
from patchops.models import CommandResult, CommandSpec


def _sample_command() -> CommandSpec:
    return CommandSpec(
        name="mp04_shape_probe",
        program="py",
        args=["-c", "print('mp04 hello')"],
        working_directory=".",
        use_profile_runtime=False,
    )


def test_run_command_result_returns_execution_result_with_current_surface(tmp_path: Path) -> None:
    result = run_command_result(
        _sample_command(),
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="validation",
    )

    assert isinstance(result, ExecutionResult)
    assert result.name == "mp04_shape_probe"
    assert result.program == "py"
    assert result.args == ["-c", "print('mp04 hello')"]
    assert result.working_directory == tmp_path.resolve()
    assert result.exit_code == 0
    assert result.stdout.strip() == "mp04 hello"
    assert result.stderr == ""
    assert result.phase == "validation"
    assert result.display_command


def test_normalize_execution_result_accepts_both_execution_and_command_results(tmp_path: Path) -> None:
    execution_result = run_command_result(
        _sample_command(),
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="audit",
    )
    command_result = run_command(
        _sample_command(),
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="audit",
    )

    normalized_from_execution = normalize_execution_result(execution_result)
    normalized_from_command = normalize_execution_result(command_result)
    normalized_via_legacy = normalize_command_result(command_result)

    assert normalized_from_execution is execution_result
    assert isinstance(normalized_from_command, ExecutionResult)
    assert normalized_from_command.name == command_result.name
    assert normalized_from_command.program == command_result.program
    assert normalized_from_command.args == command_result.args
    assert normalized_from_command.working_directory == command_result.working_directory
    assert normalized_from_command.exit_code == command_result.exit_code
    assert normalized_from_command.stdout == command_result.stdout
    assert normalized_from_command.stderr == command_result.stderr
    assert normalized_from_command.display_command == command_result.display_command
    assert normalized_from_command.phase == command_result.phase
    assert normalized_via_legacy == normalized_from_command


def test_execution_result_as_dict_preserves_current_fields_and_copies_args() -> None:
    command_result = CommandResult(
        name="manual",
        program="python",
        args=["-m", "pytest", "-q"],
        working_directory=Path("C:/dev/patchops"),
        exit_code=3,
        stdout="out",
        stderr="err",
        display_command="python -m pytest -q",
        phase="smoke",
    )

    payload = execution_result_as_dict(command_result)

    assert payload == {
        "name": "manual",
        "program": "python",
        "args": ["-m", "pytest", "-q"],
        "working_directory": Path("C:/dev/patchops"),
        "exit_code": 3,
        "stdout": "out",
        "stderr": "err",
        "display_command": "python -m pytest -q",
        "phase": "smoke",
    }

    payload_args = payload["args"]
    assert isinstance(payload_args, list)
    payload_args.append("mutated")
    assert command_result.args == ["-m", "pytest", "-q"]
