from __future__ import annotations

from pathlib import Path

import pytest

from patchops.llm_browser.orchestration_state import (
    OrchestrationState,
    OrchestrationSnapshot,
    new_orchestration_snapshot,
    transition,
)
from patchops.llm_browser.pasteback_summary import (
    clamp_line,
    format_failure_summary,
    format_pasteback_summary,
    format_success_summary,
    next_action_for_status,
    normalize_status,
)
from patchops.llm_browser.patchops_runner import PatchOpsRunCommand, PatchOpsRunResult
from patchops.llm_browser.report_locator import CanonicalReportLocation, CanonicalReportSummary


def _command(tmp_path: Path) -> PatchOpsRunCommand:
    artifact = tmp_path / "patch_d0_18_pasteback_summary_formatter_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    return PatchOpsRunCommand(
        command=("python", "-m", "patchops.cli", "run-package", str(artifact), "--wrapper-root", str(tmp_path)),
        cwd=tmp_path,
        timeout_seconds=1800,
        artifact_path=artifact,
        wrapper_root=tmp_path,
    )


def _runner(tmp_path: Path, *, ok: bool = True, reason: str = "success", report_path: str | None = None) -> PatchOpsRunResult:
    return PatchOpsRunResult(
        command=_command(tmp_path),
        exit_code=0 if ok else 1,
        stdout="",
        stderr="",
        timed_out=False,
        ok=ok,
        reason=reason,
        report_path=report_path,
        failure_category=None,
        parsed_payload={"ok": ok},
    )


def _location(tmp_path: Path, *, result: str = "PASS", exit_code: int = 0, patch: str = "D0.18 pasteback summary formatter") -> CanonicalReportLocation:
    report = tmp_path / "patchops_run_package_20260429_192100.txt"
    report.write_text("report", encoding="utf-8")
    summary = CanonicalReportSummary(
        path=report,
        result=result,
        exit_code=exit_code,
        patch=patch,
        failure_category=None if result == "PASS" else "target_content_failure",
        text_length=6,
    )
    return CanonicalReportLocation(
        found=True,
        path=report,
        reason="explicit_report_path_found",
        source="runner_result",
        summary=summary,
        candidates_seen=(report,),
    )


def test_normalize_status_maps_common_values() -> None:
    assert normalize_status("ok") == "PASS"
    assert normalize_status("success") == "PASS"
    assert normalize_status("failed") == "FAIL"
    assert normalize_status("") == "UNKNOWN"
    assert normalize_status("custom") == "CUSTOM"


def test_clamp_line_collapses_whitespace_and_truncates() -> None:
    assert clamp_line(" hello\n   world ") == "hello world"
    assert clamp_line("abcdef", max_length=4) == "abc…"

    with pytest.raises(ValueError, match="max_length"):
        clamp_line("abc", max_length=0)


def test_format_pasteback_summary_from_pass_report_location(tmp_path: Path) -> None:
    location = _location(tmp_path, result="PASS", exit_code=0)

    summary = format_pasteback_summary(report_location=location, notes=("focused pytest passed",))

    assert summary.status == "PASS"
    assert summary.patch == "D0.18 pasteback summary formatter"
    assert summary.report_path == str(location.path)
    assert "PatchOps browser-runner summary: PASS" in summary.text
    assert "Report result: PASS" in summary.text
    assert "Exit code: 0" in summary.text
    assert "Note 1: focused pytest passed" in summary.text
    assert "Next: Continue with the next patch." in summary.text


def test_format_pasteback_summary_from_failed_report_location(tmp_path: Path) -> None:
    location = _location(tmp_path, result="FAIL", exit_code=1)

    summary = format_pasteback_summary(report_location=location)

    assert summary.status == "FAIL"
    assert "Failure category: target_content_failure" in summary.text
    assert "Next: Upload the canonical report and repair the failing patch." in summary.text


def test_format_pasteback_summary_uses_runner_reason_when_no_report_summary(tmp_path: Path) -> None:
    runner = _runner(tmp_path, ok=False, reason="patchops_payload_ok_false", report_path=r"C:\Users\kostas\Desktop\report.txt")

    summary = format_pasteback_summary(runner_result=runner)

    assert summary.status == "FAIL"
    assert summary.report_path == r"C:\Users\kostas\Desktop\report.txt"
    assert "Runner reason: patchops_payload_ok_false" in summary.text
    assert "Runner exit code: 1" in summary.text


def test_format_pasteback_summary_includes_orchestration_metadata(tmp_path: Path) -> None:
    snapshot = new_orchestration_snapshot(browser="edge")
    snapshot = transition(snapshot, OrchestrationState.WAITING_FOR_REPLY_STABLE, reason="tick")
    snapshot = transition(snapshot, OrchestrationState.LOOKING_FOR_ARTIFACT, reason="stable")
    snapshot = transition(
        snapshot,
        OrchestrationState.DOWNLOADING,
        reason="found",
        artifact_filename="patch_d0_18_pasteback_summary_formatter_patchops_bundle.zip",
        artifact_sha256="abc123",
    )

    summary = format_pasteback_summary(orchestration=snapshot)

    assert summary.status == "UNKNOWN"
    assert summary.patch == "patch_d0_18_pasteback_summary_formatter_patchops_bundle.zip"
    assert "State: DOWNLOADING" in summary.text
    assert "Artifact: patch_d0_18_pasteback_summary_formatter_patchops_bundle.zip" in summary.text
    assert "SHA256: abc123" in summary.text
    assert "Failure count: 0/3" in summary.text


def test_format_pasteback_summary_blocked_orchestration_is_fail() -> None:
    snapshot = OrchestrationSnapshot(
        state=OrchestrationState.BLOCKED_REPEATED_FAILURES,
        failure_count=3,
        max_failures=3,
        last_error="same failure repeated",
    )

    summary = format_pasteback_summary(orchestration=snapshot)

    assert summary.status == "FAIL"
    assert "State: BLOCKED_REPEATED_FAILURES" in summary.text
    assert "Last error: same failure repeated" in summary.text
    assert "Stop and inspect repeated failures before running another bundle." in summary.text


def test_format_pasteback_summary_limits_notes() -> None:
    summary = format_pasteback_summary(
        notes=("one", "two", "three"),
        max_notes=2,
    )

    assert "Note 1: one" in summary.text
    assert "Note 2: two" in summary.text
    assert "Note 3:" not in summary.text

    with pytest.raises(ValueError, match="max_notes"):
        format_pasteback_summary(max_notes=-1)


def test_next_action_for_missing_report_location_is_fail_closed() -> None:
    location = CanonicalReportLocation(
        found=False,
        path=None,
        reason="explicit_report_paths_missing",
        source="runner_result",
        summary=None,
        candidates_seen=(),
    )

    assert next_action_for_status("FAIL", report_location=location) == "Stop and inspect why the canonical report was not found."


def test_next_action_for_timeout_runner_result(tmp_path: Path) -> None:
    runner = PatchOpsRunResult(
        command=_command(tmp_path),
        exit_code=None,
        stdout="",
        stderr="",
        timed_out=True,
        ok=False,
        reason="timeout",
        report_path=None,
        failure_category=None,
        parsed_payload=None,
    )

    assert next_action_for_status("FAIL", runner_result=runner) == "Stop and inspect the timed-out PatchOps run."


def test_format_success_summary_is_compact() -> None:
    summary = format_success_summary(
        patch="D0.18 pasteback summary formatter",
        report_path=r"C:\Users\kostas\Desktop\patchops_run_package_20260429_192100.txt",
        next_patch="D0.19 Composer paste helper",
    )

    assert summary.status == "PASS"
    assert summary.line_count == 5
    assert "D0.19 Composer paste helper" in summary.text


def test_format_failure_summary_is_compact() -> None:
    summary = format_failure_summary(
        patch="D0.18 pasteback summary formatter",
        report_path=r"C:\Users\kostas\Desktop\patchops_run_package_20260429_192100.txt",
        reason="focused pytest failed",
        failure_category="target_content_failure",
    )

    assert summary.status == "FAIL"
    assert "Reason: focused pytest failed" in summary.text
    assert "Failure category: target_content_failure" in summary.text
    assert summary.line_count == 6


def test_summary_payload_excludes_full_report_text(tmp_path: Path) -> None:
    location = _location(tmp_path)
    summary = format_pasteback_summary(report_location=location)
    payload = summary.to_payload()

    assert payload["status"] == "PASS"
    assert payload["text_length"] == len(summary.text)
    assert "report_text" not in payload
