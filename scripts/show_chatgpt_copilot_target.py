from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.config import ConfigValidationError, load_config, resolve_config_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show the configured PatchOps ChatGPT Co-Pilot target without printing the raw URL.")
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT))
    parser.add_argument("--target-config", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = resolve_config_path(args.target_config, repo_root=args.repo_root)
    try:
        cfg = load_config(config_path)
    except (ConfigValidationError, OSError, ValueError) as exc:
        print("TARGET_CONFIG_STATUS: MISSING_OR_INVALID")
        print(f"TARGET_CONFIG_PATH: {config_path}")
        print(f"ERROR: {exc}")
        print("RAW_TARGET_URL_PRINTED: false")
        return 2

    payload = cfg.to_payload(include_target_url=False)
    print("TARGET_CONFIG_STATUS: OK")
    print(f"TARGET_CONFIG_PATH: {config_path}")
    print(f"TARGET_URL_REDACTED: {payload['target_url_redacted']}")
    print(f"TARGET_URL_SHA256: {payload['target_url_sha256']}")
    print(f"BROWSER: {payload['browser']}")
    print(f"MODE: {payload['mode']}")
    print(f"ALLOW_UPLOAD_DEFAULT: {str(payload['allow_upload_default']).lower()}")
    print(f"ALLOW_SEND_DEFAULT: {str(payload['allow_send_default']).lower()}")
    print("RAW_TARGET_URL_PRINTED: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
