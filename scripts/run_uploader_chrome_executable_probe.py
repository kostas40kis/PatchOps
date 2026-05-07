from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_paths import (  # noqa: E402
    BLOCKED_CHROME_NOT_FOUND,
    BLOCKED_CHROME_PATH_INVALID,
    PASS_CHROME_EXECUTABLE_FOUND,
    discover_chrome_executable,
    write_discovery_evidence,
)


def _parse_candidate(value: str) -> tuple[str, Path, bool]:
    if "=" in value:
        source, raw_path = value.split("=", 1)
        source = source.strip() or "CLI_CANDIDATE"
        return source, Path(raw_path.strip()), False
    return "CLI_CANDIDATE", Path(value), False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe Chrome executable discovery for the Chrome-only uploader lane.")
    parser.add_argument("--candidate", action="append", default=[], help="Optional source=path candidate for local tests.")
    parser.add_argument("--evidence-path", default=None, help="Optional JSON evidence output path.")
    parser.add_argument("--include-executable-path", action="store_true", help="Include exact executable path in JSON output.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload instead of text lines.")
    args = parser.parse_args(argv)

    search_order = [_parse_candidate(item) for item in args.candidate] if args.candidate else None
    result = discover_chrome_executable(search_order=search_order)
    payload = result.to_payload(include_executable_path=args.include_executable_path)

    if args.evidence_path:
        write_discovery_evidence(result, args.evidence_path, include_executable_path=args.include_executable_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {result.result}")
        print(f"BROWSER: {result.browser}")
        print(f"OK: {str(result.ok).lower()}")
        print(f"EXECUTABLE_BASENAME: {result.executable_basename or ''}")
        print(f"EXECUTABLE_REDACTED_PATH: {result.executable_redacted_path or ''}")
        print(f"CANDIDATE_COUNT: {result.candidate_count}")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("cloudflare_bypass_attempted:false")
        print("captcha_bypass_attempted:false")
        print("conversation_text_logged:false")
        print("random_page_click_performed:false")
        print("chatgpt_submit_performed:false")
        print("file_upload_attempted:false")
        print("live_browser_used:false")
        print("browser_launched:false")

    if result.result in {PASS_CHROME_EXECUTABLE_FOUND, BLOCKED_CHROME_NOT_FOUND, BLOCKED_CHROME_PATH_INVALID}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())