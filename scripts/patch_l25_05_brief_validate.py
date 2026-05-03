from __future__ import annotations

import argparse
import ast
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_listing_first_controlled_proof as proof

FALSE_FIELDS = (
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
)

FORBIDDEN_ARCHIVE_CALL_SNIPPETS = (
    ".read(",
    ".extract(",
    ".extractall(",
    ".open(",
    "testzip(",
)

CONTROLLED_MEMBERS = {
    "bundle/manifest.json": "{\"synthetic\":true,\"purpose\":\"listing-proof-name-only\"}\n",
    "bundle/run_with_patchops.ps1": "# synthetic launcher name only for L25.5 listing proof\n",
}
EXPECTED_MEMBER_NAMES = sorted(CONTROLLED_MEMBERS)


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


def _refresh_controlled_zip_fixture(root: Path) -> Path:
    candidate = root / proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in EXPECTED_MEMBER_NAMES:
            archive.writestr(name, CONTROLLED_MEMBERS[name])
    return candidate


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = _refresh_controlled_zip_fixture(root)
    default_payload = proof.build_archive_listing_first_controlled_proof(root)
    authorized_payload = proof.build_archive_listing_first_controlled_proof(
        root,
        allow_archive_listing_proof=True,
        authorization_token=proof.REQUIRED_ARCHIVE_LISTING_PROOF_TOKEN,
        candidate_archive_path=str(candidate),
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_listing_first_controlled_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_listing_first_controlled_proof.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    archive_call_hits = _archive_call_hits(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled listing zip fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("real_archive_candidate_listed") is False, "default should not list archive", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.5", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_04_summary", {}).get("ok") is True, "L25.4 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_04_summary", {}).get("future_listing_authorized") is True, "L25.4 future listing authorization missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_04_summary", {}).get("archive_listed") is False, "L25.4 must not have listed archive", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listing_allowed") is True, "listing should be allowed", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_listed") is True, "archive should be listed", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_member_count_read") is True, "member count should be read", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_member_count") == len(EXPECTED_MEMBER_NAMES), "member count mismatch", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_member_names_read") is True, "member names should be read", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_member_names") == EXPECTED_MEMBER_NAMES, "member names mismatch", authorized_payload)
    _assert(authorized_payload.get("archive_listing_scope") == "controlled_runtime_zip_member_names_and_count_only_no_member_bytes", "wrong listing scope", authorized_payload)
    _assert(authorized_payload.get("zipfile_import_allowed_by_l25_5") is True, "zipfile import should be marked allowed for L25.5", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("archive_member_bytes_read") is False, "archive member bytes must remain false", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_read") is False, "manifest payload must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_archive_extraction_added_by_l25_5") is True, "L25.5 should add no extraction", authorized_payload)
    _assert(authorized_payload.get("no_archive_member_or_manifest_payload_read_added_by_l25_5") is True, "L25.5 should add no member/manifest read", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l25_5") is True, "L25.5 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l25_5") is True, "L25.5 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not archive_call_hits, "forbidden archive read/extract/member-open calls found: " + ", ".join(archive_call_hits), authorized_payload)
    _assert("list only member names and member count" in doc_text, "doc missing listing boundary", authorized_payload)
    _assert("Archive member bytes are not read" in doc_text, "doc missing no member-byte boundary", authorized_payload)
    _assert("Manifest payload is not read" in doc_text, "doc missing no manifest payload boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-extract/archive-member-byte-read/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.5",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "default_archive_listed": default_payload.get("real_archive_candidate_listed"),
        "source_l25_04_ok": authorized_payload.get("source_l25_04_summary", {}).get("ok"),
        "source_l25_04_future_authorized": authorized_payload.get("source_l25_04_summary", {}).get("future_listing_authorized"),
        "listing_allowed": authorized_payload.get("real_archive_candidate_listing_allowed"),
        "archive_listed": authorized_payload.get("real_archive_candidate_listed"),
        "archive_member_count_read": authorized_payload.get("real_archive_candidate_member_count_read"),
        "archive_member_count": authorized_payload.get("real_archive_candidate_member_count"),
        "archive_member_names_read": authorized_payload.get("real_archive_candidate_member_names_read"),
        "archive_member_names": authorized_payload.get("real_archive_candidate_member_names"),
        "archive_listing_scope": authorized_payload.get("archive_listing_scope"),
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
    parser = argparse.ArgumentParser(description="L25.5 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
