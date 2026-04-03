from pathlib import Path
from textwrap import dedent

project_root = Path(r"C:\dev\patchops")

files = {
    project_root / "patchops" / "execution" / "result_model.py": dedent(
        """
        from __future__ import annotations

        import subprocess
        from dataclasses import dataclass
        from pathlib import Path

        from patchops.models import CommandResult


        @dataclass(frozen=True)
        class ExecutionResult:
            name: str
            program: str
            args: list[str]
            working_directory: Path
            exit_code: int
            stdout: str
            stderr: str
            display_command: str
            phase: str

            @classmethod
            def from_completed_process(
                cls,
                *,
                name: str,
                program: str,
                args: list[str],
                working_directory: Path,
                completed: subprocess.CompletedProcess[str],
                display_command: str,
                phase: str,
            ) -> "ExecutionResult":
                return cls(
                    name=name,
                    program=program,
                    args=list(args),
                    working_directory=working_directory,
                    exit_code=completed.returncode,
                    stdout=completed.stdout,
                    stderr=completed.stderr,
                    display_command=display_command,
                    phase=phase,
                )

            @classmethod
            def from_command_result(cls, result: CommandResult) -> "ExecutionResult":
                return cls(
                    name=result.name,
                    program=result.program,
                    args=list(result.args),
                    working_directory=result.working_directory,
                    exit_code=result.exit_code,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    display_command=result.display_command,
                    phase=result.phase,
                )

            def to_command_result(self) -> CommandResult:
                return CommandResult(
                    name=self.name,
                    program=self.program,
                    args=list(self.args),
                    working_directory=self.working_directory,
                    exit_code=self.exit_code,
                    stdout=self.stdout,
                    stderr=self.stderr,
                    display_command=self.display_command,
                    phase=self.phase,
                )


        def normalize_command_result(result: CommandResult) -> ExecutionResult:
            return ExecutionResult.from_command_result(result)


        __all__ = ["ExecutionResult", "normalize_command_result"]
        """
    ).lstrip(),
    project_root / "patchops" / "execution" / "process_runner.py": dedent(
        """
        from __future__ import annotations

        import subprocess
        from pathlib import Path

        from patchops.execution.quoting import render_display_command
        from patchops.execution.result_model import ExecutionResult
        from patchops.models import CommandResult, CommandSpec


        def run_command(
            command: CommandSpec,
            *,
            runtime_path: Path | None,
            working_directory_root: Path,
            phase: str,
        ) -> CommandResult:
            if command.use_profile_runtime:
                if runtime_path is None:
                    raise RuntimeError(f"Command {command.name!r} requested profile runtime, but none was resolved.")
                program = str(runtime_path)
            else:
                if command.program is None:
                    raise RuntimeError(f"Command {command.name!r} has no program configured.")
                program = command.program

            working_directory = (
                (working_directory_root / command.working_directory).resolve()
                if command.working_directory
                else working_directory_root.resolve()
            )
            args = list(command.args)
            display_command = render_display_command(program, args)

            completed = subprocess.run(
                [program, *args],
                cwd=str(working_directory),
                capture_output=True,
                text=True,
                check=False,
            )
            return ExecutionResult.from_completed_process(
                name=command.name,
                program=program,
                args=args,
                working_directory=working_directory,
                completed=completed,
                display_command=display_command,
                phase=phase,
            ).to_command_result()
        """
    ).lstrip(),
    project_root / "tests" / "test_execution_result_model.py": dedent(
        """
        from __future__ import annotations

        import subprocess
        from pathlib import Path

        from patchops.execution.result_model import ExecutionResult, normalize_command_result
        from patchops.models import CommandResult


        def test_execution_result_from_completed_process_normalizes_current_fields(tmp_path: Path) -> None:
            completed = subprocess.CompletedProcess(
                args=["py", "-m", "pytest"],
                returncode=3,
                stdout="hello",
                stderr="warn",
            )

            result = ExecutionResult.from_completed_process(
                name="validation_case",
                program="py",
                args=["-m", "pytest"],
                working_directory=tmp_path,
                completed=completed,
                display_command="py -m pytest",
                phase="validation",
            )

            assert result.name == "validation_case"
            assert result.program == "py"
            assert result.args == ["-m", "pytest"]
            assert result.working_directory == tmp_path
            assert result.exit_code == 3
            assert result.stdout == "hello"
            assert result.stderr == "warn"
            assert result.display_command == "py -m pytest"
            assert result.phase == "validation"


        def test_execution_result_to_command_result_round_trips_current_shape(tmp_path: Path) -> None:
            execution_result = ExecutionResult(
                name="smoke_case",
                program="py",
                args=["-m", "pytest", "-q"],
                working_directory=tmp_path,
                exit_code=0,
                stdout="ok",
                stderr="",
                display_command="py -m pytest -q",
                phase="smoke",
            )

            command_result = execution_result.to_command_result()

            assert isinstance(command_result, CommandResult)
            assert command_result.name == "smoke_case"
            assert command_result.program == "py"
            assert command_result.args == ["-m", "pytest", "-q"]
            assert command_result.working_directory == tmp_path
            assert command_result.exit_code == 0
            assert command_result.stdout == "ok"
            assert command_result.stderr == ""
            assert command_result.display_command == "py -m pytest -q"
            assert command_result.phase == "smoke"


        def test_normalize_command_result_preserves_current_command_result_contract(tmp_path: Path) -> None:
            command_result = CommandResult(
                name="audit_case",
                program="py",
                args=["-m", "pytest", "tests/test_example.py"],
                working_directory=tmp_path,
                exit_code=5,
                stdout="",
                stderr="failed",
                display_command="py -m pytest tests/test_example.py",
                phase="audit",
            )

            normalized = normalize_command_result(command_result)

            assert normalized == ExecutionResult(
                name="audit_case",
                program="py",
                args=["-m", "pytest", "tests/test_example.py"],
                working_directory=tmp_path,
                exit_code=5,
                stdout="",
                stderr="failed",
                display_command="py -m pytest tests/test_example.py",
                phase="audit",
            )
        """
    ).lstrip(),
}

for path, content in files.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(str(path))