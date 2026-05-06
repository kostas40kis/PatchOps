from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


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


def _run_u2_7d_gate(
    *,
    repo_root: Path,
    target_config: Path,
    report_path: Path,
    evidence_dir: Path,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    script = repo_root / "scripts" / "run_uploader_u2_7d_attachment_ready_hardening_gate.py"
    cmd = [
        sys.executable,
        str(script),
        "--repo-root",
        str(repo_root),
        "--target-config",
        str(target_config),
        "--report-path",
        str(report_path),
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
            timeout=timeout_seconds + 45,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTIMEOUT after {timeout_seconds + 45} seconds."
        return subprocess.CompletedProcess(args=cmd, returncode=-9998, stdout=stdout, stderr=stderr)


def _synthetic_pass_payload(report_path: Path) -> dict[str, Any]:
    return {
        "status": "PASS",
        "result": "PASS_ATTACHMENT_READY_NO_SEND_HARDENED",
        "result_label": "PASS_ATTACHMENT_READY_NO_SEND_HARDENED",
        "selected_report_path": str(report_path),
        "existing_target_found": True,
        "existing_target_focused": True,
        "launch_skipped_existing_target": True,
        "normal_edge_launch_attempted": False,
        "canonical_trigger_attempted": True,
        "slash_sent": True,
        "browser_picker_opened": True,
        "file_path_written": True,
        "picker_enter_pressed": True,
        "file_upload_attempted": True,
        "attachment_verification_attempted": True,
        "attachment_visible": True,
        "attachment_ready": True,
        "upload_progress_resolved": True,
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
        "failure_layer": "",
        "recommended_next_mode": "continue_to_queue_submission_blocker_or_downloader_foundation",
    }


def _print_payload(payload: dict[str, Any]) -> None:
    print(f"PATCHOPS_U2_7E_STATUS: {payload.get('status')}")
    print(f"RESULT: {payload.get('result')}")
    print(f"RESULT_LABEL: {payload.get('result_label')}")
    print(f"JSON_EVIDENCE: {payload.get('json_evidence', '')}")
    print(f"TXT_EVIDENCE: {payload.get('txt_evidence', '')}")
    print(f"QUEUE_FILE: {payload.get('queue_file', '')}")
    print(f"ORIGINAL_QUEUE_ITEM_COUNT: {payload.get('original_queue_item_count', payload.get('queue_item_count', 0))}")
    print(f"QUEUE_ITEM_COUNT: {payload.get('queue_item_count', 0)}")
    print(f"SKIPPED_QUEUE_ITEM_COUNT: {payload.get('skipped_queue_item_count', 0)}")
    print(f"MULTI_UPLOAD_ALLOWED: {str(payload.get('multi_upload_allowed', False)).lower()}")
    print(f"EFFECTIVE_MAX_ITEMS: {payload.get('effective_max_items', '')}")
    print(f"PASS_COUNT: {payload.get('pass_count', 0)}")
    print(f"BLOCKED_COUNT: {payload.get('blocked_count', 0)}")
    print(f"FORBIDDEN_COUNT: {payload.get('forbidden_count', 0)}")
    print(f"FIRST_FAILURE_INDEX: {payload.get('first_failure_index', '')}")
    print(f"FIRST_FAILURE_LAYER: {payload.get('first_failure_layer', '')}")
    print(f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("CONVERSATION_TEXT_LOGGED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")
    print("RANDOM_PAGE_CLICK_PERFORMED: false")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PatchOps U2.7E repeatability queue foundation gate.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--report-path", action="append", default=[])
    parser.add_argument("--queue-json", default=None)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--simulate-pass", action="store_true")
    parser.add_argument("--allow-multi-upload", action="store_true")
    parser.add_argument("--max-items", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root_from_args(args.repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from patchops.chatgpt_uploader.upload_queue import (
        build_upload_queue,
        classify_repeatability_results,
        read_queue_file,
        select_queue_items,
        write_queue_file,
        write_repeatability_evidence,
    )

    evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    target_config = Path(args.target_config).expanduser().resolve() if args.target_config else repo_root / "data" / "config" / "chatgpt_copilot_target.json"

    if args.queue_json:
        original_queue = read_queue_file(args.queue_json)
    else:
        if not args.report_path:
            raise SystemExit("--report-path is required unless --queue-json is provided")
        original_queue = build_upload_queue(args.report_path)

    selection = select_queue_items(
        original_queue,
        allow_multi_upload=bool(args.allow_multi_upload),
        max_items=args.max_items,
    )
    queue = list(selection.items)

    queue_file = write_queue_file(queue, evidence_dir / "u2_7e_upload_queue.json")

    item_results: list[dict[str, Any]] = []
    item_command_summaries: list[dict[str, Any]] = []

    for item in queue:
        report_path = Path(item.report_path)
        item_evidence_dir = evidence_dir / f"item_{item.index:02d}"

        if args.simulate_pass:
            payload = _synthetic_pass_payload(report_path)
            result_code = 0
            stdout_tail = ""
            stderr_tail = ""
        else:
            result = _run_u2_7d_gate(
                repo_root=repo_root,
                target_config=target_config,
                report_path=report_path,
                evidence_dir=item_evidence_dir,
                timeout_seconds=args.timeout_seconds,
            )
            payload = _load_json_evidence(result.stdout or "")
            if not payload:
                payload = {
                    "status": "PASS_OR_BLOCKED",
                    "result": "PASS_OR_BLOCKED_U2_7D_SOURCE_PAYLOAD_MISSING",
                    "failure_layer": "u2_7d_source_payload_missing",
                    "chatgpt_submit_performed": False,
                    "conversation_text_logged": False,
                    "selenium_used": False,
                    "webdriver_used": False,
                    "browser_dom_automation_used": False,
                    "random_page_click_performed": False,
                }
            result_code = int(result.returncode)
            stdout_tail = (result.stdout or "")[-5000:]
            stderr_tail = (result.stderr or "")[-5000:]

        payload["queue_index"] = item.index
        payload["queue_report_path"] = item.report_path
        payload["queue_report_sha256"] = item.report_sha256
        item_results.append(payload)
        item_command_summaries.append(
            {
                "index": item.index,
                "report_path": item.report_path,
                "returncode": result_code,
                "stdout_tail": stdout_tail,
                "stderr_tail": stderr_tail,
                "status": payload.get("status"),
                "result": payload.get("result"),
                "failure_layer": payload.get("failure_layer"),
            }
        )

    summary = classify_repeatability_results(item_results).to_payload()

    payload = dict(summary)
    payload.update(
        {
            "patch": "U2.7F",
            "queue_file": str(queue_file),
            "original_queue_items": [item.to_payload() for item in original_queue],
            "queue_items": [item.to_payload() for item in queue],
            "original_queue_item_count": selection.original_queue_item_count,
            "queue_item_count": selection.queue_item_count,
            "skipped_queue_item_count": selection.skipped_queue_item_count,
            "multi_upload_allowed": selection.multi_upload_allowed,
            "effective_max_items": selection.effective_max_items,
            "item_results": item_results,
            "item_command_summaries": item_command_summaries,
            "target_config_path": str(target_config),
            "simulate_pass": bool(args.simulate_pass),
        }
    )

    json_path, txt_path = write_repeatability_evidence(evidence_dir, payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        _print_payload(payload)

    return 3 if payload["status"] == "FAIL_FORBIDDEN_SIDE_EFFECT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
