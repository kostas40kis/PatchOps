from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_filesystem_stat_proof as proof

FALSE_FIELDS = (
    "real_archive_candidate_path_hash_allowed",
    "real_archive_candidate_path_hash_performed",
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_hash_performed",
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
    "open(",
    ".read(",
    "read_bytes",
    "hashlib",
)

CONTROLLED_FIXTURE_BYTES = b"L24.4 controlled candidate fixture for filesystem stat only. No archive open in this proof.\n"


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

    default_payload = proof.build_real_archive_candidate_filesystem_stat_proof(root)
    authorized_payload = proof.build_real_archive_candidate_filesystem_stat_proof(
        root,
        allow_real_archive_candidate_stat_proof=True,
        authorization_token=proof.REQUIRED_REAL_ARCHIVE_CANDIDATE_STAT_PROOF_TOKEN,
        candidate_archive_path=str(candidate),
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_candidate_filesystem_stat_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_candidate_filesystem_stat_proof.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled candidate fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("real_archive_candidate_path_stat_performed") is False, "default should not stat", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L24.4", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l24_03_summary", {}).get("ok") is True, "L24.3 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l24_03_summary", {}).get("future_stat_authorized") is True, "L24.3 future stat authorization missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_03_summary", {}).get("stat_performed") is False, "L24.3 must not have performed stat", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_stat_allowed") is True, "stat allowed should be true", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_stat_performed") is True, "stat performed should be true", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_exists") is True, "candidate should exist", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_is_file") is True, "candidate should be file", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_size_bytes_read") is True, "candidate size should be read", authorized_payload)
    _assert(isinstance(authorized_payload.get("real_archive_candidate_size_bytes"), int) and authorized_payload.get("real_archive_candidate_size_bytes") > 0, "candidate size should be positive", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_suffix_checked_on_filesystem") is True, "suffix should be checked", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_suffix") == ".zip", "suffix should be .zip", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_mtime_read") is True, "mtime should be read", authorized_payload)
    _assert(authorized_payload.get("candidate_stat_scope") == "controlled_runtime_candidate_filesystem_metadata_only", "wrong stat scope", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_hash_performed") is False, "hash must not be performed", authorized_payload)
    _assert(authorized_payload.get("downloaded_file_bytes_read") is False, "file bytes must not be read", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_opened") is False, "candidate archive must not be opened", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listed") is False, "candidate archive must not be listed", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "candidate archive must not be extracted", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_hash_or_archive_open_permission_added_by_l24_4") is True, "L24.4 should add no hash/open permission", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l24_4") is True, "L24.4 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l24_4") is True, "L24.4 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden optional/read/hash imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert("controlled runtime candidate fixture" in doc_text, "doc missing controlled fixture boundary", authorized_payload)
    _assert("Candidate path hash is not performed" in doc_text, "doc missing no hash boundary", authorized_payload)
    _assert("Downloaded file bytes are not read" in doc_text, "doc missing no bytes-read boundary", authorized_payload)
    _assert("Candidate archive is not opened" in doc_text, "doc missing no archive open boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/real-archive-open/archive-list/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L24.4",
        "fixture_refreshed": True,
        "default_stat_performed": default_payload.get("real_archive_candidate_path_stat_performed"),
        "source_l24_03_ok": authorized_payload.get("source_l24_03_summary", {}).get("ok"),
        "source_l24_03_future_authorized": authorized_payload.get("source_l24_03_summary", {}).get("future_stat_authorized"),
        "stat_allowed": authorized_payload.get("real_archive_candidate_path_stat_allowed"),
        "stat_performed": authorized_payload.get("real_archive_candidate_path_stat_performed"),
        "candidate_exists": authorized_payload.get("real_archive_candidate_exists"),
        "candidate_is_file": authorized_payload.get("real_archive_candidate_is_file"),
        "candidate_size_read": authorized_payload.get("real_archive_candidate_size_bytes_read"),
        "candidate_size_bytes": authorized_payload.get("real_archive_candidate_size_bytes"),
        "candidate_suffix_checked": authorized_payload.get("real_archive_candidate_suffix_checked_on_filesystem"),
        "candidate_suffix": authorized_payload.get("real_archive_candidate_suffix"),
        "candidate_mtime_read": authorized_payload.get("real_archive_candidate_mtime_read"),
        "stat_scope": authorized_payload.get("candidate_stat_scope"),
        "hash_performed": authorized_payload.get("real_archive_candidate_path_hash_performed"),
        "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
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
    parser = argparse.ArgumentParser(description="L24.4 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
