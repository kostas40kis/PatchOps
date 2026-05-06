from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping


CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
SECRET_HINT_RE = re.compile(
    r"(?i)("
    r"api[_-]?key|secret|password|passwd|authorization:\s*bearer|"
    r"access[_-]?token|refresh[_-]?token|private[_-]?key|client[_-]?secret"
    r")"
)


@dataclass(frozen=True)
class ContentPastebackSafetyFlags:
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
    compact_summary_only: bool = False


@dataclass(frozen=True)
class ContentPastebackPolicy:
    max_full_report_chars: int = 14000
    max_compact_summary_chars: int = 3500
    allow_full_content: bool = True


@dataclass(frozen=True)
class ContentPastebackResult:
    ok: bool
    status: str
    mode: str
    reason: str
    report_path: str | None
    report_sha256: str | None
    report_size_chars: int
    pasteback_sha256: str
    pasteback_size_chars: int
    payload_path: str
    json_path: str
    safety_flags: ContentPastebackSafetyFlags
    extracted_summary: Mapping[str, str]

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["safety_flags"] = asdict(self.safety_flags)
        payload["extracted_summary"] = dict(self.extracted_summary)
        return payload


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_report_text(report_path: str | Path) -> tuple[str, Path]:
    path = Path(report_path)
    if not path.exists():
        raise FileNotFoundError(f"report path does not exist: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"report path is not a file: {path}")
    return path.read_text(encoding="utf-8", errors="replace"), path


def has_binary_control_chars(text: str) -> bool:
    return CONTROL_CHAR_RE.search(text) is not None


def has_secret_hint(text: str) -> bool:
    return SECRET_HINT_RE.search(text) is not None


def extract_patchops_summary(report_text: str) -> dict[str, str]:
    fields = {
        "Result": "",
        "ExitCode": "",
        "FailureCategory": "",
        "PatchName": "",
        "ReportPath": "",
        "FirstError": "",
    }

    for raw_line in report_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        lower = stripped.lower()

        def after_colon(value: str) -> str:
            return value.split(":", 1)[1].strip() if ":" in value else ""

        if not fields["Result"] and lower.startswith("result"):
            value = after_colon(stripped)
            if value:
                fields["Result"] = value
        elif not fields["ExitCode"] and (lower.startswith("exitcode") or lower.startswith("exit code")):
            value = after_colon(stripped)
            if value:
                fields["ExitCode"] = value
        elif not fields["FailureCategory"] and (
            lower.startswith("failurecategory") or lower.startswith("failure category")
        ):
            value = after_colon(stripped)
            fields["FailureCategory"] = value
        elif not fields["PatchName"] and lower.startswith("patch name"):
            value = after_colon(stripped)
            if value:
                fields["PatchName"] = value
        elif not fields["ReportPath"] and lower.startswith("report path"):
            value = after_colon(stripped)
            if value:
                fields["ReportPath"] = value

        if not fields["FirstError"] and (
            "traceback " in lower
            or "error:" in lower
            or "exception" in lower
            or "manifesterror" in lower
            or "valueerror" in lower
            or "assertionerror" in lower
        ):
            fields["FirstError"] = stripped[:240]

    return {k: v for k, v in fields.items() if v}


def build_compact_summary_text(*, report_path: str | None, report_sha256: str | None, report_text: str, reason: str) -> str:
    summary = extract_patchops_summary(report_text)
    lines = [
        "PATCHOPS_REPORT_CONTENT_PASTEBACK",
        "Mode: compact_summary",
        f"Reason: {reason}",
    ]
    if report_path:
        lines.append(f"ReportPath: {report_path}")
    if report_sha256:
        lines.append(f"ReportSha256: {report_sha256}")
    lines.append(f"ReportChars: {len(report_text)}")
    if summary:
        lines.append("Summary:")
        for key in ("Result", "ExitCode", "FailureCategory", "PatchName", "ReportPath", "FirstError"):
            if key in summary:
                lines.append(f"- {key}: {summary[key]}")
    else:
        lines.append("Summary: no standard PatchOps summary fields detected")
    lines.extend(
        [
            "Safety:",
            "- full_report_content_included:false",
            "- file_upload_attempted:false",
            "- chatgpt_submit_performed:false",
            "- selenium_used:false",
            "END_PATCHOPS_REPORT_CONTENT_PASTEBACK",
        ]
    )
    return "\n".join(lines) + "\n"


def build_full_content_text(*, report_path: str | None, report_sha256: str, report_text: str) -> str:
    lines = [
        "PATCHOPS_REPORT_CONTENT_PASTEBACK",
        "Mode: full_report",
    ]
    if report_path:
        lines.append(f"ReportPath: {report_path}")
    lines.extend(
        [
            f"ReportSha256: {report_sha256}",
            f"ReportChars: {len(report_text)}",
            "Safety:",
            "- file_upload_attempted:false",
            "- chatgpt_submit_performed:false",
            "- selenium_used:false",
            "REPORT_CONTENT_BEGIN",
            report_text.rstrip("\n"),
            "REPORT_CONTENT_END",
            "END_PATCHOPS_REPORT_CONTENT_PASTEBACK",
        ]
    )
    return "\n".join(lines) + "\n"


def build_content_pasteback(
    *,
    report_text: str,
    report_path: str | None = None,
    output_dir: str | Path = "data/runtime/u1_00_chatgpt_uploader_content_pasteback_fallback",
    policy: ContentPastebackPolicy | None = None,
) -> ContentPastebackResult:
    policy = policy or ContentPastebackPolicy()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    report_sha = sha256_text(report_text)
    report_chars = len(report_text)
    unsafe_binary = has_binary_control_chars(report_text)
    unsafe_secret = has_secret_hint(report_text)

    extracted = extract_patchops_summary(report_text)
    mode: str
    status: str
    reason: str
    safety: ContentPastebackSafetyFlags

    if not report_text.strip():
        mode = "blocked"
        status = "BLOCKED_EMPTY_REPORT"
        reason = "Report text is empty."
        pasteback = build_compact_summary_text(
            report_path=report_path,
            report_sha256=report_sha,
            report_text="",
            reason=reason,
        )
        ok = False
        safety = ContentPastebackSafetyFlags(compact_summary_only=True)
    elif unsafe_binary:
        mode = "compact_summary"
        status = "PASS_COMPACT_CONTENT_PASTEBACK_READY"
        reason = "Report contains non-text control characters; using compact summary only."
        pasteback = build_compact_summary_text(
            report_path=report_path,
            report_sha256=report_sha,
            report_text=report_text,
            reason=reason,
        )
        ok = True
        safety = ContentPastebackSafetyFlags(compact_summary_only=True)
    elif unsafe_secret:
        mode = "compact_summary"
        status = "PASS_COMPACT_CONTENT_PASTEBACK_READY"
        reason = "Report contains secret-like markers; using compact summary only."
        pasteback = build_compact_summary_text(
            report_path=report_path,
            report_sha256=report_sha,
            report_text=report_text,
            reason=reason,
        )
        ok = True
        safety = ContentPastebackSafetyFlags(compact_summary_only=True)
    elif not policy.allow_full_content:
        mode = "compact_summary"
        status = "PASS_COMPACT_CONTENT_PASTEBACK_READY"
        reason = "Full content disabled by policy."
        pasteback = build_compact_summary_text(
            report_path=report_path,
            report_sha256=report_sha,
            report_text=report_text,
            reason=reason,
        )
        ok = True
        safety = ContentPastebackSafetyFlags(compact_summary_only=True)
    elif report_chars > policy.max_full_report_chars:
        mode = "compact_summary"
        status = "PASS_COMPACT_CONTENT_PASTEBACK_READY"
        reason = f"Report is larger than max_full_report_chars={policy.max_full_report_chars}; using compact summary only."
        pasteback = build_compact_summary_text(
            report_path=report_path,
            report_sha256=report_sha,
            report_text=report_text,
            reason=reason,
        )
        ok = True
        safety = ContentPastebackSafetyFlags(compact_summary_only=True)
    else:
        mode = "full_report"
        status = "PASS_FULL_CONTENT_PASTEBACK_READY"
        reason = "Report is small and safe enough for full content pasteback."
        pasteback = build_full_content_text(
            report_path=report_path,
            report_sha256=report_sha,
            report_text=report_text,
        )
        ok = True
        safety = ContentPastebackSafetyFlags(full_report_content_included=True)

    if mode == "compact_summary" and len(pasteback) > policy.max_compact_summary_chars:
        # Keep U1.0 deliberately non-chunked. U1.1 owns chunking.
        lines = pasteback.splitlines()
        truncated = "\n".join(lines[:24])
        pasteback = (
            truncated
            + "\nSummaryTruncated: true\n"
            + "ChunkingDeferredTo: U1.1\n"
            + "END_PATCHOPS_REPORT_CONTENT_PASTEBACK\n"
        )

    payload_path = output / "content_pasteback_payload.txt"
    json_path = output / "content_pasteback_result.json"
    payload_path.write_text(pasteback, encoding="utf-8")

    result = ContentPastebackResult(
        ok=ok,
        status=status,
        mode=mode,
        reason=reason,
        report_path=report_path,
        report_sha256=report_sha,
        report_size_chars=report_chars,
        pasteback_sha256=sha256_text(pasteback),
        pasteback_size_chars=len(pasteback),
        payload_path=str(payload_path),
        json_path=str(json_path),
        safety_flags=safety,
        extracted_summary=extracted,
    )
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    return result


def create_sample_report() -> str:
    return """PATCHOPS RUN SUMMARY
--------------------
Mode               : apply
Patch Name         : sample_patch
Report Path        : C:\\Users\\kostas\\Desktop\\sample_patch_report.txt
ExitCode           : 0
Result             : PASS

STDERR
------
<empty>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="U1.0 content pasteback fallback builder")
    parser.add_argument("--report-path", default=None)
    parser.add_argument("--report-text", default=None)
    parser.add_argument("--sample-report", action="store_true")
    parser.add_argument("--output-dir", default="data/runtime/u1_00_chatgpt_uploader_content_pasteback_fallback")
    parser.add_argument("--max-full-report-chars", type=int, default=14000)
    parser.add_argument("--max-compact-summary-chars", type=int, default=3500)
    parser.add_argument("--compact-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report_path: str | None = None
    if args.report_path:
        report_text, path = read_report_text(args.report_path)
        report_path = str(path)
    elif args.report_text is not None:
        report_text = args.report_text
    elif args.sample_report:
        report_text = create_sample_report()
        sample_path = Path(args.output_dir) / "sample_patchops_report.txt"
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        sample_path.write_text(report_text, encoding="utf-8")
        report_path = str(sample_path)
    else:
        report_text = create_sample_report()

    result = build_content_pasteback(
        report_text=report_text,
        report_path=report_path,
        output_dir=args.output_dir,
        policy=ContentPastebackPolicy(
            max_full_report_chars=args.max_full_report_chars,
            max_compact_summary_chars=args.max_compact_summary_chars,
            allow_full_content=not args.compact_only,
        ),
    )

    if args.json:
        print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    else:
        print(result.status)
        print(result.reason)
        print(f"payload_path: {result.payload_path}")
        print(f"json_path: {result.json_path}")

    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
