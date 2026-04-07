from __future__ import annotations

import sys
from pathlib import Path

import patchops.execution.process_runner as runner
from patchops.execution.process_engine import ProcessExecutionResult
from patchops.execution.quoting import render_display_command
from patchops.models import CommandResult, CommandSpec


def _command(
    *,
    name: str = 'delegated',
    program: str | None = None,
    args: list[str] | None = None,
    working_directory: str = '.',
    use_profile_runtime: bool = False,
) -> CommandSpec:
    return CommandSpec(
        name=name,
        program=program if program is not None else sys.executable,
        args=list(args or ['-c', "print('zp09')"]),
        working_directory=working_directory,
        use_profile_runtime=use_profile_runtime,
        allowed_exit_codes=[0],
    )


def _engine_result(command: tuple[str, ...], cwd: Path, *, exit_code: int = 0, stdout: str = '', stderr: str = '') -> ProcessExecutionResult:
    return ProcessExecutionResult(
        command=command,
        cwd=str(cwd.resolve()),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=0.25,
        timed_out=False,
    )


def test_run_command_result_routes_through_run_process(monkeypatch, tmp_path: Path) -> None:
    observed: dict[str, object] = {}

    def fake_run_process(command, *, cwd, timeout_seconds=None, env_overrides=None):
        observed['command'] = tuple(command)
        observed['cwd'] = Path(cwd)
        observed['timeout_seconds'] = timeout_seconds
        observed['env_overrides'] = env_overrides
        return _engine_result(tuple(command), Path(cwd), exit_code=7, stdout='delegated stdout', stderr='delegated stderr')

    monkeypatch.setattr(runner, 'run_process', fake_run_process)

    command = _command(args=['-c', "print('delegated')"])
    result = runner.run_command_result(
        command,
        runtime_path=None,
        working_directory_root=tmp_path,
        phase='validation',
    )

    assert observed['command'] == (sys.executable, '-c', "print('delegated')")
    assert observed['cwd'] == tmp_path.resolve()
    assert observed['timeout_seconds'] is None
    assert observed['env_overrides'] is None
    assert result.name == 'delegated'
    assert result.program == sys.executable
    assert result.args == ['-c', "print('delegated')"]
    assert result.working_directory == tmp_path.resolve()
    assert result.exit_code == 7
    assert result.stdout == 'delegated stdout'
    assert result.stderr == 'delegated stderr'
    assert result.display_command == render_display_command(sys.executable, ['-c', "print('delegated')"])
    assert result.phase == 'validation'


def test_run_command_result_uses_resolved_profile_runtime_with_process_engine(monkeypatch, tmp_path: Path) -> None:
    observed: dict[str, object] = {}
    runtime_path = Path(sys.executable)

    def fake_run_process(command, *, cwd, timeout_seconds=None, env_overrides=None):
        observed['command'] = tuple(command)
        observed['cwd'] = Path(cwd)
        return _engine_result(tuple(command), Path(cwd), stdout='runtime ok')

    monkeypatch.setattr(runner, 'run_process', fake_run_process)

    command = _command(program='ignored', use_profile_runtime=True, args=['-c', "print('runtime')"], working_directory='nested\child')
    expected_cwd = (tmp_path / 'nested' / 'child').resolve()
    expected_cwd.mkdir(parents=True, exist_ok=True)

    result = runner.run_command_result(
        command,
        runtime_path=runtime_path,
        working_directory_root=tmp_path,
        phase='smoke',
    )

    assert observed['command'] == (str(runtime_path), '-c', "print('runtime')")
    assert observed['cwd'] == expected_cwd
    assert result.program == str(runtime_path)
    assert result.working_directory == expected_cwd
    assert result.stdout == 'runtime ok'
    assert result.display_command == render_display_command(str(runtime_path), ['-c', "print('runtime')"])
    assert result.phase == 'smoke'


def test_run_command_still_returns_command_result_after_engine_delegation(monkeypatch, tmp_path: Path) -> None:
    def fake_run_process(command, *, cwd, timeout_seconds=None, env_overrides=None):
        return _engine_result(tuple(command), Path(cwd), stdout='plain command result')

    monkeypatch.setattr(runner, 'run_process', fake_run_process)

    result = runner.run_command(
        _command(name='to_command_result'),
        runtime_path=None,
        working_directory_root=tmp_path,
        phase='audit',
    )

    assert isinstance(result, CommandResult)
    assert result.name == 'to_command_result'
    assert result.stdout == 'plain command result'
    assert result.exit_code == 0
    assert result.phase == 'audit'
