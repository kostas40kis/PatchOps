from __future__ import annotations

import json
import os
import time
from pathlib import Path

from patchops.copilot_downloader.canonical_report_locator import (
    FAIL_REPORT_MISSING,
    PASS_CANONICAL_REPORT_FOUND,
    find_latest_report_candidate,
    locate_canonical_report,
    parse_patchops_report_signals,
    sha256_file,
)


def _write_report(path: Path, *, patch_name: str = "demo_patch", result: str = "PASS", exit_code: int = 0, sentinel: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "PATCHOPS RUN SUMMARY\n"
        "--------------------\n"
        "Mode               : apply\n"
        f"Patch Name         : {patch_name}\n"
        "Report Path        : C:/tmp/report.txt\n"
        f"ExitCode           : {exit_code}\n"
        f"Result             : {result}\n"
        f"{sentinel}\n",
        encoding="utf-8",
    )
    return path


def test_canonical_report_locator_missing_report_is_controlled_block(tmp_path: Path):
    result = locate_canonical_report(
        repo_root=tmp_path,
        evidence_root=tmp_path / "evidence",
        report_search_dir=tmp_path / "empty_reports",
        patch_name="missing_patch",
        run_started_at=str(time.time()),
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_REPORT_MISSING
    assert result["report_sha256"] is None
    assert result["checks"]["missing_report_blocks"] is True
    assert result["safety"]["canonical_report_found"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_canonical_report_locator_accepts_explicit_valid_report_and_hashes_without_logging_content(tmp_path: Path):
    sentinel = "RAW_REPORT_CONTENT_SENTINEL_D4_01"
    run_start = time.time() - 10
    report = _write_report(tmp_path / "reports" / "patchops_downloader_demo_patch_001.txt", patch_name="demo_patch", sentinel=sentinel)
    os.utime(report, (time.time(), time.time()))
    result = locate_canonical_report(
        repo_root=tmp_path,
        evidence_root=tmp_path / "evidence",
        report_path=report,
        run_started_at=str(run_start),
        expected_result="PASS",
        expected_exit_code=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_CANONICAL_REPORT_FOUND
    assert result["report_sha256"] == sha256_file(report)
    assert result["signals"]["result_text"] == "PASS"
    assert result["signals"]["exit_code"] == 0
    assert result["safety"]["canonical_report_found"] is True
    serialized = json.dumps(result)
    evidence_json = Path(result["evidence_files"]["json"]).read_text(encoding="utf-8")
    assert sentinel not in serialized
    assert sentinel not in evidence_json


def test_canonical_report_locator_blocks_missing_result_or_exitcode(tmp_path: Path):
    report = tmp_path / "reports" / "bad.txt"
    report.parent.mkdir()
    report.write_text("PATCHOPS RUN SUMMARY\nResult : PASS\n", encoding="utf-8")
    result = locate_canonical_report(repo_root=tmp_path, evidence_root=tmp_path / "evidence", report_path=report)
    assert result["ok"] is True
    assert result["result_label"] == FAIL_REPORT_MISSING
    assert any("ExitCode" in issue for issue in result["issues"])
    assert result["report_sha256"] is None


def test_canonical_report_locator_blocks_stale_report(tmp_path: Path):
    report = _write_report(tmp_path / "reports" / "stale.txt")
    old = time.time() - 100
    os.utime(report, (old, old))
    result = locate_canonical_report(repo_root=tmp_path, evidence_root=tmp_path / "evidence", report_path=report, run_started_at=str(time.time()))
    assert result["ok"] is True
    assert result["result_label"] == FAIL_REPORT_MISSING
    assert any("older" in issue for issue in result["issues"])


def test_canonical_report_locator_finds_latest_matching_report(tmp_path: Path):
    reports = tmp_path / "reports"
    first = _write_report(reports / "patchops_downloader_demo_patch_001.txt", patch_name="demo_patch")
    second = _write_report(reports / "patchops_downloader_demo_patch_002.txt", patch_name="demo_patch")
    os.utime(first, (time.time() - 20, time.time() - 20))
    os.utime(second, (time.time(), time.time()))
    found = find_latest_report_candidate(search_dir=reports, patch_name="demo_patch", after_epoch=time.time() - 30)
    assert found == second.resolve(strict=False)
    result = locate_canonical_report(repo_root=tmp_path, evidence_root=tmp_path / "evidence", report_search_dir=reports, patch_name="demo_patch", run_started_at=str(time.time() - 30))
    assert result["ok"] is True
    assert result["selected_report_path"] == str(second.resolve(strict=False))


def test_canonical_report_locator_blocks_expected_result_mismatch(tmp_path: Path):
    report = _write_report(tmp_path / "reports" / "failed.txt", result="FAIL", exit_code=1)
    result = locate_canonical_report(
        repo_root=tmp_path,
        evidence_root=tmp_path / "evidence",
        report_path=report,
        expected_result="PASS",
        expected_exit_code=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_REPORT_MISSING
    assert any("Result mismatch" in issue for issue in result["issues"])
    assert any("ExitCode mismatch" in issue for issue in result["issues"])


def test_parse_patchops_report_signals_reads_summary_fields():
    signals = parse_patchops_report_signals("Mode : apply\nPatch Name : abc\nExitCode : 0\nResult : PASS\n")
    assert signals["mode_text"] == "apply"
    assert signals["patch_name_text"] == "abc"
    assert signals["exit_code"] == 0
    assert signals["result_text"] == "PASS"


def test_repository_canonical_report_locator_doctor_is_controlled_missing_report():
    result = locate_canonical_report(
        repo_root=Path.cwd(),
        evidence_root="data/runtime/copilot_downloader/d4_01_canonical_report_locator_test",
        report_search_dir="data/runtime/copilot_downloader/d4_01_empty_report_search_test",
        patch_name="d4_01_downloader_canonical_report_locator_no_such_report",
        run_started_at=str(time.time()),
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_REPORT_MISSING
    assert result["checks"]["report_lookup_performed"] is True
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["artifact_not_executed"] is True