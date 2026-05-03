from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_path_string_preflight_gate as gate

FALSE_FIELDS = (
    "real_archive_candidate_path_stat_allowed",
    "real_archive_candidate_path_stat_performed",
    "real_archive_candidate_path_hash_allowed",
    "real_archive_candidate_path_hash_performed",
    "real_archive_candidate_exists",
    "real_archive_candidate_size_bytes_read",
    "real_archive_candidate_suffix_checked_on_filesystem",
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
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
)


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    default_payload = gate.build_real_archive_candidate_path_string_preflight_gate(root)
    authorized_payload = gate.build_real_archive_candidate_path_string_preflight_gate(
        root,
        allow_candidate_path_string_preflight=True,
        authorization_token=gate.REQUIRED_REAL_ARCHIVE_CANDIDATE_PATH_STRING_PREFLIGHT_TOKEN,
        candidate_archive_path=gate.DEFAULT_CANDIDATE_ARCHIVE_PATH,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_candidate_path_string_preflight_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_candidate_path_string_preflight_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)
    string_checks = authorized_payload.get("candidate_path_string_checks", {})

    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("repair_patch") == "L24.2a", "repair marker missing from default payload", default_payload)
    _assert(default_payload.get("candidate_path_string_preflight_allowed") is False, "default should not allow preflight", default_payload)
    _assert(default_payload.get("candidate_path_string_preflight_scope") == "default_readback_only_no_candidate_path_analysis", "default should stay passive", default_payload)
    _assert(default_payload.get("failed_checks") == [], "default failed checks should be empty", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L24.2", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("repair_patch") == "L24.2a", "repair marker missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_01_summary", {}).get("future_candidate_authorized") is True, "L24.1 future candidate auth missing", authorized_payload)
    _assert(authorized_payload.get("candidate_path_string_preflight_allowed") is True, "string preflight should be allowed", authorized_payload)
    _assert(authorized_payload.get("candidate_path_string_preflight_scope") == "string_only_no_filesystem_touch", "wrong preflight scope", authorized_payload)
    _assert(string_checks.get("candidate_path_string_present") is True, "candidate string missing", authorized_payload)
    _assert(string_checks.get("candidate_path_string_nonempty") is True, "candidate string empty", authorized_payload)
    _assert(string_checks.get("candidate_path_string_absolute_windows") is True, "candidate string must look absolute Windows", authorized_payload)
    _assert(string_checks.get("candidate_path_string_zip_suffix") is True, "candidate string must end with .zip", authorized_payload)
    _assert(string_checks.get("candidate_path_string_has_no_wildcards") is True, "candidate string must have no wildcards", authorized_payload)
    _assert(string_checks.get("candidate_path_string_has_no_traversal_segments") is True, "candidate string must have no traversal", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_stat_performed") is False, "candidate stat must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_path_hash_performed") is False, "candidate hash must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_exists") is False, "candidate existence must not be checked", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_size_bytes_read") is False, "candidate size must not be read", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_opened") is False, "candidate archive must not be opened", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listed") is False, "candidate archive must not be listed", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_real_archive_candidate_filesystem_permission_added_by_l24_2") is True, "L24.2 should add no filesystem permission", authorized_payload)
    _assert(authorized_payload.get("no_archive_open_permission_added_by_l24_2") is True, "L24.2 should add no archive-open permission", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l24_2") is True, "L24.2 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l24_2") is True, "L24.2 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden optional imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert("L24.2a repairs the default/passive readback" in doc_text, "doc missing L24.2a repair note", authorized_payload)
    _assert("Candidate archive path may be analyzed as a string only" in doc_text, "doc missing string-only analysis boundary", authorized_payload)
    _assert("Candidate archive path is not statted" in doc_text, "doc missing no stat boundary", authorized_payload)
    _assert("Candidate archive path is not hashed" in doc_text, "doc missing no hash boundary", authorized_payload)
    _assert("Candidate archive existence is not checked" in doc_text, "doc missing no existence boundary", authorized_payload)
    _assert("No real downloaded archive open" in doc_text, "doc missing no real archive open boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/real-archive-open/archive-list/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L24.2",
        "repair_patch": "L24.2a",
        "default_preflight_allowed": default_payload.get("candidate_path_string_preflight_allowed"),
        "default_failed_checks": default_payload.get("failed_checks"),
        "source_l24_01_ok": authorized_payload.get("source_l24_01_summary", {}).get("ok"),
        "source_l24_01_future_authorized": authorized_payload.get("source_l24_01_summary", {}).get("future_candidate_authorized"),
        "string_preflight_allowed": authorized_payload.get("candidate_path_string_preflight_allowed"),
        "string_preflight_scope": authorized_payload.get("candidate_path_string_preflight_scope"),
        "candidate_string_nonempty": string_checks.get("candidate_path_string_nonempty"),
        "candidate_string_absolute_windows": string_checks.get("candidate_path_string_absolute_windows"),
        "candidate_string_zip_suffix": string_checks.get("candidate_path_string_zip_suffix"),
        "candidate_string_no_wildcards": string_checks.get("candidate_path_string_has_no_wildcards"),
        "candidate_string_no_traversal": string_checks.get("candidate_path_string_has_no_traversal_segments"),
        "candidate_path_stat_performed": authorized_payload.get("real_archive_candidate_path_stat_performed"),
        "candidate_path_hash_performed": authorized_payload.get("real_archive_candidate_path_hash_performed"),
        "candidate_exists_checked": authorized_payload.get("real_archive_candidate_exists"),
        "candidate_archive_opened": authorized_payload.get("real_archive_candidate_opened"),
        "candidate_archive_listed": authorized_payload.get("real_archive_candidate_listed"),
        "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L24.2a brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
