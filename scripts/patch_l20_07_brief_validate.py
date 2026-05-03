from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_final_acceptance_marker as l20_07
from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_broad_checkpoint as l20_06


def _ensure_fixture(repo_root: Path) -> Path:
    fixture = repo_root / l20_06.DEFAULT_CANDIDATE_RELATIVE_PATH
    fixture.parent.mkdir(parents=True, exist_ok=True)
    if not fixture.exists():
        fixture.write_text("L20.7 synthetic existence-only fixture. Do not read contents.\n", encoding="utf-8")
    return fixture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L20.7 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    _ensure_fixture(repo_root)
    payload = l20_07.build_edge_downloaded_file_filesystem_validation_final_acceptance_marker(
        repo_root,
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "source_l20_6_broad_checkpoint_accepted": payload.get("source_l20_6_broad_checkpoint_accepted"),
        "l20_1_through_l20_6_remain_accepted": payload.get("l20_1_through_l20_6_remain_accepted"),
        "l20_downloaded_file_filesystem_validation_stream_complete": payload.get("l20_downloaded_file_filesystem_validation_stream_complete"),
        "l20_completion_means_synthetic_fixture_existence_only_validation": payload.get("l20_completion_means_synthetic_fixture_existence_only_validation"),
        "existence_only_filesystem_validation_proof_remains_accepted": payload.get("existence_only_filesystem_validation_proof_remains_accepted"),
        "only_synthetic_patchops_runtime_fixture_existence_check_is_accepted": payload.get("only_synthetic_patchops_runtime_fixture_existence_check_is_accepted"),
        "filesystem_validation_scope": payload.get("filesystem_validation_scope"),
        "filesystem_validation_performed": payload.get("filesystem_validation_performed"),
        "real_file_exists_check_performed": payload.get("real_file_exists_check_performed"),
        "downloaded_file_exists_check_performed": payload.get("downloaded_file_exists_check_performed"),
        "real_file_stat_performed": payload.get("real_file_stat_performed"),
        "real_file_hash_performed": payload.get("real_file_hash_performed"),
        "downloaded_file_stat_performed": payload.get("downloaded_file_stat_performed"),
        "downloaded_file_hash_performed": payload.get("downloaded_file_hash_performed"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "downloaded_archive_opened": payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": payload.get("downloaded_archive_contents_listed"),
        "downloaded_archive_extracted": payload.get("downloaded_archive_extracted"),
        "downloaded_manifest_read": payload.get("downloaded_manifest_read"),
        "archive_validation_remains_separate_future_stream": payload.get("archive_validation_remains_separate_future_stream"),
        "hash_validation_remains_separate_future_stream": payload.get("hash_validation_remains_separate_future_stream"),
        "file_byte_read_remains_separate_future_stream": payload.get("file_byte_read_remains_separate_future_stream"),
        "manifest_read_remains_separate_future_stream": payload.get("manifest_read_remains_separate_future_stream"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
        "remaining_l20_patches": payload.get("remaining_l20_patches"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
