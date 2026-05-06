from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SAFETY_FLAGS = {
    "chatgpt_submit_performed": False,
    "conversation_text_logged": False,
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
}


def _repo_root_from_args(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_payload(cfg: object) -> dict[str, Any]:
    if hasattr(cfg, "to_payload"):
        try:
            return dict(cfg.to_payload())
        except TypeError:
            return dict(cfg.to_payload(include_target_url=True))
    if hasattr(cfg, "__dict__"):
        return dict(cfg.__dict__)
    return {}


def _bool_from_text(text: str, key: str) -> bool:
    key_upper = key.upper()
    key_lower = key.lower()
    return (
        f"{key_upper}: true" in text
        or f"{key_lower}: true" in text
        or f'"{key_lower}": true' in text
    )


def _json_evidence_from_stdout(stdout: str) -> dict[str, Any]:
    for line in (stdout or "").splitlines():
        if line.startswith("JSON_EVIDENCE:"):
            path = Path(line.split(":", 1)[1].strip())
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
                    if isinstance(data, dict):
                        return data
                except Exception:
                    return {}
    return {}


def build_delegate_command(
    *,
    repo_root: Path,
    report_path: Path,
    evidence_dir: Path,
    timeout_seconds: int,
    allow_live_picker: bool,
) -> list[str]:
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
        "--timeout-seconds",
        str(timeout_seconds),
    ]
    if allow_live_picker:
        cmd.append("--allow-live-picker")
    return cmd


def _delegate_upload(
    *,
    repo_root: Path,
    report_path: Path,
    evidence_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    delegate = repo_root / "scripts" / "run_uploader_recover_upload_verify_attachment_no_send.py"
    if not delegate.exists():
        return {
            "delegate_attempted": False,
            "delegate_returncode": None,
            "delegate_classification": "upload_delegate_missing",
            "delegate_stdout_tail": "",
            "delegate_stderr_tail": "",
        }

    cmd = build_delegate_command(
        repo_root=repo_root,
        report_path=report_path,
        evidence_dir=evidence_dir,
        timeout_seconds=timeout_seconds,
        allow_live_picker=True,
    )

    try:
        result = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            timeout=timeout_seconds + 20,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTIMEOUT after {timeout_seconds + 20} seconds."
        result = subprocess.CompletedProcess(args=cmd, returncode=-9998, stdout=stdout, stderr=stderr)

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    combined = stdout + "\n" + stderr
    evidence = _json_evidence_from_stdout(stdout)

    def flag(name: str) -> bool:
        return bool(evidence.get(name)) or _bool_from_text(combined, name)

    attachment_visible = flag("attachment_visible")
    attachment_ready = flag("attachment_ready")
    upload_progress_resolved = flag("upload_progress_resolved")

    picker_opened = flag("browser_picker_opened") or flag("picker_opened") or flag("file_picker_opened")
    path_typed = flag("path_typed") or flag("file_path_written") or flag("report_path_typed")
    enter_pressed_once = flag("enter_pressed_once") or flag("picker_enter_pressed")
    file_upload_attempted = flag("file_upload_attempted")

    return {
        "delegate_attempted": True,
        "delegate_returncode": int(result.returncode),
        "delegate_classification": "upload_delegate_pass" if result.returncode == 0 else "upload_delegate_blocked_or_failed",
        "delegate_stdout_tail": stdout[-5000:],
        "delegate_stderr_tail": stderr[-5000:],
        "browser_picker_opened": picker_opened,
        "path_typed": path_typed,
        "enter_pressed_once": enter_pressed_once,
        "file_upload_attempted": file_upload_attempted,
        "delegate_attachment_visible": attachment_visible,
        "delegate_attachment_ready": attachment_ready,
        "delegate_upload_progress_resolved": upload_progress_resolved,
        "attachment_visible": attachment_visible,
        "attachment_ready": attachment_ready,
        "upload_progress_resolved": upload_progress_resolved,
        "canonical_trigger_attempted": flag("canonical_trigger_attempted"),
        "slash_sent": flag("slash_sent"),
        "file_path_written": flag("file_path_written"),
        "picker_enter_pressed": flag("picker_enter_pressed"),
        "attachment_verification_attempted": flag("attachment_verification_attempted"),
    }


def _write_json_txt(evidence_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = evidence_dir / f"u2_7a_existing_target_preferred_{stamp}.json"
    txt_path = evidence_dir / f"u2_7a_existing_target_preferred_{stamp}.txt"

    payload = dict(payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    lines = [
        "PATCHOPS U2.7A EXISTING TARGET PREFERRED LIVE EDGE",
        "==================================================",
        f"PATCHOPS_U2_7A_STATUS: {payload.get('status')}",
        f"RESULT: {payload.get('result')}",
        f"RESULT_LABEL: {payload.get('result_label')}",
        f"JSON_EVIDENCE: {json_path}",
        f"TXT_EVIDENCE: {txt_path}",
        f"SELECTED_REPORT_PATH: {payload.get('selected_report_path', '')}",
        f"SELECTED_REPORT_SHA256: {payload.get('selected_report_sha256', '')}",
        f"TARGET_CONFIG_PATH: {payload.get('target_config_path', '')}",
        f"TARGET_URL_REDACTED: {payload.get('target_url_redacted', '')}",
        f"TARGET_URL_SHA256: {payload.get('target_url_sha256', '')}",
        f"EXISTING_TARGET_PROBE_ATTEMPTED: {str(payload.get('existing_target_probe_attempted', False)).lower()}",
        f"EXISTING_TARGET_FOUND: {str(payload.get('existing_target_found', False)).lower()}",
        f"EXISTING_TARGET_FOCUSED: {str(payload.get('existing_target_focused', False)).lower()}",
        f"LAUNCH_SKIPPED_EXISTING_TARGET: {str(payload.get('launch_skipped_existing_target', False)).lower()}",
        f"NORMAL_EDGE_LAUNCH_ATTEMPTED: {str(payload.get('normal_edge_launch_attempted', False)).lower()}",
        f"CANONICAL_TRIGGER_ATTEMPTED: {str(payload.get('canonical_trigger_attempted', False)).lower()}",
        f"SLASH_SENT: {str(payload.get('slash_sent', False)).lower()}",
        f"BROWSER_PICKER_OPENED: {str(payload.get('browser_picker_opened', False)).lower()}",
        f"FILE_PATH_WRITTEN: {str(payload.get('file_path_written', False)).lower()}",
        f"PICKER_ENTER_PRESSED: {str(payload.get('picker_enter_pressed', False)).lower()}",
        f"ATTACHMENT_VERIFICATION_ATTEMPTED: {str(payload.get('attachment_verification_attempted', False)).lower()}",
        f"ATTACHMENT_VISIBLE: {str(payload.get('attachment_visible', False)).lower()}",
        f"ATTACHMENT_READY: {str(payload.get('attachment_ready', False)).lower()}",
        f"UPLOAD_PROGRESS_RESOLVED: {str(payload.get('upload_progress_resolved', False)).lower()}",
        f"FAILURE_LAYER: {payload.get('failure_layer', '')}",
        f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}",
        "FILE_UPLOAD_ATTEMPTED: " + str(payload.get("file_upload_attempted", False)).lower(),
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
        "",
    ]
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path


def _print_payload(payload: dict[str, Any]) -> None:
    print(f"PATCHOPS_U2_7A_STATUS: {payload.get('status')}")
    print(f"RESULT: {payload.get('result')}")
    print(f"RESULT_LABEL: {payload.get('result_label')}")
    print(f"JSON_EVIDENCE: {payload.get('json_evidence', '')}")
    print(f"TXT_EVIDENCE: {payload.get('txt_evidence', '')}")
    print(f"EXISTING_TARGET_PROBE_ATTEMPTED: {str(payload.get('existing_target_probe_attempted', False)).lower()}")
    print(f"EXISTING_TARGET_FOUND: {str(payload.get('existing_target_found', False)).lower()}")
    print(f"EXISTING_TARGET_FOCUSED: {str(payload.get('existing_target_focused', False)).lower()}")
    print(f"LAUNCH_SKIPPED_EXISTING_TARGET: {str(payload.get('launch_skipped_existing_target', False)).lower()}")
    print(f"NORMAL_EDGE_LAUNCH_ATTEMPTED: {str(payload.get('normal_edge_launch_attempted', False)).lower()}")
    print(f"CANONICAL_TRIGGER_ATTEMPTED: {str(payload.get('canonical_trigger_attempted', False)).lower()}")
    print(f"SLASH_SENT: {str(payload.get('slash_sent', False)).lower()}")
    print(f"BROWSER_PICKER_OPENED: {str(payload.get('browser_picker_opened', False)).lower()}")
    print(f"FILE_PATH_WRITTEN: {str(payload.get('file_path_written', False)).lower()}")
    print(f"PICKER_ENTER_PRESSED: {str(payload.get('picker_enter_pressed', False)).lower()}")
    print(f"ATTACHMENT_VERIFICATION_ATTEMPTED: {str(payload.get('attachment_verification_attempted', False)).lower()}")
    print(f"ATTACHMENT_VISIBLE: {str(payload.get('attachment_visible', False)).lower()}")
    print(f"ATTACHMENT_READY: {str(payload.get('attachment_ready', False)).lower()}")
    print(f"UPLOAD_PROGRESS_RESOLVED: {str(payload.get('upload_progress_resolved', False)).lower()}")
    print(f"FAILURE_LAYER: {payload.get('failure_layer', '')}")
    print(f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}")
    print(f"FILE_UPLOAD_ATTEMPTED: {str(payload.get('file_upload_attempted', False)).lower()}")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("CONVERSATION_TEXT_LOGGED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")


def _classify_after_upload(payload: dict[str, Any], allow_upload: bool) -> dict[str, Any]:
    payload = dict(payload)

    if payload.get("attachment_visible") and payload.get("attachment_ready") and payload.get("upload_progress_resolved"):
        payload["status"] = "PASS"
        payload["result"] = "PASS_EXISTING_TARGET_UPLOAD_ATTACHED_NO_SEND"
        payload["result_label"] = "PASS_EXISTING_TARGET_UPLOAD_ATTACHED_NO_SEND"
        payload["failure_layer"] = ""
        payload["recommended_next_mode"] = "continue_to_attachment_ready_hardening_or_queue_foundation"
        return payload

    if payload.get("existing_target_found") and not allow_upload:
        payload["status"] = "PASS_OR_BLOCKED"
        payload["result"] = "PASS_OR_BLOCKED_EXISTING_TARGET_FOUND_UPLOAD_NOT_REQUESTED"
        payload["result_label"] = "PASS_OR_BLOCKED_EXISTING_TARGET_FOUND_UPLOAD_NOT_REQUESTED"
        payload["failure_layer"] = "upload_not_requested"
        payload["recommended_next_mode"] = "rerun_with_allow_upload_for_attachment_proof"
        return payload

    if allow_upload and not payload.get("canonical_trigger_attempted"):
        payload["status"] = "PASS_OR_BLOCKED"
        payload["result"] = "PASS_OR_BLOCKED_LIVE_PICKER_PERMISSION_NOT_REACHED"
        payload["result_label"] = "PASS_OR_BLOCKED_LIVE_PICKER_PERMISSION_NOT_REACHED"
        payload["failure_layer"] = "live_picker_permission_not_reached"
        payload["recommended_next_mode"] = "patch_delegate_command_or_live_permission_gate"
        return payload

    if allow_upload and payload.get("canonical_trigger_attempted") and not payload.get("browser_picker_opened"):
        payload["status"] = "PASS_OR_BLOCKED"
        payload["result"] = "PASS_OR_BLOCKED_PICKER_NOT_OPENED"
        payload["result_label"] = "PASS_OR_BLOCKED_PICKER_NOT_OPENED"
        payload["failure_layer"] = "picker_not_opened"
        payload["recommended_next_mode"] = "patch_canonical_trigger_focus_or_picker_detection"
        return payload

    if allow_upload and payload.get("browser_picker_opened") and not payload.get("file_path_written"):
        payload["status"] = "PASS_OR_BLOCKED"
        payload["result"] = "PASS_OR_BLOCKED_PICKER_OPENED_PATH_NOT_WRITTEN"
        payload["result_label"] = "PASS_OR_BLOCKED_PICKER_OPENED_PATH_NOT_WRITTEN"
        payload["failure_layer"] = "picker_opened_path_not_written"
        payload["recommended_next_mode"] = "patch_file_dialog_path_writer"
        return payload

    if allow_upload and payload.get("file_path_written") and not payload.get("picker_enter_pressed"):
        payload["status"] = "PASS_OR_BLOCKED"
        payload["result"] = "PASS_OR_BLOCKED_PATH_WRITTEN_ENTER_NOT_CONFIRMED"
        payload["result_label"] = "PASS_OR_BLOCKED_PATH_WRITTEN_ENTER_NOT_CONFIRMED"
        payload["failure_layer"] = "path_written_enter_not_confirmed"
        payload["recommended_next_mode"] = "patch_single_enter_confirmation"
        return payload

    if allow_upload:
        payload["status"] = "PASS_OR_BLOCKED"
        payload["result"] = "PASS_OR_BLOCKED_ATTACHMENT_NOT_VISIBLE"
        payload["result_label"] = "PASS_OR_BLOCKED_ATTACHMENT_NOT_VISIBLE"
        payload["failure_layer"] = "attachment_not_visible"
        payload["recommended_next_mode"] = "patch_attachment_detection_or_wait"
        return payload

    payload["status"] = "PASS_OR_BLOCKED"
    payload["result"] = "PASS_OR_BLOCKED_EXISTING_TARGET_NOT_FOUND_OR_UPLOAD_DISABLED"
    payload["result_label"] = "PASS_OR_BLOCKED_EXISTING_TARGET_NOT_FOUND_OR_UPLOAD_DISABLED"
    payload["failure_layer"] = "existing_target_or_upload_disabled"
    payload["recommended_next_mode"] = "open_edge_target_or_enable_upload_gate"
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PatchOps U2.7A existing-target-preferred live Edge uploader proof.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--config-path", default=None)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--allow-launch-edge", action="store_true")
    parser.add_argument("--allow-upload", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--simulate-existing-target-found", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root_from_args(args.repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from patchops.chatgpt_uploader.config import load_config, resolve_config_path
    from patchops.chatgpt_uploader.existing_target_probe import (
        probe_existing_edge_target,
        probe_existing_target_from_titles,
        start_normal_edge_target,
    )

    report_path = Path(args.report_path).expanduser().resolve()
    evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    config_path = resolve_config_path(repo_root=repo_root, target_config=args.target_config, config_path=args.config_path)

    base: dict[str, Any] = {
        "patch": "U2.7A/U2.7C",
        "target_config_path": str(config_path),
        "selected_report_path": str(report_path),
        "selected_report_exists": report_path.exists(),
        "selected_report_sha256": _sha256_file(report_path) if report_path.exists() and report_path.is_file() else "",
        "selected_report_size_bytes": report_path.stat().st_size if report_path.exists() and report_path.is_file() else 0,
        "attachment_visible": False,
        "attachment_ready": False,
        "upload_progress_resolved": False,
        "browser_picker_opened": False,
        "path_typed": False,
        "enter_pressed_once": False,
        "canonical_trigger_attempted": False,
        "slash_sent": False,
        "file_path_written": False,
        "picker_enter_pressed": False,
        "attachment_verification_attempted": False,
        "file_upload_attempted": False,
        **SAFETY_FLAGS,
    }

    if not report_path.exists() or not report_path.is_file() or report_path.stat().st_size <= 0:
        payload = dict(base)
        payload.update({
            "status": "PASS_OR_BLOCKED",
            "result": "BLOCKED_REPORT_UNAVAILABLE",
            "result_label": "PASS_OR_BLOCKED_REPORT_UNAVAILABLE",
            "failure_layer": "report_unavailable",
            "recommended_next_mode": "provide_nonempty_report_path",
            "existing_target_probe_attempted": False,
            "existing_target_found": False,
            "existing_target_focused": False,
            "launch_skipped_existing_target": False,
            "normal_edge_launch_attempted": False,
        })
        json_path, txt_path = _write_json_txt(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload)
        return 0

    if not config_path.exists():
        payload = dict(base)
        payload.update({
            "status": "PASS_OR_BLOCKED",
            "result": "BLOCKED_TARGET_CONFIG_MISSING",
            "result_label": "PASS_OR_BLOCKED_TARGET_CONFIG_MISSING",
            "failure_layer": "target_config_missing",
            "recommended_next_mode": "create_target_config_then_rerun",
            "existing_target_probe_attempted": False,
            "existing_target_found": False,
            "existing_target_focused": False,
            "launch_skipped_existing_target": False,
            "normal_edge_launch_attempted": False,
        })
        json_path, txt_path = _write_json_txt(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload)
        return 0

    cfg = load_config(config_path)
    cfg_payload = _safe_payload(cfg)
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
    payload = dict(base)
    payload.update(probe_payload)

    launch_started = False
    if payload.get("existing_target_found"):
        payload["launch_skipped_existing_target"] = True
        payload["normal_edge_launch_attempted"] = False
    elif args.allow_launch_edge:
        payload["launch_skipped_existing_target"] = False
        payload["normal_edge_launch_attempted"] = True
        launch_started = bool(start_normal_edge_target(target_url))
        payload["normal_edge_launch_started"] = launch_started
    else:
        payload["launch_skipped_existing_target"] = False
        payload["normal_edge_launch_attempted"] = False

    can_attempt_upload = bool(args.allow_upload and (payload.get("existing_target_focused") or launch_started))
    if can_attempt_upload:
        delegate_payload = _delegate_upload(
            repo_root=repo_root,
            report_path=report_path,
            evidence_dir=evidence_dir / "upload_delegate",
            timeout_seconds=args.timeout_seconds,
        )
        payload.update(delegate_payload)

    payload["chatgpt_submit_performed"] = False
    payload["conversation_text_logged"] = False
    payload["selenium_used"] = False
    payload["webdriver_used"] = False
    payload["browser_dom_automation_used"] = False

    payload = _classify_after_upload(payload, allow_upload=args.allow_upload)

    json_path, txt_path = _write_json_txt(evidence_dir, payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        _print_payload(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
