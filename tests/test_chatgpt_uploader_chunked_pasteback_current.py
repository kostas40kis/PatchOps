from __future__ import annotations

from pathlib import Path

from patchops.chatgpt_uploader.chunked_pasteback import (
    CHUNK_END_PREFIX,
    CHUNK_HEADER_PREFIX,
    build_chunked_pasteback,
    extract_report_summary,
    has_secret_like_content,
    split_text_into_chunks,
)


def test_extract_report_summary_reads_common_patchops_fields() -> None:
    text = """PATCHOPS RUN SUMMARY
Patch Name         : demo_patch
Report Path        : C:\\Users\\kostas\\Desktop\\demo.txt
ExitCode           : 0
Result             : PASS
"""
    summary = extract_report_summary(text)
    assert summary["PatchName"] == "demo_patch"
    assert summary["ReportPath"].endswith("demo.txt")
    assert summary["ExitCode"] == "0"
    assert summary["Result"] == "PASS"


def test_split_text_into_chunks_respects_limit() -> None:
    chunks = split_text_into_chunks("a" * 2500, max_chunk_chars=1000)
    assert len(chunks) == 3
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_chunked_pasteback_writes_numbered_chunks(tmp_path: Path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("Result : PASS\nExitCode : 0\n" + ("line content\n" * 500), encoding="utf-8")
    result = build_chunked_pasteback(report_path=report, output_dir=tmp_path / "out", max_chunk_chars=800, max_total_chars=20000)
    assert result.ok is True
    assert result.status == "PASS_CHUNKED_CONTENT_READY"
    assert result.mode == "chunked_report"
    assert result.chunk_count > 1
    assert result.safety_flags.chunked_report_content_included is True
    assert result.safety_flags.chatgpt_submit_performed is False
    assert result.safety_flags.file_upload_attempted is False
    assert result.safety_flags.clipboard_written is False
    assert Path(result.index_path).exists()
    assert Path(result.txt_index_path).exists()
    first = Path(result.chunks[0].path).read_text(encoding="utf-8")
    assert first.startswith(f"{CHUNK_HEADER_PREFIX} 1/{result.chunk_count}")
    assert f"{CHUNK_END_PREFIX} 1/{result.chunk_count}" in first


def test_secret_like_content_falls_back_to_summary_only(tmp_path: Path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("Result : FAIL\napi_key = '" + "A" * 32 + "'\n", encoding="utf-8")
    result = build_chunked_pasteback(report_path=report, output_dir=tmp_path / "out", max_chunk_chars=500)
    assert result.ok is True
    assert result.status == "PASS_SUMMARY_ONLY_SECRET_RISK"
    assert result.mode == "summary_only"
    assert result.chunk_count == 1
    assert result.safety_flags.compact_summary_only is True
    assert result.safety_flags.chunked_report_content_included is False
    payload = Path(result.chunks[0].path).read_text(encoding="utf-8")
    assert "api_key" not in payload


def test_too_large_report_falls_back_to_summary_only(tmp_path: Path) -> None:
    report = tmp_path / "huge.txt"
    report.write_text("Result : PASS\n" + ("x" * 5000), encoding="utf-8")
    result = build_chunked_pasteback(report_path=report, output_dir=tmp_path / "out", max_chunk_chars=500, max_total_chars=1000)
    assert result.ok is True
    assert result.status == "PASS_SUMMARY_ONLY_TOO_LARGE"
    assert result.mode == "summary_only"
    assert result.safety_flags.compact_summary_only is True


def test_missing_report_blocks(tmp_path: Path) -> None:
    result = build_chunked_pasteback(report_path=tmp_path / "missing.txt", output_dir=tmp_path / "out")
    assert result.ok is False
    assert result.status == "BLOCKED_REPORT_NOT_FOUND"
    assert result.safety_flags.compact_summary_only is True


def test_empty_report_blocks(tmp_path: Path) -> None:
    report = tmp_path / "empty.txt"
    report.write_text("", encoding="utf-8")
    result = build_chunked_pasteback(report_path=report, output_dir=tmp_path / "out")
    assert result.ok is False
    assert result.status == "BLOCKED_EMPTY_REPORT"


def test_secret_detector_matches_private_key() -> None:
    assert has_secret_like_content("-----BEGIN PRIVATE KEY-----\nabc") is True
