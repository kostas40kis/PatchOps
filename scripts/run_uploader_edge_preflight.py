from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


SAFETY_FLAGS = {
    "browser_picker_opened": False,
    "file_upload_attempted": False,
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


def _policy_reason() -> str:
    return "operator_set_mode_is_focus_only"


def _launch_policy_object() -> dict:
    return {
        "allow_launch": False,
        "allow_open_configured_url": False,
        "allow_launch_target": False,
        "launch_allowed": False,
        "open_configured_url_allowed": False,
        "policy": "no_real_edge",
        "reason": _policy_reason(),
    }


def _event(name: str, **details) -> dict:
    payload = {"event": name}
    payload.update(details)
    return payload


def _with_contract(payload: dict) -> dict:
    payload = dict(payload)

    safety = dict(SAFETY_FLAGS)
    safety.update({
        "browser_picker_opened": bool(payload.get("browser_picker_opened", False)),
        "file_upload_attempted": bool(payload.get("file_upload_attempted", False)),
        "chatgpt_submit_performed": bool(payload.get("chatgpt_submit_performed", False)),
        "conversation_text_logged": bool(payload.get("conversation_text_logged", False)),
        "selenium_used": bool(payload.get("selenium_used", False)),
        "webdriver_used": bool(payload.get("webdriver_used", False)),
        "browser_dom_automation_used": bool(payload.get("browser_dom_automation_used", False)),
    })

    payload.update(safety)
    payload["safety_flags"] = safety

    status = str(payload.get("status", "FAIL_OR_BLOCKED"))
    if status == "PASS_CONFIG_ONLY":
        payload["result_label"] = "PASS_CONFIG_ONLY"
    elif status == "FAIL_OR_BLOCKED":
        payload["result_label"] = "FAIL_OR_BLOCKED"
    else:
        payload["result_label"] = status

    policy = _launch_policy_object()
    payload["launch_policy"] = policy
    payload["launch_policy_label"] = policy["policy"]
    payload["launch_policy_reason"] = policy["reason"]

    payload["launch_allowed"] = False
    payload["open_configured_url_allowed"] = False
    payload["allow_launch_target"] = False
    payload["allow_open_configured_url"] = False
    payload["config_only"] = True

    events = payload.get("events")
    if not isinstance(events, list) or not events:
        if status == "PASS_CONFIG_ONLY":
            events = [_event("config_loaded", target_config_path=str(payload.get("target_config_path", "")))]
        else:
            events = [_event("config_load_failed", target_config_path=str(payload.get("target_config_path", "")), reason=str(payload.get("reason", "")))]
    payload["events"] = events

    return payload


def _write_evidence(evidence_dir: Path, payload: dict) -> tuple[Path, Path, dict]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = evidence_dir / f"u2_00_edge_preflight_{stamp}.json"
    txt_path = evidence_dir / f"u2_00_edge_preflight_{stamp}.txt"

    payload = _with_contract(payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "PATCHOPS UPLOADER EDGE PREFLIGHT",
        "================================",
        f"PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: {payload['status']}",
        f"RESULT: {payload['result']}",
        f"RESULT_LABEL: {payload['result_label']}",
        f"JSON_EVIDENCE: {json_path}",
        f"TXT_EVIDENCE: {txt_path}",
        f"TARGET_CONFIG_PATH: {payload.get('target_config_path', '')}",
        f"TARGET_URL_REDACTED: {payload.get('target_url_redacted', '')}",
        f"TARGET_URL_SHA256: {payload.get('target_url_sha256', '')}",
        f"CONFIG_ONLY: {str(payload.get('config_only', True)).lower()}",
        "LAUNCH_ALLOWED: false",
        "OPEN_CONFIGURED_URL_ALLOWED: false",
        f"LAUNCH_POLICY: {payload.get('launch_policy_label', 'no_real_edge')}",
        f"LAUNCH_POLICY_REASON: {payload.get('launch_policy_reason', _policy_reason())}",
        "BROWSER_PICKER_OPENED: false",
        "FILE_UPLOAD_ATTEMPTED: false",
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
        "",
    ]
    txt_path.write_text("\n".join(txt_lines), encoding="utf-8")
    return json_path, txt_path, payload


def _print_payload(payload: dict) -> None:
    print(f"PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: {payload['status']}")
    print(f"RESULT: {payload['result']}")
    print(f"RESULT_LABEL: {payload['result_label']}")
    print(f"JSON_EVIDENCE: {payload.get('json_evidence', '')}")
    print(f"TXT_EVIDENCE: {payload.get('txt_evidence', '')}")

    if payload.get("target_config_path"):
        print(f"TARGET_CONFIG_PATH: {payload['target_config_path']}")
    if payload.get("target_url_redacted"):
        print(f"TARGET_URL_REDACTED: {payload['target_url_redacted']}")
    if payload.get("target_url_sha256"):
        print(f"TARGET_URL_SHA256: {payload['target_url_sha256']}")

    print(f"CONFIG_ONLY: {str(payload.get('config_only', True)).lower()}")
    print("LAUNCH_ALLOWED: false")
    print("OPEN_CONFIGURED_URL_ALLOWED: false")
    print(f"LAUNCH_POLICY: {payload.get('launch_policy_label', 'no_real_edge')}")
    print(f"LAUNCH_POLICY_REASON: {payload.get('launch_policy_reason', _policy_reason())}")
    print("BROWSER_PICKER_OPENED: false")
    print("FILE_UPLOAD_ATTEMPTED: false")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("CONVERSATION_TEXT_LOGGED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")


def _safe_payload_from_config(cfg) -> dict:
    try:
        return dict(cfg.to_payload(include_target_url=False))
    except TypeError:
        payload = dict(cfg.to_payload())
        payload.pop("target_url", None)
        return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PatchOps ChatGPT uploader Edge preflight.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--evidence-dir", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--launch-if-missing", action="store_true")
    parser.add_argument("--allow-real-edge", action="store_true")
    parser.add_argument("--no-real-edge", action="store_true")
    parser.add_argument("--config-only", action="store_true")
    parser.add_argument("--allow-blocked-exit-zero", action="store_true")
    parser.add_argument("--allow-launch-target", action="store_true")
    parser.add_argument("--allow-open-configured-url", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root_from_args(args.repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from patchops.chatgpt_uploader.config import load_config, resolve_config_path

    config_path = resolve_config_path(
        repo_root=repo_root,
        target_config=args.target_config,
        config_path=args.config_path,
    )

    evidence_dir = (
        Path(args.evidence_dir).expanduser().resolve()
        if args.evidence_dir
        else repo_root / "data" / "runtime" / "chatgpt_uploader" / "u2_00_edge_preflight"
    )

    base_payload = {
        "config_only": True,
        "target_config_path": str(config_path),
        "browser_picker_opened": False,
        "file_upload_attempted": False,
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "launch_allowed": False,
        "open_configured_url_allowed": False,
        "launch_policy": _launch_policy_object(),
        "launch_policy_label": "no_real_edge",
        "launch_policy_reason": _policy_reason(),
        "allow_launch_target": False,
        "allow_open_configured_url": False,
    }

    if not config_path.exists():
        payload = dict(base_payload)
        payload.update({
            "ok": False,
            "status": "FAIL_OR_BLOCKED",
            "result": "FAIL_OR_BLOCKED_MISSING_TARGET_CONFIG",
            "reason": "target config does not exist",
            "events": [
                _event(
                    "config_load_failed",
                    target_config_path=str(config_path),
                    reason="target config does not exist",
                )
            ],
        })
        json_path, txt_path, payload = _write_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload)
        return 0 if args.allow_blocked_exit_zero else 2

    try:
        cfg = load_config(config_path)
        cfg_payload = _safe_payload_from_config(cfg)

        payload = dict(base_payload)
        payload.update(cfg_payload)
        payload.update({
            "ok": True,
            "status": "PASS_CONFIG_ONLY",
            "result": "PASS_CONFIG_ONLY",
            "target_config_path": str(config_path),
            "config_only": True,
            "launch_allowed": False,
            "open_configured_url_allowed": False,
            "allow_launch_target": False,
            "allow_open_configured_url": False,
            "browser_picker_opened": False,
            "file_upload_attempted": False,
            "chatgpt_submit_performed": False,
            "conversation_text_logged": False,
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
            "launch_policy": _launch_policy_object(),
            "launch_policy_label": "no_real_edge",
            "launch_policy_reason": _policy_reason(),
            "events": [
                _event("config_loaded", target_config_path=str(config_path))
            ],
        })

        json_path, txt_path, payload = _write_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload)
        return 0

    except Exception as exc:
        payload = dict(base_payload)
        payload.update({
            "ok": False,
            "status": "FAIL_OR_BLOCKED",
            "result": "FAIL_OR_BLOCKED_CONFIG_EXCEPTION",
            "reason": f"{type(exc).__name__}: {exc}",
            "events": [
                _event(
                    "config_load_failed",
                    target_config_path=str(config_path),
                    reason=f"{type(exc).__name__}: {exc}",
                )
            ],
        })
        json_path, txt_path, payload = _write_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload)
        return 0 if args.allow_blocked_exit_zero else 2


if __name__ == "__main__":
    raise SystemExit(main())
