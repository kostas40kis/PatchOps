from __future__ import annotations

from pathlib import Path
import os

from patchops.llm_browser.patchops_runner import PatchOpsRunCommand, PatchOpsRunResult
from patchops.llm_browser.report_locator import (
    candidate_report_paths_from_runner,
    locate_canonical_report,
    newest_report_candidate,
    parse_report_summary,
    report_paths_from_text,
)


def _command(tmp_path: Path) -> PatchOpsRunCommand:
    artifact = tmp_path / "patch_d0_17_canonical_report_locator_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    return PatchOpsRunCommand(
        command=("python", "-m", "patchops.cli", "run-package", str(artifact), "--wrapper-root", str(tmp_path)),
        cwd=tmp_path,
        timeout_seconds=1800,
        artifact_path=artifact,
        wrapper_root=tmp_path,
    )


def _runner_result(tmp_path: Path, *, stdout: str = "", stderr: str = "", payload=None, report_path=None) -> PatchOpsRunResult:
    return PatchOpsRunResult(
        command=_command(tmp_path),
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        timed_out=False,
        ok=True,
        reason="success",
        report_path=report_path,
        failure_category=None,
        parsed_payload=payload,
    )


def test_report_paths_from_text_finds_windows_paths_and_plain_txt_lines() -> None:
    text = """
    C:\\Users\\kostas\\Desktop\\patchops_run_package_20260429_191650.txt
    /tmp/not-windows.txt
    C:\\Users\\kostas\\Desktop\\patchops_run_package_20260429_191650.txt
    C:\\Users\\kostas\\Desktop\\other_report.txt
    """

    paths = report_paths_from_text(text)

    assert paths == (
        r"C:\Users\kostas\Desktop\patchops_run_package_20260429_191650.txt",
        r"C:\Users\kostas\Desktop\other_report.txt",
        "/tmp/not-windows.txt",
    )


def test_candidate_report_paths_from_runner_prefers_payload_path(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload_report.txt"
    stdout_path = tmp_path / "stdout_report.txt"
    result = _runner_result(
        tmp_path,
        stdout=str(stdout_path),
        payload={"outer_report_path": str(payload_path)},
        report_path=str(stdout_path),
    )

    candidates = candidate_report_paths_from_runner(result)

    assert candidates[0] == payload_path
    assert stdout_path in candidates


def test_parse_report_summary_reads_result_exit_patch_and_failure_category(tmp_path: Path) -> None:
    report = tmp_path / "patchops_run_package_20260429_191650.txt"
    report.write_text(
        """
PATCHOPS RUN-PACKAGE OUTER REPORT
---------------------------------
Result              : FAIL
Exit Code           : 1
Failure Category    : target_content_failure

RESULT
======
Patch      : D0.17 canonical report locator
""",
        encoding="utf-8",
    )

    summary = parse_report_summary(report)

    assert summary.result == "FAIL"
    assert summary.exit_code == 1
    assert summary.patch == "D0.17 canonical report locator"
    assert summary.failure_category == "target_content_failure"
    assert summary.passed is False
    assert summary.text_length > 0


def test_parse_report_summary_passed_requires_pass_and_zero_exit(tmp_path: Path) -> None:
    report = tmp_path / "patchops_run_package_20260429_191650.txt"
    report.write_text("Result : PASS\nExitCode : 0\nPatch : D0.17\n", encoding="utf-8")

    summary = parse_report_summary(report)

    assert summary.result == "PASS"
    assert summary.exit_code == 0
    assert summary.passed is True


def test_locate_canonical_report_uses_existing_runner_payload_path(tmp_path: Path) -> None:
    report = tmp_path / "payload_report.txt"
    report.write_text("Result : PASS\nExitCode : 0\nPatch : D0.17\n", encoding="utf-8")
    result = _runner_result(tmp_path, payload={"outer_report_path": str(report)})

    location = locate_canonical_report(runner_result=result)

    assert location.found is True
    assert location.path == report
    assert location.reason == "explicit_report_path_found"
    assert location.source == "runner_result"
    assert location.summary is not None
    assert location.summary.passed is True


def test_locate_canonical_report_reports_missing_explicit_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing_report.txt"
    result = _runner_result(tmp_path, payload={"outer_report_path": str(missing)})

    location = locate_canonical_report(runner_result=result)

    assert location.found is False
    assert location.reason == "explicit_report_paths_missing"
    assert location.candidates_seen == (missing,)


def test_newest_report_candidate_uses_mtime_then_name(tmp_path: Path) -> None:
    older = tmp_path / "patchops_run_package_20260429_191600.txt"
    newer = tmp_path / "patchops_run_package_20260429_191700.txt"
    older.write_text("old", encoding="utf-8")
    newer.write_text("new", encoding="utf-8")
    os.utime(older, (100, 100))
    os.utime(newer, (200, 200))

    assert newest_report_candidate([tmp_path]) == newer


def test_locate_canonical_report_falls_back_to_search_roots(tmp_path: Path) -> None:
    report = tmp_path / "patchops_run_package_20260429_191650.txt"
    report.write_text("Result : PASS\nExitCode : 0\nPatch : D0.17\n", encoding="utf-8")

    location = locate_canonical_report(search_roots=[tmp_path])

    assert location.found is True
    assert location.path == report
    assert location.reason == "newest_report_candidate_found"
    assert location.source == "search_roots"


def test_locate_canonical_report_prefers_explicit_over_newest_search_root(tmp_path: Path) -> None:
    explicit = tmp_path / "explicit_report.txt"
    newest = tmp_path / "patchops_run_package_20260429_191700.txt"
    explicit.write_text("Result : PASS\nExitCode : 0\nPatch : explicit\n", encoding="utf-8")
    newest.write_text("Result : PASS\nExitCode : 0\nPatch : newest\n", encoding="utf-8")
    os.utime(explicit, (100, 100))
    os.utime(newest, (200, 200))
    result = _runner_result(tmp_path, payload={"outer_report_path": str(explicit)})

    location = locate_canonical_report(runner_result=result, search_roots=[tmp_path])

    assert location.path == explicit
    assert location.summary is not None
    assert location.summary.patch == "explicit"


def test_locate_canonical_report_no_candidates() -> None:
    location = locate_canonical_report()

    assert location.found is False
    assert location.reason == "no_report_candidates"
    assert location.candidates_seen == ()


def test_location_payload_is_compact(tmp_path: Path) -> None:
    report = tmp_path / "patchops_run_package_20260429_191650.txt"
    report.write_text("Result : PASS\nExitCode : 0\nPatch : D0.17\n", encoding="utf-8")

    location = locate_canonical_report(search_roots=[tmp_path])
    payload = location.to_payload()

    assert payload["found"] is True
    assert payload["path"] == str(report)
    assert payload["summary"]["passed"] is True
    assert payload["summary"]["text_length"] == len(report.read_text(encoding="utf-8"))
    assert "text" not in payload["summary"]
