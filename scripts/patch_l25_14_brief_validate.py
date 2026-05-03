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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_structure_parse_first_controlled_proof as proof

FALSE_FIELDS = (
    "manifest_payload_schema_validated",
    "manifest_validation_performed",
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
)

FORBIDDEN_ARCHIVE_METHODS = {
    "extract",
    "extractall",
    "open",
    "testzip",
    "namelist",
    "infolist",
}

FORBIDDEN_VALIDATION_FUNCTIONS = {
    "validate",
    "check_schema",
    "validate_schema",
    "run_package",
}

MANIFEST_MEMBER = "bundle/manifest.json"
NON_MANIFEST_MEMBER = "bundle/run_with_patchops.ps1"
MANIFEST_OBJECT = {
    "bundle_schema_version": "synthetic-l25",
    "manifest_version": "1",
    "patch_name": "synthetic_l25_14_manifest_parse_fixture",
    "purpose": "structure-parse-only",
    "synthetic": True,
}
MANIFEST_PAYLOAD = (json.dumps(MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
CONTROLLED_MEMBERS = {
    MANIFEST_MEMBER: MANIFEST_PAYLOAD,
    NON_MANIFEST_MEMBER: b"# synthetic launcher name only for L25.14 manifest structure parse proof\n",
}
EXPECTED_MEMBER_NAMES = sorted(CONTROLLED_MEMBERS)
EXPECTED_TOP_LEVEL_KEYS = sorted(MANIFEST_OBJECT.keys())


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


def _archive_method_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_ARCHIVE_METHODS:
                hits.append(_qualified_call_name(node.func))
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
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _qualified_call_name(node.func) == "json.loads":
            count += 1
    return count


def _validation_call_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        qname = _qualified_call_name(node.func)
        name = qname.rsplit(".", 1)[-1]
        if name in FORBIDDEN_VALIDATION_FUNCTIONS:
            hits.append(qname or name)
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
    default_payload = proof.build_archive_manifest_structure_parse_first_controlled_proof(root)
    authorized_payload = proof.build_archive_manifest_structure_parse_first_controlled_proof(
        root,
        allow_archive_manifest_structure_parse_proof=True,
        authorization_token=proof.REQUIRED_ARCHIVE_MANIFEST_STRUCTURE_PARSE_PROOF_TOKEN,
        candidate_archive_path=str(candidate),
        member_name=MANIFEST_MEMBER,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_structure_parse_first_controlled_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_structure_parse_first_controlled_proof.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_archive_method_hits = _archive_method_hits(source_text)
    read_call_hits = _read_call_hits(source_text)
    json_loads_count = _json_loads_call_count(source_text)
    validation_call_hits = _validation_call_hits(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)
    summary = authorized_payload.get("manifest_structure_summary", {})

    _assert(candidate.exists(), "controlled manifest parse zip fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("manifest_payload_json_parsed") is False, "default should not parse manifest JSON", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.14", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_13_summary", {}).get("ok") is True, "L25.13 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_13_summary", {}).get("future_manifest_structure_parse_authorized") is True, "L25.13 future parse authorization missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_13_summary", {}).get("manifest_payload_json_parsed") is False, "L25.13 must not have parsed JSON", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_structure_parse_allowed") is True, "structure parse should be allowed", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_read") is True, "manifest payload should be read", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_bytes_read") is True, "manifest payload bytes marker should be true", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_json_parsed") is True, "manifest JSON should be parsed", authorized_payload)
    _assert(authorized_payload.get("manifest_structure_parsed") is True, "manifest structure should be parsed", authorized_payload)
    _assert(authorized_payload.get("manifest_member_name_read") == MANIFEST_MEMBER, "wrong manifest member name read", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_byte_count") == len(MANIFEST_PAYLOAD), "manifest payload byte count mismatch", authorized_payload)
    _assert(authorized_payload.get("manifest_structure_parse_scope") == proof.MANIFEST_STRUCTURE_PARSE_SCOPE, "wrong manifest structure parse scope", authorized_payload)
    _assert(summary.get("top_level_type") == "object", "manifest structure top-level type should be object", authorized_payload)
    _assert(summary.get("top_level_keys") == EXPECTED_TOP_LEVEL_KEYS, "manifest structure keys mismatch", authorized_payload)
    _assert(isinstance(summary.get("scalar_value_types"), dict), "scalar value type summary missing", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_schema_validated") is False, "schema validation must remain false", authorized_payload)
    _assert(authorized_payload.get("manifest_validation_performed") is False, "manifest validation must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_manifest_validation_performed") is False, "PatchOps manifest validation must remain false", authorized_payload)
    _assert(authorized_payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", authorized_payload)
    _assert(authorized_payload.get("package_execution_allowed") is False, "package execution allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_manifest_schema_validation_added_by_l25_14") is True, "L25.14 should add no schema validation", authorized_payload)
    _assert(authorized_payload.get("no_package_execution_added_by_l25_14") is True, "L25.14 should add no execution", authorized_payload)
    _assert(authorized_payload.get("no_archive_extraction_added_by_l25_14") is True, "L25.14 should add no extraction", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l25_14") is True, "L25.14 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l25_14") is True, "L25.14 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not forbidden_archive_method_hits, "forbidden archive method calls found: " + ", ".join(forbidden_archive_method_hits), authorized_payload)
    _assert(not validation_call_hits, "forbidden validation calls found: " + ", ".join(validation_call_hits), authorized_payload)
    _assert(read_call_hits == ["TARGET_MANIFEST_MEMBER_NAME"], "module must contain exactly one controlled manifest archive read call", authorized_payload)
    _assert(json_loads_count == 1, "module must contain exactly one json.loads parse call", authorized_payload)
    _assert("report non-sensitive structural metadata only" in doc_text, "doc missing structure metadata boundary", authorized_payload)
    _assert("Manifest schema validation is not performed" in doc_text, "doc missing no schema validation boundary", authorized_payload)
    _assert("PatchOps manifest validation is not performed" in doc_text, "doc missing no PatchOps validation boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-extract/manifest-validation/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.14",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "default_manifest_payload_json_parsed": default_payload.get("manifest_payload_json_parsed"),
        "source_l25_13_ok": authorized_payload.get("source_l25_13_summary", {}).get("ok"),
        "source_l25_13_future_authorized": authorized_payload.get("source_l25_13_summary", {}).get("future_manifest_structure_parse_authorized"),
        "manifest_structure_parse_allowed": authorized_payload.get("archive_manifest_structure_parse_allowed"),
        "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
        "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read"),
        "manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed"),
        "manifest_structure_parsed": authorized_payload.get("manifest_structure_parsed"),
        "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
        "manifest_structure_parse_scope": authorized_payload.get("manifest_structure_parse_scope"),
        "manifest_top_level_type": summary.get("top_level_type"),
        "manifest_top_level_keys": summary.get("top_level_keys"),
        "manifest_payload_schema_validated": authorized_payload.get("manifest_payload_schema_validated"),
        "manifest_validation_performed": authorized_payload.get("manifest_validation_performed"),
        "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed"),
        "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
        "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.14 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
