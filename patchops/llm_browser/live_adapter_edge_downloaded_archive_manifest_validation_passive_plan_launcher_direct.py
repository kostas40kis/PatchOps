
"""L22.3b passive manifest-validation plan checkpoint.

Launcher-direct repair after L22.3/L22.3a hangs. This module is intentionally
readback-only and does not read manifests, extract archives, read archive member
bytes, start a browser, paste, send, or run packages.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import json

PATCH = "L22.3b"
NAME = "L22.3b Microsoft Edge downloaded-archive manifest validation passive plan checkpoint"
NEXT_PATCH = "L22.4 Microsoft Edge downloaded-archive manifest validation controlled authorization gate"


def build_manifest_validation_passive_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source_l22_1e = root / "patchops" / "llm_browser" / "live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_apply_bypass.py"
    source_l22_2 = root / "patchops" / "llm_browser" / "live_adapter_edge_downloaded_archive_manifest_validation_cli_readback_apply_bypass.py"
    return {
        "ok": source_l22_1e.exists() and source_l22_2.exists(),
        "patch": PATCH,
        "name": NAME,
        "source_l22_1e_marker_present": source_l22_1e.exists(),
        "source_l22_2_cli_readback_present": source_l22_2.exists(),
        "manifest_validation_passive_plan_checkpoint": True,
        "manifest_validation_execution_allowed": False,
        "manifest_validation_active": False,
        "manifest_validation_performed": False,
        "downloaded_manifest_read": False,
        "archive_extracted": False,
        "downloaded_archive_extracted": False,
        "archive_member_bytes_read": False,
        "member_bytes_read": False,
        "browser_started": False,
        "edge_process_started": False,
        "chatgpt_url_opened": False,
        "pasteback_workflow_active": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "package_run": False,
        "no_manifest_read": True,
        "no_archive_extraction": True,
        "no_member_byte_read": True,
        "no_browser_activity": True,
        "no_pasteback": True,
        "no_package_run": True,
        "next_patch": NEXT_PATCH,
        "plan": [
            {
                "step": 1,
                "name": "confirm_l22_1e_and_l22_2_markers_exist",
                "status": "planned_not_executed",
                "side_effect": False,
            },
            {
                "step": 2,
                "name": "define_future_manifest_presence_readback_without_reading_manifest",
                "status": "planned_not_executed",
                "manifest_read": False,
                "side_effect": False,
            },
            {
                "step": 3,
                "name": "keep_manifest_read_archive_extract_member_byte_read_package_run_separately_gated",
                "status": "planned_not_executed",
                "manifest_read": False,
                "archive_extract": False,
                "member_byte_read": False,
                "package_run": False,
                "side_effect": False,
            },
        ],
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_manifest_validation_passive_plan(args.repo_root)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(f"{NAME}\nStatus: {'PASS' if payload['ok'] else 'FAIL'}\nNext: {NEXT_PATCH}")
    return 0 if payload.get("ok") else 1

if __name__ == "__main__":
    raise SystemExit(main())
