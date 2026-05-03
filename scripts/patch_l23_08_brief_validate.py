from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_synthetic_payload_broad_checkpoint as broad

FALSE_FIELDS = (
    "non_manifest_member_bytes_read",
    "non_manifest_member_payload_read",
    "readme_member_payload_read",
    "downloaded_archive_extracted",
    "archive_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "candidate_archive_path_stat_performed",
    "candidate_archive_path_hash_performed",
    "synthetic_archive_hash_performed",
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
    payload = broad.build_synthetic_payload_broad_checkpoint(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_validation_synthetic_payload_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_validation_synthetic_payload_broad_checkpoint.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    false_errors = _false_field_errors(payload)

    _assert(payload.get("ok") is True, "broad checkpoint payload is not ok", payload)
    _assert(payload.get("patch") == "L23.8", "wrong patch marker", payload)
    _assert(payload.get("broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("synthetic_payload_ladder_checkpoint") is True, "synthetic ladder marker missing", payload)
    _assert(payload.get("l23_synthetic_payload_ladder_complete") is True, "ladder completion marker missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l23_07_default_summary", {}).get("payload_read_performed") is False, "default L23.7 should remain passive", payload)
    _assert(payload.get("source_l23_07_authorized_summary", {}).get("payload_read_performed") is True, "authorized L23.7 payload proof missing", payload)
    _assert(payload.get("source_l23_07_authorized_summary", {}).get("manifest_member_name") == "manifest.json", "wrong manifest member", payload)
    _assert(payload.get("source_l23_07_authorized_summary", {}).get("synthetic_manifest_json_parsed") is True, "synthetic JSON parse missing", payload)
    _assert(payload.get("source_l23_07_authorized_summary", {}).get("synthetic_manifest_shape_validated") is True, "synthetic shape validation missing", payload)
    _assert(payload.get("accepted_synthetic_payload_scope") == "fixed_synthetic_archive_manifest_payload_only", "wrong accepted scope", payload)
    _assert(payload.get("accepted_synthetic_manifest_patch_name") == "l23_07_synthetic_manifest_payload_fixture", "wrong accepted synthetic patch name", payload)
    _assert(payload.get("manifest_member_payload_read") is True, "manifest payload read marker should be true", payload)
    _assert(payload.get("manifest_member_bytes_read") is True, "manifest bytes read marker should be true", payload)
    _assert(payload.get("non_manifest_member_bytes_read") is False, "non-manifest bytes must remain false", payload)
    _assert(payload.get("readme_member_payload_read") is False, "README payload must remain false", payload)
    _assert(payload.get("archive_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("real_archive_manifest_read") is False, "real archive manifest read must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_real_archive_permission_added_by_l23_8") is True, "L23.8 should add no real archive permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden optional imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert("L23.1 real downloaded-archive manifest authorization gate" in doc_text, "doc missing L23.1 ladder item", payload)
    _assert("L23.7 first synthetic manifest payload proof" in doc_text, "doc missing L23.7 ladder item", payload)
    _assert("Only `manifest.json` payload from that fixed synthetic fixture may be read" in doc_text, "doc missing manifest-only boundary", payload)
    _assert("Non-manifest member payload bytes are not read" in doc_text, "doc missing non-manifest no-read boundary", payload)
    _assert("No archive extraction" in doc_text, "doc missing no extraction boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/real-archive-open/archive-extract/non-manifest-member-byte-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L23.8",
        "broad_checkpoint": payload.get("broad_checkpoint"),
        "ladder_complete": payload.get("l23_synthetic_payload_ladder_complete"),
        "failed_checks": payload.get("failed_checks"),
        "default_payload_read_performed": payload.get("source_l23_07_default_summary", {}).get("payload_read_performed"),
        "authorized_payload_read_performed": payload.get("source_l23_07_authorized_summary", {}).get("payload_read_performed"),
        "manifest_member_name": payload.get("source_l23_07_authorized_summary", {}).get("manifest_member_name"),
        "synthetic_manifest_json_parsed": payload.get("source_l23_07_authorized_summary", {}).get("synthetic_manifest_json_parsed"),
        "synthetic_manifest_shape_validated": payload.get("source_l23_07_authorized_summary", {}).get("synthetic_manifest_shape_validated"),
        "accepted_scope": payload.get("accepted_synthetic_payload_scope"),
        "accepted_patch_name": payload.get("accepted_synthetic_manifest_patch_name"),
        "manifest_payload_read": payload.get("manifest_member_payload_read"),
        "non_manifest_member_bytes_read": payload.get("non_manifest_member_bytes_read"),
        "readme_payload_read": payload.get("readme_member_payload_read"),
        "archive_extracted": payload.get("archive_extracted"),
        "real_archive_manifest_read": payload.get("real_archive_manifest_read"),
        "browser_started": payload.get("browser_started"),
        "pasteback": payload.get("pasteback_workflow_active"),
        "package_run": payload.get("package_run"),
        "next_patch": payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L23.8 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
