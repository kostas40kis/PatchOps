"""Pasteback summary formatter for the optional LLM browser runner.

This module prepares compact text that can later be pasted back into ChatGPT.
It deliberately does not paste or send anything.

Safety:
- imports no Selenium modules,
- starts no browser driver,
- does not click or download anything,
- does not run PatchOps,
- does not send a message,
- emits bounded summaries instead of full report text.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .orchestration_state import OrchestrationSnapshot, OrchestrationState
from .patchops_runner import PatchOpsRunResult
from .report_locator import CanonicalReportLocation, CanonicalReportSummary


DEFAULT_MAX_LINE_LENGTH = 240
DEFAULT_MAX_NOTES = 8


@dataclass(frozen=True)
class PastebackSummary:
    text: str
    status: str
    patch: str | None
    report_path: str | None
    next_action: str | None
    line_count: int

    def to_payload(self) -> dict[str, object]:
        return {
            "text": self.text,
            "status": self.status,
            "patch": self.patch,
            "report_path": self.report_path,
            "next_action": self.next_action,
            "line_count": self.line_count,
            "text_length": len(self.text),
        }


def normalize_status(value: str | None) -> str:
    text = (value or "").strip().upper()
    if text in {"PASS", "PASSED", "SUCCESS", "OK"}:
        return "PASS"
    if text in {"FAIL", "FAILED", "ERROR", "BLOCKED"}:
        return "FAIL"
    if text:
        return text
    return "UNKNOWN"


def clamp_line(value: object, *, max_length: int = DEFAULT_MAX_LINE_LENGTH) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.split())
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    if len(text) <= max_length:
        return text
    if max_length <= 1:
        return "…"
    return text[: max_length - 1].rstrip() + "…"


def _add_kv(lines: list[str], key: str, value: object, *, max_length: int = DEFAULT_MAX_LINE_LENGTH) -> None:
    if value is None:
        return
    text = clamp_line(value, max_length=max_length)
    if text:
        lines.append(f"{key}: {text}")


def _summary_from_report_location(location: CanonicalReportLocation | None) -> CanonicalReportSummary | None:
    if location is None:
        return None
    return location.summary


def _status_from_inputs(
    *,
    report_location: CanonicalReportLocation | None,
    runner_result: PatchOpsRunResult | None,
    orchestration: OrchestrationSnapshot | None,
) -> str:
    # Fail-closed rule: a blocked orchestration state is the final truth even
    # when a lower-level runner_result was ok. Example: PatchOps exited ok, but
    # the canonical report was missing, so the summary must be FAIL.
    if orchestration is not None:
        if orchestration.blocked or orchestration.state.value.startswith("BLOCKED_"):
            return "FAIL"

    summary = _summary_from_report_location(report_location)
    if summary is not None and summary.result:
        return normalize_status(summary.result)

    if runner_result is not None:
        return "PASS" if runner_result.ok else "FAIL"

    if orchestration is not None and orchestration.state == OrchestrationState.SUMMARY_READY:
        return "PASS"

    return "UNKNOWN"


def _patch_from_inputs(
    *,
    report_location: CanonicalReportLocation | None,
    orchestration: OrchestrationSnapshot | None,
) -> str | None:
    summary = _summary_from_report_location(report_location)
    if summary is not None and summary.patch:
        return summary.patch
    if orchestration is not None and orchestration.artifact_filename:
        return orchestration.artifact_filename
    return None


def _report_path_from_inputs(
    *,
    report_location: CanonicalReportLocation | None,
    runner_result: PatchOpsRunResult | None,
    orchestration: OrchestrationSnapshot | None,
) -> str | None:
    if report_location is not None and report_location.path is not None:
        return str(report_location.path)
    if runner_result is not None and runner_result.report_path:
        return runner_result.report_path
    if orchestration is not None and orchestration.canonical_report_path:
        return orchestration.canonical_report_path
    return None


def next_action_for_status(
    status: str,
    *,
    orchestration: OrchestrationSnapshot | None = None,
    runner_result: PatchOpsRunResult | None = None,
    report_location: CanonicalReportLocation | None = None,
) -> str:
    normalized = normalize_status(status)

    if normalized == "PASS":
        return "Continue with the next patch."

    if orchestration is not None and orchestration.state == OrchestrationState.BLOCKED_REPEATED_FAILURES:
        return "Stop and inspect repeated failures before running another bundle."

    if orchestration is not None and orchestration.state == OrchestrationState.BLOCKED_REPORT_MISSING:
        return "Stop and inspect why the canonical report was not found."

    if report_location is not None and not report_location.found:
        return "Stop and inspect why the canonical report was not found."

    if runner_result is not None and runner_result.reason:
        if runner_result.reason == "timeout":
            return "Stop and inspect the timed-out PatchOps run."
        if runner_result.reason in {"patchops_payload_ok_false", "patchops_inner_result_fail", "nonzero_exit_code"}:
            return "Upload the canonical report and repair the failing patch."

    return "Upload the canonical report and repair the failing patch."


def format_pasteback_summary(
    *,
    report_location: CanonicalReportLocation | None = None,
    runner_result: PatchOpsRunResult | None = None,
    orchestration: OrchestrationSnapshot | None = None,
    notes: Iterable[str] = (),
    max_notes: int = DEFAULT_MAX_NOTES,
    max_line_length: int = DEFAULT_MAX_LINE_LENGTH,
) -> PastebackSummary:
    if max_notes < 0:
        raise ValueError("max_notes must not be negative")

    status = _status_from_inputs(
        report_location=report_location,
        runner_result=runner_result,
        orchestration=orchestration,
    )
    patch = _patch_from_inputs(report_location=report_location, orchestration=orchestration)
    report_path = _report_path_from_inputs(
        report_location=report_location,
        runner_result=runner_result,
        orchestration=orchestration,
    )
    next_action = next_action_for_status(
        status,
        orchestration=orchestration,
        runner_result=runner_result,
        report_location=report_location,
    )

    lines: list[str] = []
    lines.append(f"PatchOps browser-runner summary: {status}")

    _add_kv(lines, "Patch", patch, max_length=max_line_length)
    _add_kv(lines, "Report", report_path, max_length=max_line_length)

    summary = _summary_from_report_location(report_location)
    if summary is not None:
        _add_kv(lines, "Report result", summary.result, max_length=max_line_length)
        _add_kv(lines, "Exit code", summary.exit_code, max_length=max_line_length)
        _add_kv(lines, "Failure category", summary.failure_category, max_length=max_line_length)

    if runner_result is not None:
        _add_kv(lines, "Runner reason", runner_result.reason, max_length=max_line_length)
        _add_kv(lines, "Runner exit code", runner_result.exit_code, max_length=max_line_length)
        if runner_result.timed_out:
            lines.append("Timed out: true")

    if orchestration is not None:
        _add_kv(lines, "State", orchestration.state.value, max_length=max_line_length)
        _add_kv(lines, "Artifact", orchestration.artifact_filename, max_length=max_line_length)
        _add_kv(lines, "SHA256", orchestration.artifact_sha256, max_length=max_line_length)
        _add_kv(lines, "Last error", orchestration.last_error, max_length=max_line_length)
        lines.append(f"Failure count: {orchestration.failure_count}/{orchestration.max_failures}")

    clean_notes = [clamp_line(note, max_length=max_line_length) for note in notes]
    clean_notes = [note for note in clean_notes if note]
    for index, note in enumerate(clean_notes[:max_notes], start=1):
        lines.append(f"Note {index}: {note}")

    _add_kv(lines, "Next", next_action, max_length=max_line_length)

    text = "\n".join(lines)
    return PastebackSummary(
        text=text,
        status=status,
        patch=patch,
        report_path=report_path,
        next_action=next_action,
        line_count=len(lines),
    )


def format_success_summary(
    *,
    patch: str,
    report_path: str | Path,
    next_patch: str | None = None,
) -> PastebackSummary:
    summary = PastebackSummary(
        text="\n".join(
            line
            for line in (
                "PatchOps browser-runner summary: PASS",
                f"Patch: {clamp_line(patch)}",
                f"Report: {clamp_line(report_path)}",
                "Next: Continue with the next patch.",
                f"Note 1: Next patch: {clamp_line(next_patch)}" if next_patch else None,
            )
            if line is not None
        ),
        status="PASS",
        patch=str(patch),
        report_path=str(report_path),
        next_action="Continue with the next patch.",
        line_count=5 if next_patch else 4,
    )
    return summary


def format_failure_summary(
    *,
    patch: str | None,
    report_path: str | Path | None,
    reason: str,
    failure_category: str | None = None,
) -> PastebackSummary:
    lines = ["PatchOps browser-runner summary: FAIL"]
    _add_kv(lines, "Patch", patch)
    _add_kv(lines, "Report", report_path)
    _add_kv(lines, "Reason", reason)
    _add_kv(lines, "Failure category", failure_category)
    lines.append("Next: Upload the canonical report and repair the failing patch.")

    return PastebackSummary(
        text="\n".join(lines),
        status="FAIL",
        patch=patch,
        report_path=None if report_path is None else str(report_path),
        next_action="Upload the canonical report and repair the failing patch.",
        line_count=len(lines),
    )
