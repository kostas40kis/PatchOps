from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_hash_authorization_gate as gate
from patchops.llm_browser import live_adapter_edge_real_archive_candidate_filesystem_stat_proof as stat_proof

FALSE_FIELDS = (
    "real_archive_candidate_path_hash_allowed",
    "real_archive_candidate_path_hash_performed",
    "real_archive_candidate_sha256_read",
    "real_archive_candidate_sha256",
    "downloaded_file_bytes_read",
    "downloaded_file_hash_performed",
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
    "open(",
    ".read(",
    "read_bytes",
    "hashlib",
)

CONTROLLED_FIXTURE_BYTES = b"L24.6 controlled candidate fixture for hash authorization readback only. No hashing in this patch.\n"


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _refresh_controlled_candidate_fixture(root: Path) -> Path:
    candidate = root / stat_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(CONTROLLED_FIXTURE_BYTES)
    return candidate


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = _refresh_controlled_candidate_fixture(root)
    default_payload = gate.build_real_archive_candidate_hash_authorization_gate(root)
    authorized_payload = gate.build_real_archive_candidate_hash_authorization_gate(
        root,
        allow_real_archive_candidate_hash_authorization=True,
        authorization_token=gate.REQUIRED_REAL_ARCHIVE_CANDIDATE_HASH_AUTHORIZATION_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_candidate_hash_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_candidate_hash_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled candidate fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("real_archive_candidate_hash_authorization_granted_for_future_patch") is False, "default should not grant future hash auth", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L24.6", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l24_05_summary", {}).get("ok") is True, "L24.5 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l24_05_summary", {}).get("broad_checkpoint") is True, "L24.5 broad checkpoint missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_05_summary", {}).get("ladder_complete") is True, "L24.5 ladder completion missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_05_summary", {}).get("accepted_stat_scope") == "controlled_runtime_candidate_filesystem_metadata_only", "L24.5 accepted scope wrong", authorized_payload)
    _assert(authorized_payload.get("source_l24_05_summary", {}).get("stat_performed") is True, "L24.5 stat proof missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_05_summary", {}).get("hash_performed") is False, "L24.5 hash should be false", authorized_payload)
    _assert(authorized_payload.get("source_l24_05_summary", {}).get("downloaded_file_bytes_read") is False, "L24.5 bytes read should be false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_hash_authorization_granted_for_future_patch") is True, "future hash auth should be granted by token", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_hash_allowed") is False, "hash allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_hash_performed") is False, "hash performed must remain false", authorized_payload)
    _assert(authorized_payload.get("downloaded_file_bytes_read") is False, "downloaded bytes read must remain false", authorized_payload)
    _assert(authorized_payload.get("downloaded_file_hash_performed") is False, "downloaded hash performed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_opened") is False, "candidate archive must not be opened", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listed") is False, "candidate archive must not be listed", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "candidate archive must not be extracted", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_real_archive_candidate_hash_execution_added_by_l24_6") is True, "L24.6 should add no hash execution", authorized_payload)
    _assert(authorized_payload.get("no_file_byte_read_permission_added_by_l24_6") is True, "L24.6 should add no byte-read permission", authorized_payload)
    _assert(authorized_payload.get("no_archive_open_permission_added_by_l24_6") is True, "L24.6 should add no archive-open permission", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l24_6") is True, "L24.6 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l24_6") is True, "L24.6 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden optional/read/hash imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert("It does not hash the candidate file yet" in doc_text, "doc missing no-hash-yet statement", authorized_payload)
    _assert("Candidate hash authorization is readback-only" in doc_text, "doc missing readback-only boundary", authorized_payload)
    _assert("Candidate path hash is not performed" in doc_text, "doc missing no hash boundary", authorized_payload)
    _assert("Downloaded file bytes are not read" in doc_text, "doc missing no bytes boundary", authorized_payload)
    _assert("Candidate archive is not opened" in doc_text, "doc missing no archive open boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/real-archive-open/archive-list/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L24.6",
        "fixture_refreshed": True,
        "default_future_hash_authorized": default_payload.get("real_archive_candidate_hash_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("real_archive_candidate_hash_authorization_granted_for_future_patch"),
        "source_l24_05_ok": authorized_payload.get("source_l24_05_summary", {}).get("ok"),
        "source_l24_05_broad_checkpoint": authorized_payload.get("source_l24_05_summary", {}).get("broad_checkpoint"),
        "source_l24_05_ladder_complete": authorized_payload.get("source_l24_05_summary", {}).get("ladder_complete"),
        "source_l24_05_stat_scope": authorized_payload.get("source_l24_05_summary", {}).get("accepted_stat_scope"),
        "source_l24_05_stat_performed": authorized_payload.get("source_l24_05_summary", {}).get("stat_performed"),
        "hash_allowed": authorized_payload.get("real_archive_candidate_path_hash_allowed"),
        "hash_performed": authorized_payload.get("real_archive_candidate_path_hash_performed"),
        "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
        "downloaded_file_hash_performed": authorized_payload.get("downloaded_file_hash_performed"),
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
    parser = argparse.ArgumentParser(description="L24.6 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
