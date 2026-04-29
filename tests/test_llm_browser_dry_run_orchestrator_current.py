from __future__ import annotations

from pathlib import Path

from patchops.llm_browser.chat_page_contract import snapshot_from_html
from patchops.llm_browser.dry_run_orchestrator import dry_run_orchestrate_once
from patchops.llm_browser.orchestration_state import OrchestrationState
from patchops.llm_browser.patchops_runner import PatchOpsRunCommand, PatchOpsRunResult
from patchops.llm_browser.report_locator import CanonicalReportLocation, CanonicalReportSummary


def _html_with_bundle(filename: str = "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip") -> str:
    return f"""
    <article data-message-author-role="assistant">
      <a href="/downloads/{filename}?download=1">{filename}</a>
    </article>
    <textarea id="prompt-textarea"></textarea>
    """


def _command(tmp_path: Path) -> PatchOpsRunCommand:
    artifact = tmp_path / "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    return PatchOpsRunCommand(
        command=("python", "-m", "patchops.cli", "run-package", str(artifact), "--wrapper-root", str(tmp_path)),
        cwd=tmp_path,
        timeout_seconds=1800,
        artifact_path=artifact,
        wrapper_root=tmp_path,
    )


def _runner(tmp_path: Path, *, ok: bool = True, reason: str = "success") -> PatchOpsRunResult:
    return PatchOpsRunResult(
        command=_command(tmp_path),
        exit_code=0 if ok else 1,
        stdout='{"ok": true}' if ok else '{"ok": false}',
        stderr="",
        timed_out=False,
        ok=ok,
        reason=reason,
        report_path=str(tmp_path / "patchops_run_package_20260429_192500.txt"),
        failure_category=None if ok else "target_content_failure",
        parsed_payload={"ok": ok},
    )


def _report_location(tmp_path: Path, *, passed: bool = True) -> CanonicalReportLocation:
    report = tmp_path / "patchops_run_package_20260429_192500.txt"
    report.write_text("Result : PASS\nExitCode : 0\nPatch : D0.20\n" if passed else "Result : FAIL\nExitCode : 1\nPatch : D0.20\n", encoding="utf-8")
    summary = CanonicalReportSummary(
        path=report,
        result="PASS" if passed else "FAIL",
        exit_code=0 if passed else 1,
        patch="D0.20 end-to-end dry-run orchestrator",
        failure_category=None if passed else "target_content_failure",
        text_length=len(report.read_text(encoding="utf-8")),
    )
    return CanonicalReportLocation(
        found=True,
        path=report,
        reason="explicit_report_path_found",
        source="runner_result",
        summary=summary,
        candidates_seen=(report,),
    )


def test_dry_run_stops_waiting_when_reply_is_streaming() -> None:
    snapshot = snapshot_from_html(
        '<article data-message-author-role="assistant" data-streaming="true">working</article><textarea disabled></textarea>'
    )

    result = dry_run_orchestrate_once(snapshot, browser="edge")

    assert result.snapshot.state == OrchestrationState.WAITING_FOR_REPLY_STABLE
    assert result.artifact_detection is None
    assert "wait_for_reply_stability" in result.planned_actions
    assert result.side_effects_performed == ()
    assert result.ok is False


def test_dry_run_blocks_when_no_artifact_candidate() -> None:
    snapshot = snapshot_from_html(
        '<article data-message-author-role="assistant">no zip here</article><textarea></textarea>'
    )

    result = dry_run_orchestrate_once(snapshot, browser="opera")

    assert result.snapshot.state == OrchestrationState.BLOCKED_ARTIFACT_MISSING
    assert result.blocked is True
    assert result.artifact_detection is not None
    assert result.artifact_detection.reason == "no_patchops_bundle_candidates"
    assert "Artifact detection reason: no_patchops_bundle_candidates" in result.pasteback_summary.text


def test_dry_run_stops_at_downloading_when_no_downloaded_path_is_supplied() -> None:
    snapshot = snapshot_from_html(_html_with_bundle())

    result = dry_run_orchestrate_once(snapshot, browser="edge")

    assert result.snapshot.state == OrchestrationState.DOWNLOADING
    assert result.snapshot.artifact_filename == "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip"
    assert "would_click_download_candidate_and_wait_for_stable_file" in result.planned_actions
    assert "would_run_patchops_run_package" not in result.planned_actions
    assert result.side_effects_performed == ()


def test_dry_run_stops_at_running_patchops_when_no_runner_result_is_supplied(tmp_path: Path) -> None:
    snapshot = snapshot_from_html(_html_with_bundle())

    result = dry_run_orchestrate_once(
        snapshot,
        browser="edge",
        downloaded_path=tmp_path / "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip",
    )

    assert result.snapshot.state == OrchestrationState.RUNNING_PATCHOPS
    assert "would_run_patchops_run_package" in result.planned_actions
    assert result.pasteback_summary.status == "UNKNOWN"


def test_dry_run_blocks_on_runner_failure(tmp_path: Path) -> None:
    snapshot = snapshot_from_html(_html_with_bundle())

    result = dry_run_orchestrate_once(
        snapshot,
        downloaded_path=tmp_path / "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip",
        runner_result=_runner(tmp_path, ok=False, reason="patchops_payload_ok_false"),
    )

    assert result.snapshot.state == OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED
    assert result.snapshot.last_error == "patchops_payload_ok_false"
    assert result.pasteback_summary.status == "FAIL"
    assert result.blocked is True


def test_dry_run_blocks_when_report_location_is_missing(tmp_path: Path) -> None:
    snapshot = snapshot_from_html(_html_with_bundle())

    result = dry_run_orchestrate_once(
        snapshot,
        downloaded_path=tmp_path / "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip",
        runner_result=_runner(tmp_path, ok=True),
        report_location=None,
    )

    assert result.snapshot.state == OrchestrationState.BLOCKED_REPORT_MISSING
    assert result.snapshot.last_error == "report_location_missing"
    assert result.pasteback_summary.status == "FAIL"


def test_dry_run_blocks_when_canonical_report_is_fail(tmp_path: Path) -> None:
    snapshot = snapshot_from_html(_html_with_bundle())

    result = dry_run_orchestrate_once(
        snapshot,
        downloaded_path=tmp_path / "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip",
        runner_result=_runner(tmp_path, ok=True),
        report_location=_report_location(tmp_path, passed=False),
    )

    assert result.snapshot.state == OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED
    assert result.snapshot.canonical_report_path is not None
    assert result.pasteback_summary.status == "FAIL"
    assert "Canonical report summary was FAIL." in result.pasteback_summary.text


def test_dry_run_reaches_summary_ready_with_pass_report(tmp_path: Path) -> None:
    snapshot = snapshot_from_html(_html_with_bundle())
    downloaded = tmp_path / "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip"

    result = dry_run_orchestrate_once(
        snapshot,
        browser="edge",
        downloaded_path=downloaded,
        runner_result=_runner(tmp_path, ok=True),
        report_location=_report_location(tmp_path, passed=True),
    )

    assert result.ok is True
    assert result.blocked is False
    assert result.snapshot.state == OrchestrationState.SUMMARY_READY
    assert result.snapshot.downloaded_path == str(downloaded)
    assert result.snapshot.canonical_report_path is not None
    assert result.pasteback_summary.status == "PASS"
    assert "would_paste_summary_without_submit" in result.planned_actions
    assert result.side_effects_performed == ()


def test_dry_run_respects_processed_artifact_keys() -> None:
    filename = "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip"
    snapshot = snapshot_from_html(_html_with_bundle(filename))

    result = dry_run_orchestrate_once(
        snapshot,
        processed_artifacts={filename},
    )

    assert result.snapshot.state == OrchestrationState.BLOCKED_ARTIFACT_MISSING
    assert result.artifact_detection is not None
    assert result.artifact_detection.reason == "artifact_already_processed"


def test_dry_run_payload_is_compact(tmp_path: Path) -> None:
    snapshot = snapshot_from_html(_html_with_bundle())
    result = dry_run_orchestrate_once(
        snapshot,
        downloaded_path=tmp_path / "patch_d0_20_end_to_end_dry_run_orchestrator_patchops_bundle.zip",
        runner_result=_runner(tmp_path, ok=True),
        report_location=_report_location(tmp_path, passed=True),
    )

    payload = result.to_payload()

    assert payload["ok"] is True
    assert payload["side_effects_performed"] == []
    assert payload["snapshot"]["state"] == "SUMMARY_READY"
    assert payload["pasteback_summary"]["status"] == "PASS"
    assert "latest_assistant_text" not in payload
