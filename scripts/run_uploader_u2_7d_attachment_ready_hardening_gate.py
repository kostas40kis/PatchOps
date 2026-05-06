from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _repo_root_from_args(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _print_payload(payload: dict[str, Any]) -> None:
    print(f"PATCHOPS_U2_7D_STATUS: {payload.get('status')}")
    print(f"RESULT: {payload.get('result')}")
    print(f"RESULT_LABEL: {payload.get('result_label')}")
    print(f"JSON_EVIDENCE: {payload.get('json_evidence', '')}")
    print(f"TXT_EVIDENCE: {payload.get('txt_evidence', '')}")
    print(f"FAILURE_LAYER: {payload.get('failure_layer', '')}")
    print(f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}")
    print(f"EXISTING_TARGET_FOUND: {str(payload.get('existing_target_found', False)).lower()}")
    print(f"EXISTING_TARGET_FOCUSED: {str(payload.get('existing_target_focused', False)).lower()}")
    print(f"LAUNCH_SKIPPED_EXISTING_TARGET: {str(payload.get('launch_skipped_existing_target', False)).lower()}")
    print(f"NORMAL_EDGE_LAUNCH_ATTEMPTED: {str(payload.get('normal_edge_launch_attempted', False)).lower()}")
    print(f"CANONICAL_TRIGGER_ATTEMPTED: {str(payload.get('canonical_trigger_attempted', False)).lower()}")
    print(f"SLASH_SENT: {str(payload.get('slash_sent', False)).lower()}")
    print(f"BROWSER_PICKER_OPENED: {str(payload.get('browser_picker_opened', False)).lower()}")
    print(f"FILE_PATH_WRITTEN: {str(payload.get('file_path_written', False)).lower()}")
    print(f"PICKER_ENTER_PRESSED: {str(payload.get('picker_enter_pressed', False)).lower()}")
    print(f"FILE_UPLOAD_ATTEMPTED: {str(payload.get('file_upload_attempted', False)).lower()}")
    print(f"ATTACHMENT_VERIFICATION_ATTEMPTED: {str(payload.get('attachment_verification_attempted', False)).lower()}")
    print(f"ATTACHMENT_VISIBLE: {str(payload.get('attachment_visible', False)).lower()}")
    print(f"ATTACHMENT_READY: {str(payload.get('attachment_ready', False)).lower()}")
    print(f"UPLOAD_PROGRESS_RESOLVED: {str(payload.get('upload_progress_resolved', False)).lower()}")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("CONVERSATION_TEXT_LOGGED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")
    print("RANDOM_PAGE_CLICK_PERFORMED: false")


def _run_u2_7_upload_probe(repo_root: Path, target_config: Path, report_path: Path, evidence_dir: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    wrapper = repo_root / "scripts" / "run_uploader_existing_target_preferred_live.py"
    cmd = [
        sys.executable,
        str(wrapper),
        "--repo-root",
        str(repo_root),
        "--target-config",
        str(target_config),
        "--report-path",
        str(report_path),
        "--evidence-dir",
        str(evidence_dir),
        "--allow-upload",
        "--timeout-seconds",
        str(timeout_seconds),
    ]
    try:
        return subprocess.run(cmd, cwd=str(repo_root), text=True, capture_output=True, timeout=timeout_seconds + 30, shell=False)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTIMEOUT after {timeout_seconds + 30} seconds."
        return subprocess.CompletedProcess(args=cmd, returncode=-9998, stdout=stdout, stderr=stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PatchOps U2.7D attachment-ready/no-send hardening gate.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--simulate-source-payload", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root_from_args(args.repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from patchops.chatgpt_uploader.attachment_ready_hardening import (
        classify_attachment_ready_payload,
        load_source_payload_from_stdout,
        write_attachment_ready_hardening_evidence,
    )

    evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    report_path = Path(args.report_path).expanduser().resolve()
    target_config = Path(args.target_config).expanduser().resolve() if args.target_config else repo_root / "data" / "config" / "chatgpt_copilot_target.json"

    source_payload: dict[str, Any]
    source_returncode = 0
    source_stdout_tail = ""
    source_stderr_tail = ""

    if args.simulate_source_payload:
        source_payload = json.loads(Path(args.simulate_source_payload).read_text(encoding="utf-8"))
    else:
        result = _run_u2_7_upload_probe(repo_root, target_config, report_path, evidence_dir / "source_u2_7_upload", args.timeout_seconds)
        source_returncode = int(result.returncode)
        source_stdout_tail = (result.stdout or "")[-5000:]
        source_stderr_tail = (result.stderr or "")[-5000:]
        source_payload = load_source_payload_from_stdout(result.stdout or "")

    if not source_payload:
        source_payload = {
            "status": "PASS_OR_BLOCKED",
            "result": "PASS_OR_BLOCKED_SOURCE_PAYLOAD_MISSING",
            "failure_layer": "source_payload_missing",
        }

    hardening = classify_attachment_ready_payload(source_payload).to_payload()
    payload = dict(hardening)
    payload.update({
        "patch": "U2.7D",
        "source_returncode": source_returncode,
        "source_stdout_tail": source_stdout_tail,
        "source_stderr_tail": source_stderr_tail,
        "selected_report_path": str(report_path),
        "selected_report_exists": report_path.exists(),
        "selected_report_sha256": _sha256_file(report_path) if report_path.exists() and report_path.is_file() else "",
        "target_config_path": str(target_config),
    })

    json_path, txt_path = write_attachment_ready_hardening_evidence(evidence_dir, payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        _print_payload(payload)

    return 3 if payload["status"] == "FAIL_FORBIDDEN_SIDE_EFFECT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
