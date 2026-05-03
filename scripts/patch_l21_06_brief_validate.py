from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_broad_checkpoint as l21_06


def _ensure_fixture(repo_root: Path) -> Path:
    fixture = repo_root / l21_06.DEFAULT_CANDIDATE_RELATIVE_PATH
    fixture.parent.mkdir(parents=True, exist_ok=True)
    if not fixture.exists():
        with zipfile.ZipFile(fixture, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", "{}\n")
            zf.writestr("bundle_meta.json", "{}\n")
            zf.writestr("README.txt", "L21.6 synthetic archive fixture.\n")
            zf.writestr("content/payload.txt", "Do not read through adapter.\n")
    return fixture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L21.6 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    _ensure_fixture(repo_root)
    payload = l21_06.build_edge_downloaded_archive_validation_broad_checkpoint(
        repo_root,
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "l21_1_through_l21_5_remain_accepted": payload.get("l21_1_through_l21_5_remain_accepted"),
        "archive_metadata_only_validation_proof_remains_accepted": payload.get("archive_metadata_only_validation_proof_remains_accepted"),
        "default_archive_metadata_proof_readback_remains_passive": payload.get("default_archive_metadata_proof_readback_remains_passive"),
        "authorized_archive_metadata_proof_readback_remains_metadata_only": payload.get("authorized_archive_metadata_proof_readback_remains_metadata_only"),
        "unsafe_archive_candidate_remains_rejected_without_archive_access": payload.get("unsafe_archive_candidate_remains_rejected_without_archive_access"),
        "only_synthetic_patchops_runtime_archive_metadata_listing_is_allowed": payload.get("only_synthetic_patchops_runtime_archive_metadata_listing_is_allowed"),
        "archive_validation_scope": payload.get("archive_validation_scope"),
        "archive_validation_performed": payload.get("archive_validation_performed"),
        "downloaded_archive_opened": payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": payload.get("downloaded_archive_contents_listed"),
        "archive_entry_count": payload.get("archive_entry_count"),
        "downloaded_archive_extracted": payload.get("downloaded_archive_extracted"),
        "downloaded_manifest_read": payload.get("downloaded_manifest_read"),
        "archive_member_bytes_read": payload.get("archive_member_bytes_read"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "downloaded_file_stat_performed": payload.get("downloaded_file_stat_performed"),
        "downloaded_file_hash_performed": payload.get("downloaded_file_hash_performed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
