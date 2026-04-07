from __future__ import annotations

import json
import sys
from pathlib import Path

from patchops.execution.process_engine import run_process


def _echo_argv_result(tmp_path: Path, *args: str):
    return run_process(
        [
            sys.executable,
            "-c",
            "import json, sys; print(json.dumps(sys.argv[1:]))",
            *args,
        ],
        cwd=tmp_path,
    )


def test_run_process_preserves_argument_with_spaces(tmp_path: Path) -> None:
    result = _echo_argv_result(tmp_path, "hello world", "plain")
    assert result.exit_code == 0
    assert json.loads(result.stdout.strip()) == ["hello world", "plain"]


def test_run_process_preserves_embedded_quotes_without_splitting(tmp_path: Path) -> None:
    quoted = 'say "hello" now'
    result = _echo_argv_result(tmp_path, quoted)
    assert result.exit_code == 0
    assert json.loads(result.stdout.strip()) == [quoted]


def test_run_process_preserves_windows_hostile_backslash_shape(tmp_path: Path) -> None:
    windowsish = r"C:\Program Files\PatchOps\bundle one\manifest.json"
    result = _echo_argv_result(tmp_path, windowsish)
    assert result.exit_code == 0
    assert json.loads(result.stdout.strip()) == [windowsish]


def test_run_process_preserves_empty_argument(tmp_path: Path) -> None:
    result = _echo_argv_result(tmp_path, "", "after")
    assert result.exit_code == 0
    assert json.loads(result.stdout.strip()) == ["", "after"]
