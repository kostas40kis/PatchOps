from __future__ import annotations

import sys
from pathlib import Path

from patchops.models import CommandSpec
from patchops.workflows.common import execute_command_group


def _command(code: str, *, name: str = "inline_python", allowed_exit_codes: list[int] | None = None) -> CommandSpec:
    return CommandSpec(
        name=name,
        program=sys.executable,
        args=["-c", code],
        working_directory=".",
        use_profile_runtime=False,
        allowed_exit_codes=allowed_exit_codes or [0],
    )


def test_execute_command_group_returns_results_without_failure(tmp_path: Path) -> None:
    results, failure = execute_command_group(
        [_command("import sys; sys.stdout.write('ok')", name="ok")],
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="validation",
    )

    assert failure is None
    assert len(results) == 1
    assert results[0].name == "ok"
    assert results[0].stdout == "ok"
    assert results[0].stderr == ""
    assert results[0].exit_code == 0
    assert results[0].phase == "validation"


def test_execute_command_group_stops_on_required_failure(tmp_path: Path) -> None:
    commands = [
        _command(
            "import sys; sys.stderr.write('boom'); raise SystemExit(7)",
            name="required_failure",
            allowed_exit_codes=[0],
        ),
        _command("import sys; sys.stdout.write('later')", name="later"),
    ]

    results, failure = execute_command_group(
        commands,
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="validation",
    )

    assert len(results) == 1
    assert failure is not None
    assert failure.message
    assert results[0].name == "required_failure"
    assert results[0].stderr == "boom"
    assert results[0].exit_code == 7


def test_execute_command_group_allows_tolerated_nonzero_exit(tmp_path: Path) -> None:
    results, failure = execute_command_group(
        [
            _command(
                "raise SystemExit(4)",
                name="tolerated_nonzero",
                allowed_exit_codes=[0, 4],
            )
        ],
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="smoke",
    )

    assert failure is None
    assert len(results) == 1
    assert results[0].name == "tolerated_nonzero"
    assert results[0].exit_code == 4
    assert results[0].phase == "smoke"
