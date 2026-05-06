from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.config import resolve_config_path
from patchops.chatgpt_uploader.slash_enter_trigger import run_slash_enter_trigger, write_slash_enter_evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Open/close picker with safe-click slash Enter. No file select and no send.")
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT))
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--evidence-dir", default=None)
    parser.add_argument("--allow-open-picker", action="store_true")
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=10)
    parser.add_argument("--safe-click-x-ratio", type=float, default=0.50)
    parser.add_argument("--safe-click-y-ratio", type=float, default=0.34)
    return parser


def _print_safety(run) -> None:
    print(f"FILE_PICKER_OPEN_ATTEMPTED: {str(run.safety_flags['file_picker_open_attempted']).lower()}")
    print(f"SAFE_CLICK_ATTEMPTED: {str(run.safety_flags['safe_click_attempted']).lower()}")
    print(f"SLASH_SENT: {str(run.safety_flags['slash_sent']).lower()}")
    print(f"TAB_SENT: {str(run.safety_flags['tab_sent']).lower()}")
    print(f"SECOND_ENTER_ATTEMPTED: {str(run.safety_flags['second_enter_attempted']).lower()}")
    print(f"PLUS_CONTROL_SEARCH_ATTEMPTED: {str(run.safety_flags['plus_control_search_attempted']).lower()}")
    print(f"MENU_CONTROL_SEARCH_ATTEMPTED: {str(run.safety_flags['menu_control_search_attempted']).lower()}")
    print(f"CTRL_U_ATTEMPTED: {str(run.safety_flags['ctrl_u_attempted']).lower()}")
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
    evidence_dir = Path(args.evidence_dir).expanduser().resolve() if args.evidence_dir else repo_root / "data" / "runtime" / "chatgpt_uploader" / "u2_04g_slash_enter_trigger"
    run = run_slash_enter_trigger(
        target_config_path=target_config,
        allow_open_picker=bool(args.allow_open_picker),
        attempts=max(1, int(args.attempts)),
        timeout_seconds=max(1, int(args.timeout_seconds)),
        x_ratio=float(args.safe_click_x_ratio),
        y_ratio=float(args.safe_click_y_ratio),
    )
    json_path, txt_path = write_slash_enter_evidence(run, evidence_dir)
    print(f"PATCHOPS_UPLOADER_SLASH_ENTER_STATUS: {run.status}")
    print(f"ATTEMPTS_REQUESTED: {run.attempts_requested}")
    print(f"ATTEMPTS_COMPLETED: {run.attempts_completed}")
    print(f"PASS_COUNT: {run.pass_count}")
    print(f"JSON_EVIDENCE: {json_path}")
    print(f"TXT_EVIDENCE: {txt_path}")
    _print_safety(run)
    return 0 if run.status in {"PASS", "PASS_DRY_RUN_NO_PICKER_OPEN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
