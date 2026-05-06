from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

EXPECTED_OPERATOR_CONFIRMATION_TOKEN = "UPLOAD_ONE_ATTACHMENT_NO_SEND"


def _repo_root_from_args(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _load_json_evidence(stdout: str) -> dict[str, Any]:
    for line in (stdout or "").splitlines():
        if line.startswith("JSON_EVIDENCE:"):
            candidate = Path(line.split(":", 1)[1].strip())
            if candidate.exists():
                data = json.loads(candidate.read_text(encoding="utf-8", errors="replace"))
                if isinstance(data, dict):
                    return data
    return {}


def _run_queue_gate(
    *,
    repo_root: Path,
    report_path: Path,
    evidence_dir: Path,
    timeout_seconds: int,
    simulate_pass: bool,
) -> subprocess.CompletedProcess[str]:
    script = repo_root / "scripts" / "run_uploader_u2_7e_repeatability_queue_gate.py"

    cmd = [
        sys.executable,
        str(script),
        "--repo-root",
        str(repo_root),
        "--report-path",
        str(report_path),
        "--evidence-dir",
        str(evidence_dir),
        "--timeout-seconds",
        str(timeout_seconds),
    ]

    if simulate_pass:
        cmd.append("--simulate-pass")

    try:
        return subprocess.run(
            cmd,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=timeout_seconds + 90,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTIMEOUT after {timeout_seconds + 90} seconds."
        return subprocess.CompletedProcess(args=cmd, returncode=-9998, stdout=stdout, stderr=stderr)


def _run_submission_blocker(
    *,
    repo_root: Path,
    source_json: Path,
    evidence_dir: Path,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    script = repo_root / "scripts" / "run_uploader_u2_7g_submission_blocker_gate.py"

    cmd = [
        sys.executable,
        str(script),
        "--repo-root",
        str(repo_root),
        "--source-json",
        str(source_json),
        "--evidence-dir",
        str(evidence_dir),
        "--timeout-seconds",
        str(timeout_seconds),
    ]

    try:
        return subprocess.run(
            cmd,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=timeout_seconds + 30,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTIMEOUT after {timeout_seconds + 30} seconds."
        return subprocess.CompletedProcess(args=cmd, returncode=-9998, stdout=stdout, stderr=stderr)


def _print_payload(payload: dict[str, Any]) -> None:
    print(f"PATCHOPS_U2_7H_STATUS: {payload.get('status')}")
    print(f"RESULT: {payload.get('result')}")
    print(f"RESULT_LABEL: {payload.get('result_label')}")
    print(f"JSON_EVIDENCE: {payload.get('json_evidence', '')}")
    print(f"TXT_EVIDENCE: {payload.get('txt_evidence', '')}")
    print(f"LIVE_SINGLE_UPLOAD_ALLOWED: {str(payload.get('live_single_upload_allowed', False)).lower()}")
    print(f"REPORT_PATH_COUNT: {payload.get('report_path_count', 0)}")
    print(f"SELECTED_REPORT_PATH: {payload.get('selected_report_path', '')}")
    print(f"ALLOW_LIVE_SINGLE_UPLOAD: {str(payload.get('allow_live_single_upload', False)).lower()}")
    print(f"OPERATOR_CONFIRMATION_VALID: {str(payload.get('operator_confirmation_valid', False)).lower()}")
    print(f"EXPECTED_CONFIRMATION_TOKEN: {payload.get('expected_confirmation_token', EXPECTED_OPERATOR_CONFIRMATION_TOKEN)}")
    print(f"MULTI_UPLOAD_BLOCKED: {str(payload.get('multi_upload_blocked', False)).lower()}")
    print(f"SUBMISSION_BLOCKER_PASSED: {str(payload.get('submission_blocker_passed', False)).lower()}")
    print(f"QUEUE_ITEM_COUNT: {payload.get('queue_item_count', 0)}")
    print(f"SKIPPED_QUEUE_ITEM_COUNT: {payload.get('skipped_queue_item_count', 0)}")
    print(f"FAILURE_LAYER: {payload.get('failure_layer', '')}")
    print(f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("CONVERSATION_TEXT_LOGGED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PatchOps U2.7H live single-upload operator gate.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--report-path", action="append", default=[])
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--allow-live-single-upload", action="store_true")
    parser.add_argument("--operator-confirm", default="")
    parser.add_argument("--simulate-pass", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root_from_args(args.repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from patchops.chatgpt_uploader.live_operator_gate import (
        CONFIRMATION_TOKEN,
        validate_live_single_upload_request,
        write_live_operator_gate_evidence,
    )

    evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    report_paths = [Path(path).expanduser().resolve() for path in args.report_path]

    gate = validate_live_single_upload_request(
        report_paths,
        allow_live_single_upload=bool(args.allow_live_single_upload),
        operator_confirm=str(args.operator_confirm or ""),
        confirmation_token=EXPECTED_OPERATOR_CONFIRMATION_TOKEN,
    ).to_payload()

    payload: dict[str, Any] = dict(gate)
    payload.update(
        {
            "patch": "U2.7H",
            "status": gate["gate_status"],
            "result": gate["gate_result"],
            "result_label": gate["gate_result"],
            "failure_layer": gate["gate_failure_layer"],
            "submission_blocker_passed": False,
            "queue_item_count": 0,
            "skipped_queue_item_count": 0,
            "chatgpt_submit_performed": False,
            "conversation_text_logged": False,
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
        }
    )

    if not gate["live_single_upload_allowed"] and not args.simulate_pass:
        json_path, txt_path = write_live_operator_gate_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload) if not args.json else print(json.dumps(payload, indent=2, sort_keys=True, default=str))
        return 0

    if args.simulate_pass and not report_paths:
        payload.update(
            {
                "status": "PASS_OR_BLOCKED",
                "result": "BLOCKED_SIMULATED_GATE_REQUIRES_REPORT_PATH",
                "result_label": "BLOCKED_SIMULATED_GATE_REQUIRES_REPORT_PATH",
                "failure_layer": "simulated_report_path_missing",
                "recommended_next_mode": "provide_one_report_path",
            }
        )
        json_path, txt_path = write_live_operator_gate_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload) if not args.json else print(json.dumps(payload, indent=2, sort_keys=True, default=str))
        return 0

    selected_report = Path(gate["selected_report_path"]) if gate.get("selected_report_path") else report_paths[0]

    queue_result = _run_queue_gate(
        repo_root=repo_root,
        report_path=selected_report,
        evidence_dir=evidence_dir / "source_single_queue_gate",
        timeout_seconds=args.timeout_seconds,
        simulate_pass=bool(args.simulate_pass),
    )
    queue_payload = _load_json_evidence(queue_result.stdout or "")

    if not queue_payload:
        queue_payload = {
            "status": "PASS_OR_BLOCKED",
            "result": "PASS_OR_BLOCKED_U2_7H_SOURCE_QUEUE_PAYLOAD_MISSING",
            "failure_layer": "source_queue_payload_missing",
            "queue_item_count": 0,
            "skipped_queue_item_count": 0,
            "chatgpt_submit_performed": False,
            "conversation_text_logged": False,
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
        }

    queue_json_path = evidence_dir / "u2_7h_source_queue_payload.json"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    queue_json_path.write_text(json.dumps(queue_payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    guard_result = _run_submission_blocker(
        repo_root=repo_root,
        source_json=queue_json_path,
        evidence_dir=evidence_dir / "submission_blocker",
        timeout_seconds=args.timeout_seconds,
    )
    guard_payload = _load_json_evidence(guard_result.stdout or "")

    payload.update(
        {
            "source_queue_status": queue_payload.get("status", ""),
            "source_queue_result": queue_payload.get("result", ""),
            "source_queue_returncode": int(queue_result.returncode),
            "source_queue_stdout_tail": (queue_result.stdout or "")[-5000:],
            "source_queue_stderr_tail": (queue_result.stderr or "")[-5000:],
            "submission_guard_status": guard_payload.get("status", ""),
            "submission_guard_result": guard_payload.get("result", ""),
            "submission_guard_returncode": int(guard_result.returncode),
            "submission_guard_stdout_tail": (guard_result.stdout or "")[-5000:],
            "submission_guard_stderr_tail": (guard_result.stderr or "")[-5000:],
            "submission_blocker_passed": bool(guard_payload.get("submission_blocker_passed")),
            "queue_item_count": int(queue_payload.get("queue_item_count") or 0),
            "skipped_queue_item_count": int(queue_payload.get("skipped_queue_item_count") or 0),
            "multi_upload_allowed": bool(queue_payload.get("multi_upload_allowed", False)),
            "chatgpt_submit_performed": False,
            "conversation_text_logged": False,
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
        }
    )

    if guard_result.returncode == 3 or guard_payload.get("status") == "FAIL_FORBIDDEN_SUBMISSION_SIDE_EFFECT":
        payload.update(
            {
                "status": "FAIL_FORBIDDEN_SUBMISSION_SIDE_EFFECT",
                "result": "FAIL_U2_7H_SUBMISSION_BLOCKER_DETECTED_FORBIDDEN_SIDE_EFFECT",
                "result_label": "FAIL_U2_7H_SUBMISSION_BLOCKER_DETECTED_FORBIDDEN_SIDE_EFFECT",
                "failure_layer": guard_payload.get("first_violation_key") or "submission_blocker_violation",
                "recommended_next_mode": "stop_and_repair_submission_guard_before_any_live_upload",
            }
        )
    elif queue_payload.get("status") == "PASS" and bool(guard_payload.get("submission_blocker_passed")):
        payload.update(
            {
                "status": "PASS",
                "result": "PASS_U2_7H_LIVE_SINGLE_UPLOAD_OPERATOR_GATED_NO_SEND",
                "result_label": "PASS_U2_7H_LIVE_SINGLE_UPLOAD_OPERATOR_GATED_NO_SEND",
                "failure_layer": "",
                "recommended_next_mode": "continue_to_downloader_foundation",
            }
        )
    else:
        payload.update(
            {
                "status": "PASS_OR_BLOCKED",
                "result": "PASS_OR_BLOCKED_U2_7H_SINGLE_UPLOAD_FIRST_LAYER_CLASSIFIED",
                "result_label": "PASS_OR_BLOCKED_U2_7H_SINGLE_UPLOAD_FIRST_LAYER_CLASSIFIED",
                "failure_layer": queue_payload.get("first_failure_layer") or queue_payload.get("failure_layer") or "single_upload_blocked",
                "recommended_next_mode": queue_payload.get("recommended_next_mode") or "patch_first_single_upload_blocked_layer",
            }
        )

    json_path, txt_path = write_live_operator_gate_evidence(evidence_dir, payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        _print_payload(payload)

    return 3 if payload["status"] == "FAIL_FORBIDDEN_SUBMISSION_SIDE_EFFECT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
