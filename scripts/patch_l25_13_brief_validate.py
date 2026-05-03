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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_structure_parse_authorization_gate as gate
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_payload_read_first_controlled_proof as manifest_proof

FALSE_FIELDS = (
    "archive_manifest_structure_parse_authorization_executes_parse",
    "archive_manifest_structure_parse_allowed",
    "manifest_payload_json_parsed",
    "manifest_structure_parsed",
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
    "zipfile",
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

FORBIDDEN_PARSE_OR_VALIDATION_FUNCTIONS = {
    "loads",
    "load",
    "validate",
    "check_schema",
    "validate_schema",
    "run_package",
}

MANIFEST_MEMBER = "bundle/manifest.json"
NON_MANIFEST_MEMBER = "bundle/run_with_patchops.ps1"
MANIFEST_PAYLOAD = b'{"synthetic":true,"purpose":"manifest-parse-auth-readback-only","manifest_version":"1"}\n'
CONTROLLED_MEMBERS = {
    MANIFEST_MEMBER: MANIFEST_PAYLOAD,
    NON_MANIFEST_MEMBER: b"# synthetic launcher name only for L25.13 manifest parse auth\n",
}
EXPECTED_MEMBER_NAMES = sorted(CONTROLLED_MEMBERS)


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


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


def _forbidden_call_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = ""
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
            if name in FORBIDDEN_ARCHIVE_METHODS:
                hits.append(_qualified_call_name(node.func))
        elif isinstance(node.func, ast.Name):
            name = node.func.id
        if name in FORBIDDEN_PARSE_OR_VALIDATION_FUNCTIONS:
            qname = _qualified_call_name(node.func)
            if qname not in {"json.dumps"}:
                hits.append(qname or name)
    return sorted(set(hits))


def _refresh_controlled_zip_fixture(root: Path) -> Path:
    candidate = root / manifest_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in EXPECTED_MEMBER_NAMES:
            archive.writestr(name, CONTROLLED_MEMBERS[name])
    return candidate


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = _refresh_controlled_zip_fixture(root)
    default_payload = gate.build_archive_manifest_structure_parse_authorization_gate(root)
    authorized_payload = gate.build_archive_manifest_structure_parse_authorization_gate(
        root,
        allow_archive_manifest_structure_parse_authorization=True,
        authorization_token=gate.REQUIRED_ARCHIVE_MANIFEST_STRUCTURE_PARSE_AUTHORIZATION_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_structure_parse_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_structure_parse_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_call_hits = _forbidden_call_hits(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled manifest parse auth zip fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("archive_manifest_structure_parse_authorization_granted_for_future_patch") is False, "default should not grant future parse auth", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.13", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_12_summary", {}).get("ok") is True, "L25.12 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_12_summary", {}).get("broad_checkpoint") is True, "L25.12 broad checkpoint missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_12_summary", {}).get("manifest_payload_read_ladder_complete") is True, "L25.12 manifest payload ladder completion missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_12_summary", {}).get("manifest_payload_read") is True, "L25.12 manifest payload read missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_12_summary", {}).get("manifest_payload_bytes_read") is True, "L25.12 manifest payload bytes missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_12_summary", {}).get("manifest_member_name_read") == MANIFEST_MEMBER, "L25.12 wrong manifest member", authorized_payload)
    _assert(authorized_payload.get("source_l25_12_summary", {}).get("manifest_payload_json_parsed") is False, "L25.12 JSON parse must be false", authorized_payload)
    _assert(authorized_payload.get("source_l25_12_summary", {}).get("manifest_validation_performed") is False, "L25.12 validation must be false", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_structure_parse_authorization_granted_for_future_patch") is True, "future parse auth should be granted by token", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_structure_parse_authorization_readback_only") is True, "parse auth must be readback-only", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_structure_parse_allowed") is False, "parse allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_json_parsed") is False, "JSON parsing must remain false", authorized_payload)
    _assert(authorized_payload.get("manifest_structure_parsed") is False, "structure parsed must remain false", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_schema_validated") is False, "schema validation must remain false", authorized_payload)
    _assert(authorized_payload.get("manifest_validation_performed") is False, "manifest validation must remain false", authorized_payload)
    _assert(authorized_payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_manifest_structure_parse_execution_added_by_l25_13") is True, "L25.13 should add no parse execution", authorized_payload)
    _assert(authorized_payload.get("no_manifest_schema_validation_added_by_l25_13") is True, "L25.13 should add no schema validation", authorized_payload)
    _assert(authorized_payload.get("no_package_execution_added_by_l25_13") is True, "L25.13 should add no execution", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not forbidden_call_hits, "forbidden parse/validation/archive calls found: " + ", ".join(forbidden_call_hits), authorized_payload)
    _assert("It does not parse the archive manifest payload yet" in doc_text, "doc missing no-parse-yet statement", authorized_payload)
    _assert("Archive manifest structure parse authorization is readback-only" in doc_text, "doc missing readback-only boundary", authorized_payload)
    _assert("Manifest JSON parsing is not performed" in doc_text, "doc missing no JSON parse boundary", authorized_payload)
    _assert("Manifest schema validation is not performed" in doc_text, "doc missing no schema validation boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-extract/manifest-parse/manifest-validation/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.13",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "default_future_manifest_structure_parse_authorized": default_payload.get("archive_manifest_structure_parse_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("archive_manifest_structure_parse_authorization_granted_for_future_patch"),
        "source_l25_12_ok": authorized_payload.get("source_l25_12_summary", {}).get("ok"),
        "source_l25_12_broad_checkpoint": authorized_payload.get("source_l25_12_summary", {}).get("broad_checkpoint"),
        "source_l25_12_manifest_payload_ladder_complete": authorized_payload.get("source_l25_12_summary", {}).get("manifest_payload_read_ladder_complete"),
        "source_l25_12_manifest_payload_read": authorized_payload.get("source_l25_12_summary", {}).get("manifest_payload_read"),
        "source_l25_12_manifest_payload_bytes_read": authorized_payload.get("source_l25_12_summary", {}).get("manifest_payload_bytes_read"),
        "source_l25_12_manifest_member_name_read": authorized_payload.get("source_l25_12_summary", {}).get("manifest_member_name_read"),
        "manifest_structure_parse_allowed": authorized_payload.get("archive_manifest_structure_parse_allowed"),
        "manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed"),
        "manifest_structure_parsed": authorized_payload.get("manifest_structure_parsed"),
        "manifest_payload_schema_validated": authorized_payload.get("manifest_payload_schema_validated"),
        "manifest_validation_performed": authorized_payload.get("manifest_validation_performed"),
        "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
        "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.13 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
