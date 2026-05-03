from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_downloaded_file_validation_cli_readback_checkpoint as l19_02


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L19.2 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    payload = l19_02.build_edge_downloaded_file_validation_cli_readback_checkpoint(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "l19_1_passive_preflight_gate_accepted": payload.get("l19_1_passive_preflight_gate_accepted"),
        "l19_1_default_compact_readback_ok": payload.get("l19_1_default_compact_readback_ok"),
        "l19_1_authorized_compact_readback_ok": payload.get("l19_1_authorized_compact_readback_ok"),
        "default_downloaded_file_validation_preflight_authorized": payload.get("default_downloaded_file_validation_preflight_authorized"),
        "authorized_downloaded_file_validation_preflight_authorized": payload.get("authorized_downloaded_file_validation_preflight_authorized"),
        "downloaded_file_validation_preflight_authorization_remains_readback_only": payload.get("downloaded_file_validation_preflight_authorization_remains_readback_only"),
        "downloaded_file_validation_execution_allowed": payload.get("downloaded_file_validation_execution_allowed"),
        "downloaded_file_validation_active": payload.get("downloaded_file_validation_active"),
        "downloaded_file_validation_performed": payload.get("downloaded_file_validation_performed"),
        "downloaded_file_exists_check_performed": payload.get("downloaded_file_exists_check_performed"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "downloaded_archive_opened": payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": payload.get("downloaded_archive_contents_listed"),
        "downloaded_manifest_read": payload.get("downloaded_manifest_read"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "avoid_nested_cli_validation_cascades": payload.get("avoid_nested_cli_validation_cascades"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
