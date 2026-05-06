from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.config import ConfigValidationError, load_config, resolve_config_path
from patchops.chatgpt_uploader.edge_target import focus_chatgpt_edge_target
from patchops.chatgpt_uploader.preflight_policy import decide_launch_permission
from patchops.chatgpt_uploader.windows_file_picker import detect_file_picker, write_detection_evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect Windows file picker/error modal state. No file selection and no send.")
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT))
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--evidence-dir", default=None)
    parser.add_argument("--wait-seconds", type=float, default=0.0)
    parser.add_argument("--poll-interval-seconds", type=float, default=0.5)
    parser.add_argument("--focus-edge-first", action="store_true")
    parser.add_argument("--focus-timeout-seconds", type=int, default=10)
    parser.add_argument("--allow-launch-target", action="store_true")
    parser.add_argument("--allow-open-configured-url", action="store_true")
    return parser


def _print_safety() -> None:
    print("FILE_PICKER_OPEN_ATTEMPTED: false")
    print("FILE_PATH_WRITTEN: false")
    print("FILE_SELECTED: false")
    print("OPEN_BUTTON_PRESSED: false")
    print("FILE_UPLOAD_ATTEMPTED: false")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    evidence_dir = Path(args.evidence_dir).expanduser().resolve() if args.evidence_dir else repo_root / "data" / "runtime" / "chatgpt_uploader" / "u2_02_picker_detection"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    edge_status = "SKIPPED"
    launch_allowed = False
    launch_reason = "not_requested"
    config_path = resolve_config_path(args.target_config, repo_root=repo_root)
    if args.focus_edge_first:
        try:
            cfg = load_config(config_path)
            decision = decide_launch_permission(
                target_mode=cfg.mode,
                allow_launch_target_requested=bool(args.allow_launch_target),
                allow_open_configured_url_requested=bool(args.allow_open_configured_url),
            )
            launch_allowed = decision.allow_launch
            launch_reason = decision.reason
            edge_result = focus_chatgpt_edge_target(
                target_url=cfg.target_url,
                allow_launch=decision.allow_launch,
                timeout_seconds=max(1, int(args.focus_timeout_seconds)),
            )
            edge_status = str(edge_result.get("status") or "UNKNOWN")
        except (ConfigValidationError, OSError, ValueError, RuntimeError) as exc:
            edge_status = f"FAIL_OR_BLOCKED:{exc}"

    detection = detect_file_picker(wait_seconds=max(0.0, float(args.wait_seconds)), poll_interval_seconds=max(0.05, float(args.poll_interval_seconds)))
    json_path, txt_path = write_detection_evidence(detection, evidence_dir)

    print(f"PATCHOPS_UPLOADER_PICKER_DETECT_STATUS: {detection.status}")
    print(f"EDGE_FOCUS_STATUS: {edge_status}")
    print(f"LAUNCH_ALLOWED: {str(launch_allowed).lower()}")
    print(f"LAUNCH_POLICY_REASON: {launch_reason}")
    print(f"PICKER_DETECTED: {str(detection.picker_detected).lower()}")
    print(f"PICKER_COUNT: {detection.picker_count}")
    print(f"AMBIGUOUS_PICKERS: {str(detection.ambiguous).lower()}")
    print(f"ERROR_MODAL_DETECTED: {str(detection.error_modal_detected).lower()}")
    print(f"ERROR_MODAL_COUNT: {detection.error_modal_count}")
    print(f"JSON_EVIDENCE: {json_path}")
    print(f"TXT_EVIDENCE: {txt_path}")
    _print_safety()
    return 2 if detection.ambiguous else 0


if __name__ == "__main__":
    raise SystemExit(main())
