from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# L22.4a repair: when this validator is executed as
# `py scripts/patch_l22_04_brief_validate.py`, Python puts scripts/ on
# sys.path instead of the repository root. Add the repo root explicitly before
# importing PatchOps modules. This is a validator/import bootstrap only; it does
# not read manifests, archives, archive members, browser state, or artifacts.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_controlled_authorization_gate as gate

FALSE_FIELDS = (
    "manifest_validation_execution_allowed",
    "manifest_validation_active",
    "manifest_validation_performed",
    "downloaded_manifest_read",
    "manifest_read",
    "archive_extracted",
    "downloaded_archive_extracted",
    "downloaded_archive_opened",
    "archive_member_bytes_read",
    "member_bytes_read",
    "artifact_content_read",
    "downloaded_file_bytes_read",
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
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def build_validation_payload(repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root).resolve()
    default_payload = gate.build_manifest_validation_controlled_authorization_gate(root)
    authorized_payload = gate.build_manifest_validation_controlled_authorization_gate(
        root,
        allow_manifest_validation_authorization=True,
        authorization_token=gate.REQUIRED_MANIFEST_VALIDATION_AUTHORIZATION_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_downloaded_archive_manifest_validation_controlled_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_controlled_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")

    forbidden_import_hits = [snippet for snippet in FORBIDDEN_IMPORT_SNIPPETS if snippet in source_text]
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(default_payload.get("ok") is True, "default payload is not ok")
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok")
    _assert(default_payload.get("patch") == "L22.4", "wrong patch marker")
    _assert(default_payload.get("source_patch") == "L22.3b", "wrong source patch marker")
    _assert(default_payload.get("manifest_validation_authorization_requested") is False, "default authorization should not be requested")
    _assert(default_payload.get("manifest_validation_authorization_granted_for_future_patch") is False, "default authorization should not be granted")
    _assert(authorized_payload.get("manifest_validation_authorization_requested") is True, "authorized readback should be requested")
    _assert(authorized_payload.get("manifest_validation_authorization_token_valid") is True, "authorization token should be valid")
    _assert(authorized_payload.get("manifest_validation_authorization_granted_for_future_patch") is True, "future authorization should be granted in readback")
    _assert(not default_false_errors, "default payload has non-false safety fields: " + ", ".join(default_false_errors))
    _assert(not authorized_false_errors, "authorized payload has non-false safety fields: " + ", ".join(authorized_false_errors))
    _assert(not forbidden_import_hits, "forbidden optional imports found: " + ", ".join(forbidden_import_hits))
    _assert("Manifest validation execution allowed: false" in doc_text, "doc missing execution false boundary")
    _assert("Downloaded manifest is not read" in doc_text, "doc missing no manifest read boundary")
    _assert("Archive extraction is not performed" in doc_text, "doc missing no archive extraction boundary")
    _assert("Archive member bytes are not read" in doc_text, "doc missing no member-byte-read boundary")
    _assert("No Edge start" in doc_text, "doc missing no Edge start boundary")
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary")
    _assert("No click/download/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary")

    return {
        "ok": True,
        "patch": "L22.4",
        "repair_patch": "L22.4a",
        "repair": "validator direct-script import bootstrap",
        "default_authorized": default_payload.get("manifest_validation_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("manifest_validation_authorization_granted_for_future_patch"),
        "manifest_validation_execution_allowed": authorized_payload.get("manifest_validation_execution_allowed"),
        "manifest_read": authorized_payload.get("downloaded_manifest_read"),
        "archive_extracted": authorized_payload.get("archive_extracted"),
        "member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L22.4 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
