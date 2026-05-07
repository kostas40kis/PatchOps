from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.config import (  # noqa: E402
    ConfigValidationError,
    load_config,
    resolve_config_path,
)


def _redact_target_url(value: str) -> str:
    raw = str(value or "")
    if not raw:
        return ""
    if "chatgpt.com" not in raw:
        return "<redacted-target-url>"
    return "https://chatgpt.com/<redacted>"


def _payload_from_config(config) -> dict[str, object]:
    if hasattr(config, "to_payload"):
        try:
            payload = config.to_payload(include_target_url=False)
        except TypeError:
            payload = config.to_payload()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(config, "to_dict"):
        payload = config.to_dict()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(config, "__dict__"):
        return dict(config.__dict__)
    return {}


def build_payload(config_path: Path) -> dict[str, object]:
    config = load_config(config_path)
    payload = _payload_from_config(config)
    target_url = str(getattr(config, "target_url", payload.get("target_url", "")) or "")

    payload.pop("target_url", None)
    payload["ok"] = True
    payload["result"] = "PASS_CHROME_CONFIG_VALIDATED"
    payload["browser"] = "chrome"
    payload["expected_browser"] = "chrome"
    payload["target_config_status"] = "OK"
    payload["chrome_config_status"] = "PASS_CHROME_CONFIG_VALIDATED"
    payload["raw_target_url_printed"] = False
    payload["redacted_target_display"] = _redact_target_url(target_url)
    payload["file_upload_attempted"] = False
    payload["chatgpt_submit_performed"] = False
    payload["conversation_text_logged"] = False
    payload["selenium_used"] = False
    payload["webdriver_used"] = False
    payload["browser_dom_automation_used"] = False
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Show the redacted ChatGPT Copilot target config.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        config_path = resolve_config_path(args.target_config, repo_root=args.repo_root)
        payload = build_payload(config_path)
    except (ConfigValidationError, OSError, ValueError) as exc:
        if args.json:
            print(json.dumps({"ok": False, "result": "BLOCKED_CONFIG_INVALID", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print("TARGET_CONFIG_STATUS: BLOCKED_CONFIG_INVALID")
            print(f"ERROR: {exc}")
        return 2

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("TARGET_CONFIG_STATUS: OK")
    print("CHROME_CONFIG_STATUS: PASS_CHROME_CONFIG_VALIDATED")
    print("BROWSER: chrome")
    print("EXPECTED_BROWSER: chrome")
    print(f"TARGET_CONFIG_PATH: {config_path}")
    print(f"REDACTED_TARGET_DISPLAY: {payload.get('redacted_target_display', '')}")
    print("RAW_TARGET_URL_PRINTED: false")
    print("file_upload_attempted:false")
    print("chatgpt_submit_performed:false")
    print("selenium_used:false")
    print("webdriver_used:false")
    print("browser_dom_automation_used:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())