from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from patchops.chatgpt_uploader.chrome_self_report_tab_enter_picker_upload_no_send import (
    CONFIRM_CHROME_TAB_ENTER_PICKER_SELF_REPORT_UPLOAD_NO_SEND,
    DEFAULT_CONFIG_PATH,
    DEFAULT_JSON_OUTPUT_PATH,
    DEFAULT_TXT_OUTPUT_PATH,
    PASS_CHROME_SELF_REPORT_TAB_ENTER_PICKER_ATTACHED_NO_SEND,
    load_json_object,
    render_text,
    run_tab_enter_picker_upload_no_send,
    sha256_file,
    write_evidence,
)

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_08_tab_enter_picker_path"
DEFAULT_SELF_REPORT_PATH = Path("data/runtime/copilot_handoff/pseudo_self_report_tab_enter_picker_upload_no_send_self_report.txt")


def write_self_report(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"patch_name: {PATCH_NAME}",
        "purpose: pseudo patch generated self-report for Chrome tab-enter-picker attach no-send smoke",
        f"created_at: {datetime.now(timezone.utc).isoformat()}",
        "selected_action: upload_self_report_tab_enter_picker_no_send",
        "browser_lane: chrome",
        "keyboard_shortcuts_used: TAB,ENTER_FOR_PICKER_TRIGGER_ONLY,SECOND_ENTER_FOR_PICKER_TRIGGER_ONLY_IF_NEEDED",
        "expected_result_label: PASS_CHROME_SELF_REPORT_TAB_ENTER_PICKER_ATTACHED_NO_SEND",
        "operator_report_uploaded: false",
        "chatgpt_submit_performed: false",
        "status_message_posted: false",
        "send_button_pressed: false",
        "enter_key_pressed_in_chat_composer: false",
        "enter_key_pressed_in_picker: false",
        "raw_conversation_text_available: false",
        "selenium_used: false",
        "webdriver_used: false",
        "browser_dom_automation_used: false",
        "cloudflare_bypass_attempted: false",
        "captcha_bypass_attempted: false",
        "conversation_text_logged: false",
        "random_page_click_performed: false",
        "note: This file is selected through native file picker using tab_enter command trigger, exact path write, and Open button click. The smoke stops before Send.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return sha256_file(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PatchOps apply smoke: tab-enter-picker attach self-report in Chrome without Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--self-report-path", default=str(DEFAULT_SELF_REPORT_PATH))
    parser.add_argument("--provider", choices=("pywinauto", "fake-ready"), default="pywinauto")
    parser.add_argument("--confirm-live-browser-text", default=CONFIRM_CHROME_TAB_ENTER_PICKER_SELF_REPORT_UPLOAD_NO_SEND)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    self_report_path = Path(args.self_report_path)
    self_report_hash = write_self_report(self_report_path)
    config_payload = load_json_object(config_path) if config_path.exists() else None

    result = run_tab_enter_picker_upload_no_send(
        config_payload=config_payload,
        config_path=config_path,
        provider=args.provider,
        live_browser=True,
        confirmation_text=args.confirm_live_browser_text,
        self_report_path=str(self_report_path),
        expected_self_report_sha256=self_report_hash,
    )

    write_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))

    print(f"SELF_REPORT_PATH: {self_report_path}")
    print(f"SELF_REPORT_SHA256: {self_report_hash}")
    print(f"EVIDENCE_JSON: {args.json_output_path}")
    print(f"EVIDENCE_TXT: {args.txt_output_path}")
    print(render_text(result), end="")

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))

    return 0 if result.result_label == PASS_CHROME_SELF_REPORT_TAB_ENTER_PICKER_ATTACHED_NO_SEND else 2


if __name__ == "__main__":
    raise SystemExit(main())