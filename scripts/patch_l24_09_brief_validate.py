from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_metadata_hash_final_acceptance_marker as marker
from patchops.llm_browser import live_adapter_edge_real_archive_candidate_first_controlled_hash_proof as proof

FALSE_FIELDS = (
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "download_workflow_active",
    "download_workflow_execution_allowed",
    "real_browser_download_active",
    "browser_started",
    "edge_process_started",
    "browser_session_created",
    "selenium_imported",
    "cdp_used",
    "dom_scraping_used",
    "page_inspection_performed",
    "conversation_text_read",
    "prompt_text_extracted",
    "chatgpt_url_opened",
    "pasteback_workflow_active",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "package_run",
    "localhost_server_started",
    "browser_extension_used",
    "git_commit_performed",
    "git_push_performed",
)

FORBIDDEN_IMPORT_SNIPPETS = (
    "import selenium",
    "from selenium",
    "import webdriver_manager",
    "from webdriver_manager",
    "import pyperclip",
    "from pyperclip",
    "import psutil",
    "from psutil",
    "import zipfile",
    "from zipfile",
)

CONTROLLED_FIXTURE_BYTES = b"L24.9 controlled candidate fixture for final metadata/hash marker only. No archive open.\n"


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _refresh_controlled_candidate_fixture(root: Path) -> Path:
    candidate = root / proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(CONTROLLED_FIXTURE_BYTES)
    return candidate


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = _refresh_controlled_candidate_fixture(root)
    payload = marker.build_metadata_hash_final_acceptance_marker(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_candidate_metadata_hash_final_acceptance_marker.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_candidate_metadata_hash_final_acceptance_marker.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    false_errors = _false_field_errors(payload)

    _assert(candidate.exists(), "controlled candidate fixture missing", payload)
    _assert(payload.get("ok") is True, "final marker payload is not ok", payload)
    _assert(payload.get("patch") == "L24.9", "wrong patch marker", payload)
    _assert(payload.get("final_metadata_hash_acceptance_marker") is True, "final marker missing", payload)
    _assert(payload.get("l24_metadata_hash_stream_complete") is True, "L24 completion missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l24_08_summary", {}).get("ok") is True, "L24.8 source not ok", payload)
    _assert(payload.get("source_l24_08_summary", {}).get("broad_checkpoint") is True, "L24.8 broad checkpoint missing", payload)
    _assert(payload.get("source_l24_08_summary", {}).get("hash_ladder_complete") is True, "L24.8 hash ladder completion missing", payload)
    _assert(payload.get("source_l24_08_summary", {}).get("authorized_hash_performed") is True, "L24.8 authorized hash proof missing", payload)
    _assert(payload.get("accepted_hash_scope") == "controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open", "wrong accepted hash scope", payload)
    _assert(payload.get("accepted_sha256_is_lower_hex") is True, "sha256 should be lowercase hex", payload)
    _assert(payload.get("real_archive_candidate_path_hash_performed") is True, "hash performed should be true", payload)
    _assert(payload.get("downloaded_file_bytes_read") is True, "bytes read should be true", payload)
    _assert(payload.get("downloaded_file_hash_performed") is True, "file hash marker should be true", payload)
    _assert(payload.get("l24_archive_open_permission_granted") is False, "archive-open permission must remain false", payload)
    _assert(payload.get("l24_archive_listing_permission_granted") is False, "archive-listing permission must remain false", payload)
    _assert(payload.get("l24_archive_extraction_permission_granted") is False, "archive-extraction permission must remain false", payload)
    _assert(payload.get("l24_archive_member_read_permission_granted") is False, "archive member read permission must remain false", payload)
    _assert(payload.get("l24_manifest_payload_read_permission_granted") is False, "manifest payload read permission must remain false", payload)
    _assert(payload.get("l24_browser_permission_granted") is False, "browser permission must remain false", payload)
    _assert(payload.get("l24_pasteback_permission_granted") is False, "pasteback permission must remain false", payload)
    _assert(payload.get("l24_package_run_permission_granted") is False, "package run permission must remain false", payload)
    _assert(payload.get("real_archive_candidate_opened") is False, "candidate archive must not be opened", payload)
    _assert(payload.get("real_archive_candidate_listed") is False, "candidate archive must not be listed", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "candidate archive must not be extracted", payload)
    _assert(payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_archive_open_permission_added_by_l24_9") is True, "L24.9 should add no archive-open permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden optional/archive imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert("L24.8 controlled hash broad checkpoint" in doc_text, "doc missing L24.8 ladder item", payload)
    _assert("L24 itself adds no archive open/list/extract/read" in doc_text, "doc missing post-L24 boundary", payload)
    _assert("Candidate archive is not opened as an archive" in doc_text, "doc missing no archive open boundary", payload)
    _assert("No archive member-byte read" in doc_text, "doc missing no member-byte read boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/real-archive-open/archive-list/archive-extract/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L24.9",
        "fixture_refreshed": True,
        "final_metadata_hash_acceptance_marker": payload.get("final_metadata_hash_acceptance_marker"),
        "l24_metadata_hash_complete": payload.get("l24_metadata_hash_stream_complete"),
        "source_l24_08_ok": payload.get("source_l24_08_summary", {}).get("ok"),
        "source_l24_08_broad_checkpoint": payload.get("source_l24_08_summary", {}).get("broad_checkpoint"),
        "source_l24_08_hash_ladder_complete": payload.get("source_l24_08_summary", {}).get("hash_ladder_complete"),
        "accepted_hash_scope": payload.get("accepted_hash_scope"),
        "hash_performed": payload.get("real_archive_candidate_path_hash_performed"),
        "bytes_read_for_hash": payload.get("downloaded_file_bytes_read"),
        "sha256_read": payload.get("real_archive_candidate_sha256_read"),
        "sha256_is_lower_hex": payload.get("accepted_sha256_is_lower_hex"),
        "archive_open_permission": payload.get("l24_archive_open_permission_granted"),
        "archive_listing_permission": payload.get("l24_archive_listing_permission_granted"),
        "archive_extraction_permission": payload.get("l24_archive_extraction_permission_granted"),
        "archive_member_read_permission": payload.get("l24_archive_member_read_permission_granted"),
        "manifest_payload_read_permission": payload.get("l24_manifest_payload_read_permission_granted"),
        "browser_permission": payload.get("l24_browser_permission_granted"),
        "pasteback_permission": payload.get("l24_pasteback_permission_granted"),
        "package_run_permission": payload.get("l24_package_run_permission_granted"),
        "candidate_archive_opened": payload.get("real_archive_candidate_opened"),
        "candidate_archive_listed": payload.get("real_archive_candidate_listed"),
        "candidate_archive_extracted": payload.get("real_archive_candidate_extracted"),
        "real_archive_manifest_read": payload.get("real_archive_manifest_read"),
        "browser_started": payload.get("browser_started"),
        "pasteback": payload.get("pasteback_workflow_active"),
        "package_run": payload.get("package_run"),
        "next_patch": payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L24.9 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
