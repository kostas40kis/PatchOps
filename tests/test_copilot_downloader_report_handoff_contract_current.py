from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.downloader_session_report import run_downloader_session_report, sha256_file as session_sha256_file
from patchops.copilot_downloader.report_handoff_contract import (
    FAIL_HANDOFF_WRITE,
    PASS_HANDOFF_WRITTEN,
    build_handoff_payload,
    run_report_handoff_contract,
    summarize_report,
    uploader_modules_imported,
    write_latest_report_handoff,
)


def _write_canonical_report(path: Path, *, result: str = "PASS", exit_code: int = 0, sentinel: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "PATCHOPS RUN SUMMARY\n"
        "--------------------\n"
        "Mode               : apply\n"
        "Patch Name         : demo_patch\n"
        "Report Path        : C:/tmp/demo.txt\n"
        f"ExitCode           : {exit_code}\n"
        f"Result             : {result}\n"
        f"{sentinel}\n",
        encoding="utf-8",
    )
    return path


def test_handoff_writes_ready_json_and_text_for_valid_pass_report(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "patchops_report.txt")
    digest = session_sha256_file(canonical)
    result = run_report_handoff_contract(
        repo_root=tmp_path,
        handoff_dir=tmp_path / "handoff",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=canonical,
        canonical_report_sha256=digest,
        final_result="PASS",
        exit_code=0,
        artifact_kind="patchops_bundle_zip",
        artifact_sha256="abc123",
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_HANDOFF_WRITTEN
    assert result["uploader_ready"] is True
    assert result["canonical_report_sha256"] == digest
    assert result["result"] == "PASS"
    assert result["exit_code"] == 0
    assert Path(result["handoff_paths"]["json"]).is_file()
    assert Path(result["handoff_paths"]["text"]).is_file()
    payload = json.loads(Path(result["handoff_paths"]["json"]).read_text(encoding="utf-8"))
    assert payload["uploader_ready"] is True
    assert payload["handoff_contract"] == "file_only_no_uploader_import"
    assert payload["artifact_kind"] == "patchops_bundle_zip"
    assert payload["artifact_sha256"] == "abc123"
    assert payload["uploader_import"]["uploader_import_performed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_handoff_sets_uploader_ready_false_when_report_missing(tmp_path: Path):
    result = run_report_handoff_contract(
        repo_root=tmp_path,
        handoff_dir=tmp_path / "handoff",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=tmp_path / "missing.txt",
        final_result="PASS",
        exit_code=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_HANDOFF_WRITE
    assert result["uploader_ready"] is False
    assert "canonical report is missing" in result["issues"]
    payload = json.loads(Path(result["handoff_paths"]["json"]).read_text(encoding="utf-8"))
    assert payload["uploader_ready"] is False


def test_handoff_sets_uploader_ready_false_for_fail_report_or_nonzero_exit(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "failed.txt", result="FAIL", exit_code=7)
    result = run_report_handoff_contract(
        repo_root=tmp_path,
        handoff_dir=tmp_path / "handoff",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=canonical,
        canonical_report_sha256=session_sha256_file(canonical),
        final_result="FAIL",
        exit_code=7,
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_HANDOFF_WRITE
    assert result["uploader_ready"] is False
    assert any("Result must be PASS" in issue for issue in result["issues"])
    assert any("ExitCode must be 0" in issue for issue in result["issues"])


def test_handoff_blocks_sha_mismatch(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "patchops_report.txt")
    result = run_report_handoff_contract(
        repo_root=tmp_path,
        handoff_dir=tmp_path / "handoff",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=canonical,
        canonical_report_sha256="0" * 64,
        final_result="PASS",
        exit_code=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_HANDOFF_WRITE
    assert result["uploader_ready"] is False
    assert any("sha256" in issue for issue in result["issues"])


def test_handoff_can_consume_d4_session_report_json(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "patchops_report.txt")
    session = run_downloader_session_report(
        repo_root=tmp_path,
        output_dir=tmp_path / "session_reports",
        evidence_root=tmp_path / "session_evidence",
        canonical_report_path=canonical,
        requested_result="PASS",
        requested_exit_code=0,
    )
    result = run_report_handoff_contract(
        repo_root=tmp_path,
        handoff_dir=tmp_path / "handoff",
        evidence_root=tmp_path / "handoff_evidence",
        session_report_path=session["report_paths"]["json"],
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_HANDOFF_WRITTEN
    assert result["uploader_ready"] is True
    payload = json.loads(Path(result["handoff_paths"]["json"]).read_text(encoding="utf-8"))
    assert payload["session_report_path"] == str(Path(session["report_paths"]["json"]).resolve(strict=False))


def test_handoff_text_contains_human_readable_contract_fields(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "patchops_report.txt")
    result = write_latest_report_handoff(
        repo_root=tmp_path,
        handoff_dir=tmp_path / "handoff",
        canonical_report_path=canonical,
        canonical_report_sha256=session_sha256_file(canonical),
        final_result="PASS",
        exit_code=0,
    )
    text = Path(result["handoff_paths"]["text"]).read_text(encoding="utf-8")
    assert "PATCHOPS DOWNLOADER REPORT HANDOFF" in text
    assert "uploader_ready: True" in text
    assert "canonical_report_path:" in text
    assert "canonical_report_sha256:" in text
    assert "result: PASS" in text
    assert "exit_code: 0" in text


def test_handoff_does_not_copy_report_content_into_handoff_or_evidence(tmp_path: Path):
    sentinel = "RAW_CANONICAL_REPORT_SENTINEL_D5_01"
    canonical = _write_canonical_report(tmp_path / "reports" / "patchops_report.txt", sentinel=sentinel)
    result = run_report_handoff_contract(
        repo_root=tmp_path,
        handoff_dir=tmp_path / "handoff",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=canonical,
        canonical_report_sha256=session_sha256_file(canonical),
        final_result="PASS",
        exit_code=0,
    )
    serialized = json.dumps(result)
    handoff_json = Path(result["handoff_paths"]["json"]).read_text(encoding="utf-8")
    evidence_json = Path(result["evidence_files"]["json"]).read_text(encoding="utf-8")
    assert sentinel not in serialized
    assert sentinel not in handoff_json
    assert sentinel not in evidence_json


def test_handoff_safety_violation_prevents_uploader_ready(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "patchops_report.txt")
    result = run_report_handoff_contract(
        repo_root=tmp_path,
        handoff_dir=tmp_path / "handoff",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=canonical,
        canonical_report_sha256=session_sha256_file(canonical),
        final_result="PASS",
        exit_code=0,
        safety={"webdriver_used": True},
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_HANDOFF_WRITE
    assert result["uploader_ready"] is False
    assert any("webdriver" in issue for issue in result["issues"])


def test_summarize_report_parses_signals_and_hash(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "patchops_report.txt")
    summary = summarize_report(canonical, session_sha256_file(canonical))
    assert summary["canonical_report_exists"] is True
    assert summary["canonical_report_sha256_matches"] is True
    assert summary["signals"]["result_text"] == "PASS"
    assert summary["signals"]["exit_code"] == 0


def test_build_handoff_payload_uses_fail_label_when_invalid(tmp_path: Path):
    payload = build_handoff_payload(repo_root=tmp_path, canonical_report_path=tmp_path / "missing.txt", final_result="PASS", exit_code=0)
    assert payload["status"] == FAIL_HANDOFF_WRITE
    assert payload["uploader_ready"] is False


def test_uploader_import_probe_does_not_import_or_call_uploader():
    result = uploader_modules_imported()
    assert result["uploader_import_performed"] is False
    assert result["uploader_called"] is False


def test_repository_report_handoff_doctor_writes_controlled_not_ready_handoff():
    result = run_report_handoff_contract(
        repo_root=Path.cwd(),
        handoff_dir="data/runtime/copilot_handoff",
        evidence_root="data/runtime/copilot_downloader/d5_01_report_handoff_contract_test",
        canonical_report_path="data/runtime/copilot_downloader/d5_01_missing_canonical_report.txt",
        final_result="PASS",
        exit_code=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_HANDOFF_WRITE
    assert result["uploader_ready"] is False
    assert result["checks"]["handoff_json_written"] is True
    assert result["checks"]["handoff_text_written"] is True
    assert result["checks"]["uploader_import_not_performed"] is True
    assert result["checks"]["file_based_contract_only"] is True