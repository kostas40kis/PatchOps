from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
PATCH_ROOT = Path(r"C:\\dev\\patchops\\data\\runtime\\manual_repairs\\patch_134_summary_integrity_report_derivation_20260328_232659")
CONTENT_ROOT = PATCH_ROOT / "content"


def write_utf8_no_bom(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


renderer_text = """from __future__ import annotations

from patchops.execution.failure_classifier import classify_command_failure
from patchops.models import WorkflowResult
from patchops.reporting.sections import (
    backup_section,
    command_group_section,
    failure_section,
    full_output_section,
    header_section,
    target_files_section,
    wrapper_only_retry_section,
    write_section,
)
from patchops.reporting.summary import render_summary


def _first_required_command_failure_exit_code(result: WorkflowResult) -> int | None:
    required_groups = (
        (result.validation_results, result.manifest.validation_commands),
        (result.smoke_results, result.manifest.smoke_commands),
    )

    for command_results, command_specs in required_groups:
        for index, command_result in enumerate(command_results):
            allowed_exit_codes = [0]
            if index < len(command_specs):
                allowed_exit_codes = list(command_specs[index].allowed_exit_codes)

            if classify_command_failure(command_result, allowed_exit_codes) is not None:
                return command_result.exit_code

    return None


def _resolve_summary_state(result: WorkflowResult) -> tuple[int, str]:
    required_failure_exit_code = _first_required_command_failure_exit_code(result)
    if required_failure_exit_code is not None:
        return required_failure_exit_code, "FAIL"

    if result.failure is not None:
        derived_exit_code = result.exit_code if result.exit_code != 0 else 1
        return derived_exit_code, "FAIL"

    return result.exit_code, result.result_label


def render_workflow_report(result: WorkflowResult) -> str:
    target_paths = [
        result.target_project_root / spec.path
        for spec in result.manifest.files_to_write
    ]
    derived_exit_code, derived_result_label = _resolve_summary_state(result)

    sections = [
        header_section(result),
        wrapper_only_retry_section(result),
        target_files_section(target_paths),
        backup_section(result.backup_records),
        write_section(result.write_records),
        command_group_section("VALIDATION COMMANDS", result.validation_results),
        full_output_section(result.validation_results, "FULL OUTPUT"),
        command_group_section("SMOKE COMMANDS", result.smoke_results),
        full_output_section(result.smoke_results, "SMOKE OUTPUT"),
        command_group_section("AUDIT COMMANDS", result.audit_results),
        full_output_section(result.audit_results, "AUDIT OUTPUT"),
        command_group_section("CLEANUP COMMANDS", result.cleanup_results),
        full_output_section(result.cleanup_results, "CLEANUP OUTPUT"),
        command_group_section("ARCHIVE COMMANDS", result.archive_results),
        full_output_section(result.archive_results, "ARCHIVE OUTPUT"),
        failure_section(result),
        render_summary(derived_exit_code, derived_result_label),
    ]
    return "\\n\\n".join(section for section in sections if section)
"""

test_reporting_path = PROJECT_ROOT / "tests" / "test_reporting.py"
test_reporting_text = test_reporting_path.read_text(encoding="utf-8")

old_import = "from patchops.models import FileWriteSpec, Manifest, ResolvedProfile, WorkflowResult"
new_import = "from patchops.models import CommandResult, CommandSpec, FileWriteSpec, Manifest, ResolvedProfile, WorkflowResult"

if old_import in test_reporting_text:
    test_reporting_text = test_reporting_text.replace(old_import, new_import, 1)
elif new_import not in test_reporting_text:
    raise RuntimeError("Could not locate expected test_reporting.py import line to patch.")

reporting_block = """
# PATCHOPS_PATCH134_REPORT_SUMMARY_INTEGRITY_START
def _command(name: str, exit_code: int, phase: str = "validation") -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest", "-q"],
        working_directory=Path("."),
        exit_code=exit_code,
        stdout="",
        stderr="",
        display_command="py -m pytest -q",
        phase=phase,
    )


def _command_spec(name: str, *, allowed_exit_codes: list[int] | None = None) -> CommandSpec:
    return CommandSpec(
        name=name,
        program="py",
        args=["-m", "pytest", "-q"],
        working_directory=".",
        use_profile_runtime=False,
        allowed_exit_codes=list(allowed_exit_codes or [0]),
    )


def test_report_summary_derives_fail_from_required_validation_result(tmp_path: Path):
    result = _build_result(tmp_path, "apply")
    result.manifest.validation_commands.append(_command_spec("required_validation"))
    result.validation_results.append(_command("required_validation", 4, "validation"))

    text = render_workflow_report(result)

    assert "NAME    : required_validation" in text
    assert "EXIT    : 4" in text
    assert "ExitCode : 4" in text
    assert "Result   : FAIL" in text


def test_report_summary_respects_allowed_exit_codes_for_validation(tmp_path: Path):
    result = _build_result(tmp_path, "apply")
    result.manifest.validation_commands.append(
        _command_spec("expected_verifier", allowed_exit_codes=[0, 3])
    )
    result.validation_results.append(_command("expected_verifier", 3, "validation"))

    text = render_workflow_report(result)

    assert "NAME    : expected_verifier" in text
    assert "EXIT    : 3" in text
    assert "ExitCode : 0" in text
    assert "Result   : PASS" in text
# PATCHOPS_PATCH134_REPORT_SUMMARY_INTEGRITY_END
""".strip()

pattern = re.compile(
    r"\n# PATCHOPS_PATCH134_REPORT_SUMMARY_INTEGRITY_START.*?# PATCHOPS_PATCH134_REPORT_SUMMARY_INTEGRITY_END\n?",
    re.DOTALL,
)

if pattern.search(test_reporting_text):
    test_reporting_text = pattern.sub("\n" + reporting_block + "\n", test_reporting_text)
else:
    test_reporting_text = test_reporting_text.rstrip() + "\n\n" + reporting_block + "\n"

write_utf8_no_bom(CONTENT_ROOT / "renderer.py", renderer_text)
write_utf8_no_bom(CONTENT_ROOT / "test_reporting.py", test_reporting_text)

manifest = {
    "manifest_version": "1",
    "patch_name": "patch_134_summary_integrity_report_derivation",
    "active_profile": "generic_python",
    "target_project_root": "C:/dev/patchops",
    "backup_files": [
        "patchops/reporting/renderer.py",
        "tests/test_reporting.py",
    ],
    "files_to_write": [
        {
            "path": "patchops/reporting/renderer.py",
            "content": None,
            "content_path": "content/renderer.py",
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_reporting.py",
            "content": None,
            "content_path": "content/test_reporting.py",
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "summary_integrity_reporting_contract",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_summary_integrity_current.py",
                "tests/test_reporting.py",
                "tests/test_failure_classifier.py",
            ],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        }
    ],
    "report_preferences": {
        "report_name_prefix": "patch_134_summary_integrity_report_derivation",
        "write_to_desktop": True,
    },
    "tags": [
        "self_hosted",
        "summary_integrity",
        "reporting",
        "maintenance",
    ],
    "notes": "Derive report summary from required command results and preserve allowed_exit_codes for tolerated verifier-style runs.",
}

write_utf8_no_bom(PATCH_ROOT / "patch_manifest.json", json.dumps(manifest, indent=2) + "\\n")
print(str(PATCH_ROOT / "patch_manifest.json"))