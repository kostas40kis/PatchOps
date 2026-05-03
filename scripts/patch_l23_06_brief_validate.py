from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_synthetic_manifest_payload_authorization_gate as gate

FALSE_FIELDS = (
    "synthetic_manifest_payload_read_execution_allowed",
    "synthetic_manifest_payload_read_active",
    "synthetic_manifest_payload_read_performed",
    "synthetic_manifest_json_parsed",
    "synthetic_manifest_shape_validated",
    "archive_member_bytes_read",
    "archive_member_content_read",
    "archive_member_payload_read",
    "downloaded_archive_extracted",
    "archive_extracted",
    "manifest_member_bytes_read",
    "manifest_member_payload_read",
    "manifest_member_content_read",
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
    default_payload = gate.build_synthetic_manifest_payload_authorization_gate(root)
    authorized_payload = gate.build_synthetic_manifest_payload_authorization_gate(
        root,
        allow_synthetic_manifest_payload_authorization=True,
        authorization_token=gate.REQUIRED_SYNTHETIC_MANIFEST_PAYLOAD_AUTHORIZATION_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_validation_synthetic_manifest_payload_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_validation_synthetic_manifest_payload_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("synthetic_manifest_payload_authorization_granted_for_future_patch") is False, "default should not grant future payload read", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L23.6", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l23_05_summary", {}).get("ok") is True, "L23.5 source summary not ok", authorized_payload)
    _assert(authorized_payload.get("source_l23_05_summary", {}).get("selected_name") == "manifest.json", "L23.5 selected name missing", authorized_payload)
    _assert(authorized_payload.get("source_l23_05_summary", {}).get("selection_scope") == "metadata_member_name_only_no_payload_read", "L23.5 selection scope wrong", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_payload_authorization_granted_for_future_patch") is True, "authorized readback should grant future payload proof", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_payload_read_execution_allowed") is False, "payload execution must remain false", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_payload_read_performed") is False, "payload read must not be performed", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_json_parsed") is False, "synthetic manifest JSON must not be parsed", authorized_payload)
    _assert(authorized_payload.get("manifest_member_payload_read") is False, "manifest payload must not be read", authorized_payload)
    _assert(authorized_payload.get("archive_member_bytes_read") is False, "member bytes must not be read", authorized_payload)
    _assert(authorized_payload.get("archive_member_payload_read") is False, "member payload must not be read", authorized_payload)
    _assert(authorized_payload.get("archive_extracted") is False, "archive must not be extracted", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_new_payload_read_permission_added_by_l23_6") is True, "L23.6 must not add payload read permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden optional imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert("Payload authorization is readback-only" in doc_text, "doc missing readback-only boundary", authorized_payload)
    _assert("Synthetic manifest payload read execution allowed remains false" in doc_text, "doc missing execution false boundary", authorized_payload)
    _assert("`manifest.json` contents are not read" in doc_text, "doc missing no manifest content boundary", authorized_payload)
    _assert("Member payload bytes are not read" in doc_text, "doc missing no member payload boundary", authorized_payload)
    _assert("No archive extraction" in doc_text, "doc missing no extraction boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/real-archive-open/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L23.6",
        "default_future_payload_authorized": default_payload.get("synthetic_manifest_payload_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("synthetic_manifest_payload_authorization_granted_for_future_patch"),
        "source_l23_05_ok": authorized_payload.get("source_l23_05_summary", {}).get("ok"),
        "source_l23_05_selected_name": authorized_payload.get("source_l23_05_summary", {}).get("selected_name"),
        "payload_execution_allowed": authorized_payload.get("synthetic_manifest_payload_read_execution_allowed"),
        "payload_read_performed": authorized_payload.get("synthetic_manifest_payload_read_performed"),
        "synthetic_manifest_json_parsed": authorized_payload.get("synthetic_manifest_json_parsed"),
        "manifest_payload_read": authorized_payload.get("manifest_member_payload_read"),
        "member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
        "member_payload_read": authorized_payload.get("archive_member_payload_read"),
        "archive_extracted": authorized_payload.get("archive_extracted"),
        "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L23.6 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
