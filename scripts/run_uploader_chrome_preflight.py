from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_focus_guard import (  # noqa: E402
    BLOCKED_CHROME_NOT_RUNNING,
    BLOCKED_CHROME_TARGET_AMBIGUOUS,
    BLOCKED_CHROME_TARGET_NOT_READY,
    BLOCKED_LOGIN_OR_CHALLENGE,
    PASS_CHROME_TARGET_READY,
    LIVE_CONFIRM_TEXT,
    build_candidate,
    run_chrome_preflight,
    write_chrome_preflight_evidence,
)
from patchops.chatgpt_uploader.chrome_target import probe_chrome_target_config  # noqa: E402


def _candidate_from_arg(value: str, target_url: str | None):
    parts = value.split("|")
    while len(parts) < 5:
        parts.append("")
    process_name = parts[0] or "chrome.exe"
    title = parts[1] or "ChatGPT - Google Chrome"
    visible = (parts[2] or "true").strip().lower() in {"1", "true", "yes", "visible"}
    minimized = (parts[3] or "false").strip().lower() in {"1", "true", "yes", "minimized"}
    hwnd_raw = parts[4] or "0"
    try:
        hwnd = int(hwnd_raw)
    except ValueError:
        hwnd = 0
    return build_candidate(
        hwnd=hwnd,
        process_id=None,
        process_name=process_name,
        title=title,
        visible=visible,
        minimized=minimized,
        target_url=target_url,
    )


def _target_url_from_config(path: str | None) -> str | None:
    if not path:
        return None
    evidence = probe_chrome_target_config(path)
    if evidence.ok and evidence.redacted_target_display:
        try:
            import json as _json

            payload = _json.loads(Path(path).read_text(encoding="utf-8"))
            return str(payload.get("target_url") or "")
        except Exception:
            return None
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chrome-only visible target preflight. No upload, no paste, no send.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--target-url", default=None)
    parser.add_argument("--candidate", action="append", default=[], help="Local test candidate: process|title|visible|minimized|hwnd")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else PROJECT_ROOT
    target_config_path = None
    if args.target_config:
        raw = Path(args.target_config).expanduser()
        target_config_path = raw if raw.is_absolute() else repo_root / raw

    target_url = args.target_url or (_target_url_from_config(str(target_config_path)) if target_config_path else None)
    local_candidates = [_candidate_from_arg(item, target_url) for item in args.candidate]

    evidence = run_chrome_preflight(
        target_url=target_url,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        candidates=local_candidates,
    )

    if args.evidence_path:
        write_chrome_preflight_evidence(evidence, args.evidence_path)

    payload = evidence.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"LIVE_BROWSER_USED: {str(evidence.live_browser_used).lower()}")
        print(f"CANDIDATE_COUNT: {evidence.candidate_count}")
        print(f"SELECTABLE_COUNT: {evidence.selectable_count}")
        print(f"SELECTED_HWND: {evidence.selected_hwnd or ''}")
        print(f"TARGET_URL_HASH: {evidence.target_url_hash or ''}")
        print(f"REDACTED_TARGET_DISPLAY: {evidence.redacted_target_display or ''}")
        print("raw_conversation_text_logged:false")
        print("conversation_text_logged:false")
        print("file_upload_attempted:false")
        print("chatgpt_submit_performed:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("random_page_click_performed:false")
        if evidence.error:
            print(f"ERROR: {evidence.error}")

    if evidence.result in {
        PASS_CHROME_TARGET_READY,
        BLOCKED_CHROME_NOT_RUNNING,
        BLOCKED_CHROME_TARGET_AMBIGUOUS,
        BLOCKED_LOGIN_OR_CHALLENGE,
        BLOCKED_CHROME_TARGET_NOT_READY,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())