import json
from pathlib import Path

import pytest

from patchops.handoff import (
    build_current_handoff_payload,
    build_latest_report_index_payload,
    render_current_handoff_lines,
    write_current_handoff,
    write_current_handoff_json,
    write_latest_report_copy,
    write_latest_report_index,
)
from patchops.models import FailureInfo, Manifest, ResolvedProfile, WorkflowResult


def _build_result(
    tmp_path: Path,
    *,
    mode: str = "apply",
    patch_name: str = "patch_62_latest_report_indexing",
    result_label: str = "PASS",
    exit_code: int = 0,
    failure: FailureInfo | None = None,
) -> WorkflowResult:
    report_path = tmp_path / f"{mode}_report.txt"
    report_path.write_text("SUMMARY\n-------\nExitCode : 0\nResult   : PASS\n", encoding="utf-8")

    return WorkflowResult(
        mode=mode,
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name=patch_name,
            active_profile="generic_python",
            files_to_write=[],
        ),
        resolved_profile=ResolvedProfile(
            name="generic_python",
            default_target_root=None,
            runtime_path=None,
        ),
        workspace_root=tmp_path.parent,
        wrapper_project_root=tmp_path,
        target_project_root=tmp_path / "target_project",
        runtime_path=None,
        backup_root=tmp_path / "backup_root",
        report_path=report_path,
        backup_records=[],
        write_records=[],
        validation_results=[],
        smoke_results=[],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
        failure=failure,
        exit_code=exit_code,
        result_label=result_label,
    )


def test_build_current_handoff_payload_for_green_result(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    payload = build_current_handoff_payload(result)

    assert payload["schema_version"] == 1
    assert payload["project"] == "PatchOps"
    assert payload["current_stage"] == "Stage 2 in progress"
    assert payload["repo_state"]["latest_run_mode"] == "apply"
    assert payload["repo_state"]["current_status"] == "pass"
    assert payload["repo_state"]["failure_class"] == "none"
    assert payload["latest_patch"]["manifest_patch_name"] == "patch_62_latest_report_indexing"
    assert payload["latest_patch"]["latest_attempted_patch"] == "Patch 62"
    assert payload["latest_patch"]["latest_passed_patch"] == "Patch 62"
    assert payload["resume"]["next_recommended_mode"] == "new_patch"
    assert payload["resume"]["next_action"] == "Continue with Patch 63."
    assert "docs/llm_usage.md" in payload["required_reading"]


def test_build_current_handoff_payload_for_target_failure(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="target_project_failure", message="docs failed"),
    )
    payload = build_current_handoff_payload(result)

    assert payload["repo_state"]["current_status"] == "fail"
    assert payload["repo_state"]["failure_class"] == "target_project_failure"
    assert payload["latest_patch"]["latest_passed_patch"] == "unknown from this run"
    assert payload["resume"]["next_recommended_mode"] == "repair_patch"
    assert payload["resume"]["next_action"] == "Keep the repair narrow. Write a repair patch for the failed target surface."


def test_write_current_handoff_json_writes_default_file(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    written = write_current_handoff_json(result)

    handoff_path = Path(written)
    assert handoff_path == tmp_path / "handoff" / "current_handoff.json"
    assert handoff_path.exists()

    payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    assert payload["latest_patch"]["latest_attempted_patch"] == "Patch 62"
    assert payload["resume"]["next_recommended_mode"] == "new_patch"
    assert payload["required_reading"][0] == "docs/llm_usage.md"


def test_write_current_handoff_markdown_still_writes_default_file(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    written = write_current_handoff(result)

    handoff_path = Path(written)
    assert handoff_path == tmp_path / "handoff" / "current_handoff.md"
    assert handoff_path.exists()

    text = handoff_path.read_text(encoding="utf-8")
    assert "Latest Attempted Patch: Patch 62" in text
    assert "Next Recommended Mode : new_patch" in text


def test_build_latest_report_index_payload_for_green_result(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    payload = build_latest_report_index_payload(result)

    assert payload["schema_version"] == 1
    assert payload["project"] == "PatchOps"
    assert payload["manifest_patch_name"] == "patch_62_latest_report_indexing"
    assert payload["latest_attempted_patch"] == "Patch 62"
    assert payload["latest_passed_patch"] == "Patch 62"
    assert payload["latest_run_mode"] == "apply"
    assert payload["current_status"] == "pass"
    assert payload["failure_class"] == "none"
    assert payload["latest_report_exists"] is True
    assert payload["latest_report_copy_filename"] == "latest_report_copy.txt"


def test_write_latest_report_copy_writes_default_file(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    written = write_latest_report_copy(result)

    copy_path = Path(written)
    assert copy_path == tmp_path / "handoff" / "latest_report_copy.txt"
    assert copy_path.exists()
    assert copy_path.read_text(encoding="utf-8") == result.report_path.read_text(encoding="utf-8")


def test_write_latest_report_copy_raises_when_source_report_missing(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    result.report_path.unlink()

    with pytest.raises(FileNotFoundError):
        write_latest_report_copy(result)


def test_write_latest_report_index_writes_default_file(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    copy_path = Path(write_latest_report_copy(result))
    index_written = write_latest_report_index(result, latest_report_copy_path=copy_path)

    index_path = Path(index_written)
    assert index_path == tmp_path / "handoff" / "latest_report_index.json"
    assert index_path.exists()

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    assert payload["latest_report_path"] == str(result.report_path)
    assert payload["latest_report_copy_path"] == str(copy_path)
    assert payload["latest_report_exists"] is True


def test_render_current_handoff_lines_for_wrapper_failure(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="wrapper_failure", message="report write failed"),
    )
    text = "\n".join(render_current_handoff_lines(result))

    assert "Failure Class         : wrapper_failure" in text
    assert "Next Recommended Mode : wrapper_only_retry" in text
    assert "Prefer wrapper-only retry or wrapper-only repair." in text