from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint as l21_02


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L21.2 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    payload = l21_02.build_edge_downloaded_archive_validation_cli_readback_checkpoint(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "l21_1_passive_preflight_gate_accepted": payload.get("l21_1_passive_preflight_gate_accepted"),
        "l21_1_default_archive_preflight_readback_ok": payload.get("l21_1_default_archive_preflight_readback_ok"),
        "l21_1_authorized_archive_preflight_readback_ok": payload.get("l21_1_authorized_archive_preflight_readback_ok"),
        "default_archive_validation_preflight_authorized": payload.get("default_archive_validation_preflight_authorized"),
        "authorized_archive_validation_preflight_authorized": payload.get("authorized_archive_validation_preflight_authorized"),
        "archive_validation_preflight_authorization_remains_readback_only": payload.get("archive_validation_preflight_authorization_remains_readback_only"),
        "archive_validation_execution_allowed": payload.get("archive_validation_execution_allowed"),
        "archive_validation_active": payload.get("archive_validation_active"),
        "archive_validation_performed": payload.get("archive_validation_performed"),
        "downloaded_archive_opened": payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": payload.get("downloaded_archive_contents_listed"),
        "downloaded_archive_extracted": payload.get("downloaded_archive_extracted"),
        "downloaded_manifest_read": payload.get("downloaded_manifest_read"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "downloaded_file_stat_performed": payload.get("downloaded_file_stat_performed"),
        "downloaded_file_hash_performed": payload.get("downloaded_file_hash_performed"),
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
