from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_filesystem_stat_broad_checkpoint as broad
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

CONTROLLED_FIXTURE_BYTES = b"L24.5 controlled candidate fixture for broad filesystem stat checkpoint only. No archive open.\n"


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
    payload = broad.build_real_archive_candidate_filesystem_stat_broad_checkpoint(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_candidate_filesystem_stat_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_candidate_filesystem_stat_broad_checkpoint.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    false_errors = _false_field_errors(payload)

    _assert(candidate.exists(), "controlled candidate fixture missing", payload)
    _assert(payload.get("ok") is True, "broad checkpoint payload is not ok", payload)
    _assert(payload.get("patch") == "L24.5", "wrong patch marker", payload)
    _assert(payload.get("broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("filesystem_stat_ladder_checkpoint") is True, "filesystem stat ladder marker missing", payload)
    _assert(payload.get("l24_candidate_stat_ladder_complete") is True, "stat ladder completion marker missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l24_04_default_summary", {}).get("stat_performed") is False, "default L24.4 should remain passive", payload)
    _assert(payload.get("source_l24_04_authorized_summary", {}).get("stat_performed") is True, "authorized L24.4 stat proof missing", payload)
    _assert(payload.get("source_l24_04_authorized_summary", {}).get("candidate_exists") is True, "candidate existence missing", payload)
    _assert(payload.get("source_l24_04_authorized_summary", {}).get("candidate_is_file") is True, "candidate file marker missing", payload)
    _assert(payload.get("source_l24_04_authorized_summary", {}).get("candidate_size_read") is True, "candidate size marker missing", payload)
    _assert(isinstance(payload.get("source_l24_04_authorized_summary", {}).get("candidate_size_bytes"), int) and payload.get("source_l24_04_authorized_summary", {}).get("candidate_size_bytes") > 0, "candidate size should be positive", payload)
    _assert(payload.get("source_l24_04_authorized_summary", {}).get("candidate_suffix") == ".zip", "candidate suffix should be .zip", payload)
    _assert(payload.get("source_l24_04_authorized_summary", {}).get("candidate_mtime_read") is True, "candidate mtime marker missing", payload)
    _assert(payload.get("accepted_stat_scope") == "controlled_runtime_candidate_filesystem_metadata_only", "wrong accepted scope", payload)
    _assert(payload.get("real_archive_candidate_path_stat_performed") is True, "stat performed should be true", payload)
    _assert(payload.get("real_archive_candidate_path_hash_performed") is False, "hash must remain false", payload)
    _assert(payload.get("downloaded_file_bytes_read") is False, "file bytes must remain false", payload)
    _assert(payload.get("real_archive_candidate_opened") is False, "candidate archive must not be opened", payload)
    _assert(payload.get("real_archive_candidate_listed") is False, "candidate archive must not be listed", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "candidate archive must not be extracted", payload)
    _assert(payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_hash_or_archive_open_permission_added_by_l24_5") is True, "L24.5 should add no hash/open permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden optional/read/hash imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert("L24.1 real downloaded-archive candidate authorization gate" in doc_text, "doc missing L24.1 ladder item", payload)
    _assert("L24.4 controlled runtime candidate filesystem stat proof" in doc_text, "doc missing L24.4 ladder item", payload)
    _assert("Candidate filesystem stat is metadata-only" in doc_text, "doc missing metadata-only boundary", payload)
    _assert("Candidate path hash is not performed" in doc_text, "doc missing no hash boundary", payload)
    _assert("Downloaded file bytes are not read" in doc_text, "doc missing no bytes boundary", payload)
    _assert("Candidate archive is not opened" in doc_text, "doc missing no archive open boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/real-archive-open/archive-list/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L24.5",
        "fixture_refreshed": True,
        "broad_checkpoint": payload.get("broad_checkpoint"),
        "ladder_complete": payload.get("l24_candidate_stat_ladder_complete"),
        "failed_checks": payload.get("failed_checks"),
        "default_stat_performed": payload.get("source_l24_04_default_summary", {}).get("stat_performed"),
        "authorized_stat_performed": payload.get("source_l24_04_authorized_summary", {}).get("stat_performed"),
        "candidate_exists": payload.get("source_l24_04_authorized_summary", {}).get("candidate_exists"),
        "candidate_is_file": payload.get("source_l24_04_authorized_summary", {}).get("candidate_is_file"),
        "candidate_size_read": payload.get("source_l24_04_authorized_summary", {}).get("candidate_size_read"),
        "candidate_size_bytes": payload.get("source_l24_04_authorized_summary", {}).get("candidate_size_bytes"),
        "candidate_suffix": payload.get("source_l24_04_authorized_summary", {}).get("candidate_suffix"),
        "candidate_mtime_read": payload.get("source_l24_04_authorized_summary", {}).get("candidate_mtime_read"),
        "accepted_scope": payload.get("accepted_stat_scope"),
        "hash_performed": payload.get("real_archive_candidate_path_hash_performed"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
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
    parser = argparse.ArgumentParser(description="L24.5 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
