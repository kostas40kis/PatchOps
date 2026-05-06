from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.chatgpt_uploader.report_parser import ParsedReport, parse_report_file


DEFAULT_SAFETY_FLAGS: Mapping[str, str] = {
    "webdriver_used": "false",
    "selenium_used": "false",
    "browser_dom_automation_used": "false",
    "cloudflare_bypass_attempted": "false",
    "captcha_bypass_attempted": "false",
    "file_upload_attempted": "false",
    "chatgpt_submit_performed": "false",
    "conversation_text_logged": "false",
    "random_page_click_performed": "false",
}


@dataclass(frozen=True)
class PastebackBuildOptions:
    """Bounded rendering options for compact LLM pasteback text."""

    max_field_chars: int = 260
    max_total_chars: int = 3800
    include_safety: bool = True


@dataclass(frozen=True)
class PastebackMessage:
    """A compact, transport-safe PATCHOPS_LLM_PASTEBACK message."""

    status: str
    text: str
    payload: Mapping[str, Any]

    @property
    def ok(self) -> bool:
        return self.status == "PASS"

    def to_payload(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "text": self.text,
            "payload": dict(self.payload),
        }


def _single_line(value: object, *, limit: int) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3] + "..."


def _status_from_report(parsed: ParsedReport) -> str:
    result = parsed.result.upper()
    if parsed.ok:
        return "PASS"
    if result == "FAIL":
        return "FAIL"
    if result == "BLOCKED":
        return "BLOCKED"
    return "BLOCKED"


def _next_action(parsed: ParsedReport) -> str:
    if parsed.ok:
        return "Continue to the next planned PatchOps Co-Pilot patch."
    layer = (parsed.failure_layer or "unknown").lower()
    if layer == "manifest_validation":
        return "Repair the manifest or bundle authoring shape, then rerun the same patch."
    if layer in {"bundle_shape_preflight", "package_authoring"}:
        return "Repair bundle metadata/shape, then rerun the same patch."
    if layer == "target_validation":
        return "Repair the failing target content or test, then rerun the same patch."
    if layer == "launcher_execution":
        return "Repair launcher/runtime execution evidence, then rerun the same patch."
    if layer == "inner_report_detection":
        return "Repair canonical report creation/detection before continuing."
    return "Inspect the canonical report and repair the first failing layer before continuing."


def _canonical_report(parsed: ParsedReport) -> str:
    return parsed.report_path or parsed.source_path or "unknown"


def _merged_safety_flags(parsed: ParsedReport) -> dict[str, str]:
    merged = dict(DEFAULT_SAFETY_FLAGS)
    for key, value in dict(parsed.safety_flags).items():
        merged[key] = str(value).lower()
    merged["canonical_report_found"] = "true" if _canonical_report(parsed) != "unknown" else "false"
    return merged


def build_pasteback(parsed: ParsedReport, *, options: PastebackBuildOptions | None = None) -> PastebackMessage:
    """Build a compact PATCHOPS_LLM_PASTEBACK message from parsed report evidence.

    This is intentionally only a text builder. It does not touch the clipboard, browser,
    filesystem upload surfaces, or ChatGPT send controls.
    """

    options = options or PastebackBuildOptions()
    field_limit = max(40, options.max_field_chars)
    status = _status_from_report(parsed)
    primary = parsed.to_payload()["primary_error"]
    safety = _merged_safety_flags(parsed)

    payload: dict[str, Any] = {
        "status": status,
        "result": parsed.result,
        "exit_code": parsed.exit_code,
        "failure_category": parsed.failure_category,
        "failure_layer": parsed.failure_layer,
        "patch_name": parsed.patch_name,
        "first_failing_command": parsed.first_failing_command,
        "canonical_report": _canonical_report(parsed),
        "primary_error": primary,
        "next_action": _next_action(parsed),
        "safety": safety,
    }

    lines = [
        "PATCHOPS_LLM_PASTEBACK",
        f"Status: {status}",
        f"Result: {_single_line(parsed.result, limit=field_limit)}",
        f"ExitCode: {parsed.exit_code if parsed.exit_code is not None else 'unknown'}",
        f"FailureLayer: {_single_line(parsed.failure_layer or 'unknown', limit=field_limit)}",
        f"FailureCategory: {_single_line(parsed.failure_category or 'n/a', limit=field_limit)}",
        f"PatchName: {_single_line(parsed.patch_name or 'n/a', limit=field_limit)}",
        f"FirstFailingCommand: {_single_line(parsed.first_failing_command or 'n/a', limit=field_limit)}",
        "PrimaryError:",
        f"  Type: {_single_line(primary.get('type') or 'n/a', limit=field_limit)}",
        f"  Message: {_single_line(primary.get('message') or 'n/a', limit=field_limit)}",
        f"  File: {_single_line(primary.get('file') or 'n/a', limit=field_limit)}",
        f"  Line: {_single_line(primary.get('line') if primary.get('line') is not None else 'n/a', limit=field_limit)}",
        f"CanonicalReport: {_single_line(_canonical_report(parsed), limit=field_limit)}",
        f"NextAction: {_single_line(payload['next_action'], limit=field_limit)}",
    ]

    if options.include_safety:
        lines.append("Safety:")
        for key in sorted(safety):
            lines.append(f"  {key}: {safety[key]}")

    lines.append("END_PATCHOPS_LLM_PASTEBACK")
    text = "\n".join(lines) + "\n"

    if len(text) > options.max_total_chars:
        overflow_note = "NextAction: Pasteback was shortened; inspect the canonical report for full detail."
        keep = max(200, options.max_total_chars - len("\n" + overflow_note + "\nEND_PATCHOPS_LLM_PASTEBACK\n"))
        text = text[:keep].rstrip() + "\n" + overflow_note + "\nEND_PATCHOPS_LLM_PASTEBACK\n"
        payload["truncated"] = True
    else:
        payload["truncated"] = False

    return PastebackMessage(status=status, text=text, payload=payload)


def write_pasteback_outputs(message: PastebackMessage, output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    text_path = out / "u0_05_patchops_llm_pasteback.txt"
    json_path = out / "u0_05_patchops_llm_pasteback.json"
    text_path.write_text(message.text, encoding="utf-8")
    json_path.write_text(json.dumps(message.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    return {"text_path": str(text_path), "json_path": str(json_path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build compact PATCHOPS_LLM_PASTEBACK text from a PatchOps report.")
    parser.add_argument("--report", required=True, help="PatchOps report txt file to parse and summarize.")
    parser.add_argument("--output-dir", default="data/runtime/u0_05_chatgpt_uploader_pasteback_builder")
    parser.add_argument("--json", action="store_true", help="Print JSON payload instead of pasteback text.")
    args = parser.parse_args(argv)

    parsed = parse_report_file(args.report)
    message = build_pasteback(parsed)
    outputs = write_pasteback_outputs(message, args.output_dir)

    if args.json:
        print(json.dumps({**message.to_payload(), "outputs": outputs}, indent=2, sort_keys=True))
    else:
        print(message.text, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
