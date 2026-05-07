from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from patchops.chatgpt_uploader.chrome_self_report_open_chrome_slash_path_enter_no_send import (
    CONFIRM_CHROME_OPEN_SLASH_PATH_ENTER_NO_SEND,
    DEFAULT_CONFIG_PATH,
    DEFAULT_DESKTOP_DIR,
    DEFAULT_JSON_OUTPUT_PATH,
    DEFAULT_TXT_OUTPUT_PATH,
    PASS_CHROME_SELF_REPORT_OPEN_SLASH_PATH_ENTER_ATTACHED_NO_SEND,
    load_json_object,
    render_text,
    run_open_chrome_slash_path_enter_no_send,
    sha256_file,
    write_evidence,
)

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_12_open_chrome_slash_path_enter"
DEFAULT_SELF_REPORT_FILENAME = "pseudo_self_report_upload_no_send_repair_12_open_chrome_slash_path_enter_self_report.txt"


def write_self_report(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"patch_name: {PATCH_NAME}",
        "purpose: open Chrome target URL, slash+Enter, paste full Desktop path into native picker, press picker Enter, no Send",
        f"created_at: {datetime.now(timezone.utc).isoformat()}",
        "selected_action: upload_self_report_open_chrome_slash_full_path_enter_no_send",
        "browser_lane: chrome",
        "manual_sequence: open_chrome_target_url__slash__enter__paste_full_path__enter",
        "expected_result_label: PASS_CHROME_SELF_REPORT_OPEN_SLASH_PATH_ENTER_ATTACHED_NO_SEND",
        "operator_report_uploaded: false",
        "chatgpt_submit_performed: false",
        "send_button_pressed: false",
        "mouse_clicks_used: false",
        "raw_conversation_text_available: false",
        "selenium_used: false",
        "webdriver_used: false",
        "browser_dom_automation_used: false",
        "cloudflare_bypass_attempted: false",
        "captcha_bypass_attempted: false",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return sha256_file(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PatchOps apply smoke: open Chrome target URL, slash+Enter, paste full Desktop path, picker Enter, no Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--desktop-dir", default=str(DEFAULT_DESKTOP_DIR))
    parser.add_argument("--self-report-filename", default=DEFAULT_SELF_REPORT_FILENAME)
    parser.add_argument("--provider", choices=("pywinauto", "fake-ready"), default="pywinauto")
    parser.add_argument("--confirm-live-browser-text", default=CONFIRM_CHROME_OPEN_SLASH_PATH_ENTER_NO_SEND)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    desktop_dir = Path(args.desktop_dir)
    self_report_path = desktop_dir / args.self_report_filename
    self_report_hash = write_self_report(self_report_path)
    config_payload = load_json_object(config_path) if config_path.exists() else None

    result = run_open_chrome_slash_path_enter_no_send(
        config_payload=config_payload,
        config_path=config_path,
        provider=args.provider,
        live_browser=True,
        confirmation_text=args.confirm_live_browser_text,
        self_report_path=str(self_report_path),
        expected_self_report_sha256=self_report_hash,
        desktop_dir=str(desktop_dir),
    )

    write_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))

    print(f"DESKTOP_DIR: {desktop_dir}")
    print(f"SELF_REPORT_FILENAME: {self_report_path.name}")
    print(f"SELF_REPORT_PATH: {self_report_path}")
    print(f"SELF_REPORT_SHA256: {self_report_hash}")
    print(f"EVIDENCE_JSON: {args.json_output_path}")
    print(f"EVIDENCE_TXT: {args.txt_output_path}")
    print(render_text(result), end="")

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))

    return 0 if result.result_label == PASS_CHROME_SELF_REPORT_OPEN_SLASH_PATH_ENTER_ATTACHED_NO_SEND else 2


if __name__ == "__main__":
    raise SystemExit(main())