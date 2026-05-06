from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.downloader_session_report import (
    FAIL_DOWNLOADER_SESSION_REPORTED,
    PASS_DOWNLOADER_SESSION_REPORTED,
    build_session_payload,
    normalize_patchops_commands,
    run_downloader_session_report,
    sha256_file,
    summarize_canonical_report,
    write_downloader_session_report,
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


def test_session_report_writes_pass_report_with_required_fields(tmp_path: Path):
    artifact = tmp_path / "artifact.zip"
    artifact.write_text("artifact", encoding="utf-8")
    staged = tmp_path / "staged" / "artifact.zip"
    staged.parent.mkdir()
    staged.write_text("artifact", encoding="utf-8")
    canonical = _write_canonical_report(tmp_path / "reports" / "patchops_report.txt")
    commands = [
        {
            "label": "apply-bundle",
            "command": "python -m patchops.cli apply-bundle artifact.zip",
            "working_directory": str(tmp_path),
            "exit_code": 0,
            "timed_out": False,
            "stdout": "Result : PASS\nExitCode : 0\n",
            "stderr": "",
        }
    ]
    result = run_downloader_session_report(
        repo_root=tmp_path,
        output_dir=tmp_path / "session_reports",
        evidence_root=tmp_path / "evidence",
        artifact_path=artifact,
        artifact_sha256=sha256_file(artifact),
        staged_path=staged,
        patchops_commands=commands,
        canonical_report_path=canonical,
        requested_result="PASS",
        requested_exit_code=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_DOWNLOADER_SESSION_REPORTED
    assert result["final_result"] == "PASS"
    assert result["artifact"]["path"] == str(artifact.resolve(strict=False))
    assert result["artifact"]["sha256"] == sha256_file(artifact)
    assert result["staging"]["staged_path"] == str(staged.resolve(strict=False))
    assert result["patchops_command_count"] == 1
    assert result["canonical_report"]["canonical_report_sha256"] == sha256_file(canonical)
    assert Path(result["report_paths"]["json"]).is_file()
    assert Path(result["report_paths"]["text"]).is_file()
    assert Path(result["report_paths"]["latest_json"]).is_file()
    assert Path(result["report_paths"]["latest_text"]).is_file()
    assert Path(result["evidence_files"]["json"]).is_file()


def test_session_report_writes_fail_report_when_canonical_report_missing(tmp_path: Path):
    result = run_downloader_session_report(
        repo_root=tmp_path,
        output_dir=tmp_path / "session_reports",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=tmp_path / "missing.txt",
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_DOWNLOADER_SESSION_REPORTED
    assert result["final_result"] == "FAIL"
    assert "canonical report is missing" in result["issues"]
    assert result["canonical_report"]["canonical_report_exists"] is False
    assert result["checks"]["final_pass_fail_included"] is True
    assert Path(result["report_paths"]["latest_text"]).is_file()


def test_session_report_includes_stdout_stderr_exit_codes_in_text(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "report.txt")
    result = write_downloader_session_report(
        repo_root=tmp_path,
        output_dir=tmp_path / "session_reports",
        canonical_report_path=canonical,
        patchops_commands=[{"label": "cmd", "command": "run", "exit_code": 0, "timed_out": False, "stdout": "hello stdout", "stderr": "hello stderr"}],
    )
    text = Path(result["report_paths"]["text"]).read_text(encoding="utf-8")
    assert "hello stdout" in text
    assert "hello stderr" in text
    assert "exit_code: 0" in text
    assert "final PASS/FAIL" in text


def test_session_report_does_not_copy_canonical_report_content_into_payload_or_evidence(tmp_path: Path):
    sentinel = "RAW_CANONICAL_REPORT_SENTINEL_D4_02"
    canonical = _write_canonical_report(tmp_path / "reports" / "report.txt", sentinel=sentinel)
    result = run_downloader_session_report(
        repo_root=tmp_path,
        output_dir=tmp_path / "session_reports",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=canonical,
    )
    serialized = json.dumps(result)
    evidence_json = Path(result["evidence_files"]["json"]).read_text(encoding="utf-8")
    session_json = Path(result["report_paths"]["json"]).read_text(encoding="utf-8")
    assert sentinel not in serialized
    assert sentinel not in evidence_json
    assert sentinel not in session_json


def test_session_report_marks_fail_on_nonzero_command_even_if_report_passes(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "report.txt")
    result = run_downloader_session_report(
        repo_root=tmp_path,
        output_dir=tmp_path / "session_reports",
        evidence_root=tmp_path / "evidence",
        canonical_report_path=canonical,
        patchops_commands=[{"label": "cmd", "command": "run", "exit_code": 2, "timed_out": False, "stdout": "", "stderr": "bad"}],
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_DOWNLOADER_SESSION_REPORTED
    assert result["final_result"] == "FAIL"
    assert any("nonzero" in issue for issue in result["issues"])


def test_normalize_patchops_commands_fills_required_command_fields():
    commands = normalize_patchops_commands([{"name": "check", "stdout": "out", "stderr": "err", "exit_code": 0}])
    assert commands[0]["label"] == "check"
    assert commands[0]["stdout"] == "out"
    assert commands[0]["stderr"] == "err"
    assert commands[0]["exit_code"] == 0
    assert commands[0]["stdout_size_chars"] == 3


def test_summarize_canonical_report_parses_report_signals_and_hash(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "report.txt", result="FAIL", exit_code=7)
    summary = summarize_canonical_report(canonical)
    assert summary["canonical_report_exists"] is True
    assert summary["canonical_report_sha256"] == sha256_file(canonical)
    assert summary["signals"]["result_text"] == "FAIL"
    assert summary["signals"]["exit_code"] == 7


def test_build_session_payload_accepts_absent_artifact_and_staged_path(tmp_path: Path):
    canonical = _write_canonical_report(tmp_path / "reports" / "report.txt")
    payload = build_session_payload(repo_root=tmp_path, canonical_report_path=canonical)
    assert payload["artifact"]["path"] is None
    assert payload["staging"]["staged_path"] is None
    assert payload["canonical_report"]["canonical_report_exists"] is True
    assert payload["final"]["final_result"] == "PASS"


def test_repository_session_report_doctor_writes_controlled_fail_report():
    result = run_downloader_session_report(
        repo_root=Path.cwd(),
        output_dir="data/runtime/copilot_downloader/d4_02_session_report_doctor",
        evidence_root="data/runtime/copilot_downloader/d4_02_session_report_doctor_evidence",
        canonical_report_path="data/runtime/copilot_downloader/d4_02_missing_canonical_report.txt",
    )
    assert result["ok"] is True
    assert result["result_label"] == FAIL_DOWNLOADER_SESSION_REPORTED
    assert result["final_result"] == "FAIL"
    assert result["checks"]["session_report_written"] is True
    assert result["checks"]["safety_flags_included"] is True
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["artifact_not_executed_by_reporter"] is True