"""End-to-end dry-run orchestrator for the optional LLM browser runner.

This module wires the passive browser-runner layers together without performing
side effects. It is intended to prove the loop shape before the real interactive
runner is enabled.

Dry-run behavior:
- no Selenium imports,
- no browser driver starts,
- no click/download happens,
- no PatchOps subprocess is executed,
- no text is pasted into a real composer,
- no message is sent.

The dry run consumes already-captured/synthetic metadata and returns the state,
artifact detection, pasteback summary, and planned next actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .artifact_detector import ArtifactDetectionResult, detect_downloadable_patchops_artifact
from .chat_page_contract import ChatPageSnapshot
from .orchestration_state import (
    OrchestrationSnapshot,
    OrchestrationState,
    new_orchestration_snapshot,
    transition,
)
from .pasteback_summary import PastebackSummary, format_pasteback_summary
from .patchops_runner import PatchOpsRunResult
from .report_locator import CanonicalReportLocation


@dataclass(frozen=True)
class DryRunOrchestrationResult:
    snapshot: OrchestrationSnapshot
    artifact_detection: ArtifactDetectionResult | None
    pasteback_summary: PastebackSummary
    planned_actions: tuple[str, ...]
    side_effects_performed: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.snapshot.state == OrchestrationState.SUMMARY_READY and self.pasteback_summary.status == "PASS"

    @property
    def blocked(self) -> bool:
        return self.snapshot.blocked

    def to_payload(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "blocked": self.blocked,
            "snapshot": self.snapshot.to_payload(),
            "artifact_detection": None
            if self.artifact_detection is None
            else self.artifact_detection.to_payload(),
            "pasteback_summary": self.pasteback_summary.to_payload(),
            "planned_actions": list(self.planned_actions),
            "side_effects_performed": list(self.side_effects_performed),
        }


def _summary(
    snapshot: OrchestrationSnapshot,
    *,
    runner_result: PatchOpsRunResult | None = None,
    report_location: CanonicalReportLocation | None = None,
    notes: Iterable[str] = (),
) -> PastebackSummary:
    return format_pasteback_summary(
        report_location=report_location,
        runner_result=runner_result,
        orchestration=snapshot,
        notes=notes,
    )


def _not_ready_reason(chat_snapshot: ChatPageSnapshot) -> str | None:
    if not chat_snapshot.has_latest_assistant_reply:
        return "missing_latest_assistant_reply"
    if chat_snapshot.streaming:
        return "reply_still_streaming"
    if not chat_snapshot.composer_enabled:
        return "composer_not_ready"
    return None


def dry_run_orchestrate_once(
    chat_snapshot: ChatPageSnapshot,
    *,
    browser: str | None = None,
    processed_artifacts: Iterable[str] | None = None,
    downloaded_path: str | Path | None = None,
    runner_result: PatchOpsRunResult | None = None,
    report_location: CanonicalReportLocation | None = None,
    max_failures: int = 3,
) -> DryRunOrchestrationResult:
    """Run one passive orchestration pass from a page snapshot.

    The caller supplies any later-stage facts (downloaded_path, runner_result,
    report_location). Missing later-stage facts cause the dry run to stop at the
    corresponding planned action instead of performing that action.
    """

    planned: list[str] = ["would_acquire_run_lock"]
    snapshot = new_orchestration_snapshot(browser=browser, max_failures=max_failures)
    snapshot = transition(snapshot, OrchestrationState.WAITING_FOR_REPLY_STABLE, reason="dry_run_started")

    not_ready = _not_ready_reason(chat_snapshot)
    if not_ready is not None:
        planned.append("wait_for_reply_stability")
        summary = _summary(snapshot, notes=(f"Dry run stopped before artifact scan: {not_ready}",))
        return DryRunOrchestrationResult(
            snapshot=snapshot,
            artifact_detection=None,
            pasteback_summary=summary,
            planned_actions=tuple(planned),
        )

    snapshot = transition(snapshot, OrchestrationState.LOOKING_FOR_ARTIFACT, reason="reply_is_stable")
    planned.append("scan_latest_assistant_reply_for_patchops_bundle")

    detection = detect_downloadable_patchops_artifact(
        chat_snapshot,
        processed_artifacts=processed_artifacts,
    )

    if not detection.found or detection.candidate is None:
        snapshot = transition(
            snapshot,
            OrchestrationState.BLOCKED_ARTIFACT_MISSING,
            reason=detection.reason,
            last_error=detection.reason,
            failure_increment=1,
        )
        summary = _summary(snapshot, notes=(f"Artifact detection reason: {detection.reason}",))
        return DryRunOrchestrationResult(
            snapshot=snapshot,
            artifact_detection=detection,
            pasteback_summary=summary,
            planned_actions=tuple(planned),
        )

    candidate = detection.candidate
    snapshot = transition(
        snapshot,
        OrchestrationState.DOWNLOADING,
        reason="artifact_detected",
        artifact_filename=candidate.filename,
    )
    planned.append("would_click_download_candidate_and_wait_for_stable_file")

    if downloaded_path is None:
        summary = _summary(snapshot, notes=("Dry run stopped before download because no downloaded_path was supplied.",))
        return DryRunOrchestrationResult(
            snapshot=snapshot,
            artifact_detection=detection,
            pasteback_summary=summary,
            planned_actions=tuple(planned),
        )

    snapshot = transition(
        snapshot,
        OrchestrationState.RUNNING_PATCHOPS,
        reason="download_ready",
        downloaded_path=str(downloaded_path),
    )
    planned.append("would_run_patchops_run_package")

    if runner_result is None:
        summary = _summary(snapshot, notes=("Dry run stopped before PatchOps execution because no runner_result was supplied.",))
        return DryRunOrchestrationResult(
            snapshot=snapshot,
            artifact_detection=detection,
            pasteback_summary=summary,
            planned_actions=tuple(planned),
        )

    if not runner_result.ok:
        snapshot = transition(
            snapshot,
            OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED,
            reason=runner_result.reason,
            last_error=runner_result.reason,
            failure_increment=1,
        )
        summary = _summary(snapshot, runner_result=runner_result, notes=("PatchOps runner result was not ok.",))
        return DryRunOrchestrationResult(
            snapshot=snapshot,
            artifact_detection=detection,
            pasteback_summary=summary,
            planned_actions=tuple(planned),
        )

    planned.append("would_locate_canonical_report")
    if report_location is None or not report_location.found or report_location.path is None:
        missing_reason = "report_location_missing" if report_location is None else report_location.reason
        snapshot = transition(
            snapshot,
            OrchestrationState.BLOCKED_REPORT_MISSING,
            reason=missing_reason,
            last_error=missing_reason,
            failure_increment=1,
        )
        summary = _summary(
            snapshot,
            runner_result=runner_result,
            report_location=report_location,
            notes=("Canonical report was not available to the dry run.",),
        )
        return DryRunOrchestrationResult(
            snapshot=snapshot,
            artifact_detection=detection,
            pasteback_summary=summary,
            planned_actions=tuple(planned),
        )

    if report_location.summary is not None and not report_location.summary.passed:
        snapshot = transition(
            snapshot,
            OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED,
            reason="canonical_report_failed",
            canonical_report_path=str(report_location.path),
            last_error="canonical_report_failed",
            failure_increment=1,
        )
        summary = _summary(
            snapshot,
            runner_result=runner_result,
            report_location=report_location,
            notes=("Canonical report summary was FAIL.",),
        )
        return DryRunOrchestrationResult(
            snapshot=snapshot,
            artifact_detection=detection,
            pasteback_summary=summary,
            planned_actions=tuple(planned),
        )

    snapshot = transition(
        snapshot,
        OrchestrationState.SUMMARY_READY,
        reason="canonical_report_passed",
        canonical_report_path=str(report_location.path),
    )
    planned.append("would_format_pasteback_summary")
    planned.append("would_paste_summary_without_submit")

    summary = _summary(
        snapshot,
        runner_result=runner_result,
        report_location=report_location,
        notes=("Dry run reached SUMMARY_READY without performing side effects.",),
    )
    return DryRunOrchestrationResult(
        snapshot=snapshot,
        artifact_detection=detection,
        pasteback_summary=summary,
        planned_actions=tuple(planned),
    )
