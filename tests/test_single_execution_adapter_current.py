from __future__ import annotations

from pathlib import Path

from patchops.execution.result_model import ExecutionResult
from patchops.models import CommandResult, CommandSpec
from patchops.workflows import common


def _command(name: str, *, allowed_exit_codes: list[int] | None = None) -> CommandSpec:
    return CommandSpec(
        name=name,
        program="py",
        args=["-c", "print('mp05 hello')"],
        working_directory=".",
        use_profile_runtime=False,
        allowed_exit_codes=list(allowed_exit_codes or [0]),
    )


def _execution_result(name: str, *, exit_code: int, phase: str = "validation") -> ExecutionResult:
    return ExecutionResult(
        name=name,
        program="py",
        args=["-c", "print('mp05 hello')"],
        working_directory=Path("C:/dev/patchops"),
        exit_code=exit_code,
        stdout=f"stdout:{name}",
        stderr=f"stderr:{name}" if exit_code else "",
        display_command='py -c "print(\'mp05 hello\')"',
        phase=phase,
    )


def test_execute_command_adapter_routes_through_run_command_result(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[str, Path, str]] = []
    expected = _execution_result("adapter_probe", exit_code=0, phase="validation")

    def fake_run_command_result(command, *, runtime_path, working_directory_root, phase):
        calls.append((command.name, Path(working_directory_root), phase))
        return expected

    monkeypatch.setattr(common, "run_command_result", fake_run_command_result)

    execution_result, command_result, failure = common.execute_command_adapter(
        _command("adapter_probe"),
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="validation",
    )

    assert calls == [("adapter_probe", tmp_path, "validation")]
    assert execution_result is expected
    assert isinstance(command_result, CommandResult)
    assert command_result == expected.to_command_result()
    assert failure is None


def test_execute_command_group_preserves_command_result_surface_and_stops_on_failure(monkeypatch, tmp_path: Path) -> None:
    mapping = {
        "first": _execution_result("first", exit_code=0, phase="smoke"),
        "second": _execution_result("second", exit_code=7, phase="smoke"),
    }
    call_order: list[str] = []

    def fake_run_command_result(command, *, runtime_path, working_directory_root, phase):
        call_order.append(command.name)
        return mapping[command.name]

    monkeypatch.setattr(common, "run_command_result", fake_run_command_result)

    results, failure = common.execute_command_group(
        [
            _command("first"),
            _command("second", allowed_exit_codes=[0]),
            _command("third"),
        ],
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="smoke",
    )

    assert call_order == ["first", "second"]
    assert [type(item) for item in results] == [CommandResult, CommandResult]
    assert [item.name for item in results] == ["first", "second"]
    assert results[1].exit_code == 7
    assert failure is not None
    assert failure.category == "target_project_failure"
    assert "second" in failure.message


def test_execute_command_group_preserves_allowed_exit_code_behavior(monkeypatch, tmp_path: Path) -> None:
    tolerated = _execution_result("tolerated", exit_code=7, phase="audit")

    def fake_run_command_result(command, *, runtime_path, working_directory_root, phase):
        return tolerated

    monkeypatch.setattr(common, "run_command_result", fake_run_command_result)

    results, failure = common.execute_command_group(
        [_command("tolerated", allowed_exit_codes=[0, 7])],
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="audit",
    )

    assert failure is None
    assert len(results) == 1
    assert isinstance(results[0], CommandResult)
    assert results[0].exit_code == 7
    assert results[0].stdout == "stdout:tolerated"
