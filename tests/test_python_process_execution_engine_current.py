from __future__ import annotations

import os
import sys
from pathlib import Path

from patchops.execution.process_engine import run_process


def test_run_process_captures_stdout(tmp_path: Path) -> None:
    result = run_process(
        [sys.executable, "-c", "print('hello from process engine')"],
        cwd=tmp_path,
    )
    assert result.exit_code == 0
    assert result.timed_out is False
    assert "hello from process engine" in result.stdout
    assert result.stderr == ""
    assert result.cwd == str(tmp_path.resolve())
    assert result.command[0] == sys.executable


def test_run_process_captures_stderr_and_nonzero_exit(tmp_path: Path) -> None:
    result = run_process(
        [
            sys.executable,
            "-c",
            "import sys; sys.stderr.write('bad news\\n'); raise SystemExit(3)",
        ],
        cwd=tmp_path,
    )
    assert result.exit_code == 3
    assert result.timed_out is False
    assert "bad news" in result.stderr
    assert result.stdout == ""


def test_run_process_preserves_working_directory(tmp_path: Path) -> None:
    result = run_process(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; print(Path.cwd().name)",
        ],
        cwd=tmp_path,
    )
    assert result.exit_code == 0
    assert tmp_path.name in result.stdout


def test_run_process_applies_environment_overrides(tmp_path: Path) -> None:
    result = run_process(
        [
            sys.executable,
            "-c",
            "import os; print(os.environ['PATCHOPS_ENGINE_MARKER'])",
        ],
        cwd=tmp_path,
        env_overrides={"PATCHOPS_ENGINE_MARKER": "marker_value"},
    )
    assert result.exit_code == 0
    assert "marker_value" in result.stdout
