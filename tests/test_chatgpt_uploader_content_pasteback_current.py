from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.content_pasteback import (
    ContentPastebackPolicy,
    build_content_pasteback,
    create_sample_report,
    extract_patchops_summary,
    has_secret_hint,
)


def test_extract_patchops_summary_from_standard_report() -> None:
    summary = extract_patchops_summary(create_sample_report())

    assert summary["Result"] == "PASS"
    assert summary["ExitCode"] == "0"
    assert summary["PatchName"] == "sample_patch"


def test_small_safe_report_gets_full_content_payload(tmp_path: Path) -> None:
    result = build_content_pasteback(
        report_text=create_sample_report(),
        report_path=r"C:\Users\kostas\Desktop\sample_patch_report.txt",
        output_dir=tmp_path,
    )

    payload = Path(result.payload_path).read_text(encoding="utf-8")

    assert result.ok is True
    assert result.status == "PASS_FULL_CONTENT_PASTEBACK_READY"
    assert result.mode == "full_report"
    assert "REPORT_CONTENT_BEGIN" in payload
    assert "Result             : PASS" in payload
    assert result.safety_flags.full_report_content_included is True
    assert result.safety_flags.chatgpt_submit_performed is False
    assert result.safety_flags.file_upload_attempted is False
    assert result.safety_flags.selenium_used is False


def test_large_report_uses_compact_summary_only_without_chunks(tmp_path: Path) -> None:
    report = create_sample_report() + ("\nnoise line" * 5000)

    result = build_content_pasteback(
        report_text=report,
        output_dir=tmp_path,
        policy=ContentPastebackPolicy(max_full_report_chars=400),
    )

    payload = Path(result.payload_path).read_text(encoding="utf-8")

    assert result.ok is True
    assert result.status == "PASS_COMPACT_CONTENT_PASTEBACK_READY"
    assert result.mode == "compact_summary"
    assert "REPORT_CONTENT_BEGIN" not in payload
    assert "PATCHOPS_REPORT_CHUNK" not in payload
    assert "ChunkingDeferredTo: U1.1" in payload or result.pasteback_size_chars <= 3500
    assert result.safety_flags.compact_summary_only is True


def test_secret_like_report_uses_compact_summary_and_does_not_include_secret_body(tmp_path: Path) -> None:
    report = create_sample_report() + "\napi_key = SHOULD_NOT_BE_INCLUDED_IN_FULL_BODY\n"

    assert has_secret_hint(report) is True

    result = build_content_pasteback(report_text=report, output_dir=tmp_path)
    payload = Path(result.payload_path).read_text(encoding="utf-8")

    assert result.ok is True
    assert result.mode == "compact_summary"
    assert "REPORT_CONTENT_BEGIN" not in payload
    assert "SHOULD_NOT_BE_INCLUDED_IN_FULL_BODY" not in payload
    assert "secret-like markers" in result.reason


def test_empty_report_blocks(tmp_path: Path) -> None:
    result = build_content_pasteback(report_text="   \n", output_dir=tmp_path)

    assert result.ok is False
    assert result.status == "BLOCKED_EMPTY_REPORT"
    assert result.safety_flags.compact_summary_only is True


def test_json_evidence_written(tmp_path: Path) -> None:
    result = build_content_pasteback(report_text=create_sample_report(), output_dir=tmp_path)

    data = json.loads(Path(result.json_path).read_text(encoding="utf-8"))

    assert data["status"] == "PASS_FULL_CONTENT_PASTEBACK_READY"
    assert data["safety_flags"]["chatgpt_submit_performed"] is False
    assert data["safety_flags"]["file_upload_attempted"] is False


def test_runner_executes_directly_by_path(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_u1_00_chatgpt_uploader_content_pasteback_fallback.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--sample-report",
            "--output-dir",
            str(tmp_path / "runner"),
            "--json",
        ],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS_FULL_CONTENT_PASTEBACK_READY"
    assert Path(payload["payload_path"]).exists()
