from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_authorization_gate as gate

FALSE_FIELDS = (
    "real_archive_manifest_validation_execution_allowed",
    "real_archive_manifest_validation_active",
    "real_archive_manifest_validation_performed",
    "real_downloaded_manifest_read",
    "real_archive_manifest_read",
    "real_archive_opened",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "archive_member_bytes_read",
    "archive_member_content_read",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "candidate_archive_path_stat_performed",
    "candidate_archive_path_hash_performed",
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
    default_payload = gate.build_real_archive_manifest_validation_authorization_gate(root)
    authorized_payload = gate.build_real_archive_manifest_validation_authorization_gate(
        root,
        allow_real_archive_manifest_validation_authorization=True,
        authorization_token=gate.REQUIRED_REAL_ARCHIVE_MANIFEST_AUTHORIZATION_TOKEN,
        candidate_archive_path=r"C:\Users\kostas\Downloads\patch_future_example_patchops_bundle.zip",
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_validation_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_validation_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L23.1", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l22_07_summary", {}).get("l22_complete") is True, "L22 completion source missing", authorized_payload)
    _assert(default_payload.get("real_archive_manifest_authorization_granted_for_future_patch") is False, "default should not be future-authorized", default_payload)
    _assert(authorized_payload.get("real_archive_manifest_authorization_granted_for_future_patch") is True, "authorized readback should be granted", authorized_payload)
    _assert(authorized_payload.get("candidate_archive_path_recorded") is True, "candidate path should be recorded as string", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_validation_execution_allowed") is False, "L23.1 execution must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_opened") is False, "archive must not be opened", authorized_payload)
    _assert(authorized_payload.get("downloaded_archive_contents_listed") is False, "archive contents must not be listed", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", authorized_payload)
    _assert(authorized_payload.get("archive_member_bytes_read") is False, "member bytes must not be read", authorized_payload)
    _assert(authorized_payload.get("candidate_archive_path_stat_performed") is False, "candidate path must not be statted", authorized_payload)
    _assert(authorized_payload.get("candidate_archive_path_hash_performed") is False, "candidate path must not be hashed", authorized_payload)
    _assert(authorized_payload.get("no_new_execution_permission_added_by_l23_1") is True, "L23.1 should add no execution permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden optional imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert("Candidate archive path may be recorded as a string only" in doc_text, "doc missing string-only path boundary", authorized_payload)
    _assert("No archive open" in doc_text, "doc missing no archive open boundary", authorized_payload)
    _assert("No archive listing" in doc_text, "doc missing no archive listing boundary", authorized_payload)
    _assert("No archive member-byte read" in doc_text, "doc missing no member-byte boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-open/archive-list/archive-extract/member-byte-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L23.1",
        "default_future_authorized": default_payload.get("real_archive_manifest_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("real_archive_manifest_authorization_granted_for_future_patch"),
        "execution_allowed": authorized_payload.get("real_archive_manifest_validation_execution_allowed"),
        "candidate_path_recorded": authorized_payload.get("candidate_archive_path_recorded"),
        "candidate_path_stat_performed": authorized_payload.get("candidate_archive_path_stat_performed"),
        "candidate_path_hash_performed": authorized_payload.get("candidate_archive_path_hash_performed"),
        "real_archive_opened": authorized_payload.get("real_archive_opened"),
        "archive_listed": authorized_payload.get("downloaded_archive_contents_listed"),
        "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
        "member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L23.1 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
