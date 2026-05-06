from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _repo_root_from_args(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _print_payload(payload: dict[str, Any]) -> None:
    print(f"PATCHOPS_U2_7B_STATUS: {payload.get('status')}")
    print(f"RESULT: {payload.get('result')}")
    print(f"RESULT_LABEL: {payload.get('result_label')}")
    print(f"JSON_EVIDENCE: {payload.get('json_evidence', '')}")
    print(f"TXT_EVIDENCE: {payload.get('txt_evidence', '')}")
    print(f"EXISTING_TARGET_FOUND: {str(payload.get('existing_target_found', False)).lower()}")
    print(f"EXISTING_TARGET_FOCUSED: {str(payload.get('existing_target_focused', False)).lower()}")
    print(f"DELEGATE_ATTEMPTED: {str(payload.get('delegate_attempted', False)).lower()}")
    print(f"DELEGATE_EXIT_CODE: {payload.get('delegate_exit_code', '')}")
    print(f"DELEGATE_EXIT_ZERO: {str(payload.get('delegate_exit_zero', False)).lower()}")
    print(f"BROWSER_PICKER_OPENED: {str(payload.get('browser_picker_opened', False)).lower()}")
    print(f"PATH_TYPED: {str(payload.get('path_typed', False)).lower()}")
    print(f"ENTER_PRESSED_ONCE: {str(payload.get('enter_pressed_once', False)).lower()}")
    print(f"FILE_UPLOAD_ATTEMPTED: {str(payload.get('file_upload_attempted', False)).lower()}")
    print(f"ATTACHMENT_VISIBLE: {str(payload.get('attachment_visible', False)).lower()}")
    print(f"ATTACHMENT_READY: {str(payload.get('attachment_ready', False)).lower()}")
    print(f"UPLOAD_PROGRESS_RESOLVED: {str(payload.get('upload_progress_resolved', False)).lower()}")
    print(f"FAILURE_LAYER: {payload.get('failure_layer', '')}")
    print(f"CLASSIFICATION: {payload.get('classification', '')}")
    print(f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("CONVERSATION_TEXT_LOGGED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")


def _run_delegate(repo_root: Path, report_path: Path, evidence_dir: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    delegate = repo_root / "scripts" / "run_uploader_recover_upload_verify_attachment_no_send.py"
    cmd = [
        sys.executable,
        str(delegate),
        "--repo-root",
        str(repo_root),
        "--report-path",
        str(report_path),
        "--evidence-dir",
        str(evidence_dir),
    ]

    try:
        return subprocess.run(
            cmd,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTIMEOUT after {timeout_seconds} seconds."
        return subprocess.CompletedProcess(args=cmd, returncode=-9998, stdout=stdout, stderr=stderr)


def _forbidden_positive_marker(payload: dict[str, Any], text: str) -> bool:
    forbidden = [
        "CHATGPT_SUBMIT_PERFORMED: true",
        "CONVERSATION_TEXT_LOGGED: true",
        "SELENIUM_USED: true",
        "WEBDRIVER_USED: true",
        "BROWSER_DOM_AUTOMATION_USED: true",
        '"chatgpt_submit_performed": true',
        '"conversation_text_logged": true',
        '"selenium_used": true',
        '"webdriver_used": true',
        '"browser_dom_automation_used": true',
    ]
    if any(marker in text for marker in forbidden):
        return True
    return any(bool(payload.get(key)) for key in [
        "chatgpt_submit_performed",
        "conversation_text_logged",
        "selenium_used",
        "webdriver_used",
        "browser_dom_automation_used",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PatchOps U2.7B upload delegate first-failing-layer diagnostic.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--config-path", default=None)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--simulate-existing-target-found", action="store_true")
    parser.add_argument("--simulate-delegate-stdout", default=None)
    parser.add_argument("--simulate-delegate-stderr", default="")
    parser.add_argument("--simulate-delegate-returncode", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root_from_args(args.repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from patchops.chatgpt_uploader.config import load_config, resolve_config_path
    from patchops.chatgpt_uploader.existing_target_probe import (
        probe_existing_edge_target,
        probe_existing_target_from_titles,
    )
    from patchops.chatgpt_uploader.upload_delegate_diagnostics import (
        classify_delegate_output,
        write_delegate_diagnostic_evidence,
    )

    report_path = Path(args.report_path).expanduser().resolve()
    evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    delegate_evidence_dir = evidence_dir / "delegate_raw"
    config_path = resolve_config_path(
        repo_root=repo_root,
        target_config=args.target_config,
        config_path=args.config_path,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base: dict[str, Any] = {
        "patch": "U2.7B",
        "timestamp": timestamp,
        "target_config_path": str(config_path),
        "selected_report_path": str(report_path),
        "selected_report_exists": report_path.exists(),
        "selected_report_sha256": _sha256_file(report_path) if report_path.exists() and report_path.is_file() else "",
        "selected_report_size_bytes": report_path.stat().st_size if report_path.exists() and report_path.is_file() else 0,
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
    }

    if not report_path.exists() or not report_path.is_file() or report_path.stat().st_size <= 0:
        diagnostic = classify_delegate_output(
            delegate_attempted=False,
            delegate_exit_code=None,
            stdout="",
            stderr="",
            evidence_dir=delegate_evidence_dir,
        ).to_payload()
        payload = dict(base)
        payload.update(diagnostic)
        payload.update({
            "status": "PASS_OR_BLOCKED",
            "result": "BLOCKED_REPORT_UNAVAILABLE",
            "result_label": "PASS_OR_BLOCKED_REPORT_UNAVAILABLE",
            "failure_layer": "report_unavailable",
            "classification": "report_unavailable",
            "recommended_next_mode": "provide_nonempty_report_path",
            "existing_target_found": False,
            "existing_target_focused": False,
        })
        json_path, txt_path = write_delegate_diagnostic_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload)
        return 0

    if not config_path.exists():
        diagnostic = classify_delegate_output(
            delegate_attempted=False,
            delegate_exit_code=None,
            stdout="",
            stderr="",
            evidence_dir=delegate_evidence_dir,
        ).to_payload()
        payload = dict(base)
        payload.update(diagnostic)
        payload.update({
            "status": "PASS_OR_BLOCKED",
            "result": "BLOCKED_TARGET_CONFIG_MISSING",
            "result_label": "PASS_OR_BLOCKED_TARGET_CONFIG_MISSING",
            "failure_layer": "target_config_missing",
            "classification": "target_config_missing",
            "recommended_next_mode": "create_target_config_then_rerun",
            "existing_target_found": False,
            "existing_target_focused": False,
        })
        json_path, txt_path = write_delegate_diagnostic_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload)
        return 0

    cfg = load_config(config_path)
    cfg_payload = cfg.to_payload() if hasattr(cfg, "to_payload") else {}
    target_url = str(cfg_payload.get("target_url") or "https://chatgpt.com/")

    base.update({
        "target_url_redacted": cfg_payload.get("target_url_redacted") or cfg_payload.get("redacted_target_url") or "",
        "target_url_sha256": cfg_payload.get("target_url_sha256") or "",
    })

    if args.simulate_existing_target_found:
        probe = probe_existing_target_from_titles(["ChatGPT - Microsoft Edge"], target_url=target_url, focused=True)
    else:
        probe = probe_existing_edge_target(target_url=target_url, focus=True)

    probe_payload = probe.to_payload()

    if not probe_payload.get("existing_target_focused"):
        diagnostic = classify_delegate_output(
            delegate_attempted=False,
            delegate_exit_code=None,
            stdout="",
            stderr="",
            evidence_dir=delegate_evidence_dir,
        ).to_payload()
        payload = dict(base)
        payload.update(probe_payload)
        payload.update(diagnostic)
        payload.update({
            "status": "PASS_OR_BLOCKED",
            "result": "BLOCKED_EXISTING_TARGET_NOT_FOCUSED",
            "result_label": "PASS_OR_BLOCKED_EXISTING_TARGET_NOT_FOCUSED",
            "failure_layer": "existing_target_not_focused",
            "classification": "existing_target_not_focused",
            "recommended_next_mode": "open_or_focus_configured_chatgpt_edge_target_then_rerun",
        })
        json_path, txt_path = write_delegate_diagnostic_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload)
        return 0

    if args.simulate_delegate_stdout is not None:
        delegate_stdout = args.simulate_delegate_stdout
        delegate_stderr = args.simulate_delegate_stderr or ""
        delegate_returncode = args.simulate_delegate_returncode
    else:
        delegate_result = _run_delegate(repo_root, report_path, delegate_evidence_dir, args.timeout_seconds)
        delegate_stdout = delegate_result.stdout or ""
        delegate_stderr = delegate_result.stderr or ""
        delegate_returncode = int(delegate_result.returncode)

    diagnostic = classify_delegate_output(
        delegate_attempted=True,
        delegate_exit_code=delegate_returncode,
        stdout=delegate_stdout,
        stderr=delegate_stderr,
        evidence_dir=delegate_evidence_dir,
    ).to_payload()

    payload = dict(base)
    payload.update(probe_payload)
    payload.update(diagnostic)
    payload["delegate_stdout_tail"] = delegate_stdout[-5000:]
    payload["delegate_stderr_tail"] = delegate_stderr[-5000:]

    if payload.get("attachment_visible") and payload.get("attachment_ready") and payload.get("upload_progress_resolved"):
        payload["status"] = "PASS"
        payload["result"] = "PASS_UPLOAD_DELEGATE_ATTACHMENT_VERIFIED_NO_SEND"
        payload["result_label"] = "PASS_UPLOAD_DELEGATE_ATTACHMENT_VERIFIED_NO_SEND"
        payload["failure_layer"] = ""
        payload["recommended_next_mode"] = "continue_to_u2_7c_no_send_existing_target_upload_proof"
    else:
        payload["status"] = "PASS_OR_BLOCKED"
        payload["result"] = "PASS_OR_BLOCKED_UPLOAD_DELEGATE_FIRST_LAYER_CLASSIFIED"
        payload["result_label"] = "PASS_OR_BLOCKED_UPLOAD_DELEGATE_FIRST_LAYER_CLASSIFIED"

    payload["chatgpt_submit_performed"] = False
    payload["conversation_text_logged"] = False
    payload["selenium_used"] = False
    payload["webdriver_used"] = False
    payload["browser_dom_automation_used"] = False

    combined_text = delegate_stdout + "\n" + delegate_stderr
    if _forbidden_positive_marker(payload, combined_text):
        payload["status"] = "FAIL_FORBIDDEN_SIDE_EFFECT"
        payload["result"] = "FAIL_FORBIDDEN_SIDE_EFFECT"
        payload["result_label"] = "FAIL_FORBIDDEN_SIDE_EFFECT"
        payload["failure_layer"] = "forbidden_side_effect"

    json_path, txt_path = write_delegate_diagnostic_evidence(evidence_dir, payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        _print_payload(payload)

    return 3 if payload["status"] == "FAIL_FORBIDDEN_SIDE_EFFECT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
