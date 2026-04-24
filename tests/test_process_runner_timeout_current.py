from __future__ import annotations

import sys

from patchops.execution.process_runner import run_command_result
from patchops.models import CommandSpec


def test_process_runner_timeout_converts_hang_to_failed_result(tmp_path, monkeypatch):
    monkeypatch.setenv("PATCHOPS_COMMAND_TIMEOUT_SECONDS", "0.2")

    result = run_command_result(
        CommandSpec(
            name="slow_command",
            program=sys.executable,
            args=["-c", "import time; time.sleep(5)"],
        ),
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="validation",
    )

    assert result.exit_code == -1
    assert "timed out" in result.stderr.lower()
    assert "0.2" in result.stderr
