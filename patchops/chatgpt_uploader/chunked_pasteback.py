from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_MAX_CHUNK_CHARS = 3500
DEFAULT_MAX_TOTAL_CHARS = 60000
CHUNK_HEADER_PREFIX = "PATCHOPS_REPORT_CHUNK"
CHUNK_END_PREFIX = "END_PATCHOPS_REPORT_CHUNK"

_SECRET_PATTERNS = (
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)secret\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)token\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


@dataclass(frozen=True)
class ChunkedPastebackSafetyFlags:
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    file_upload_attempted: bool = False
    chatgpt_submit_performed: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False
    clipboard_written: bool = False
    paste_attempted: bool = False
    full_report_content_included: bool = False
    chunked_report_content_included: bool = False
    compact_summary_only: bool = False


@dataclass(frozen=True)
class ChunkInfo:
    index: int
    total: int
    size_chars: int
    sha256: str
    path: str


@dataclass(frozen=True)
class ChunkedPastebackResult:
    ok: bool
    status: str
    mode: str
    reason: str
    report_path: str | None
    report_size_chars: int
    report_sha256: str | None
    chunk_count: int
    max_chunk_chars: int
    max_total_chars: int
    payload_dir: str
    index_path: str
    txt_index_path: str
    chunks: tuple[ChunkInfo, ...]
    safety_flags: ChunkedPastebackSafetyFlags
    extracted_summary: dict[str, str]

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["safety_flags"] = asdict(self.safety_flags)
        return payload


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def has_secret_like_content(text: str) -> bool:
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)


def extract_report_summary(text: str) -> dict[str, str]:
    patterns = {
        "Result": re.compile(r"(?im)^\s*Result\s*:\s*(.+?)\s*$"),
        "ExitCode": re.compile(r"(?im)^\s*ExitCode\s*:\s*(.+?)\s*$"),
        "Exit Code": re.compile(r"(?im)^\s*Exit Code\s*:\s*(.+?)\s*$"),
        "FailureCategory": re.compile(r"(?im)^\s*FailureCategory\s*:\s*(.+?)\s*$"),
        "Failure Category": re.compile(r"(?im)^\s*Failure Category\s*:\s*(.+?)\s*$"),
        "PatchName": re.compile(r"(?im)^\s*(?:Patch Name|PatchName|Patch)\s*:\s*(.+?)\s*$"),
        "ReportPath": re.compile(r"(?im)^\s*(?:Report Path|ReportPath|Outer Report Path|OuterReportPath)\s*:\s*(.+?)\s*$"),
    }
    summary: dict[str, str] = {}
    for key, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            out_key = "ExitCode" if key == "Exit Code" else "FailureCategory" if key == "Failure Category" else key
            value = match.group(1).strip()
            if value:
                summary[out_key] = value
    return summary


def build_summary_payload(summary: dict[str, str], *, reason: str, report_sha256: str | None, report_size_chars: int) -> str:
    lines = [
        "PATCHOPS_LLM_PASTEBACK_SUMMARY_ONLY",
        f"Reason: {reason}",
        f"ReportSha256: {report_sha256 or '<none>'}",
        f"ReportSizeChars: {report_size_chars}",
    ]
    for key in sorted(summary):
        lines.append(f"{key}: {summary[key]}")
    lines.append("END_PATCHOPS_LLM_PASTEBACK_SUMMARY_ONLY")
    return "\n".join(lines) + "\n"


def split_text_into_chunks(text: str, max_chunk_chars: int) -> tuple[str, ...]:
    if max_chunk_chars <= 200:
        raise ValueError("max_chunk_chars must be greater than 200")
    chunks: list[str] = []
    cursor = 0
    length = len(text)
    while cursor < length:
        limit = min(cursor + max_chunk_chars, length)
        if limit < length:
            newline = text.rfind("\n", cursor, limit)
            if newline > cursor + max_chunk_chars // 2:
                limit = newline + 1
        chunks.append(text[cursor:limit])
        cursor = limit
    return tuple(chunks or ("",))


def wrap_chunk(chunk_text: str, *, index: int, total: int, report_sha256: str) -> str:
    chunk_hash = sha256_text(chunk_text)
    return (
        f"{CHUNK_HEADER_PREFIX} {index}/{total}\n"
        f"ReportSha256: {report_sha256}\n"
        f"ChunkSha256: {chunk_hash}\n"
        "```text\n"
        f"{chunk_text}"
        "\n```\n"
        f"{CHUNK_END_PREFIX} {index}/{total}\n"
    )


def build_chunked_pasteback(*, report_path: str | Path, output_dir: str | Path,
                            max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
                            max_total_chars: int = DEFAULT_MAX_TOTAL_CHARS) -> ChunkedPastebackResult:
    path = Path(report_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    index_path = out / "chunked_pasteback_index.json"
    txt_path = out / "chunked_pasteback_index.txt"

    if not path.exists() or not path.is_file():
        return _write_index(ChunkedPastebackResult(
            ok=False, status="BLOCKED_REPORT_NOT_FOUND", mode="blocked",
            reason=f"Report path does not exist or is not a file: {path}", report_path=str(path),
            report_size_chars=0, report_sha256=None, chunk_count=0,
            max_chunk_chars=max_chunk_chars, max_total_chars=max_total_chars,
            payload_dir=str(out), index_path=str(index_path), txt_index_path=str(txt_path), chunks=(),
            safety_flags=ChunkedPastebackSafetyFlags(compact_summary_only=True), extracted_summary={}
        ), index_path, txt_path)

    text = path.read_text(encoding="utf-8", errors="replace")
    report_size = len(text)
    report_hash = sha256_text(text)
    summary = extract_report_summary(text)

    if report_size == 0:
        return _write_index(ChunkedPastebackResult(
            ok=False, status="BLOCKED_EMPTY_REPORT", mode="blocked", reason="Report is empty.",
            report_path=str(path), report_size_chars=0, report_sha256=report_hash, chunk_count=0,
            max_chunk_chars=max_chunk_chars, max_total_chars=max_total_chars,
            payload_dir=str(out), index_path=str(index_path), txt_index_path=str(txt_path), chunks=(),
            safety_flags=ChunkedPastebackSafetyFlags(compact_summary_only=True), extracted_summary=summary
        ), index_path, txt_path)

    if has_secret_like_content(text):
        return _summary_only(out, index_path, txt_path, path, report_size, report_hash, summary,
                             max_chunk_chars, max_total_chars, "PASS_SUMMARY_ONLY_SECRET_RISK",
                             "Secret-like content detected; wrote compact summary only.")

    if report_size > max_total_chars:
        return _summary_only(out, index_path, txt_path, path, report_size, report_hash, summary,
                             max_chunk_chars, max_total_chars, "PASS_SUMMARY_ONLY_TOO_LARGE",
                             "Report exceeds max_total_chars; wrote compact summary only.")

    raw_chunks = split_text_into_chunks(text, max_chunk_chars=max_chunk_chars)
    infos: list[ChunkInfo] = []
    total = len(raw_chunks)
    for idx, raw in enumerate(raw_chunks, 1):
        wrapped = wrap_chunk(raw, index=idx, total=total, report_sha256=report_hash)
        chunk_path = out / f"chunk_{idx:03d}_of_{total:03d}.txt"
        chunk_path.write_text(wrapped, encoding="utf-8")
        infos.append(ChunkInfo(idx, total, len(wrapped), sha256_text(wrapped), str(chunk_path)))

    return _write_index(ChunkedPastebackResult(
        ok=True, status="PASS_CHUNKED_CONTENT_READY", mode="chunked_report",
        reason="Report was split into chunked pasteback payloads.", report_path=str(path),
        report_size_chars=report_size, report_sha256=report_hash, chunk_count=total,
        max_chunk_chars=max_chunk_chars, max_total_chars=max_total_chars,
        payload_dir=str(out), index_path=str(index_path), txt_index_path=str(txt_path), chunks=tuple(infos),
        safety_flags=ChunkedPastebackSafetyFlags(chunked_report_content_included=True), extracted_summary=summary
    ), index_path, txt_path)


def _summary_only(out: Path, index_path: Path, txt_path: Path, path: Path, report_size: int, report_hash: str,
                  summary: dict[str, str], max_chunk_chars: int, max_total_chars: int,
                  status: str, reason: str) -> ChunkedPastebackResult:
    payload = build_summary_payload(summary, reason=reason, report_sha256=report_hash, report_size_chars=report_size)
    summary_path = out / "chunked_pasteback_summary_only.txt"
    summary_path.write_text(payload, encoding="utf-8")
    result = ChunkedPastebackResult(
        ok=True, status=status, mode="summary_only", reason=reason,
        report_path=str(path), report_size_chars=report_size, report_sha256=report_hash,
        chunk_count=1, max_chunk_chars=max_chunk_chars, max_total_chars=max_total_chars,
        payload_dir=str(out), index_path=str(index_path), txt_index_path=str(txt_path),
        chunks=(ChunkInfo(1, 1, len(payload), sha256_text(payload), str(summary_path)),),
        safety_flags=ChunkedPastebackSafetyFlags(compact_summary_only=True), extracted_summary=summary
    )
    return _write_index(result, index_path, txt_path)


def _write_index(result: ChunkedPastebackResult, index_path: Path, txt_path: Path) -> ChunkedPastebackResult:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "PATCHOPS_CHUNKED_CONTENT_PASTEBACK",
        f"Status         : {result.status}",
        f"Mode           : {result.mode}",
        f"Ok             : {str(result.ok).lower()}",
        f"Reason         : {result.reason}",
        f"ReportPath     : {result.report_path}",
        f"ReportSha256   : {result.report_sha256}",
        f"ReportSizeChars: {result.report_size_chars}",
        f"ChunkCount     : {result.chunk_count}",
        f"MaxChunkChars  : {result.max_chunk_chars}",
        f"MaxTotalChars  : {result.max_total_chars}",
        f"PayloadDir     : {result.payload_dir}",
        f"IndexPath      : {result.index_path}",
    ]
    if result.extracted_summary:
        lines.append("SUMMARY")
        for key in sorted(result.extracted_summary):
            lines.append(f"{key}: {result.extracted_summary[key]}")
    lines.append("CHUNKS")
    if not result.chunks:
        lines.append("<none>")
    for chunk in result.chunks:
        lines.append(f"[{chunk.index}/{chunk.total}] size={chunk.size_chars} sha256={chunk.sha256} path={chunk.path}")
    lines.append("SAFETY_FLAGS")
    for key, value in asdict(result.safety_flags).items():
        lines.append(f"{key}:{str(value).lower()}")
    lines.append("END_PATCHOPS_CHUNKED_CONTENT_PASTEBACK")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def write_sample_report(path: Path, *, repeat: int = 140) -> None:
    lines = [
        "PATCHOPS RUN-PACKAGE OUTER REPORT",
        "---------------------------------",
        "Result              : PASS",
        "ExitCode            : 0",
        "PatchName           : sample_chunked_patch",
        r"ReportPath          : C:\Users\kostas\Desktop\sample_chunked_patch.txt",
        "",
        "STDOUT",
        "------",
    ]
    for i in range(repeat):
        lines.append(f"sample output line {i:03d}: this line exists to force chunking without containing secrets.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="U1.1A chunked content pasteback builder")
    parser.add_argument("--report-path", default=None)
    parser.add_argument("--sample-report", action="store_true")
    parser.add_argument("--output-dir", default="data/runtime/u1_01_chatgpt_uploader_chunked_content_pasteback")
    parser.add_argument("--max-chunk-chars", type=int, default=DEFAULT_MAX_CHUNK_CHARS)
    parser.add_argument("--max-total-chars", type=int, default=DEFAULT_MAX_TOTAL_CHARS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.sample_report:
        report_path = output_dir / "sample_large_patchops_report.txt"
        write_sample_report(report_path)
    elif args.report_path:
        report_path = Path(args.report_path)
    else:
        raise SystemExit("Provide --report-path or --sample-report")
    result = build_chunked_pasteback(report_path=report_path, output_dir=output_dir,
                                     max_chunk_chars=args.max_chunk_chars,
                                     max_total_chars=args.max_total_chars)
    if args.json:
        print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    else:
        print(result.status)
        print(result.reason)
        print(result.index_path)
    return 0 if result.ok else 2

if __name__ == "__main__":
    raise SystemExit(main())
