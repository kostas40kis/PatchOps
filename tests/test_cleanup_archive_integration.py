import json
from pathlib import Path

from patchops.workflows.archive import (
    ARCHIVE_REPORT_SECTIONS,
    build_archive_workflow_state,
    render_archive_scope_lines,
)
from patchops.workflows.cleanup import (
    CLEANUP_REPORT_SECTIONS,
    build_cleanup_workflow_state,
    render_cleanup_scope_lines,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = PROJECT_ROOT / "examples" / "generic_cleanup_archive_patch.json"


def test_cleanup_archive_example_manifest_exists_and_is_maintenance_shaped() -> None:
    assert EXAMPLE_PATH.exists(), f"Missing example manifest: {EXAMPLE_PATH}"
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    assert payload["active_profile"] == "generic_python"
    assert payload["patch_name"] == "generic_cleanup_archive_example"
    assert len(payload.get("cleanup_commands") or []) >= 1
    assert len(payload.get("archive_commands") or []) >= 1


def test_cleanup_and_archive_workflows_can_be_built_from_same_manifest() -> None:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    cleanup_state = build_cleanup_workflow_state(payload)
    archive_state = build_archive_workflow_state(payload)

    assert cleanup_state.mode == "cleanup"
    assert archive_state.mode == "archive"
    assert cleanup_state.cleanup_command_count >= 1
    assert archive_state.archive_command_count >= 1
    assert cleanup_state.deterministic_reporting is True
    assert archive_state.deterministic_reporting is True


def test_cleanup_and_archive_report_sections_stay_distinct_and_explicit() -> None:
    assert CLEANUP_REPORT_SECTIONS == (
        "TARGET FILES",
        "BACKUP",
        "CLEANUP COMMANDS",
        "CLEANUP OUTPUT",
        "SUMMARY",
    )
    assert ARCHIVE_REPORT_SECTIONS == (
        "TARGET FILES",
        "BACKUP",
        "ARCHIVE COMMANDS",
        "ARCHIVE OUTPUT",
        "SUMMARY",
    )


def test_cleanup_and_archive_scope_lines_are_human_readable() -> None:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    cleanup_lines = render_cleanup_scope_lines(build_cleanup_workflow_state(payload))
    archive_lines = render_archive_scope_lines(build_archive_workflow_state(payload))

    assert "Scope    : cleanup workflow" in cleanup_lines
    assert "Evidence : explicit and deterministic cleanup sections" in cleanup_lines
    assert "Scope    : archive workflow" in archive_lines
    assert "Evidence : explicit and traceable archive sections" in archive_lines


def test_maintenance_example_proves_non_code_patch_flow_support() -> None:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    target_files = payload.get("target_files") or []
    files_to_write = payload.get("files_to_write") or []

    assert len(payload.get("cleanup_commands") or []) >= 1
    assert len(payload.get("archive_commands") or []) >= 1
    assert target_files == []
    assert len(files_to_write) == 1
    assert files_to_write[0]["path"] == "CLEANUP_ARCHIVE_EXAMPLE.txt"
