from __future__ import annotations

import json
import sys
from pathlib import Path


PATCH_NAME = "mp09a_header_renderer_cleanup_recovery"


def write_utf8(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def as_repo_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_mp09a.py <repo_root> <work_root>")

    repo_root = Path(sys.argv[1]).resolve()
    work_root = Path(sys.argv[2]).resolve()
    content_root = work_root / "content"
    inner_reports = work_root / "inner_reports"
    inner_reports.mkdir(parents=True, exist_ok=True)

    renderer_path = repo_root / "patchops" / "reporting" / "renderer.py"
    sections_path = repo_root / "patchops" / "reporting" / "sections.py"
    metadata_path = repo_root / "patchops" / "reporting" / "metadata.py"
    tests_path = repo_root / "tests" / "test_reporting.py"

    required_paths = (renderer_path, sections_path, tests_path)
    for path in required_paths:
        if not path.exists():
            raise RuntimeError(f"Required repo file missing: {path}")

    renderer_text = renderer_path.read_text(encoding="utf-8")
    sections_text = sections_path.read_text(encoding="utf-8")
    tests_text = tests_path.read_text(encoding="utf-8")
    metadata_exists = metadata_path.exists()

    print(f"INFO: repo_root={repo_root}")
    print(f"INFO: renderer_exists={renderer_path.exists()}")
    print(f"INFO: sections_exists={sections_path.exists()}")
    print(f"INFO: metadata_exists={metadata_exists}")
    print(f"INFO: tests_exists={tests_path.exists()}")

    if "header_section(result)" in renderer_text:
        print("INFO: renderer.py still routes header rendering through header_section(result).")
    else:
        print("INFO: renderer.py no longer contains the exact header_section(result) call; MP09 keeps renderer scope unchanged.")

    if "def header_section(" in sections_text:
        print("AUTHORING NOTE: current sections.py still contains def header_section(...).")
        print("AUTHORING NOTE: the earlier failure is therefore most likely a brittle regex/block-match mismatch against live file text.")
    else:
        print("AUTHORING NOTE: current sections.py does not expose def header_section(...); this recovery rewrites the file explicitly.")

    metadata_code = """from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from patchops.models import WorkflowResult


def _display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


@dataclass(frozen=True)
class ReportHeaderMetadata:
    title_line: str
    patch_name: str
    manifest_path: str
    workspace_root: str
    wrapper_project_root: str
    target_project_root: str
    active_profile: str
    runtime_path: str
    backup_root: str
    report_path: str
    manifest_version: str


def build_report_header_metadata(result: WorkflowResult) -> ReportHeaderMetadata:
    return ReportHeaderMetadata(
        title_line=f"PATCHOPS {result.mode.upper()}",
        patch_name=result.manifest.patch_name,
        manifest_path=_display_path(result.manifest_path),
        workspace_root=_display_path(result.workspace_root),
        wrapper_project_root=_display_path(result.wrapper_project_root),
        target_project_root=_display_path(result.target_project_root),
        active_profile=result.resolved_profile.name,
        runtime_path=_display_path(result.runtime_path),
        backup_root=_display_path(result.backup_root),
        report_path=_display_path(result.report_path),
        manifest_version=str(result.manifest.manifest_version),
    )


def render_report_header(metadata: ReportHeaderMetadata) -> str:
    return "\\n".join(
        [
            metadata.title_line,
            f"Patch Name           : {metadata.patch_name}",
            f"Manifest Path        : {metadata.manifest_path}",
            f"Workspace Root       : {metadata.workspace_root}",
            f"Wrapper Project Root : {metadata.wrapper_project_root}",
            f"Target Project Root  : {metadata.target_project_root}",
            f"Active Profile       : {metadata.active_profile}",
            f"Runtime Path         : {metadata.runtime_path}",
            f"Backup Root          : {metadata.backup_root}",
            f"Report Path          : {metadata.report_path}",
            f"Manifest Version     : {metadata.manifest_version}",
        ]
    )
"""

    sections_code = """from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord
from patchops.reporting.metadata import build_report_header_metadata, render_report_header
from patchops.workflows.wrapper_retry import (
    WRAPPER_ONLY_RETRY_KIND,
    build_wrapper_only_retry_state,
    get_active_wrapper_only_retry_reason,
    render_wrapper_only_retry_report_lines,
)


def _rule(title: str) -> str:
    return f"\\n{title}\\n{'-' * len(title)}"


def display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


def header_section(result: WorkflowResult) -> str:
    return render_report_header(build_report_header_metadata(result))


def wrapper_only_retry_section(result: WorkflowResult) -> str:
    if result.mode != WRAPPER_ONLY_RETRY_KIND:
        return ""

    state = build_wrapper_only_retry_state(
        asdict(result.manifest),
        result.target_project_root,
        reason=get_active_wrapper_only_retry_reason(),
    )
    lines = [_rule("WRAPPER-ONLY RETRY")]
    lines.extend(render_wrapper_only_retry_report_lines(state))
    return "\\n".join(lines)


def target_files_section(paths: list[Path]) -> str:
    lines = [_rule("TARGET FILES")]
    if not paths:
        lines.append("(none)")
        return "\\n".join(lines)
    lines.extend(display_path(path) for path in paths)
    return "\\n".join(lines)


def backup_section(records: list[BackupRecord]) -> str:
    lines = [_rule("BACKUP")]
    if not records:
        lines.append("(none)")
        return "\\n".join(lines)
    for record in records:
        if record.existed and record.destination is not None:
            lines.append(
                f"BACKUP : {display_path(record.source)} -> {display_path(record.destination)}"
            )
        else:
            lines.append(f"MISSING: {display_path(record.source)}")
    return "\\n".join(lines)


def write_section(records: list[WriteRecord]) -> str:
    lines = [_rule("WRITING FILES")]
    if not records:
        lines.append("(none)")
        return "\\n".join(lines)
    lines.extend(f"WROTE : {display_path(record.path)}" for record in records)
    return "\\n".join(lines)


def command_group_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        lines.append(f"NAME    : {result.name}")
        lines.append(f"COMMAND : {result.display_command}")
        lines.append(f"CWD     : {display_path(result.working_directory)}")
        lines.append(f"EXIT    : {result.exit_code}")
    return "\\n".join(lines)


def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        lines.append(f"[{result.name}][stdout]")
        lines.append(result.stdout if result.stdout else "")
        lines.append(f"[{result.name}][stderr]")
        lines.append(result.stderr if result.stderr else "")
    return "\\n".join(lines)


def failure_section(result: WorkflowResult) -> str:
    lines = [_rule("FAILURE DETAILS")]
    if result.failure is None:
        lines.append("(none)")
        return "\\n".join(lines)
    lines.append(f"Category : {result.failure.category}")
    lines.append(f"Message  : {result.failure.message}")
    if result.failure.details:
        lines.append(f"Details  : {result.failure.details}")
    return "\\n".join(lines)
"""

    import_block = """from patchops.reporting.metadata import (
    build_report_header_metadata,
    render_report_header,
)
from patchops.reporting.renderer import render_workflow_report
"""
    if "from patchops.reporting.metadata import (" not in tests_text:
        marker = "from patchops.reporting.renderer import render_workflow_report\n"
        if marker not in tests_text:
            raise RuntimeError("Could not locate render_workflow_report import in tests/test_reporting.py.")
        tests_text = tests_text.replace(marker, import_block, 1)

    header_test_block = """
def test_header_helper_preserves_current_header_shape(tmp_path: Path):
    result = _build_result(tmp_path, "apply")
    metadata = build_report_header_metadata(result)
    text = render_report_header(metadata)

    assert text.startswith("PATCHOPS APPLY")
    assert f"Patch Name           : {result.manifest.patch_name}" in text
    assert f"Manifest Path        : {display_path(result.manifest_path)}" in text
    assert f"Workspace Root       : {display_path(result.workspace_root)}" in text
    assert f"Wrapper Project Root : {display_path(result.wrapper_project_root)}" in text
    assert f"Target Project Root  : {display_path(result.target_project_root)}" in text
    assert f"Active Profile       : {result.resolved_profile.name}" in text
    assert f"Runtime Path         : {display_path(result.runtime_path)}" in text
    assert f"Backup Root          : {display_path(result.backup_root)}" in text
    assert f"Report Path          : {display_path(result.report_path)}" in text
    assert f"Manifest Version     : {result.manifest.manifest_version}" in text


def test_report_header_stays_visible_after_helper_cleanup(tmp_path: Path):
    result = _build_result(tmp_path, "apply")
    text = render_workflow_report(result)

    assert "PATCHOPS APPLY" in text
    assert f"Patch Name           : {result.manifest.patch_name}" in text
    assert f"Active Profile       : {result.resolved_profile.name}" in text
    assert f"Report Path          : {display_path(result.report_path)}" in text
"""
    if "def test_header_helper_preserves_current_header_shape" not in tests_text:
        tests_text = tests_text.rstrip() + "\\n\\n\\n" + header_test_block.strip() + "\\n"

    metadata_content_path = content_root / "patchops" / "reporting" / "metadata.py"
    sections_content_path = content_root / "patchops" / "reporting" / "sections.py"
    tests_content_path = content_root / "tests" / "test_reporting.py"

    write_utf8(metadata_content_path, metadata_code)
    write_utf8(sections_content_path, sections_code)
    write_utf8(tests_content_path, tests_text)

    selected_tests = [
        "tests/test_reporting.py",
        "tests/test_summary_integrity_current.py",
    ]
    workflow_summary_test = repo_root / "tests" / "test_summary_integrity_workflow_current.py"
    if workflow_summary_test.exists():
        selected_tests.append("tests/test_summary_integrity_workflow_current.py")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(repo_root).replace("\\\\", "/"),
        "backup_files": [
            "patchops/reporting/metadata.py",
            "patchops/reporting/sections.py",
            "tests/test_reporting.py",
        ],
        "files_to_write": [
            {
                "path": "patchops/reporting/metadata.py",
                "content_path": as_repo_relative(metadata_content_path, work_root),
                "encoding": "utf-8",
            },
            {
                "path": "patchops/reporting/sections.py",
                "content_path": as_repo_relative(sections_content_path, work_root),
                "encoding": "utf-8",
            },
            {
                "path": "tests/test_reporting.py",
                "content_path": as_repo_relative(tests_content_path, work_root),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "reporting_contracts",
                "program": "py",
                "args": ["-m", "pytest", "-q", *selected_tests],
                "working_directory": ".",
            }
        ],
        "report_preferences": {
            "report_name_prefix": "mp09a",
            "report_dir": str(inner_reports.resolve()).replace("\\\\", "/"),
        },
        "tags": [
            "self_hosted",
            "pythonization",
            "mp09",
            "mp09a",
            "header_renderer_cleanup",
            "recovery",
        ],
        "notes": "MP09 recovery: centralize header rendering behind one metadata helper without widening the rest of report rendering.",
    }

    manifest_path = work_root / "patch_manifest.json"
    write_utf8(manifest_path, json.dumps(manifest, indent=2) + "\n")

    print(f"INFO: staged_metadata={metadata_content_path}")
    print(f"INFO: staged_sections={sections_content_path}")
    print(f"INFO: staged_tests={tests_content_path}")
    print(f"INFO: selected_tests={selected_tests}")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())