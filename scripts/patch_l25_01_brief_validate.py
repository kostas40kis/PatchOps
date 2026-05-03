from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_open_authorization_gate as gate
from patchops.llm_browser import live_adapter_edge_real_archive_candidate_first_controlled_hash_proof as proof

FALSE_FIELDS = (
    "archive_open_authorization_executes_archive_open",
    "real_archive_candidate_open_allowed",
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_candidate_member_count_read",
    "real_archive_candidate_member_names_read",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "archive_member_bytes_read",
    "archive_member_payload_read",
    "manifest_payload_read",
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

FORBIDDEN_IMPORT_MODULES = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "zipfile",
)

CONTROLLED_FIXTURE_BYTES = b"L25.1a controlled candidate fixture for archive-open authorization readback only. No archive open.\n"


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _forbidden_import_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    forbidden = set(FORBIDDEN_IMPORT_MODULES)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".", 1)[0]
                if root_name in forbidden:
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            root_name = (node.module or "").split(".", 1)[0]
            if root_name in forbidden:
                hits.append(node.module or "")
    return sorted(set(hits))


def _refresh_controlled_candidate_fixture(root: Path) -> Path:
    candidate = root / proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(CONTROLLED_FIXTURE_BYTES)
    return candidate


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = _refresh_controlled_candidate_fixture(root)
    default_payload = gate.build_archive_open_authorization_gate(root)
    authorized_payload = gate.build_archive_open_authorization_gate(
        root,
        allow_archive_open_authorization=True,
        authorization_token=gate.REQUIRED_ARCHIVE_OPEN_AUTHORIZATION_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_open_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_open_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled candidate fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("repair_patch") == "L25.1a", "default payload missing repair marker", default_payload)
    _assert(default_payload.get("archive_open_authorization_granted_for_future_patch") is False, "default should not grant future archive-open auth", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.1", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("repair_patch") == "L25.1a", "repair marker missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("ok") is True, "L24.9 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("final_metadata_hash_acceptance_marker") is True, "L24.9 final marker missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("l24_metadata_hash_complete") is True, "L24.9 completion missing", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("archive_open_permission") is False, "L24.9 archive-open permission must be false", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("archive_listing_permission") is False, "L24.9 archive listing permission must be false", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("archive_member_read_permission") is False, "L24.9 archive member read permission must be false", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("manifest_payload_read_permission") is False, "L24.9 manifest payload read permission must be false", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("browser_permission") is False, "L24.9 browser permission must be false", authorized_payload)
    _assert(authorized_payload.get("source_l24_09_summary", {}).get("package_run_permission") is False, "L24.9 package run permission must be false", authorized_payload)
    _assert(authorized_payload.get("archive_open_authorization_granted_for_future_patch") is True, "future archive-open auth should be granted by token", authorized_payload)
    _assert(authorized_payload.get("archive_open_authorization_readback_only") is True, "archive-open auth must be readback-only", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_open_allowed") is False, "archive-open allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_opened") is False, "candidate archive must not be opened", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listed") is False, "candidate archive must not be listed", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "candidate archive must not be extracted", authorized_payload)
    _assert(authorized_payload.get("archive_member_bytes_read") is False, "archive member bytes must not be read", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_read") is False, "manifest payload must not be read", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_archive_open_execution_added_by_l25_1") is True, "L25.1 should add no archive-open execution", authorized_payload)
    _assert(authorized_payload.get("no_archive_listing_or_extraction_added_by_l25_1") is True, "L25.1 should add no listing/extraction", authorized_payload)
    _assert(authorized_payload.get("no_manifest_payload_read_added_by_l25_1") is True, "L25.1 should add no manifest payload read", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l25_1") is True, "L25.1 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l25_1") is True, "L25.1 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert("L25.1a repairs the validator" in doc_text, "doc missing L25.1a repair note", authorized_payload)
    _assert("Archive-open authorization is readback-only" in doc_text, "doc missing readback-only boundary", authorized_payload)
    _assert("The `zipfile` module is not loaded in L25.1" in doc_text, "doc missing no zipfile boundary", authorized_payload)
    _assert("Candidate archive is not opened as an archive" in doc_text, "doc missing no archive open boundary", authorized_payload)
    _assert("Archive member bytes are not read" in doc_text, "doc missing no archive member read boundary", authorized_payload)
    _assert("Manifest payload is not read" in doc_text, "doc missing no manifest payload boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/real-archive-open/archive-list/archive-extract/archive-member-byte-read/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.1",
        "repair_patch": "L25.1a",
        "fixture_refreshed": True,
        "forbidden_executable_import_hits": forbidden_import_hits,
        "default_future_archive_open_authorized": default_payload.get("archive_open_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("archive_open_authorization_granted_for_future_patch"),
        "source_l24_09_ok": authorized_payload.get("source_l24_09_summary", {}).get("ok"),
        "source_l24_09_final_marker": authorized_payload.get("source_l24_09_summary", {}).get("final_metadata_hash_acceptance_marker"),
        "source_l24_09_complete": authorized_payload.get("source_l24_09_summary", {}).get("l24_metadata_hash_complete"),
        "source_l24_09_archive_open_permission": authorized_payload.get("source_l24_09_summary", {}).get("archive_open_permission"),
        "archive_open_allowed": authorized_payload.get("real_archive_candidate_open_allowed"),
        "archive_opened": authorized_payload.get("real_archive_candidate_opened"),
        "archive_listed": authorized_payload.get("real_archive_candidate_listed"),
        "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
        "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
        "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.1a brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
