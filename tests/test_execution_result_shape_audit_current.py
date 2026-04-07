from __future__ import annotations

import sys
from pathlib import Path

from patchops.execution.process_runner import run_command
from patchops.execution.quoting import render_display_command
from patchops.execution.result_model import ExecutionResult, normalize_command_result
from patchops.models import CommandSpec


def _command(
    code: str,
    *,
    name: str = "inline_python",
    program: str | None = None,
    args: list[str] | None = None,
    working_directory: str = ".",
    use_profile_runtime: bool = False,
) -> CommandSpec:
    return CommandSpec(
        name=name,
        program=program if program is not None else sys.executable,
        args=args if args is not None else ["-c", code],
        working_directory=working_directory,
        use_profile_runtime=use_profile_runtime,
        allowed_exit_codes=[0],
    )


def _run(
    tmp_path: Path,
    code: str,
    *,
    phase: str = "validation",
    name: str = "inline_python",
    program: str | None = None,
    args: list[str] | None = None,
    working_directory: str = ".",
    runtime_path: Path | None = None,
    use_profile_runtime: bool = False,
):
    return run_command(
        _command(
            code,
            name=name,
            program=program,
            args=args,
            working_directory=working_directory,
            use_profile_runtime=use_profile_runtime,
        ),
        runtime_path=runtime_path,
        working_directory_root=tmp_path,
        phase=phase,
    )


def test_current_execution_result_shape_stays_explicit_for_downstream_workflows(tmp_path: Path) -> None:
    code = "import sys; sys.stdout.write('shape-ok')"
    args = ["-c", code]

    result = _run(tmp_path, code, name="shape_audit", args=args)

    assert result.name == "shape_audit"
    assert result.program == sys.executable
    assert result.args == args
    assert result.working_directory == tmp_path.resolve()
    assert result.exit_code == 0
    assert result.stdout == "shape-ok"
    assert result.stderr == ""
    assert result.display_command == render_display_command(sys.executable, args)
    assert result.phase == "validation"


def test_normalize_command_result_round_trips_the_current_shape_without_loss(tmp_path: Path) -> None:
    code = "import sys; sys.stderr.write('warn')"
    args = ["-c", code]

    result = _run(tmp_path, code, name="shape_roundtrip", args=args)
    normalized = normalize_command_result(result)

    assert isinstance(normalized, ExecutionResult)
    assert normalized.name == result.name
    assert normalized.program == result.program
    assert normalized.args == result.args
    assert normalized.working_directory == result.working_directory
    assert normalized.exit_code == result.exit_code
    assert normalized.stdout == result.stdout
    assert normalized.stderr == result.stderr
    assert normalized.display_command == result.display_command
    assert normalized.phase == result.phase

    round_tripped = normalized.to_command_result()
    assert round_tripped.name == result.name
    assert round_tripped.program == result.program
    assert round_tripped.args == result.args
    assert round_tripped.working_directory == result.working_directory
    assert round_tripped.exit_code == result.exit_code
    assert round_tripped.stdout == result.stdout
    assert round_tripped.stderr == result.stderr
    assert round_tripped.display_command == result.display_command
    assert round_tripped.phase == result.phase


def test_current_execution_result_shape_keeps_profile_runtime_and_cwd_visible(tmp_path: Path) -> None:
    runtime_path = Path(sys.executable)
    working_directory = "nested\\child"
    expected_cwd = (tmp_path / "nested" / "child").resolve()
    expected_cwd.mkdir(parents=True, exist_ok=True)
    code = "import os, sys; sys.stdout.write(os.getcwd())"
    args = ["-c", code]

    result = _run(
        tmp_path,
        code,
        name="runtime_shape",
        args=args,
        working_directory=working_directory,
        runtime_path=runtime_path,
        use_profile_runtime=True,
    )

    assert result.program == str(runtime_path)
    assert result.args == args
    assert result.working_directory == expected_cwd
    assert Path(result.stdout) == expected_cwd
    assert result.display_command == render_display_command(str(runtime_path), args)
    assert result.phase == "validation"