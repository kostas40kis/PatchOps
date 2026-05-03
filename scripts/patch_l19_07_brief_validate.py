from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_downloaded_file_validation_final_acceptance_marker as l19_07


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L19.7 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    payload = l19_07.build_edge_downloaded_file_validation_final_acceptance_marker(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "source_l19_6_broad_checkpoint_accepted": payload.get("source_l19_6_broad_checkpoint_accepted"),
        "l19_1_through_l19_6_remain_accepted": payload.get("l19_1_through_l19_6_remain_accepted"),
        "l19_downloaded_file_validation_stream_complete": payload.get("l19_downloaded_file_validation_stream_complete"),
        "downloaded_file_validation_stream_completion_is_metadata_readback_only": payload.get("downloaded_file_validation_stream_completion_is_metadata_readback_only"),
        "metadata_only_downloaded_file_validation_proof_accepted": payload.get("metadata_only_downloaded_file_validation_proof_accepted"),
        "downloaded_file_metadata_validation_ready_from_positive_metadata": payload.get("downloaded_file_metadata_validation_ready_from_positive_metadata"),
        "real_filesystem_validation_remains_inactive": payload.get("real_filesystem_validation_remains_inactive"),
        "real_file_existence_check_remains_inactive": payload.get("real_file_existence_check_remains_inactive"),
        "real_file_stat_remains_inactive": payload.get("real_file_stat_remains_inactive"),
        "real_file_hash_remains_inactive": payload.get("real_file_hash_remains_inactive"),
        "archive_validation_remains_inactive": payload.get("archive_validation_remains_inactive"),
        "real_filesystem_validation_active": payload.get("real_filesystem_validation_active"),
        "real_file_existence_check_active": payload.get("real_file_existence_check_active"),
        "real_file_stat_active": payload.get("real_file_stat_active"),
        "real_file_hash_active": payload.get("real_file_hash_active"),
        "archive_validation_active": payload.get("archive_validation_active"),
        "downloaded_file_validation_execution_allowed": payload.get("downloaded_file_validation_execution_allowed"),
        "downloaded_file_validation_active": payload.get("downloaded_file_validation_active"),
        "downloaded_file_validation_performed": payload.get("downloaded_file_validation_performed"),
        "downloaded_file_exists_check_performed": payload.get("downloaded_file_exists_check_performed"),
        "downloaded_file_stat_performed": payload.get("downloaded_file_stat_performed"),
        "downloaded_file_hash_performed": payload.get("downloaded_file_hash_performed"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "downloaded_archive_opened": payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": payload.get("downloaded_archive_contents_listed"),
        "downloaded_archive_extracted": payload.get("downloaded_archive_extracted"),
        "downloaded_manifest_read": payload.get("downloaded_manifest_read"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
        "remaining_l19_patches": payload.get("remaining_l19_patches"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
