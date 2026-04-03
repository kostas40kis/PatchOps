from __future__ import annotations

import json
import re
import sys
from pathlib import Path


MP15_MARKER = "PATCHOPS_MP15_COMMAND_OUTPUT_HELPER_START"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_import(text: str) -> str:
    import_line = "from patchops.reporting.command_sections import render_command_output_section"
    if import_line in text:
        return text

    anchor = "from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord\n"
    if anchor not in text:
        raise RuntimeError("Could not find sections.py import anchor for command output helper import.")
    return text.replace(anchor, anchor + import_line + "\n", 1)


def patch_full_output_section(text: str) -> str:
    pattern = re.compile(
        r"def full_output_section\(results: list\[CommandResult\], title: str\) -> str:\n(?:    .*\n)+?(?=\ndef failure_section)",
        re.MULTILINE,
    )
    replacement = (
        "def full_output_section(results: list[CommandResult], title: str) -> str:\n"
        "    return render_command_output_section(title, results)\n\n"
    )
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError("Could not patch full_output_section in sections.py.")
    return updated


def append_command_output_helper(text: str) -> str:
    if MP15_MARKER in text:
        return text

    helper = """

# PATCHOPS_MP15_COMMAND_OUTPUT_HELPER_START
from patchops.models import CommandResult


def render_command_output_lines(result: CommandResult) -> tuple[str, ...]:
    return (
        f"[{result.name}][stdout]",
        result.stdout if result.stdout else "",
        f"[{result.name}][stderr]",
        result.stderr if result.stderr else "",
    )


def render_command_output_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        lines.extend(render_command_output_lines(result))
    return "\\n".join(lines)
# PATCHOPS_MP15_COMMAND_OUTPUT_HELPER_END
"""
    if not text.endswith("\n"):
        text += "\n"
    return text + helper.lstrip("\n")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    command_sections_rel = Path("patchops") / "reporting" / "command_sections.py"
    sections_rel = Path("patchops") / "reporting" / "sections.py"
    test_rel = Path("tests") / "test_reporting_additional_helper_path_current.py"

    command_sections_path = wrapper_root / command_sections_rel
    sections_path = wrapper_root / sections_rel
    test_path = wrapper_root / test_rel

    command_sections_text = read_text(command_sections_path)
    sections_text = read_text(sections_path)

    command_sections_before = MP15_MARKER in command_sections_text
    full_output_delegated_before = "return render_command_output_section(title, results)" in sections_text

    updated_command_sections = append_command_output_helper(command_sections_text)
    updated_sections = patch_full_output_section(ensure_import(sections_text))

    test_text = """from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult, Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.command_sections import render_command_output_section
from patchops.reporting.renderer import render_workflow_report
from patchops.reporting.sections import full_output_section


def _command(tmp_path: Path) -> CommandResult:
    return CommandResult(
        name="smoke_ping",
        program="python",
        args=["-c", "print('smoke ok')"],
        working_directory=tmp_path,
        exit_code=0,
        stdout="smoke ok\\n",
        stderr="",
        display_command="python -c \\"print('smoke ok')\\"",
        phase="smoke",
    )


def test_full_output_section_delegates_to_command_output_helper(tmp_path: Path) -> None:
    command = _command(tmp_path)
    expected = render_command_output_section("SMOKE OUTPUT", [command])

    assert full_output_section([command], "SMOKE OUTPUT") == expected
    assert "[smoke_ping][stdout]" in expected
    assert "[smoke_ping][stderr]" in expected


def test_render_workflow_report_uses_helper_owned_smoke_output_path(tmp_path: Path) -> None:
    command = _command(tmp_path)
    manifest = Manifest(
        manifest_version="1",
        patch_name="mp15_report_helper_additional_workflow_path",
        active_profile="generic_python",
    )
    profile = ResolvedProfile(
        name="generic_python",
        default_target_root=None,
        runtime_path=None,
    )
    result = WorkflowResult(
        mode="apply",
        manifest_path=tmp_path / "manifest.json",
        manifest=manifest,
        resolved_profile=profile,
        workspace_root=tmp_path.parent,
        wrapper_project_root=tmp_path,
        target_project_root=tmp_path,
        runtime_path=None,
        backup_root=None,
        report_path=tmp_path / "report.txt",
        backup_records=[],
        write_records=[],
        validation_results=[],
        smoke_results=[command],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
        failure=None,
        exit_code=0,
        result_label="PASS",
    )

    report_text = render_workflow_report(result)
    expected_smoke_output = render_command_output_section("SMOKE OUTPUT", [command])

    assert expected_smoke_output in report_text
    assert "SMOKE COMMANDS" in report_text
    assert "SMOKE OUTPUT" in report_text
    assert "[smoke_ping][stdout]" in report_text
"""
    content_command_sections_path = working_root / "content" / command_sections_rel
    content_sections_path = working_root / "content" / sections_rel
    content_test_path = working_root / "content" / test_rel

    write_text(content_command_sections_path, updated_command_sections)
    write_text(content_sections_path, updated_sections)
    write_text(content_test_path, test_text)

    validation_candidates = [
        Path("tests") / "test_reporting.py",
        Path("tests") / "test_reporting_command_sections_current.py",
        Path("tests") / "test_reporting_additional_helper_path_current.py",
        Path("tests") / "test_summary_integrity_current.py",
        Path("tests") / "test_summary_derivation_lock_current.py",
        Path("tests") / "test_required_vs_tolerated_report_current.py",
        Path("tests") / "test_summary_integrity_workflow_current.py",
    ]
    validation_targets = [str(path).replace("\\\\", "/") for path in validation_candidates if (wrapper_root / path).exists()]
    new_test_rel = str(test_rel).replace("\\\\", "/")
    if new_test_rel not in validation_targets:
        validation_targets.append(new_test_rel)

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp15_report_helper_additional_workflow_path",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace("\\\\", "/"),
        "backup_files": [
            str(command_sections_rel).replace("\\\\", "/"),
            str(sections_rel).replace("\\\\", "/"),
            new_test_rel,
        ],
        "files_to_write": [
            {
                "path": str(command_sections_rel).replace("\\\\", "/"),
                "content_path": "content/patchops/reporting/command_sections.py",
                "encoding": "utf-8",
            },
            {
                "path": str(sections_rel).replace("\\\\", "/"),
                "content_path": "content/patchops/reporting/sections.py",
                "encoding": "utf-8",
            },
            {
                "path": new_test_rel,
                "content_path": "content/tests/test_reporting_additional_helper_path_current.py",
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "reporting_stream_pytest",
                "program": "python",
                "args": ["-m", "pytest", "-q", *validation_targets],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str((working_root / "inner_reports")).replace("\\\\", "/"),
            "report_name_prefix": "mp15_report_helper_additional_workflow_path",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper_reuse"],
        "notes": "MP15 wires one additional workflow path through the shared report helper model by routing full-output rendering through a helper-owned command output section.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\\n")

    lines = [
        f"decision=mp15_report_helper_reuse",
        f"command_sections_marker_before={str(command_sections_before).lower()}",
        f"full_output_delegated_before={str(full_output_delegated_before).lower()}",
        f"manifest_path={manifest_path}",
        f"target_file={wrapper_root / command_sections_rel}",
        f"target_file={wrapper_root / sections_rel}",
        f"target_file={wrapper_root / test_rel}",
    ]
    for item in validation_targets:
        lines.append(f"validation_target={item}")
    write_text(working_root / "prepare_result.txt", "\\n".join(lines) + "\\n")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())