from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root_from_args(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Set PatchOps ChatGPT Co-Pilot target config.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--config-path", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--browser", default="msedge", choices=["msedge"])
    parser.add_argument("--mode", default="operator_set", choices=["operator_set", "launch_target", "normal_edge_session"])
    parser.add_argument("--disable-real-edge-default", action="store_true")
    parser.add_argument("--allow-upload-default", action="store_true")
    parser.add_argument("--allow-send-default", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root_from_args(args.repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, default_config_path, write_config

    config_path = Path(args.target_config or args.config_path).expanduser().resolve() if (args.target_config or args.config_path) else default_config_path(repo_root)

    allow_real_edge_default = not args.disable_real_edge_default
    cfg = ChatGPTUploaderConfig.create(
        args.target_url,
        mode=args.mode,
        browser=args.browser,
        allow_upload=args.allow_upload_default,
        allow_send=args.allow_send_default,
        allow_upload_default=args.allow_upload_default,
        allow_send_default=args.allow_send_default,
        allow_real_edge_default=allow_real_edge_default,
        real_edge_default=allow_real_edge_default,
        allow_browser_launch=allow_real_edge_default,
        target_config_path=str(config_path),
    )

    written = write_config(cfg, config_path)
    payload = cfg.to_payload()
    payload["target_config_path"] = str(written)
    payload["ok"] = True
    payload["result"] = "PASS_TARGET_CONFIG_WRITTEN"
    payload["file_upload_attempted"] = False
    payload["chatgpt_submit_performed"] = False
    payload["conversation_text_logged"] = False
    payload["selenium_used"] = False
    payload["webdriver_used"] = False
    payload["browser_dom_automation_used"] = False

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("PATCHOPS CHATGPT COPILOT TARGET CONFIG")
        print("=====================================")
        print("TARGET_CONFIG_WRITTEN: " + str(written))
        print("TARGET_URL_REDACTED: " + str(payload.get("target_url_redacted", "")))
        print("TARGET_URL_SHA256: " + str(payload.get("target_url_sha256", "")))
        print("Result                : PASS_TARGET_CONFIG_WRITTEN")
        print(f"Target Config Path    : {written}")
        print(f"Target URL Redacted   : {payload.get('target_url_redacted')}")
        print(f"Mode                  : {payload.get('mode')}")
        print(f"Browser               : {payload.get('browser')}")
        print("File Upload Attempted : false")
        print("ChatGPT Submit        : false")
        print("Selenium Used         : false")
        print("WebDriver Used        : false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
