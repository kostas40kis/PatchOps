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

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_metadata_proof as l21_05


def _ensure_fixture(repo_root: Path) -> Path:
    fixture = repo_root / l21_05.DEFAULT_CANDIDATE_RELATIVE_PATH
    fixture.parent.mkdir(parents=True, exist_ok=True)
    if not fixture.exists():
        with zipfile.ZipFile(fixture, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", "{}\n")
            zf.writestr("bundle_meta.json", "{}\n")
            zf.writestr("README.txt", "L21.5 synthetic archive fixture.\n")
            zf.writestr("content/payload.txt", "Do not read through adapter.\n")
    return fixture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L21.5 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    _ensure_fixture(repo_root)
    default_payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(repo_root, target_url=args.target_url)
    authorized_payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(
        repo_root,
        allow_archive_metadata_proof=True,
        authorization_token=l21_05.REQUIRED_ARCHIVE_METADATA_PROOF_AUTHORIZATION_TOKEN,
        candidate_path_metadata=l21_05.DEFAULT_CANDIDATE_RELATIVE_PATH,
        target_url=args.target_url,
    )
    result = authorized_payload.get("archive_metadata_validation_result") or {}
    ok = (
        default_payload.get("ok") is True
        and authorized_payload.get("ok") is True
        and default_payload.get("archive_metadata_proof_authorized") is False
        and default_payload.get("downloaded_archive_opened") is False
        and authorized_payload.get("archive_metadata_proof_authorized") is True
        and authorized_payload.get("archive_validation_performed") is True
        and authorized_payload.get("downloaded_archive_opened") is True
        and authorized_payload.get("downloaded_archive_contents_listed") is True
        and result.get("manifest_entry_detected_from_listing") is True
        and authorized_payload.get("downloaded_archive_extracted") is False
        and authorized_payload.get("downloaded_manifest_read") is False
        and authorized_payload.get("archive_member_bytes_read") is False
        and authorized_payload.get("downloaded_file_bytes_read") is False
        and authorized_payload.get("downloaded_file_stat_performed") is False
        and authorized_payload.get("downloaded_file_hash_performed") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
    )
    summary = {
        "ok": ok,
        "patch": authorized_payload.get("patch"),
        "source_patch": authorized_payload.get("source_patch"),
        "source_l21_4_controlled_authorization_gate_accepted": authorized_payload.get("source_l21_4_controlled_authorization_gate_accepted"),
        "l21_4_complete": authorized_payload.get("l21_4_complete"),
        "default_archive_metadata_proof_authorized": default_payload.get("archive_metadata_proof_authorized"),
        "authorized_archive_metadata_proof_authorized": authorized_payload.get("archive_metadata_proof_authorized"),
        "candidate_safe_for_l21_5_metadata_only_proof": (authorized_payload.get("candidate_safety") or {}).get("candidate_safe_for_l21_5_metadata_only_proof"),
        "archive_metadata_validation_performed": result.get("archive_metadata_validation_performed"),
        "archive_validation_ready": result.get("archive_validation_ready"),
        "manifest_entry_detected_from_listing": result.get("manifest_entry_detected_from_listing"),
        "archive_entry_count": result.get("archive_entry_count"),
        "archive_validation_performed": authorized_payload.get("archive_validation_performed"),
        "downloaded_archive_opened": authorized_payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": authorized_payload.get("downloaded_archive_contents_listed"),
        "downloaded_archive_extracted": authorized_payload.get("downloaded_archive_extracted"),
        "downloaded_manifest_read": authorized_payload.get("downloaded_manifest_read"),
        "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
        "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
        "downloaded_file_stat_performed": authorized_payload.get("downloaded_file_stat_performed"),
        "downloaded_file_hash_performed": authorized_payload.get("downloaded_file_hash_performed"),
        "browser_started": authorized_payload.get("browser_started"),
        "edge_process_started": authorized_payload.get("edge_process_started"),
        "chatgpt_url_opened": authorized_payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": authorized_payload.get("package_run_performed_by_adapter"),
        "missing_commands": authorized_payload.get("missing_commands"),
        "missing_doc_phrases": authorized_payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (authorized_payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": authorized_payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
