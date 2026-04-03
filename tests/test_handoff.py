import json
from pathlib import Path

import patchops.cli as cli
from patchops.handoff import (
    build_current_handoff_payload,
    build_latest_report_index_payload,
    build_next_action_recommendation,
    build_next_prompt_text_from_report_state,
    export_handoff_bundle,
    render_current_handoff_lines,
    write_current_handoff,
    write_current_handoff_json,
    write_latest_report_copy,
    write_latest_report_index,
)
from patchops.models import FailureInfo, FileWriteSpec, Manifest, ResolvedProfile, WorkflowResult


def _build_result(
    tmp_path: Path,
    *,
    mode: str = "apply",
    patch_name: str = "patch_66_generated_next_prompt",
    result_label: str = "PASS",
    exit_code: int = 0,
    failure: FailureInfo | None = None,
    file_specs: list[FileWriteSpec] | None = None,
    existing_target_files: list[str] | None = None,
) -> WorkflowResult:
    report_path = tmp_path / f"{mode}_report.txt"
    report_path.write_text("SUMMARY\n-------\nExitCode : 0\nResult   : PASS\n", encoding="utf-8")

    target_root = tmp_path / "target_project"
    target_root.mkdir(parents=True, exist_ok=True)

    for relative in existing_target_files or []:
        destination = target_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("ok\n", encoding="utf-8")

    return WorkflowResult(
        mode=mode,
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name=patch_name,
            active_profile="generic_python",
            files_to_write=file_specs or [],
        ),
        resolved_profile=ResolvedProfile(
            name="generic_python",
            default_target_root=None,
            runtime_path=None,
        ),
        workspace_root=tmp_path.parent,
        wrapper_project_root=tmp_path,
        target_project_root=target_root,
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


def _write_apply_report(
    root: Path,
    *,
    patch_name: str = "patch_64_export_handoff_cli_surface",
    result_label: str = "PASS",
    failure_category: str | None = None,
) -> Path:
    report_path = root / "latest_report.txt"
    failure_block = "(none)"
    if failure_category is not None:
        failure_block = f"Category : {failure_category}\nMessage  : simulated failure\n"

    report_text = (
        "PATCHOPS APPLY\n"
        f"Patch Name           : {patch_name}\n"
        "Manifest Path        : C:\\dev\\patchops\\data\\runtime\\self_hosted\\example.json\n"
        "Workspace Root       : C:\\dev\n"
        f"Wrapper Project Root : {root}\n"
        f"Target Project Root  : {root}\n"
        "Active Profile       : generic_python\n"
        "Runtime Path         : (none)\n"
        f"Backup Root          : {root}\\data\\runtime\\patch_backups\\example\n"
        f"Report Path          : {report_path}\n"
        "Manifest Version     : 1\n"
        "\n"
        "TARGET FILES\n"
        "------------\n"
        f"{root}\\patchops\\handoff.py\n"
        "\n"
        "BACKUP\n"
        "------\n"
        "(none)\n"
        "\n"
        "WRITING FILES\n"
        "-------------\n"
        f"WROTE : {root}\\patchops\\handoff.py\n"
        "\n"
        "VALIDATION COMMANDS\n"
        "-------------------\n"
        "NAME    : pytest\n"
        "COMMAND : python -m pytest -q\n"
        f"CWD     : {root}\n"
        "EXIT    : 0\n"
        "\n"
        "FULL OUTPUT\n"
        "-----------\n"
        "[pytest][stdout]\n"
        "...\n"
        "\n"
        "[pytest][stderr]\n"
        "\n"
        "\n"
        "FAILURE DETAILS\n"
        "---------------\n"
        f"{failure_block}\n"
        "SUMMARY\n"
        "-------\n"
        f"ExitCode : {0 if result_label == 'PASS' else 1}\n"
        f"Result   : {result_label}\n"
    )
    report_path.write_text(report_text, encoding="utf-8")
    return report_path


def test_recommendation_for_green_result_is_new_patch(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    recommendation = build_next_action_recommendation(result)

    assert recommendation["recommended_mode"] == "new_patch"
    assert recommendation["next_action"] == "Continue with Patch 67."
    assert recommendation["escalation_required"] is False
    assert "latest run passed" in recommendation["rationale"].lower()


def test_recommendation_for_target_failure_is_repair_patch(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="target_project_failure", message="pytest failed"),
    )
    recommendation = build_next_action_recommendation(result)

    assert recommendation["recommended_mode"] == "repair_patch"
    assert recommendation["escalation_required"] is False
    assert "repair patch" in recommendation["next_action"].lower()


def test_recommendation_for_wrapper_failure_after_apply_with_existing_targets_is_wrapper_only_retry(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        mode="apply",
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="wrapper_failure", message="report writer failed"),
        file_specs=[FileWriteSpec(path="docs/example.md", content="hello\n")],
        existing_target_files=["docs/example.md"],
    )
    recommendation = build_next_action_recommendation(result)

    assert recommendation["recommended_mode"] == "wrapper_only_retry"
    assert recommendation["escalation_required"] is False
    assert "wrapper-only retry" in recommendation["next_action"].lower()


def test_recommendation_for_wrapper_failure_during_verify_with_existing_targets_is_verify_only(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        mode="verify_only",
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="wrapper_failure", message="report writer failed"),
        file_specs=[FileWriteSpec(path="docs/example.md", content="hello\n")],
        existing_target_files=["docs/example.md"],
    )
    recommendation = build_next_action_recommendation(result)

    assert recommendation["recommended_mode"] == "verify_only"
    assert recommendation["escalation_required"] is False
    assert "verify-only rerun" in recommendation["next_action"].lower()


def test_recommendation_for_wrapper_failure_with_missing_targets_requires_manual_review(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        mode="apply",
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="wrapper_failure", message="report writer failed"),
        file_specs=[FileWriteSpec(path="docs/missing.md", content="hello\n")],
        existing_target_files=[],
    )
    recommendation = build_next_action_recommendation(result)

    assert recommendation["recommended_mode"] == "manual_review"
    assert recommendation["escalation_required"] is True
    assert recommendation["missing_target_count"] == 1
    assert recommendation["known_blockers"] == [str(result.target_project_root / "docs" / "missing.md")]


def test_current_handoff_payload_includes_recommendation_details(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    payload = build_current_handoff_payload(result)

    assert payload["resume"]["next_recommended_mode"] == "new_patch"
    assert payload["recommendation"]["rationale"]
    assert payload["recommendation"]["escalation_required"] is False


def test_latest_report_index_payload_includes_next_action_fields(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    payload = build_latest_report_index_payload(result)

    assert payload["next_recommended_mode"] == "new_patch"
    assert payload["next_action"] == "Continue with Patch 67."
    assert payload["escalation_required"] is False


def test_write_current_handoff_json_writes_recommendation_payload(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    written = write_current_handoff_json(result)

    payload = json.loads(Path(written).read_text(encoding="utf-8"))
    assert payload["recommendation"]["recommended_mode"] == "new_patch"
    assert payload["recommendation"]["next_action"] == "Continue with Patch 67."


def test_write_current_handoff_markdown_includes_recommendation_reason_and_escalation(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    written = write_current_handoff(result)

    text = Path(written).read_text(encoding="utf-8")
    lines = text.splitlines()

    assert any(
        line.startswith("Recommendation Why") and
        "The latest run passed, so the trustworthy next step is the next planned patch." in line
        for line in lines
    )
    assert any(
        line.startswith("Escalation Required") and line.rstrip().endswith("no")
        for line in lines
    )


def test_write_latest_report_copy_and_index_still_work(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    copy_path = Path(write_latest_report_copy(result))
    index_path = Path(write_latest_report_index(result, latest_report_copy_path=copy_path))

    assert copy_path.exists()
    assert index_path.exists()

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    assert payload["latest_report_copy_path"] == str(copy_path)
    assert payload["next_recommended_mode"] == "new_patch"


def test_build_next_prompt_text_from_report_state_contains_required_shape(tmp_path: Path) -> None:
    report_path = _write_apply_report(tmp_path, result_label="PASS")
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    next_prompt_path = Path(payload["next_prompt_path"])
    text = next_prompt_path.read_text(encoding="utf-8")

    assert "Read these files in this order:" in text
    assert "1. handoff/current_handoff.md" in text
    assert "2. handoff/current_handoff.json" in text
    assert "3. handoff/latest_report_copy.txt" in text
    assert "Then produce only the next repair patch or next planned patch." in text


def test_export_handoff_bundle_from_green_report_creates_bundle_and_next_prompt(tmp_path: Path) -> None:
    report_path = _write_apply_report(tmp_path, result_label="PASS")
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    bundle_root = handoff_root / "bundle" / "current"

    assert payload["current_status"] == "pass"
    assert payload["next_recommended_mode"] == "new_patch"
    assert payload["next_action"] == "Continue with Patch 65."
    assert (handoff_root / "current_handoff.md").exists()
    assert (handoff_root / "current_handoff.json").exists()
    assert (handoff_root / "latest_report_copy.txt").exists()
    assert (handoff_root / "latest_report_index.json").exists()
    assert (handoff_root / "next_prompt.txt").exists()
    assert (bundle_root / "current_handoff.md").exists()
    assert (bundle_root / "current_handoff.json").exists()
    assert (bundle_root / "latest_report_copy.txt").exists()
    assert (bundle_root / "latest_report_index.json").exists()
    assert (bundle_root / "next_prompt.txt").exists()


def test_export_handoff_bundle_from_target_failure_report_recommends_repair_and_writes_prompt(tmp_path: Path) -> None:
    report_path = _write_apply_report(
        tmp_path,
        result_label="FAIL",
        failure_category="target_project_failure",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    assert payload["current_status"] == "fail"
    assert payload["failure_class"] == "target_project_failure"
    assert payload["next_recommended_mode"] == "repair_patch"
    assert "repair patch" in payload["next_action"].lower()

    next_prompt_path = Path(payload["next_prompt_path"])
    text = next_prompt_path.read_text(encoding="utf-8")
    assert "failure class: target_project_failure" in text
    assert "Keep the repair narrow. Write a repair patch for the failed target surface." in text


def test_cli_export_handoff_command_generates_bundle_and_next_prompt(tmp_path: Path) -> None:
    report_path = _write_apply_report(tmp_path, result_label="PASS")

    exit_code = cli.main(
        [
            "export-handoff",
            "--report-path",
            str(report_path),
            "--wrapper-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "handoff" / "current_handoff.md").exists()
    assert (tmp_path / "handoff" / "current_handoff.json").exists()
    assert (tmp_path / "handoff" / "latest_report_copy.txt").exists()
    assert (tmp_path / "handoff" / "latest_report_index.json").exists()
    assert (tmp_path / "handoff" / "next_prompt.txt").exists()
    assert (tmp_path / "handoff" / "bundle" / "current" / "current_handoff.md").exists()
    assert (tmp_path / "handoff" / "bundle" / "current" / "next_prompt.txt").exists()