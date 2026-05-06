from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.config import resolve_config_path
from patchops.chatgpt_uploader.edge_session_recovery import (
    run_edge_recovery_then_type_path_enter_no_send,
    write_edge_recovery_upload_evidence,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recover normal Edge if needed, then type path + Enter in picker, no ChatGPT send.")
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT))
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--evidence-dir", default=None)
    parser.add_argument("--allow-launch-edge", action="store_true")
    parser.add_argument("--allow-open-picker", action="store_true")
    parser.add_argument("--launch-wait-seconds", type=float, default=8.0)
    parser.add_argument("--timeout-seconds", type=int, default=10)
    parser.add_argument("--safe-click-x-ratio", type=float, default=0.50)
    parser.add_argument("--safe-click-y-ratio", type=float, default=0.34)
    return parser


def _print_safety(result) -> None:
    print(f"NORMAL_EDGE_LAUNCH_ATTEMPTED: {str(result.safety_flags['normal_edge_launch_attempted']).lower()}")
    print(f"CONFIGURED_TARGET_OPEN_ATTEMPTED: {str(result.safety_flags['configured_target_open_attempted']).lower()}")
    print(f"TARGET_CONFIG_OVERWRITTEN: {str(result.safety_flags['target_config_overwritten']).lower()}")
    print(f"HARDCODED_TARGET_URL_USED: {str(result.safety_flags['hardcoded_target_url_used']).lower()}")
    print(f"CANONICAL_TRIGGER_ATTEMPTED: {str(result.safety_flags['canonical_picker_trigger_attempted']).lower()}")
    print(f"SLASH_SENT: {str(result.safety_flags['slash_sent']).lower()}")
    print(f"TAB_SENT: {str(result.safety_flags['tab_sent']).lower()}")
    print(f"SECOND_ENTER_ATTEMPTED: {str(result.safety_flags['second_enter_attempted']).lower()}")
    print(f"PLUS_CONTROL_SEARCH_ATTEMPTED: {str(result.safety_flags['plus_control_search_attempted']).lower()}")
    print(f"MENU_CONTROL_SEARCH_ATTEMPTED: {str(result.safety_flags['menu_control_search_attempted']).lower()}")
    print(f"CTRL_U_ATTEMPTED: {str(result.safety_flags['ctrl_u_attempted']).lower()}")
    print(f"FILE_PATH_WRITTEN: {str(result.safety_flags['file_path_written']).lower()}")
    print(f"PICKER_ENTER_PRESSED: {str(result.safety_flags['picker_enter_pressed']).lower()}")
    print(f"FILE_UPLOAD_ATTEMPTED: {str(result.safety_flags['file_upload_attempted']).lower()}")
    print("OPEN_BUTTON_CLICKED: false")
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
    evidence_dir = Path(args.evidence_dir).expanduser().resolve() if args.evidence_dir else repo_root / "data" / "runtime" / "chatgpt_uploader" / "u2_06a_edge_recovery_upload"
    result = run_edge_recovery_then_type_path_enter_no_send(
        target_config_path=target_config,
        report_path=Path(args.report_path).expanduser().resolve(),
        evidence_dir=evidence_dir,
        allow_launch_edge=bool(args.allow_launch_edge),
        allow_open_picker=bool(args.allow_open_picker),
        launch_wait_seconds=float(args.launch_wait_seconds),
        timeout_seconds=max(1, int(args.timeout_seconds)),
        safe_click_x_ratio=float(args.safe_click_x_ratio),
        safe_click_y_ratio=float(args.safe_click_y_ratio),
    )
    json_path, txt_path = write_edge_recovery_upload_evidence(result, evidence_dir)
    launch = result.launch_result or {}
    upload = result.upload_result or {}
    print(f"PATCHOPS_UPLOADER_EDGE_RECOVERY_UPLOAD_STATUS: {result.status}")
    print(f"REPORT_PATH: {result.report_path or ''}")
    print(f"LAUNCH_STATUS: {launch.get('status', '')}")
    print(f"UPLOAD_STATUS: {upload.get('status', 'NOT_RUN')}")
    print(f"JSON_EVIDENCE: {json_path}")
    print(f"TXT_EVIDENCE: {txt_path}")
    _print_safety(result)
    return 0 if result.status in {"PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND", "PASS_DRY_RUN_NO_PICKER_OPEN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
