import sys
from pathlib import Path

from patchops.execution.process_runner import run_command
from patchops.models import CommandSpec


def test_process_runner_captures_stdout(tmp_path: Path):
    result = run_command(
        CommandSpec(name="hello", program=sys.executable, args=["-c", "print('hello')"]),
        runtime_path=None,
        working_directory_root=tmp_path,
        phase="validation",
    )
    assert result.exit_code == 0
    assert "hello" in result.stdout
