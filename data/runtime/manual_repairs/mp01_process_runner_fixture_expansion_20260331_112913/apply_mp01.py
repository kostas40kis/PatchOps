from pathlib import Path
from textwrap import dedent

project_root = Path(r"C:\dev\patchops")
target_path = project_root / "tests" / "test_process_runner.py"

content = dedent(
    """
    from __future__ import annotations

    import sys
    from pathlib import Path

    from patchops.execution.process_runner import run_command
    from patchops.models import CommandSpec


    def _command(code: str, *, name: str = "inline_python") -> CommandSpec:
        return CommandSpec(
            name=name,
            program=sys.executable,
            args=["-c", code],
            working_directory=".",
            use_profile_runtime=False,
            allowed_exit_codes=[0],
        )


    def _run(tmp_path: Path, code: str, *, phase: str = "validation", name: str = "inline_python"):
        return run_command(
            _command(code, name=name),
            runtime_path=None,
            working_directory_root=tmp_path,
            phase=phase,
        )


    def test_run_command_captures_stdout_only(tmp_path: Path) -> None:
        result = _run(tmp_path, "import sys; sys.stdout.write('stdout only')", name="stdout_only")

        assert result.name == "stdout_only"
        assert result.exit_code == 0
        assert result.stdout == "stdout only"
        assert result.stderr == ""
        assert result.working_directory == tmp_path.resolve()
        assert result.phase == "validation"


    def test_run_command_captures_stderr_only(tmp_path: Path) -> None:
        result = _run(tmp_path, "import sys; sys.stderr.write('stderr only')", name="stderr_only")

        assert result.name == "stderr_only"
        assert result.exit_code == 0
        assert result.stdout == ""
        assert result.stderr == "stderr only"


    def test_run_command_captures_mixed_stdout_and_stderr(tmp_path: Path) -> None:
        result = _run(
            tmp_path,
            "import sys; sys.stdout.write('hello'); sys.stderr.write('warn')",
            name="mixed_output",
        )

        assert result.name == "mixed_output"
        assert result.exit_code == 0
        assert result.stdout == "hello"
        assert result.stderr == "warn"


    def test_run_command_preserves_non_zero_exit_and_stderr(tmp_path: Path) -> None:
        result = _run(
            tmp_path,
            "import sys; sys.stderr.write('boom'); raise SystemExit(7)",
            name="non_zero_exit",
        )

        assert result.name == "non_zero_exit"
        assert result.exit_code == 7
        assert result.stdout == ""
        assert result.stderr == "boom"


    def test_run_command_captures_empty_output(tmp_path: Path) -> None:
        result = _run(tmp_path, "pass", name="empty_output")

        assert result.name == "empty_output"
        assert result.exit_code == 0
        assert result.stdout == ""
        assert result.stderr == ""
    """
).lstrip()

target_path.write_text(content, encoding="utf-8")
print(str(target_path))