from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_hash_broad_checkpoint as broad
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

CONTROLLED_FIXTURE_BYTES = b"L24.8 controlled candidate fixture for hash broad checkpoint only. No archive open.\n"


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
    payload = broad.build_real_archive_candidate_hash_broad_checkpoint(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_candidate_hash_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_candidate_hash_broad_checkpoint.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    false_errors = _false_field_errors(payload)

    _assert(candidate.exists(), "controlled candidate fixture missing", payload)
    _assert(payload.get("ok") is True, "hash broad checkpoint payload is not ok", payload)
    _assert(payload.get("patch") == "L24.8", "wrong patch marker", payload)
    _assert(payload.get("broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("hash_ladder_checkpoint") is True, "hash ladder marker missing", payload)
    _assert(payload.get("l24_candidate_hash_ladder_complete") is True, "hash ladder completion marker missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l24_07_default_summary", {}).get("hash_performed") is False, "default L24.7 should remain passive", payload)
    _assert(payload.get("source_l24_07_authorized_summary", {}).get("hash_performed") is True, "authorized L24.7 hash proof missing", payload)
    _assert(payload.get("source_l24_07_authorized_summary", {}).get("downloaded_file_bytes_read") is True, "L24.7 byte-read-for-hash missing", payload)
    _assert(payload.get("source_l24_07_authorized_summary", {}).get("downloaded_file_hash_performed") is True, "L24.7 hash marker missing", payload)
    _assert(payload.get("source_l24_07_authorized_summary", {}).get("sha256_read") is True, "L24.7 sha256 marker missing", payload)
    _assert(isinstance(payload.get("source_l24_07_authorized_summary", {}).get("bytes_read_count"), int) and payload.get("source_l24_07_authorized_summary", {}).get("bytes_read_count") > 0, "L24.7 byte count missing", payload)
    _assert(payload.get("accepted_hash_scope") == "controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open", "wrong accepted hash scope", payload)
    _assert(payload.get("accepted_sha256_is_lower_hex") is True, "sha256 should be lowercase hex", payload)
    _assert(payload.get("real_archive_candidate_path_hash_performed") is True, "hash performed should be true", payload)
    _assert(payload.get("downloaded_file_bytes_read") is True, "bytes read should be true", payload)
    _assert(payload.get("downloaded_file_hash_performed") is True, "hash performed marker should be true", payload)
    _assert(payload.get("real_archive_candidate_opened") is False, "candidate archive must not be opened", payload)
    _assert(payload.get("real_archive_candidate_listed") is False, "candidate archive must not be listed", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "candidate archive must not be extracted", payload)
    _assert(payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_archive_open_permission_added_by_l24_8") is True, "L24.8 should add no archive-open permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden optional/archive imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert("L24.6 candidate hash authorization gate" in doc_text, "doc missing L24.6 ladder item", payload)
    _assert("L24.7 first controlled SHA-256 proof" in doc_text, "doc missing L24.7 ladder item", payload)
    _assert("Candidate archive is not opened as an archive" in doc_text, "doc missing no archive open boundary", payload)
    _assert("No archive member-byte read" in doc_text, "doc missing no archive member-byte boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/real-archive-open/archive-list/archive-extract/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L24.8",
        "fixture_refreshed": True,
        "broad_checkpoint": payload.get("broad_checkpoint"),
        "hash_ladder_complete": payload.get("l24_candidate_hash_ladder_complete"),
        "failed_checks": payload.get("failed_checks"),
        "default_hash_performed": payload.get("source_l24_07_default_summary", {}).get("hash_performed"),
        "authorized_hash_performed": payload.get("source_l24_07_authorized_summary", {}).get("hash_performed"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "downloaded_file_hash_performed": payload.get("downloaded_file_hash_performed"),
        "sha256_read": payload.get("real_archive_candidate_sha256_read"),
        "sha256_is_lower_hex": payload.get("accepted_sha256_is_lower_hex"),
        "bytes_read_count": payload.get("accepted_bytes_read_count"),
        "accepted_hash_scope": payload.get("accepted_hash_scope"),
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
    parser = argparse.ArgumentParser(description="L24.8 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
