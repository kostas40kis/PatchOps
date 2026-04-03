from pathlib import Path
import re
from textwrap import dedent

project_root = Path(r"C:\dev\patchops")

common_path = project_root / "patchops" / "workflows" / "common.py"
apply_path = project_root / "patchops" / "workflows" / "apply_patch.py"
verify_path = project_root / "patchops" / "workflows" / "verify_only.py"
common_test_path = project_root / "tests" / "test_common_execution_adapter.py"
workflow_contract_test_path = project_root / "tests" / "test_workflow_execution_adapter_current.py"

common_text = common_path.read_text(encoding="utf-8")

if "from patchops.execution.failure_classifier import classify_command_failure" not in common_text:
    common_text = common_text.replace(
        "from patchops.files.paths import ensure_directory\n",
        "from patchops.files.paths import ensure_directory\nfrom patchops.execution.failure_classifier import classify_command_failure\nfrom patchops.execution.process_runner import run_command\n",
    )

if "def execute_command_group(" not in common_text:
    common_text = common_text.rstrip() + "\n\n\ndef execute_command_group(commands, *, runtime_path, working_directory_root, phase: str):\n    results = []\n    for command in commands:\n        result = run_command(\n            command,\n            runtime_path=runtime_path,\n            working_directory_root=working_directory_root,\n            phase=phase,\n        )\n        results.append(result)\n        command_failure = classify_command_failure(result, command.allowed_exit_codes)\n        if command_failure is not None:\n            return results, command_failure\n    return results, None\n"

common_path.write_text(common_text, encoding="utf-8")

apply_text = apply_path.read_text(encoding="utf-8")
apply_text = apply_text.replace(
    "from patchops.execution.failure_classifier import classify_command_failure, classify_exception\n",
    "from patchops.execution.failure_classifier import classify_exception\n",
)
apply_text = apply_text.replace(
    "from patchops.execution.process_runner import run_command\n",
    "",
)
apply_text = apply_text.replace(
    "from patchops.workflows.common import build_report_path, default_report_directory, infer_workspace_root\n",
    "from patchops.workflows.common import build_report_path, default_report_directory, execute_command_group, infer_workspace_root\n",
)
apply_loop_pattern = re.compile(
    r"""        for phase_name, commands, sink in \[\n            \(\"validation\", manifest\.validation_commands, validation_results\),\n            \(\"smoke\", manifest\.smoke_commands, smoke_results\),\n            \(\"audit\", manifest\.audit_commands, audit_results\),\n            \(\"cleanup\", manifest\.cleanup_commands, cleanup_results\),\n            \(\"archive\", manifest\.archive_commands, archive_results\),\n        \]:\n            for command in commands:\n                result = run_command\(command, runtime_path=runtime_path, working_directory_root=target_root, phase=phase_name\)\n                sink.append\(result\)\n                command_failure = classify_command_failure\(result, command\.allowed_exit_codes\)\n                if command_failure is not None:\n                    failure = command_failure\n                    exit_code = result\.exit_code\n                    result_label = \"FAIL\"\n                    raise RuntimeError\(command_failure\.message\)\n"""
)
apply_loop_replacement = dedent(
    """
            for phase_name, commands, sink in [
                ("validation", manifest.validation_commands, validation_results),
                ("smoke", manifest.smoke_commands, smoke_results),
                ("audit", manifest.audit_commands, audit_results),
                ("cleanup", manifest.cleanup_commands, cleanup_results),
                ("archive", manifest.archive_commands, archive_results),
            ]:
                phase_results, command_failure = execute_command_group(
                    commands,
                    runtime_path=runtime_path,
                    working_directory_root=target_root,
                    phase=phase_name,
                )
                sink.extend(phase_results)
                if command_failure is not None:
                    failure = command_failure
                    exit_code = phase_results[-1].exit_code
                    result_label = "FAIL"
                    raise RuntimeError(command_failure.message)
    """
)
apply_text, apply_count = apply_loop_pattern.subn(apply_loop_replacement, apply_text, count=1)
if apply_count != 1:
    raise RuntimeError("Failed to update apply_patch.py command loop for MP05.")
apply_path.write_text(apply_text, encoding="utf-8")

verify_text = verify_path.read_text(encoding="utf-8")
verify_text = verify_text.replace(
    "from patchops.execution.failure_classifier import classify_command_failure, classify_exception\n",
    "from patchops.execution.failure_classifier import classify_exception\n",
)
verify_text = verify_text.replace(
    "from patchops.execution.process_runner import run_command\n",
    "",
)
verify_text = verify_text.replace(
    "from patchops.workflows.common import build_report_path, default_report_directory, infer_workspace_root\n",
    "from patchops.workflows.common import build_report_path, default_report_directory, execute_command_group, infer_workspace_root\n",
)
verify_loop_pattern = re.compile(
    r"""        for phase_name, commands, sink in \[\n            \(\"validation\", manifest\.validation_commands, validation_results\),\n            \(\"smoke\", manifest\.smoke_commands, smoke_results\),\n            \(\"audit\", manifest\.audit_commands, audit_results\),\n        \]:\n            for command in commands:\n                result = run_command\(command, runtime_path=runtime_path, working_directory_root=target_root, phase=phase_name\)\n                sink.append\(result\)\n                command_failure = classify_command_failure\(result, command\.allowed_exit_codes\)\n                if command_failure is not None:\n                    failure = command_failure\n                    exit_code = result\.exit_code\n                    result_label = \"FAIL\"\n                    raise RuntimeError\(command_failure\.message\)\n"""
)
verify_loop_replacement = dedent(
    """
            for phase_name, commands, sink in [
                ("validation", manifest.validation_commands, validation_results),
                ("smoke", manifest.smoke_commands, smoke_results),
                ("audit", manifest.audit_commands, audit_results),
            ]:
                phase_results, command_failure = execute_command_group(
                    commands,
                    runtime_path=runtime_path,
                    working_directory_root=target_root,
                    phase=phase_name,
                )
                sink.extend(phase_results)
                if command_failure is not None:
                    failure = command_failure
                    exit_code = phase_results[-1].exit_code
                    result_label = "FAIL"
                    raise RuntimeError(command_failure.message)
    """
)
verify_text, verify_count = verify_loop_pattern.subn(verify_loop_replacement, verify_text, count=1)
if verify_count != 1:
    raise RuntimeError("Failed to update verify_only.py command loop for MP05.")
verify_path.write_text(verify_text, encoding="utf-8")

common_test_path.write_text(
    dedent(
        '''
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
        '''
    ).lstrip(),
    encoding="utf-8",
)

workflow_contract_test_path.write_text(
    dedent(
        '''
        from __future__ import annotations

        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]


        def _read(relative_path: str) -> str:
            return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


        def test_apply_and_verify_use_common_execution_adapter() -> None:
            apply_text = _read("patchops/workflows/apply_patch.py")
            verify_text = _read("patchops/workflows/verify_only.py")

            assert "execute_command_group(" in apply_text
            assert "execute_command_group(" in verify_text
            assert "from patchops.execution.process_runner import run_command" not in apply_text
            assert "from patchops.execution.process_runner import run_command" not in verify_text


        def test_common_module_exposes_single_execution_adapter() -> None:
            common_text = _read("patchops/workflows/common.py")

            assert "def execute_command_group(" in common_text
            assert "classify_command_failure" in common_text
            assert "run_command(" in common_text
        '''
    ).lstrip(),
    encoding="utf-8",
)

for path in (
    common_path,
    apply_path,
    verify_path,
    common_test_path,
    workflow_contract_test_path,
):
    print(str(path))