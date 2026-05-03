from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_payload_read_broad_checkpoint as broad
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_payload_read_first_controlled_proof as proof

FALSE_FIELDS = (
    "manifest_payload_json_parsed",
    "manifest_payload_schema_validated",
    "manifest_validation_performed",
    "package_manifest_used_for_execution",
    "real_downloaded_manifest_read",
    "real_downloaded_artifact_read",
    "real_archive_candidate_extracted",
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

FORBIDDEN_ARCHIVE_METHODS = {
    "extract",
    "extractall",
    "open",
    "testzip",
    "namelist",
    "infolist",
    "read",
}

FORBIDDEN_VALIDATION_FUNCTIONS = {
    "validate",
    "check_schema",
    "validate_schema",
    "run_package",
}

MANIFEST_MEMBER = "bundle/manifest.json"
NON_MANIFEST_MEMBER = "bundle/run_with_patchops.ps1"
MANIFEST_PAYLOAD = b'{"synthetic":true,"purpose":"manifest-payload-read-broad-checkpoint-only","manifest_version":"1"}\n'
CONTROLLED_MEMBERS = {
    MANIFEST_MEMBER: MANIFEST_PAYLOAD,
    NON_MANIFEST_MEMBER: b"# synthetic launcher name only for L25.12 manifest payload broad checkpoint\n",
}
EXPECTED_MEMBER_NAMES = sorted(CONTROLLED_MEMBERS)
EXPECTED_SHA256 = hashlib.sha256(MANIFEST_PAYLOAD).hexdigest()


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _qualified_call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _qualified_call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


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


def _forbidden_direct_archive_method_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_ARCHIVE_METHODS:
                hits.append(node.func.attr)
    return sorted(set(hits))


def _validation_call_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        qualified = _qualified_call_name(node.func)
        if qualified in {"json.load", "json.loads"}:
            hits.append(qualified)
        elif name in FORBIDDEN_VALIDATION_FUNCTIONS:
            hits.append(qualified or name)
    return sorted(set(hits))


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
    payload = broad.build_archive_manifest_payload_read_broad_checkpoint(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_payload_read_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_payload_read_broad_checkpoint.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_archive_method_hits = _forbidden_direct_archive_method_hits(source_text)
    validation_call_hits = _validation_call_hits(source_text)
    false_errors = _false_field_errors(payload)

    _assert(candidate.exists(), "controlled manifest payload zip fixture missing", payload)
    _assert(payload.get("ok") is True, "manifest payload broad checkpoint payload is not ok", payload)
    _assert(payload.get("patch") == "L25.12", "wrong patch marker", payload)
    _assert(payload.get("broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("archive_manifest_payload_read_ladder_checkpoint") is True, "manifest payload read ladder marker missing", payload)
    _assert(payload.get("l25_archive_manifest_payload_read_ladder_complete") is True, "manifest payload read ladder completion missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l25_11_default_summary", {}).get("manifest_payload_read") is False, "default L25.11 should remain passive", payload)
    _assert(payload.get("source_l25_11_authorized_summary", {}).get("manifest_payload_read") is True, "authorized L25.11 manifest payload missing", payload)
    _assert(payload.get("source_l25_11_authorized_summary", {}).get("manifest_payload_bytes_read") is True, "authorized L25.11 manifest bytes marker missing", payload)
    _assert(payload.get("source_l25_11_authorized_summary", {}).get("manifest_payload_sha256_read") is True, "authorized L25.11 manifest sha256 marker missing", payload)
    _assert(payload.get("source_l25_11_authorized_summary", {}).get("manifest_member_name_read") == MANIFEST_MEMBER, "wrong source manifest member name", payload)
    _assert(payload.get("accepted_manifest_payload_read_scope") == "controlled_runtime_manifest_payload_bytes_only_no_validation_no_execution", "wrong accepted manifest read scope", payload)
    _assert(payload.get("accepted_manifest_member_name_read") == MANIFEST_MEMBER, "wrong accepted manifest member name", payload)
    _assert(payload.get("manifest_payload_read") is True, "manifest payload should be true", payload)
    _assert(payload.get("manifest_payload_bytes_read") is True, "manifest payload bytes should be true", payload)
    _assert(payload.get("manifest_payload_sha256_read") is True, "manifest sha256 marker should be true", payload)
    _assert(payload.get("manifest_payload_byte_count") == len(MANIFEST_PAYLOAD), "manifest byte count mismatch", payload)
    _assert(payload.get("manifest_payload_sha256") == EXPECTED_SHA256, "manifest sha256 mismatch", payload)
    _assert(payload.get("manifest_payload_json_parsed") is False, "manifest JSON parsing must remain false", payload)
    _assert(payload.get("manifest_payload_schema_validated") is False, "manifest schema validation must remain false", payload)
    _assert(payload.get("manifest_validation_performed") is False, "manifest validation must remain false", payload)
    _assert(payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_manifest_json_parse_or_validation_added_by_l25_12") is True, "L25.12 should add no JSON parse/validation", payload)
    _assert(payload.get("no_archive_extraction_added_by_l25_12") is True, "L25.12 should add no extraction", payload)
    _assert(payload.get("no_browser_permission_added_by_l25_12") is True, "L25.12 should add no browser permission", payload)
    _assert(payload.get("no_pasteback_or_package_run_permission_added_by_l25_12") is True, "L25.12 should add no pasteback/package permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert(not forbidden_archive_method_hits, "forbidden direct archive method calls found: " + ", ".join(forbidden_archive_method_hits), payload)
    _assert(not validation_call_hits, "forbidden validation calls found: " + ", ".join(validation_call_hits), payload)
    _assert("L25.11a validator AST scan repair" in doc_text, "doc missing L25.11a ladder item", payload)
    _assert("Manifest payload bytes are read, but manifest JSON parsing is not performed" in doc_text, "doc missing no JSON parse boundary", payload)
    _assert("Manifest schema validation is not performed" in doc_text, "doc missing no schema validation boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/archive-extract/manifest-validation/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L25.12",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "broad_checkpoint": payload.get("broad_checkpoint"),
        "archive_manifest_payload_read_ladder_complete": payload.get("l25_archive_manifest_payload_read_ladder_complete"),
        "failed_checks": payload.get("failed_checks"),
        "default_manifest_payload_read": payload.get("source_l25_11_default_summary", {}).get("manifest_payload_read"),
        "authorized_manifest_payload_read": payload.get("source_l25_11_authorized_summary", {}).get("manifest_payload_read"),
        "manifest_payload_bytes_read": payload.get("manifest_payload_bytes_read"),
        "manifest_payload_sha256_read": payload.get("manifest_payload_sha256_read"),
        "manifest_payload_sha256_matches": payload.get("manifest_payload_sha256") == EXPECTED_SHA256,
        "manifest_payload_byte_count": payload.get("manifest_payload_byte_count"),
        "manifest_member_name_read": payload.get("manifest_member_name_read"),
        "accepted_manifest_payload_read_scope": payload.get("accepted_manifest_payload_read_scope"),
        "manifest_payload_json_parsed": payload.get("manifest_payload_json_parsed"),
        "manifest_payload_schema_validated": payload.get("manifest_payload_schema_validated"),
        "manifest_validation_performed": payload.get("manifest_validation_performed"),
        "package_manifest_used_for_execution": payload.get("package_manifest_used_for_execution"),
        "archive_extracted": payload.get("real_archive_candidate_extracted"),
        "browser_started": payload.get("browser_started"),
        "pasteback": payload.get("pasteback_workflow_active"),
        "package_run": payload.get("package_run"),
        "next_patch": payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.12 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
