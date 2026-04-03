import json
from pathlib import Path

from patchops.handoff import (
    build_current_handoff_payload,
    render_current_handoff_lines,
    write_current_handoff,
    write_current_handoff_json,
)
from patchops.models import FailureInfo, Manifest, ResolvedProfile, WorkflowResult


def _build_result(
    tmp_path: Path,
    *,
    mode: str = "apply",
    patch_name: str = "patch_61_current_handoff_json",
    result_label: str = "PASS",
    exit_code: int = 0,
    failure: FailureInfo | None = None,
) -> WorkflowResult:
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
        report_path=tmp_path / f"{mode}_report.txt",
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
    assert payload["latest_patch"]["manifest_patch_name"] == "patch_61_current_handoff_json"
    assert payload["latest_patch"]["latest_attempted_patch"] == "Patch 61"
    assert payload["latest_patch"]["latest_passed_patch"] == "Patch 61"
    assert payload["resume"]["next_recommended_mode"] == "new_patch"
    assert payload["resume"]["next_action"] == "Continue with Patch 62."
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
    assert payload["latest_patch"]["latest_attempted_patch"] == "Patch 61"
    assert payload["resume"]["next_recommended_mode"] == "new_patch"
    assert payload["required_reading"][0] == "docs/llm_usage.md"


def test_write_current_handoff_markdown_still_writes_default_file(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    written = write_current_handoff(result)

    handoff_path = Path(written)
    assert handoff_path == tmp_path / "handoff" / "current_handoff.md"
    assert handoff_path.exists()

    text = handoff_path.read_text(encoding="utf-8")
    assert "Latest Attempted Patch: Patch 61" in text
    assert "Next Recommended Mode : new_patch" in text


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