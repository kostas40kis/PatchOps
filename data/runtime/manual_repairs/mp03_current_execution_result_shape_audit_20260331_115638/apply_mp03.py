from pathlib import Path
from textwrap import dedent

project_root = Path(r"C:\dev\patchops")
target_path = project_root / "tests" / "test_process_runner.py"

content = dedent(
    """
    from __future__ import annotations

    import json
    import sys
    from pathlib import Path

    from patchops.execution.process_runner import run_command
    from patchops.execution.quoting import render_display_command
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


    def test_run_command_preserves_arguments_with_spaces(tmp_path: Path) -> None:
        payload = "two words"
        code = (
            "import json, sys; "
            "print(json.dumps(sys.argv[1:]))"
        )
        args = ["-c", code, payload]

        result = _run(tmp_path, code, name="argv_spaces", args=args)

        assert json.loads(result.stdout.strip()) == [payload]
        assert result.args == args


    def test_run_command_preserves_quotes_and_backslashes_in_arguments(tmp_path: Path) -> None:
        payload = 'quote "and" slash \\\\ path'
        code = (
            "import json, sys; "
            "print(json.dumps(sys.argv[1:]))"
        )
        args = ["-c", code, payload]

        result = _run(tmp_path, code, name="argv_quotes", args=args)

        assert json.loads(result.stdout.strip()) == [payload]
        assert result.args == args


    def test_run_command_exposes_current_result_fields_used_downstream(tmp_path: Path) -> None:
        code = "pass"
        args = ["-c", code]

        result = _run(tmp_path, code, name="shape_audit", args=args)

        assert result.name == "shape_audit"
        assert result.program == sys.executable
        assert result.args == args
        assert result.working_directory == tmp_path.resolve()
        assert result.exit_code == 0
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.display_command == render_display_command(sys.executable, args)
        assert result.phase == "validation"


    def test_run_command_uses_profile_runtime_in_result_shape(tmp_path: Path) -> None:
        runtime_path = Path(sys.executable)
        code = "import sys; sys.stdout.write(sys.executable)"
        args = ["-c", code]

        result = _run(
            tmp_path,
            code,
            name="profile_runtime_shape",
            args=args,
            runtime_path=runtime_path,
            use_profile_runtime=True,
        )

        assert result.program == str(runtime_path)
        assert result.args == args
        assert result.stdout == str(runtime_path)
        assert result.display_command == render_display_command(str(runtime_path), args)
        assert result.phase == "validation"


    def test_run_command_resolves_relative_working_directory_in_result_shape(tmp_path: Path) -> None:
        working_directory = "nested\\child"
        expected_cwd = (tmp_path / "nested" / "child").resolve()
        expected_cwd.mkdir(parents=True, exist_ok=True)
        code = "import os, sys; sys.stdout.write(os.getcwd())"

        result = _run(
            tmp_path,
            code,
            name="cwd_shape",
            working_directory=working_directory,
        )

        assert result.working_directory == expected_cwd
        assert Path(result.stdout) == expected_cwd
    """
).lstrip()

target_path.write_text(content, encoding="utf-8")
print(str(target_path))