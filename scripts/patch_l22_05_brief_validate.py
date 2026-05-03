from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_first_controlled_manifest_proof as proof

ALWAYS_FALSE_FIELDS = (
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


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in ALWAYS_FALSE_FIELDS if payload.get(name) is not False]


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    default_payload = proof.build_first_controlled_manifest_validation_proof(root)
    authorized_payload = proof.build_first_controlled_manifest_validation_proof(
        root,
        allow_manifest_validation_proof=True,
        authorization_token=proof.REQUIRED_MANIFEST_VALIDATION_PROOF_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_downloaded_archive_manifest_validation_first_controlled_manifest_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_first_controlled_manifest_proof.md"
    fixture_path = root / proof.DEFAULT_SYNTHETIC_MANIFEST_RELATIVE_PATH
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")

    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(default_payload.get("ok") is True, "default payload is not ok")
    _assert(default_payload.get("manifest_validation_execution_allowed") is False, "default execution must be false")
    _assert(default_payload.get("downloaded_manifest_read") is False, "default manifest read must be false")
    _assert(default_payload.get("synthetic_manifest_fixture_read") is False, "default fixture read must be false")
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok")
    _assert(authorized_payload.get("patch") == "L22.5", "wrong patch marker")
    _assert(authorized_payload.get("manifest_validation_execution_allowed") is True, "authorized execution should be true")
    _assert(authorized_payload.get("manifest_validation_performed") is True, "authorized validation should be performed")
    _assert(authorized_payload.get("downloaded_manifest_read") is True, "authorized manifest read should be true")
    _assert(authorized_payload.get("synthetic_manifest_fixture_read") is True, "synthetic fixture should be read")
    _assert(authorized_payload.get("synthetic_manifest_json_parsed") is True, "synthetic JSON should parse")
    _assert(authorized_payload.get("manifest_shape_validated") is True, "manifest shape should be validated")
    _assert(authorized_payload.get("manifest_validation_result") is True, "manifest validation result should be true")
    _assert(authorized_payload.get("manifest_validation_scope") == "synthetic_patchops_runtime_manifest_fixture_only", "wrong validation scope")
    _assert(authorized_payload.get("manifest_summary", {}).get("patch_name") == "l22_05_synthetic_manifest_fixture", "wrong manifest summary patch name")
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors))
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors))
    _assert(not forbidden_import_hits, "forbidden optional imports found: " + ", ".join(forbidden_import_hits))
    _assert(fixture_path.exists(), "synthetic manifest fixture missing")
    _assert("Default readback is passive and does not read the synthetic manifest fixture" in doc_text, "doc missing default passive boundary")
    _assert("Authorized readback reads only the explicit synthetic manifest fixture" in doc_text, "doc missing authorized fixture boundary")
    _assert("No archive extraction" in doc_text, "doc missing no archive extraction boundary")
    _assert("No archive member-byte read" in doc_text, "doc missing no member-byte-read boundary")
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary")
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary")
    _assert("No click/download/archive-extract/member-byte-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary")

    return {
        "ok": True,
        "patch": "L22.5",
        "default_manifest_read": default_payload.get("downloaded_manifest_read"),
        "authorized_manifest_read": authorized_payload.get("downloaded_manifest_read"),
        "manifest_validation_execution_allowed": authorized_payload.get("manifest_validation_execution_allowed"),
        "manifest_validation_result": authorized_payload.get("manifest_validation_result"),
        "manifest_scope": authorized_payload.get("manifest_validation_scope"),
        "manifest_patch_name": authorized_payload.get("manifest_summary", {}).get("patch_name"),
        "archive_extracted": authorized_payload.get("archive_extracted"),
        "member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L22.5 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
