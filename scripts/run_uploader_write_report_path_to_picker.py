from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.config import ConfigValidationError, load_config, resolve_config_path
from patchops.chatgpt_uploader.edge_target import focus_chatgpt_edge_target
from patchops.chatgpt_uploader.picker_path_writer import write_path_writer_evidence, write_report_path_to_detected_picker
from patchops.chatgpt_uploader.preflight_policy import decide_launch_permission


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write exact report path into an already-open Windows file picker. Does not press Open or send.")
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT))
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--evidence-dir", default=None)
    parser.add_argument("--wait-seconds", type=float, default=0.0)
    parser.add_argument("--focus-edge-first", action="store_true")
    parser.add_argument("--focus-timeout-seconds", type=int, default=10)
    parser.add_argument("--allow-launch-target", action="store_true")
    parser.add_argument("--allow-open-configured-url", action="store_true")
    return parser


def _print_safety(result_status: str) -> None:
    print(f"PICKER_PATH_WRITER_STATUS: {result_status}")
    print("FILE_PICKER_OPEN_ATTEMPTED: false")
    print("OPEN_BUTTON_PRESSED: false")
    print("FILE_SELECTED: false")
    print("FILE_UPLOAD_ATTEMPTED: false")
    print("ATTACHMENT_CONFIRMED: false")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")
    print("CLIPBOARD_WRITTEN: false")
    print("PASTE_ATTEMPTED: false")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    evidence_dir = Path(args.evidence_dir).expanduser().resolve() if args.evidence_dir else repo_root / "data" / "runtime" / "chatgpt_uploader" / "u2_03_picker_path_writer"
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

    result = write_report_path_to_detected_picker(report_path=args.report_path, wait_seconds=max(0.0, float(args.wait_seconds)))
    json_path, txt_path = write_path_writer_evidence(result, evidence_dir)

    print(f"PATCHOPS_UPLOADER_PICKER_PATH_WRITE_STATUS: {result.status}")
    print(f"EDGE_FOCUS_STATUS: {edge_status}")
    print(f"LAUNCH_ALLOWED: {str(launch_allowed).lower()}")
    print(f"LAUNCH_POLICY_REASON: {launch_reason}")
    print(f"REPORT_PATH: {result.report_path or ''}")
    print(f"REPORT_NAME: {result.report_name or ''}")
    print(f"REPORT_SHA256: {result.report_sha256 or ''}")
    print(f"PICKER_DETECTED: {str(result.picker_detected).lower()}")
    print(f"PICKER_COUNT: {result.picker_count}")
    print(f"AMBIGUOUS_PICKERS: {str(result.ambiguous).lower()}")
    print(f"PATH_WRITTEN: {str(result.wrote_path).lower()}")
    print(f"JSON_EVIDENCE: {json_path}")
    print(f"TXT_EVIDENCE: {txt_path}")
    _print_safety(result.status)

    if result.status in {"BLOCKED_AMBIGUOUS_PICKERS", "FAIL_REPORT_NOT_RESOLVED", "FAIL_PICKER_HANDLE_MISSING", "FAIL_FILENAME_CONTROL_NOT_FOUND", "FAIL_PATH_WRITE_NOT_VERIFIED"}:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
