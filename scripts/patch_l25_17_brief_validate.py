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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_schema_validation_first_controlled_proof as proof

FALSE_FIELDS = (
    "patchops_manifest_validation_performed",
    "package_manifest_used_for_execution",
    "package_execution_allowed",
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
    "jsonschema",
)

FORBIDDEN_ARCHIVE_METHODS = {
    "extract",
    "extractall",
    "open",
    "testzip",
    "namelist",
    "infolist",
}

FORBIDDEN_EXECUTION_FUNCTIONS = {
    "run_package",
    "apply",
    "execute",
}

MANIFEST_MEMBER = "bundle/manifest.json"
NON_MANIFEST_MEMBER = "bundle/run_with_patchops.ps1"
MANIFEST_OBJECT = {
    "bundle_schema_version": "synthetic-l25",
    "manifest_version": "1",
    "patch_name": "synthetic_l25_17_schema_validation_fixture",
    "purpose": "schema-validation-proof-only",
    "synthetic": True,
}
MANIFEST_PAYLOAD = (json.dumps(MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
CONTROLLED_MEMBERS = {
    MANIFEST_MEMBER: MANIFEST_PAYLOAD,
    NON_MANIFEST_MEMBER: b"# synthetic launcher name only for L25.17 schema validation proof\n",
}
EXPECTED_MEMBER_NAMES = sorted(CONTROLLED_MEMBERS)
EXPECTED_REQUIRED_KEYS = sorted(MANIFEST_OBJECT.keys())


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
        qname = _qualified_call_name(node.func)
        method = qname.rsplit(".", 1)[-1]
        if method in FORBIDDEN_ARCHIVE_METHODS or method in FORBIDDEN_EXECUTION_FUNCTIONS:
            hits.append(qname or method)
    return sorted(set(hits))


def _read_call_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "read":
            if node.args and isinstance(node.args[0], ast.Name):
                hits.append(node.args[0].id)
            elif node.args and isinstance(node.args[0], ast.Constant):
                hits.append(str(node.args[0].value))
            else:
                hits.append("<dynamic>")
    return hits


def _json_loads_call_count(source_text: str) -> int:
    tree = ast.parse(source_text)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Call) and _qualified_call_name(node.func) == "json.loads")


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
    default_payload = proof.build_archive_manifest_schema_validation_first_controlled_proof(root)
    authorized_payload = proof.build_archive_manifest_schema_validation_first_controlled_proof(
        root,
        allow_archive_manifest_schema_validation_proof=True,
        authorization_token=proof.REQUIRED_ARCHIVE_MANIFEST_SCHEMA_VALIDATION_PROOF_TOKEN,
        candidate_archive_path=str(candidate),
        member_name=MANIFEST_MEMBER,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_schema_validation_first_controlled_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_schema_validation_first_controlled_proof.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_call_hits = _forbidden_call_hits(source_text)
    read_call_hits = _read_call_hits(source_text)
    json_loads_count = _json_loads_call_count(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)
    schema_summary = authorized_payload.get("manifest_schema_validation_summary", {})

    _assert(candidate.exists(), "controlled schema validation zip fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("manifest_schema_validated") is False, "default should not validate schema", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.17", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_16_summary", {}).get("ok") is True, "L25.16 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_16_summary", {}).get("future_schema_validation_authorized") is True, "L25.16 future schema authorization missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_16_summary", {}).get("manifest_schema_validated") is False, "L25.16 must not have validated schema", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_schema_validation_allowed") is True, "schema validation should be allowed", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_read") is True, "manifest payload should be read", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_json_parsed") is True, "manifest JSON should be parsed", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_schema_validated") is True, "manifest payload schema should be validated", authorized_payload)
    _assert(authorized_payload.get("manifest_schema_validated") is True, "manifest schema should be validated", authorized_payload)
    _assert(authorized_payload.get("manifest_validation_performed") is True, "manifest validation marker should be true for tiny internal schema", authorized_payload)
    _assert(authorized_payload.get("manifest_member_name_read") == MANIFEST_MEMBER, "wrong manifest member name read", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_byte_count") == len(MANIFEST_PAYLOAD), "manifest payload byte count mismatch", authorized_payload)
    _assert(authorized_payload.get("manifest_schema_validation_scope") == proof.SCHEMA_VALIDATION_SCOPE, "wrong schema validation scope", authorized_payload)
    _assert(schema_summary.get("ok") is True, "schema summary should be ok", authorized_payload)
    _assert(schema_summary.get("required_keys") == EXPECTED_REQUIRED_KEYS, "schema required keys mismatch", authorized_payload)
    _assert(schema_summary.get("validated_keys") == EXPECTED_REQUIRED_KEYS, "schema validated keys mismatch", authorized_payload)
    _assert(schema_summary.get("errors") == [], "schema errors should be empty", authorized_payload)
    _assert(authorized_payload.get("patchops_manifest_validation_performed") is False, "PatchOps manifest validation must remain false", authorized_payload)
    _assert(authorized_payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", authorized_payload)
    _assert(authorized_payload.get("package_execution_allowed") is False, "package execution allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_patchops_manifest_validation_added_by_l25_17") is True, "L25.17 should add no PatchOps validation", authorized_payload)
    _assert(authorized_payload.get("no_package_execution_added_by_l25_17") is True, "L25.17 should add no execution", authorized_payload)
    _assert(authorized_payload.get("no_archive_extraction_added_by_l25_17") is True, "L25.17 should add no extraction", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l25_17") is True, "L25.17 should add no browser permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not forbidden_call_hits, "forbidden archive/execution calls found: " + ", ".join(forbidden_call_hits), authorized_payload)
    _assert(read_call_hits == ["TARGET_MANIFEST_MEMBER_NAME"], "module must contain exactly one controlled manifest archive read call", authorized_payload)
    _assert(json_loads_count == 1, "module must contain exactly one json.loads parse call", authorized_payload)
    _assert("tiny internal schema" in doc_text, "doc missing tiny internal schema boundary", authorized_payload)
    _assert("PatchOps manifest validation is not performed" in doc_text, "doc missing no PatchOps validation boundary", authorized_payload)
    _assert("The validated manifest is not used for package execution" in doc_text, "doc missing no execution boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-extract/PatchOps-manifest-validation/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.17",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "default_manifest_schema_validated": default_payload.get("manifest_schema_validated"),
        "source_l25_16_ok": authorized_payload.get("source_l25_16_summary", {}).get("ok"),
        "source_l25_16_future_authorized": authorized_payload.get("source_l25_16_summary", {}).get("future_schema_validation_authorized"),
        "schema_validation_allowed": authorized_payload.get("archive_manifest_schema_validation_allowed"),
        "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
        "manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed"),
        "manifest_payload_schema_validated": authorized_payload.get("manifest_payload_schema_validated"),
        "manifest_schema_validated": authorized_payload.get("manifest_schema_validated"),
        "manifest_validation_performed": authorized_payload.get("manifest_validation_performed"),
        "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "manifest_schema_validation_scope": authorized_payload.get("manifest_schema_validation_scope"),
        "schema_summary_ok": schema_summary.get("ok"),
        "schema_required_keys": schema_summary.get("required_keys"),
        "schema_validated_keys": schema_summary.get("validated_keys"),
        "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed"),
        "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
        "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
        "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.17 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
