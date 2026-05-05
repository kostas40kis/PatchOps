from __future__ import annotations

import argparse
from pathlib import Path

from patchops.chatgpt_uploader.target_readiness import probe_target_readiness


DEFAULT_TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f9e01d-f588-838f-b2c8-3e3f0f0153cf"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the U0.2 ChatGPT uploader target readiness probe.")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--output-dir", default="data/runtime/u0_02_chatgpt_uploader_target_readiness_probe")
    parser.add_argument("--allow-pywinauto-probe", action="store_true")
    args = parser.parse_args()

    result = probe_target_readiness(
        target_url=args.target_url,
        output_dir=Path(args.output_dir),
        allow_pywinauto_probe=bool(args.allow_pywinauto_probe),
    )
    print(f"u0_02_target_readiness_result:{result.result}")
    print(f"safe_target_url:{result.safe_target_url}")
    print(f"file_upload_attempted:{result.file_upload_attempted}")
    print(f"chatgpt_submit_performed:{result.chatgpt_submit_performed}")
    print(f"selenium_used:{result.selenium_used}")
    return 0 if result.result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
