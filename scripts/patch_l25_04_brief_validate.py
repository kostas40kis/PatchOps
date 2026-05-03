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

from patchops.llm_browser import live_adapter_edge_real_archive_listing_authorization_gate as gate
from patchops.llm_browser import live_adapter_edge_real_archive_open_first_controlled_proof as open_proof

FALSE_FIELDS = (
    "archive_listing_authorization_executes_listing",
    "real_archive_candidate_listing_allowed",
    "real_archive_candidate_listed",
    "real_archive_candidate_member_count_read",
    "real_archive_candidate_member_names_read",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
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

FORBIDDEN_ARCHIVE_CALL_SNIPPETS = (
    ".namelist(",
    ".infolist(",
    ".read(",
    ".extract(",
    ".extractall(",
    ".open(",
    "testzip(",
)

EMPTY_ZIP_BYTES = b"PK\x05\x06" + (b"\x00" * 18)


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


def _archive_call_hits(source_text: str) -> list[str]:
    return sorted(snippet for snippet in FORBIDDEN_ARCHIVE_CALL_SNIPPETS if snippet in source_text)


def _refresh_controlled_empty_zip_fixture(root: Path) -> Path:
    candidate = root / open_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(EMPTY_ZIP_BYTES)
    return candidate


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = _refresh_controlled_empty_zip_fixture(root)
    default_payload = gate.build_archive_listing_authorization_gate(root)
    authorized_payload = gate.build_archive_listing_authorization_gate(
        root,
        allow_archive_listing_authorization=True,
        authorization_token=gate.REQUIRED_ARCHIVE_LISTING_AUTHORIZATION_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_listing_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_listing_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    archive_call_hits = _archive_call_hits(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled empty zip fixture missing", authorized_payload)
    _assert(candidate.read_bytes() == EMPTY_ZIP_BYTES, "controlled fixture is not expected empty ZIP bytes", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("archive_listing_authorization_granted_for_future_patch") is False, "default should not grant future listing auth", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.4", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("ok") is True, "L25.3 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("broad_checkpoint") is True, "L25.3 broad checkpoint missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("archive_open_ladder_complete") is True, "L25.3 archive-open ladder completion missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("archive_opened") is True, "L25.3 archive open missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("archive_open_closed") is True, "L25.3 archive close missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("archive_listed") is False, "L25.3 archive listing must be false", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("archive_member_count_read") is False, "L25.3 member count must be false", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("archive_member_names_read") is False, "L25.3 member names must be false", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("archive_member_bytes_read") is False, "L25.3 member bytes must be false", authorized_payload)
    _assert(authorized_payload.get("source_l25_03_summary", {}).get("manifest_payload_read") is False, "L25.3 manifest payload must be false", authorized_payload)
    _assert(authorized_payload.get("archive_listing_authorization_granted_for_future_patch") is True, "future listing auth should be granted by token", authorized_payload)
    _assert(authorized_payload.get("archive_listing_authorization_readback_only") is True, "listing auth must be readback-only", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listing_allowed") is False, "listing allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listed") is False, "archive listed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_member_count_read") is False, "member count read must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_member_names_read") is False, "member names read must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("archive_member_bytes_read") is False, "archive member bytes must remain false", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_read") is False, "manifest payload must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_archive_listing_execution_added_by_l25_4") is True, "L25.4 should add no listing execution", authorized_payload)
    _assert(authorized_payload.get("no_archive_member_or_manifest_payload_read_added_by_l25_4") is True, "L25.4 should add no member/manifest read", authorized_payload)
    _assert(authorized_payload.get("no_archive_extraction_added_by_l25_4") is True, "L25.4 should add no extraction", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l25_4") is True, "L25.4 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l25_4") is True, "L25.4 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not archive_call_hits, "forbidden archive list/read/extract calls found: " + ", ".join(archive_call_hits), authorized_payload)
    _assert("It does not list archive members yet" in doc_text, "doc missing no-list-yet statement", authorized_payload)
    _assert("Archive listing authorization is readback-only" in doc_text, "doc missing readback-only boundary", authorized_payload)
    _assert("Candidate archive is not listed" in doc_text, "doc missing no list boundary", authorized_payload)
    _assert("Candidate archive member names are not read" in doc_text, "doc missing no member-name boundary", authorized_payload)
    _assert("Candidate archive member count is not read" in doc_text, "doc missing no member-count boundary", authorized_payload)
    _assert("Archive member bytes are not read" in doc_text, "doc missing no member-byte boundary", authorized_payload)
    _assert("Manifest payload is not read" in doc_text, "doc missing no manifest payload boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-list/archive-extract/archive-member-byte-read/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.4",
        "fixture_refreshed": True,
        "fixture_is_empty_zip": True,
        "default_future_listing_authorized": default_payload.get("archive_listing_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("archive_listing_authorization_granted_for_future_patch"),
        "source_l25_03_ok": authorized_payload.get("source_l25_03_summary", {}).get("ok"),
        "source_l25_03_broad_checkpoint": authorized_payload.get("source_l25_03_summary", {}).get("broad_checkpoint"),
        "source_l25_03_archive_open_ladder_complete": authorized_payload.get("source_l25_03_summary", {}).get("archive_open_ladder_complete"),
        "source_l25_03_archive_opened": authorized_payload.get("source_l25_03_summary", {}).get("archive_opened"),
        "source_l25_03_archive_open_closed": authorized_payload.get("source_l25_03_summary", {}).get("archive_open_closed"),
        "listing_allowed": authorized_payload.get("real_archive_candidate_listing_allowed"),
        "archive_listed": authorized_payload.get("real_archive_candidate_listed"),
        "archive_member_count_read": authorized_payload.get("real_archive_candidate_member_count_read"),
        "archive_member_names_read": authorized_payload.get("real_archive_candidate_member_names_read"),
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
    parser = argparse.ArgumentParser(description="L25.4 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
