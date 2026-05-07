from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_target import (  # noqa: E402
    BLOCKED_TARGET_CONFIG_INVALID,
    BLOCKED_TARGET_CONFIG_MISSING,
    BLOCKED_UNSUPPORTED_BROWSER,
    PASS_CHROME_TARGET_CONFIG_VALIDATED,
    default_target_config_path,
    probe_chrome_target_config,
    write_chrome_target_evidence,
)


def _resolve_config_path(raw_path: str | None, repo_root: str | None) -> Path:
    root = Path(repo_root).expanduser().resolve() if repo_root else PROJECT_ROOT
    if raw_path:
        candidate = Path(raw_path).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        return candidate.resolve()
    return default_target_config_path(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Chrome-only target config without browser launch, upload, or send.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-config", default=None)
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    config_path = _resolve_config_path(args.target_config, args.repo_root)
    evidence = probe_chrome_target_config(config_path)
    payload = evidence.to_payload()

    if args.evidence_path:
        write_chrome_target_evidence(evidence, args.evidence_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"BROWSER: {evidence.browser or ''}")
        print(f"TARGET_URL_HASH: {evidence.target_url_hash or ''}")
        print(f"REDACTED_TARGET_DISPLAY: {evidence.redacted_target_display or ''}")
        print("raw_conversation_text_logged:false")
        print("conversation_text_logged:false")
        print("file_upload_attempted:false")
        print("chatgpt_submit_performed:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("live_browser_used:false")
        print("browser_launched:false")
        if evidence.error:
            print(f"ERROR: {evidence.error}")

    if evidence.result in {
        PASS_CHROME_TARGET_CONFIG_VALIDATED,
        BLOCKED_TARGET_CONFIG_MISSING,
        BLOCKED_TARGET_CONFIG_INVALID,
        BLOCKED_UNSUPPORTED_BROWSER,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())