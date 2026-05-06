from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.config import resolve_config_path
from patchops.chatgpt_uploader.upload_trigger import run_open_picker_attempts, write_upload_trigger_evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Open and close the ChatGPT upload picker. Does not select a file or send.")
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT))
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--evidence-dir", default=None)
    parser.add_argument("--attempts", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=10)
    parser.add_argument("--allow-open-picker", action="store_true")
    # Legacy flags remain accepted but U2.4E does not actuate legacy paths.
    parser.add_argument("--allow-keyboard-shortcut", action="store_true")
    parser.add_argument("--allow-tab-enter-sequence", action="store_true")
    parser.add_argument("--allow-neutral-click", action="store_true")
    parser.add_argument("--allow-single-safe-click-tab-enter", action="store_true")
    parser.add_argument("--safe-click-x-ratio", type=float, default=0.50)
    parser.add_argument("--safe-click-y-ratio", type=float, default=0.34)
    return parser


def _print_safety(run) -> None:
    print(f"KEYBOARD_SHORTCUT_ATTEMPTED: {str(run.safety_flags.get('keyboard_shortcut_attempted', False)).lower()}")
    print(f"TAB_ENTER_ATTEMPTED: {str(run.safety_flags.get('tab_enter_attempted', False)).lower()}")
    print(f"NEUTRAL_CLICK_ATTEMPTED: {str(run.safety_flags.get('neutral_click_attempted', False)).lower()}")
    print(f"SAFE_CLICK_ATTEMPTED: {str(run.safety_flags.get('safe_click_attempted', False)).lower()}")
    print(f"PLUS_CONTROL_SEARCH_ATTEMPTED: {str(run.safety_flags.get('plus_control_search_attempted', False)).lower()}")
    print(f"MENU_CONTROL_SEARCH_ATTEMPTED: {str(run.safety_flags.get('menu_control_search_attempted', False)).lower()}")
    print(f"CTRL_U_ATTEMPTED: {str(run.safety_flags.get('ctrl_u_attempted', False)).lower()}")
    print("FILE_PATH_WRITTEN: false")
    print("FILE_SELECTED: false")
    print("OPEN_BUTTON_PRESSED: false")
    print("ATTACHMENT_CONFIRMED: false")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")
    print("RANDOM_PAGE_CLICK_PERFORMED: false")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    target_config = resolve_config_path(args.target_config, repo_root=repo_root)
    evidence_dir = Path(args.evidence_dir).expanduser().resolve() if args.evidence_dir else repo_root / "data" / "runtime" / "chatgpt_uploader" / "u2_04_upload_trigger"

    try:
        run = run_open_picker_attempts(
            target_config_path=target_config,
            attempts=max(1, int(args.attempts)),
            timeout_seconds=max(1, int(args.timeout_seconds)),
            allow_open_picker=bool(args.allow_open_picker),
            allow_keyboard_shortcut=bool(args.allow_keyboard_shortcut),
            allow_tab_enter_sequence=bool(args.allow_tab_enter_sequence),
            allow_neutral_click=bool(args.allow_neutral_click),
            allow_single_safe_click_tab_enter=bool(args.allow_single_safe_click_tab_enter),
            safe_click_x_ratio=float(args.safe_click_x_ratio),
            safe_click_y_ratio=float(args.safe_click_y_ratio),
        )
    except Exception as exc:
        from patchops.chatgpt_uploader.upload_trigger import UploadTriggerRun, default_trigger_safety_flags, utc_now_iso
        run = UploadTriggerRun(
            status="FAIL_OR_BLOCKED_EXCEPTION",
            attempts_requested=max(1, int(args.attempts)),
            attempts_completed=0,
            pass_count=0,
            attempts=[{"index": 1, "status": "FAIL_OR_BLOCKED_EXCEPTION", "reason": str(exc), "safety_flags": default_trigger_safety_flags(picker_open_attempted=False)}],
            safety_flags=default_trigger_safety_flags(picker_open_attempted=False),
            created_at=utc_now_iso(),
        )

    json_path, txt_path = write_upload_trigger_evidence(run, evidence_dir)

    print(f"PATCHOPS_UPLOADER_OPEN_PICKER_STATUS: {run.status}")
    print(f"ATTEMPTS_REQUESTED: {run.attempts_requested}")
    print(f"ATTEMPTS_COMPLETED: {run.attempts_completed}")
    print(f"PASS_COUNT: {run.pass_count}")
    print(f"JSON_EVIDENCE: {json_path}")
    print(f"TXT_EVIDENCE: {txt_path}")
    print(f"FILE_PICKER_OPEN_ATTEMPTED: {str(run.safety_flags['file_picker_open_attempted']).lower()}")
    _print_safety(run)
    return 0 if run.status in {"PASS", "PASS_DRY_RUN_NO_PICKER_OPEN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
