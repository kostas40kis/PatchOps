from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_first_synthetic_manifest_payload_proof as proof

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

SYNTHETIC_MANIFEST = {
    "manifest_version": "1",
    "patch_name": "l23_07_synthetic_manifest_payload_fixture",
    "active_profile": "generic_python",
    "target_project_root": "C:\\dev\\patchops",
    "files_to_write": [],
    "validation_commands": [],
    "notes": "synthetic fixture only; not a real downloaded archive manifest",
}


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _refresh_fixed_synthetic_archive_fixture(root: Path) -> Path:
    """Create/replace only the fixed synthetic archive fixture for L23.7.

    This setup writes a tiny synthetic manifest payload and an empty README. It is
    not real downloaded archive handling and does not read any member payload.
    """
    archive_path = root / proof.DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    zip_module = importlib.import_module("zipfile")
    manifest_text = json.dumps(SYNTHETIC_MANIFEST, sort_keys=True, separators=(",", ":"))
    with zip_module.ZipFile(archive_path, "w", compression=zip_module.ZIP_STORED) as archive:
        archive.writestr("manifest.json", manifest_text)
        archive.writestr("README.txt", "")
    return archive_path


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    fixture_path = _refresh_fixed_synthetic_archive_fixture(root)

    default_payload = proof.build_first_synthetic_manifest_payload_proof(root)
    authorized_payload = proof.build_first_synthetic_manifest_payload_proof(
        root,
        allow_synthetic_manifest_payload_proof=True,
        authorization_token=proof.REQUIRED_SYNTHETIC_MANIFEST_PAYLOAD_PROOF_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_validation_first_synthetic_manifest_payload_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_validation_first_synthetic_manifest_payload_proof.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(fixture_path.exists(), "refreshed synthetic fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("synthetic_manifest_payload_read_performed") is False, "default should not read payload", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L23.7", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l23_06_summary", {}).get("ok") is True, "L23.6 source summary not ok", authorized_payload)
    _assert(authorized_payload.get("source_l23_06_summary", {}).get("future_payload_authorized") is True, "L23.6 future authorization missing", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_payload_read_execution_allowed") is True, "payload proof should be allowed", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_payload_read_performed") is True, "payload read should be performed", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_member_name") == "manifest.json", "wrong member was read", authorized_payload)
    _assert(isinstance(authorized_payload.get("synthetic_manifest_payload_size_bytes"), int) and authorized_payload.get("synthetic_manifest_payload_size_bytes") > 0, "payload size should be positive", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_payload_sha256_performed") is False, "payload hash must remain false", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_json_parsed") is True, "synthetic manifest JSON should be parsed", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_shape_validated") is True, "synthetic manifest shape should be valid", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_patch_name") == "l23_07_synthetic_manifest_payload_fixture", "wrong synthetic patch name", authorized_payload)
    _assert(authorized_payload.get("synthetic_manifest_scope") == "fixed_synthetic_archive_manifest_payload_only", "wrong synthetic scope", authorized_payload)
    _assert(authorized_payload.get("manifest_member_bytes_read") is True, "manifest member bytes should be read", authorized_payload)
    _assert(authorized_payload.get("manifest_member_payload_read") is True, "manifest member payload should be read", authorized_payload)
    _assert(authorized_payload.get("archive_member_bytes_read") is True, "archive member bytes marker should reflect manifest payload read", authorized_payload)
    _assert(authorized_payload.get("non_manifest_member_bytes_read") is False, "non-manifest member bytes must not be read", authorized_payload)
    _assert(authorized_payload.get("readme_member_payload_read") is False, "README payload must not be read", authorized_payload)
    _assert(authorized_payload.get("archive_extracted") is False, "archive must not be extracted", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must not be read", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_real_archive_permission_added_by_l23_7") is True, "L23.7 must add no real archive permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden optional imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert("Only `manifest.json` payload may be read" in doc_text, "doc missing manifest-only boundary", authorized_payload)
    _assert("Non-manifest member payload bytes are not read" in doc_text, "doc missing non-manifest no-read boundary", authorized_payload)
    _assert("No archive extraction" in doc_text, "doc missing no extraction boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/real-archive-open/archive-extract/non-manifest-member-byte-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L23.7",
        "fixture_refreshed": True,
        "default_payload_read_performed": default_payload.get("synthetic_manifest_payload_read_performed"),
        "source_l23_06_ok": authorized_payload.get("source_l23_06_summary", {}).get("ok"),
        "source_l23_06_future_authorized": authorized_payload.get("source_l23_06_summary", {}).get("future_payload_authorized"),
        "payload_execution_allowed": authorized_payload.get("synthetic_manifest_payload_read_execution_allowed"),
        "payload_read_performed": authorized_payload.get("synthetic_manifest_payload_read_performed"),
        "manifest_member_name": authorized_payload.get("synthetic_manifest_member_name"),
        "payload_size_bytes": authorized_payload.get("synthetic_manifest_payload_size_bytes"),
        "payload_hash_performed": authorized_payload.get("synthetic_manifest_payload_sha256_performed"),
        "synthetic_manifest_json_parsed": authorized_payload.get("synthetic_manifest_json_parsed"),
        "synthetic_manifest_shape_validated": authorized_payload.get("synthetic_manifest_shape_validated"),
        "synthetic_manifest_patch_name": authorized_payload.get("synthetic_manifest_patch_name"),
        "synthetic_scope": authorized_payload.get("synthetic_manifest_scope"),
        "manifest_member_bytes_read": authorized_payload.get("manifest_member_bytes_read"),
        "manifest_payload_read": authorized_payload.get("manifest_member_payload_read"),
        "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
        "non_manifest_member_bytes_read": authorized_payload.get("non_manifest_member_bytes_read"),
        "readme_payload_read": authorized_payload.get("readme_member_payload_read"),
        "archive_extracted": authorized_payload.get("archive_extracted"),
        "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L23.7 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
