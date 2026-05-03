from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_final_marker as final_marker

FALSE_FIELDS = (
    "archive_extracted",
    "downloaded_archive_extracted",
    "downloaded_archive_opened",
    "archive_member_bytes_read",
    "member_bytes_read",
    "archive_member_content_read",
    "artifact_content_read",
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
    payload = final_marker.build_manifest_validation_final_acceptance_marker(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_downloaded_archive_manifest_validation_final_marker.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_final_marker.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")

    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    false_errors = _false_field_errors(payload)

    _assert(payload.get("ok") is True, "final marker payload is not ok", payload)
    _assert(payload.get("patch") == "L22.7", "wrong patch marker", payload)
    _assert(payload.get("l22_final_acceptance_marker") is True, "final marker missing", payload)
    _assert(payload.get("l22_downloaded_archive_manifest_validation_stream_complete") is True, "L22 completion marker missing", payload)
    _assert(payload.get("accepted_scope") == "synthetic_manifest_fixture_validation_only", "wrong accepted scope", payload)
    _assert(payload.get("no_new_execution_permission_added_by_l22_7") is True, "L22.7 should not add execution permission", payload)
    _assert(payload.get("l22_06_summary", {}).get("ok") is True, "L22.6 summary not ok", payload)
    _assert(payload.get("l22_06_summary", {}).get("repair_patch") == "L22.6a", "L22.6a repair marker missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("manifest_validation_scope") == "synthetic_patchops_runtime_manifest_fixture_only", "wrong manifest scope", payload)
    _assert(payload.get("manifest_validation_result") is True, "manifest validation result should be true", payload)
    _assert(payload.get("synthetic_manifest_fixture_read") is True, "synthetic fixture should be read", payload)
    _assert(payload.get("real_downloaded_manifest_read") is False, "real downloaded manifest read must remain false", payload)
    _assert(payload.get("real_archive_manifest_read") is False, "real archive manifest read must remain false", payload)
    _assert(not false_errors, "forbidden fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden optional imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert("L22.3b passive plan launcher-direct checkpoint" in doc_text, "doc missing L22.3b source", payload)
    _assert("L22.4/L22.4a controlled authorization gate" in doc_text, "doc missing L22.4 source", payload)
    _assert("L22.5 first controlled synthetic manifest fixture validation proof" in doc_text, "doc missing L22.5 source", payload)
    _assert("L22.6/L22.6a broad checkpoint" in doc_text, "doc missing L22.6 source", payload)
    _assert("L22 does not grant permission for real browser/download/archive/package-run activity" in doc_text, "doc missing no-permission statement", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No archive extraction" in doc_text, "doc missing no archive extraction boundary", payload)
    _assert("No archive member-byte read" in doc_text, "doc missing no member-byte-read boundary", payload)
    _assert("No click/download/archive-extract/member-byte-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L22.7",
        "l22_final_acceptance_marker": payload.get("l22_final_acceptance_marker"),
        "l22_complete": payload.get("l22_downloaded_archive_manifest_validation_stream_complete"),
        "accepted_scope": payload.get("accepted_scope"),
        "no_new_execution_permission_added_by_l22_7": payload.get("no_new_execution_permission_added_by_l22_7"),
        "l22_06_ok": payload.get("l22_06_summary", {}).get("ok"),
        "l22_06_repair_patch": payload.get("l22_06_summary", {}).get("repair_patch"),
        "failed_checks": payload.get("failed_checks"),
        "manifest_scope": payload.get("manifest_validation_scope"),
        "manifest_validation_result": payload.get("manifest_validation_result"),
        "synthetic_manifest_fixture_read": payload.get("synthetic_manifest_fixture_read"),
        "real_downloaded_manifest_read": payload.get("real_downloaded_manifest_read"),
        "real_archive_manifest_read": payload.get("real_archive_manifest_read"),
        "archive_extracted": payload.get("archive_extracted"),
        "member_bytes_read": payload.get("archive_member_bytes_read"),
        "browser_started": payload.get("browser_started"),
        "pasteback": payload.get("pasteback_workflow_active"),
        "package_run": payload.get("package_run"),
        "next_patch": payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L22.7 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
