from __future__ import annotations

import os
import sys
from pathlib import Path

from patchops.execution.process_engine import run_process


def test_process_engine_honors_env_timeout_when_timeout_is_none(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PATCHOPS_COMMAND_TIMEOUT_SECONDS", "0.2")

    result = run_process(
        [
            sys.executable,
            "-c",
            "import time; time.sleep(3); print('finished')",
        ],
        cwd=tmp_path,
        timeout_seconds=None,
    )

    assert result.exit_code != 0
    assert getattr(result, "timed_out", False) is True
    assert "timed out" in result.stderr.lower()


def test_process_engine_ignores_env_timeout_when_explicit_timeout_is_set(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PATCHOPS_COMMAND_TIMEOUT_SECONDS", "0.2")

    result = run_process(
        [
            sys.executable,
            "-c",
            "print('explicit timeout wins')",
        ],
        cwd=tmp_path,
        timeout_seconds=5,
    )

    assert result.exit_code == 0
    assert "explicit timeout wins" in result.stdout
    assert getattr(result, "timed_out", False) is False
