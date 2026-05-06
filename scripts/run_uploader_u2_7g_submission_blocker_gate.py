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


def _run_queue_gate(
    *,
    repo_root: Path,
    report_paths: list[Path],
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
        "--evidence-dir",
        str(evidence_dir),
        "--timeout-seconds",
        str(timeout_seconds),
    ]

    for report_path in report_paths:
        cmd.extend(["--report-path", str(report_path)])

    if simulate_pass:
        cmd.append("--simulate-pass")

    try:
        return subprocess.run(
            cmd,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=timeout_seconds + 60,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTIMEOUT after {timeout_seconds + 60} seconds."
        return subprocess.CompletedProcess(args=cmd, returncode=-9998, stdout=stdout, stderr=stderr)


def _print_payload(payload: dict[str, Any]) -> None:
    print(f"PATCHOPS_U2_7G_STATUS: {payload.get('status')}")
    print(f"RESULT: {payload.get('result')}")
    print(f"RESULT_LABEL: {payload.get('result_label')}")
    print(f"JSON_EVIDENCE: {payload.get('json_evidence', '')}")
    print(f"TXT_EVIDENCE: {payload.get('txt_evidence', '')}")
    print(f"SUBMISSION_BLOCKER_PASSED: {str(payload.get('submission_blocker_passed', False)).lower()}")
    print(f"VIOLATION_COUNT: {payload.get('violation_count', 0)}")
    print(f"FIRST_VIOLATION_PATH: {payload.get('first_violation_path', '')}")
    print(f"FIRST_VIOLATION_KEY: {payload.get('first_violation_key', '')}")
    print(f"CHECKED_PAYLOAD_COUNT: {payload.get('checked_payload_count', 0)}")
    print(f"CHECKED_QUEUE_ITEM_COUNT: {payload.get('checked_queue_item_count', 0)}")
    print(f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("CONVERSATION_TEXT_LOGGED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PatchOps U2.7G queue submission blocker gate.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-json", default=None)
    parser.add_argument("--report-path", action="append", default=[])
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--simulate-pass", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root_from_args(args.repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from patchops.chatgpt_uploader.submission_guard import (
        evaluate_submission_blocker,
        load_payload,
        write_submission_guard_evidence,
    )

    evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    source_payload: dict[str, Any]
    source_returncode = 0
    source_stdout_tail = ""
    source_stderr_tail = ""

    if args.source_json:
        source_payload = load_payload(args.source_json)
    else:
        if not args.report_path:
            raise SystemExit("--source-json or at least one --report-path is required")
        result = _run_queue_gate(
            repo_root=repo_root,
            report_paths=[Path(p).expanduser().resolve() for p in args.report_path],
            evidence_dir=evidence_dir / "source_queue_gate",
            timeout_seconds=args.timeout_seconds,
            simulate_pass=bool(args.simulate_pass),
        )
        source_returncode = int(result.returncode)
        source_stdout_tail = (result.stdout or "")[-5000:]
        source_stderr_tail = (result.stderr or "")[-5000:]
        source_payload = _load_json_evidence(result.stdout or "")
        if not source_payload:
            source_payload = {
                "status": "PASS_OR_BLOCKED",
                "result": "PASS_OR_BLOCKED_SOURCE_QUEUE_PAYLOAD_MISSING",
                "failure_layer": "source_queue_payload_missing",
                "chatgpt_submit_performed": False,
                "conversation_text_logged": False,
                "selenium_used": False,
                "webdriver_used": False,
                "browser_dom_automation_used": False,
            }

    guard = evaluate_submission_blocker(source_payload).to_payload()
    payload = dict(guard)
    payload.update(
        {
            "patch": "U2.7G",
            "source_status": source_payload.get("status", ""),
            "source_result": source_payload.get("result", ""),
            "source_returncode": source_returncode,
            "source_stdout_tail": source_stdout_tail,
            "source_stderr_tail": source_stderr_tail,
            "source_queue_item_count": source_payload.get("queue_item_count", 0),
            "source_original_queue_item_count": source_payload.get("original_queue_item_count", source_payload.get("queue_item_count", 0)),
            "source_skipped_queue_item_count": source_payload.get("skipped_queue_item_count", 0),
            "source_multi_upload_allowed": source_payload.get("multi_upload_allowed", False),
        }
    )

    json_path, txt_path = write_submission_guard_evidence(evidence_dir, payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        _print_payload(payload)

    return 3 if payload["status"] == "FAIL_FORBIDDEN_SUBMISSION_SIDE_EFFECT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
