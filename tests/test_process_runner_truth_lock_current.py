from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.execution.process_engine import run_process
from patchops.execution.process_runner import run_command_result
from patchops.models import CommandSpec


def _write_script(directory: Path, name: str, content: str) -> Path:
    path = directory / name
    path.write_text(content, encoding="utf-8")
    return path


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="process_runner_truth_") as temp_dir:
        root = Path(temp_dir)

        stdout_script = _write_script(
            root,
            "stdout_only.py",
            "print('stdout-only-ok')\n",
        )
        stderr_script = _write_script(
            root,
            "stderr_only.py",
            "import sys\nsys.stderr.write('stderr-only-ok\\n')\n",
        )
        mixed_script = _write_script(
            root,
            "mixed_exit.py",
            "import sys\nprint('mixed-stdout')\nsys.stderr.write('mixed-stderr\\n')\nraise SystemExit(3)\n",
        )
        argv_script = _write_script(
            root,
            "argv_dump.py",
            "import json, sys\nprint(json.dumps(sys.argv[1:]))\n",
        )

        stdout_result = run_process([sys.executable, str(stdout_script)], cwd=root)
        _assert(stdout_result.exit_code == 0, f"stdout-only exit code mismatch: {stdout_result.exit_code}")
        _assert(stdout_result.stdout.strip() == "stdout-only-ok", f"stdout-only stdout mismatch: {stdout_result.stdout!r}")
        _assert(stdout_result.stderr == "", f"stdout-only stderr mismatch: {stdout_result.stderr!r}")
        _assert(stdout_result.timed_out is False, "stdout-only unexpectedly timed out")

        stderr_result = run_process([sys.executable, str(stderr_script)], cwd=root)
        _assert(stderr_result.exit_code == 0, f"stderr-only exit code mismatch: {stderr_result.exit_code}")
        _assert(stderr_result.stdout == "", f"stderr-only stdout mismatch: {stderr_result.stdout!r}")
        _assert("stderr-only-ok" in stderr_result.stderr, f"stderr-only stderr mismatch: {stderr_result.stderr!r}")

        mixed_result = run_process([sys.executable, str(mixed_script)], cwd=root)
        _assert(mixed_result.exit_code == 3, f"mixed exit code mismatch: {mixed_result.exit_code}")
        _assert("mixed-stdout" in mixed_result.stdout, f"mixed stdout mismatch: {mixed_result.stdout!r}")
        _assert("mixed-stderr" in mixed_result.stderr, f"mixed stderr mismatch: {mixed_result.stderr!r}")
        _assert(mixed_result.timed_out is False, "mixed result unexpectedly timed out")

        preserved_args = ["alpha beta", 'quote"mark', r"C:\temp\a b.txt"]
        command = CommandSpec(
            name="argv_preservation",
            program=sys.executable,
            args=[str(argv_script), *preserved_args],
            working_directory=".",
            use_profile_runtime=False,
            allowed_exit_codes=[0],
        )
        execution_result = run_command_result(
            command,
            runtime_path=None,
            working_directory_root=root,
            phase="validation",
        )
        _assert(execution_result.exit_code == 0, f"run_command_result exit mismatch: {execution_result.exit_code}")
        observed_args = json.loads(execution_result.stdout.strip())
        _assert(observed_args == preserved_args, f"argv preservation mismatch: {observed_args!r}")
        _assert(execution_result.stderr == "", f"run_command_result stderr mismatch: {execution_result.stderr!r}")
        _assert(
            Path(execution_result.working_directory).resolve() == root.resolve(),
            f"working directory mismatch: {execution_result.working_directory!r}",
        )
        _assert(execution_result.phase == "validation", f"phase mismatch: {execution_result.phase!r}")
        _assert(str(argv_script) in execution_result.display_command, "display command did not include script path")

    print("process-runner truth-lock validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
