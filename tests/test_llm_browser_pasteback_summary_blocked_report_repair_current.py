from __future__ import annotations

from pathlib import Path

from patchops.llm_browser.orchestration_state import OrchestrationState, OrchestrationSnapshot
from patchops.llm_browser.pasteback_summary import format_pasteback_summary, next_action_for_status
from patchops.llm_browser.patchops_runner import PatchOpsRunCommand, PatchOpsRunResult


def _runner(tmp_path: Path) -> PatchOpsRunResult:
    artifact = tmp_path / "patch_d0_20b_dry_run_missing_report_status_repair_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    command = PatchOpsRunCommand(
        command=("python", "-m", "patchops.cli", "run-package", str(artifact), "--wrapper-root", str(tmp_path)),
        cwd=tmp_path,
        timeout_seconds=1800,
        artifact_path=artifact,
        wrapper_root=tmp_path,
    )
    return PatchOpsRunResult(
        command=command,
        exit_code=0,
        stdout='{"ok": true}',
        stderr="",
        timed_out=False,
        ok=True,
        reason="success",
        report_path=str(tmp_path / "missing_report.txt"),
        failure_category=None,
        parsed_payload={"ok": True},
    )


def test_blocked_report_missing_overrides_successful_runner_status(tmp_path: Path) -> None:
    orchestration = OrchestrationSnapshot(
        state=OrchestrationState.BLOCKED_REPORT_MISSING,
        failure_count=1,
        max_failures=3,
        last_error="report_location_missing",
    )

    summary = format_pasteback_summary(
        runner_result=_runner(tmp_path),
        orchestration=orchestration,
        notes=("Canonical report was not available to the dry run.",),
    )

    assert summary.status == "FAIL"
    assert "PatchOps browser-runner summary: FAIL" in summary.text
    assert "State: BLOCKED_REPORT_MISSING" in summary.text
    assert "Last error: report_location_missing" in summary.text
    assert summary.next_action == "Stop and inspect why the canonical report was not found."


def test_next_action_prioritizes_blocked_report_missing_even_without_location() -> None:
    orchestration = OrchestrationSnapshot(
        state=OrchestrationState.BLOCKED_REPORT_MISSING,
        failure_count=1,
        max_failures=3,
        last_error="report_location_missing",
    )

    assert (
        next_action_for_status("FAIL", orchestration=orchestration)
        == "Stop and inspect why the canonical report was not found."
    )
