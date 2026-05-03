from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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

CONTROLLED_FIXTURE_BYTES = b"L24.7 controlled candidate fixture for first SHA-256 proof only. No archive open.\n"


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
    expected_sha256 = hashlib.sha256(CONTROLLED_FIXTURE_BYTES).hexdigest()

    default_payload = proof.build_real_archive_candidate_first_controlled_hash_proof(root)
    authorized_payload = proof.build_real_archive_candidate_first_controlled_hash_proof(
        root,
        allow_real_archive_candidate_hash_proof=True,
        authorization_token=proof.REQUIRED_REAL_ARCHIVE_CANDIDATE_HASH_PROOF_TOKEN,
        candidate_archive_path=str(candidate),
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_candidate_first_controlled_hash_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_candidate_first_controlled_hash_proof.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled candidate fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("real_archive_candidate_path_hash_performed") is False, "default should not hash", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L24.7", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l24_06_summary", {}).get("ok") is True, "L24.6 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l24_06_summary", {}).get("future_hash_authorized") is True, "L24.6 future hash authorization missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_06_summary", {}).get("hash_performed") is False, "L24.6 must not have performed hash", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_hash_allowed") is True, "hash allowed should be true", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_hash_performed") is True, "hash performed should be true", authorized_payload)
    _assert(authorized_payload.get("downloaded_file_bytes_read") is True, "bytes should be read for hash", authorized_payload)
    _assert(authorized_payload.get("downloaded_file_hash_performed") is True, "downloaded file hash marker should be true", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_sha256_read") is True, "sha256 marker should be true", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_sha256") == expected_sha256, "sha256 digest mismatch", authorized_payload)
    _assert(isinstance(authorized_payload.get("real_archive_candidate_bytes_read_count"), int) and authorized_payload.get("real_archive_candidate_bytes_read_count") == len(CONTROLLED_FIXTURE_BYTES), "byte count mismatch", authorized_payload)
    _assert(authorized_payload.get("candidate_hash_scope") == "controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open", "wrong hash scope", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_opened") is False, "candidate archive must not be opened", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listed") is False, "candidate archive must not be listed", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "candidate archive must not be extracted", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_archive_open_permission_added_by_l24_7") is True, "L24.7 should add no archive-open permission", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l24_7") is True, "L24.7 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l24_7") is True, "L24.7 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden optional/archive imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert("read only that controlled fixture's file bytes for SHA-256 hashing" in doc_text, "doc missing controlled hash boundary", authorized_payload)
    _assert("Candidate archive is not opened as an archive" in doc_text, "doc missing no archive open boundary", authorized_payload)
    _assert("No archive member-byte read" in doc_text, "doc missing no member-byte boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/real-archive-open/archive-list/archive-extract/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L24.7",
        "fixture_refreshed": True,
        "default_hash_performed": default_payload.get("real_archive_candidate_path_hash_performed"),
        "source_l24_06_ok": authorized_payload.get("source_l24_06_summary", {}).get("ok"),
        "source_l24_06_future_authorized": authorized_payload.get("source_l24_06_summary", {}).get("future_hash_authorized"),
        "hash_allowed": authorized_payload.get("real_archive_candidate_path_hash_allowed"),
        "hash_performed": authorized_payload.get("real_archive_candidate_path_hash_performed"),
        "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
        "downloaded_file_hash_performed": authorized_payload.get("downloaded_file_hash_performed"),
        "sha256_read": authorized_payload.get("real_archive_candidate_sha256_read"),
        "sha256_matches_expected": authorized_payload.get("real_archive_candidate_sha256") == expected_sha256,
        "bytes_read_count": authorized_payload.get("real_archive_candidate_bytes_read_count"),
        "hash_scope": authorized_payload.get("candidate_hash_scope"),
        "candidate_archive_opened": authorized_payload.get("real_archive_candidate_opened"),
        "candidate_archive_listed": authorized_payload.get("real_archive_candidate_listed"),
        "candidate_archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L24.7 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
