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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_schema_validation_broad_checkpoint as broad
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
    "zipfile",
)

FORBIDDEN_DIRECT_CALLS = {
    "run_package",
    "apply",
    "execute",
    "extract",
    "extractall",
    "open",
    "testzip",
    "namelist",
    "infolist",
    "read",
    "loads",
}

MANIFEST_MEMBER = "bundle/manifest.json"
NON_MANIFEST_MEMBER = "bundle/run_with_patchops.ps1"
MANIFEST_OBJECT = {
    "bundle_schema_version": "synthetic-l25",
    "manifest_version": "1",
    "patch_name": "synthetic_l25_18_schema_broad_fixture",
    "purpose": "schema-validation-broad-only",
    "synthetic": True,
}
MANIFEST_PAYLOAD = (json.dumps(MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
CONTROLLED_MEMBERS = {
    MANIFEST_MEMBER: MANIFEST_PAYLOAD,
    NON_MANIFEST_MEMBER: b"# synthetic launcher name only for L25.18 schema validation broad checkpoint\n",
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


def _forbidden_direct_call_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        qname = _qualified_call_name(node.func)
        method = qname.rsplit(".", 1)[-1]
        if method in FORBIDDEN_DIRECT_CALLS and qname not in {"json.dumps"}:
            hits.append(qname or method)
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
    payload = broad.build_archive_manifest_schema_validation_broad_checkpoint(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_schema_validation_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_schema_validation_broad_checkpoint.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_direct_call_hits = _forbidden_direct_call_hits(source_text)
    false_errors = _false_field_errors(payload)
    schema_summary = payload.get("manifest_schema_validation_summary") or {}

    _assert(candidate.exists(), "controlled schema broad zip fixture missing", payload)
    _assert(payload.get("ok") is True, "schema broad checkpoint payload is not ok", payload)
    _assert(payload.get("patch") == "L25.18", "wrong patch marker", payload)
    _assert(payload.get("broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("archive_manifest_schema_validation_ladder_checkpoint") is True, "schema ladder marker missing", payload)
    _assert(payload.get("l25_archive_manifest_schema_validation_ladder_complete") is True, "schema ladder completion missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l25_17_default_summary", {}).get("manifest_schema_validated") is False, "default L25.17 should remain passive", payload)
    _assert(payload.get("source_l25_17_authorized_summary", {}).get("schema_validation_allowed") is True, "authorized L25.17 schema validation missing", payload)
    _assert(payload.get("source_l25_17_authorized_summary", {}).get("manifest_payload_json_parsed") is True, "authorized L25.17 JSON parse missing", payload)
    _assert(payload.get("source_l25_17_authorized_summary", {}).get("manifest_payload_schema_validated") is True, "authorized L25.17 payload schema marker missing", payload)
    _assert(payload.get("source_l25_17_authorized_summary", {}).get("manifest_schema_validated") is True, "authorized L25.17 manifest schema marker missing", payload)
    _assert(payload.get("source_l25_17_authorized_summary", {}).get("manifest_validation_performed") is True, "authorized L25.17 manifest validation marker missing", payload)
    _assert(payload.get("source_l25_17_authorized_summary", {}).get("manifest_member_name_read") == MANIFEST_MEMBER, "wrong source manifest member name", payload)
    _assert(payload.get("accepted_schema_validation_scope") == proof.SCHEMA_VALIDATION_SCOPE, "wrong accepted schema validation scope", payload)
    _assert(payload.get("manifest_payload_schema_validated") is True, "manifest payload schema marker should be true", payload)
    _assert(payload.get("manifest_schema_validated") is True, "manifest schema marker should be true", payload)
    _assert(payload.get("manifest_validation_performed") is True, "manifest validation marker should be true for tiny internal schema", payload)
    _assert(schema_summary.get("ok") is True, "schema summary should be ok", payload)
    _assert(schema_summary.get("required_keys") == EXPECTED_REQUIRED_KEYS, "schema required keys mismatch", payload)
    _assert(schema_summary.get("validated_keys") == EXPECTED_REQUIRED_KEYS, "schema validated keys mismatch", payload)
    _assert(schema_summary.get("errors") == [], "schema errors should be empty", payload)
    _assert(payload.get("patchops_manifest_validation_performed") is False, "PatchOps manifest validation must remain false", payload)
    _assert(payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", payload)
    _assert(payload.get("package_execution_allowed") is False, "package execution allowed must remain false", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_patchops_manifest_validation_added_by_l25_18") is True, "L25.18 should add no PatchOps validation", payload)
    _assert(payload.get("no_package_execution_added_by_l25_18") is True, "L25.18 should add no execution", payload)
    _assert(payload.get("no_archive_extraction_added_by_l25_18") is True, "L25.18 should add no extraction", payload)
    _assert(payload.get("no_browser_permission_added_by_l25_18") is True, "L25.18 should add no browser permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert(not forbidden_direct_call_hits, "forbidden direct archive/parse/execution calls found: " + ", ".join(forbidden_direct_call_hits), payload)
    _assert("L25.17 first controlled synthetic manifest tiny internal schema validation proof" in doc_text, "doc missing L25.17 ladder item", payload)
    _assert("Schema validation is a tiny internal synthetic-fixture check only" in doc_text, "doc missing tiny schema boundary", payload)
    _assert("PatchOps manifest validation is not performed" in doc_text, "doc missing no PatchOps validation boundary", payload)
    _assert("The validated manifest is not used for package execution" in doc_text, "doc missing no execution boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/archive-extract/PatchOps-manifest-validation/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L25.18",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "broad_checkpoint": payload.get("broad_checkpoint"),
        "archive_manifest_schema_validation_ladder_complete": payload.get("l25_archive_manifest_schema_validation_ladder_complete"),
        "failed_checks": payload.get("failed_checks"),
        "default_manifest_schema_validated": payload.get("source_l25_17_default_summary", {}).get("manifest_schema_validated"),
        "authorized_schema_validation_allowed": payload.get("source_l25_17_authorized_summary", {}).get("schema_validation_allowed"),
        "manifest_payload_schema_validated": payload.get("manifest_payload_schema_validated"),
        "manifest_schema_validated": payload.get("manifest_schema_validated"),
        "manifest_validation_performed": payload.get("manifest_validation_performed"),
        "manifest_member_name_read": payload.get("manifest_member_name_read"),
        "accepted_schema_validation_scope": payload.get("accepted_schema_validation_scope"),
        "schema_summary_ok": payload.get("accepted_schema_summary_ok"),
        "schema_required_keys": payload.get("accepted_schema_required_keys"),
        "schema_validated_keys": payload.get("accepted_schema_validated_keys"),
        "schema_errors": payload.get("accepted_schema_errors"),
        "patchops_manifest_validation_performed": payload.get("patchops_manifest_validation_performed"),
        "package_manifest_used_for_execution": payload.get("package_manifest_used_for_execution"),
        "package_execution_allowed": payload.get("package_execution_allowed"),
        "archive_extracted": payload.get("real_archive_candidate_extracted"),
        "browser_started": payload.get("browser_started"),
        "pasteback": payload.get("pasteback_workflow_active"),
        "package_run": payload.get("package_run"),
        "next_patch": payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.18 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
