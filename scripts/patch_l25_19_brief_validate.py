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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_authorization_gate as gate
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_schema_validation_first_controlled_proof as schema_proof

FALSE_FIELDS = (
    "archive_manifest_patchops_preflight_authorization_executes_preflight",
    "archive_manifest_patchops_preflight_allowed",
    "patchops_manifest_preflight_performed",
    "patchops_manifest_validation_performed",
    "patchops_cli_check_invoked_for_archive_manifest",
    "patchops_cli_inspect_invoked_for_archive_manifest",
    "patchops_cli_plan_invoked_for_archive_manifest",
    "patchops_cli_apply_invoked_for_archive_manifest",
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
    "zipfile",
    "subprocess",
)

FORBIDDEN_CALL_NAMES = {
    "run",
    "Popen",
    "check_call",
    "check_output",
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
    "load",
}

MANIFEST_MEMBER = "bundle/manifest.json"
NON_MANIFEST_MEMBER = "bundle/run_with_patchops.ps1"
MANIFEST_OBJECT = {
    "bundle_schema_version": "synthetic-l25",
    "manifest_version": "1",
    "patch_name": "synthetic_l25_19_preflight_auth_fixture",
    "purpose": "patchops-preflight-auth-readback-only",
    "synthetic": True,
}
MANIFEST_PAYLOAD = (json.dumps(MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
CONTROLLED_MEMBERS = {
    MANIFEST_MEMBER: MANIFEST_PAYLOAD,
    NON_MANIFEST_MEMBER: b"# synthetic launcher name only for L25.19 preflight auth\n",
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
        if isinstance(node, ast.Call):
            qname = _qualified_call_name(node.func)
            name = qname.rsplit(".", 1)[-1]
            if name in FORBIDDEN_CALL_NAMES and qname not in {"json.dumps"}:
                hits.append(qname or name)
    return sorted(set(hits))


def _refresh_controlled_zip_fixture(root: Path) -> Path:
    candidate = root / schema_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in EXPECTED_MEMBER_NAMES:
            archive.writestr(name, CONTROLLED_MEMBERS[name])
    return candidate


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = _refresh_controlled_zip_fixture(root)
    default_payload = gate.build_archive_manifest_patchops_preflight_authorization_gate(root)
    authorized_payload = gate.build_archive_manifest_patchops_preflight_authorization_gate(
        root,
        allow_archive_manifest_patchops_preflight_authorization=True,
        authorization_token=gate.REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_AUTHORIZATION_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_patchops_preflight_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_patchops_preflight_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_call_hits = _forbidden_call_hits(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled preflight auth zip fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("archive_manifest_patchops_preflight_authorization_granted_for_future_patch") is False, "default should not grant future preflight auth", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.19", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_18_summary", {}).get("ok") is True, "L25.18 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_18_summary", {}).get("broad_checkpoint") is True, "L25.18 broad checkpoint missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_18_summary", {}).get("schema_validation_ladder_complete") is True, "L25.18 schema ladder completion missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_18_summary", {}).get("manifest_schema_validated") is True, "L25.18 schema validation missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_18_summary", {}).get("manifest_validation_performed") is True, "L25.18 internal validation marker missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_18_summary", {}).get("manifest_member_name_read") == MANIFEST_MEMBER, "L25.18 wrong manifest member", authorized_payload)
    _assert(authorized_payload.get("source_l25_18_summary", {}).get("patchops_manifest_validation_performed") is False, "L25.18 PatchOps validation must be false", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_patchops_preflight_authorization_granted_for_future_patch") is True, "future preflight auth should be granted by token", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_patchops_preflight_authorization_readback_only") is True, "preflight auth must be readback-only", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_patchops_preflight_allowed") is False, "preflight allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_manifest_preflight_performed") is False, "PatchOps preflight must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_manifest_validation_performed") is False, "PatchOps manifest validation must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_check_invoked_for_archive_manifest") is False, "PatchOps check must not be invoked for archive manifest", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_inspect_invoked_for_archive_manifest") is False, "PatchOps inspect must not be invoked for archive manifest", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest") is False, "PatchOps plan must not be invoked for archive manifest", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest") is False, "PatchOps apply must not be invoked for archive manifest", authorized_payload)
    _assert(authorized_payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", authorized_payload)
    _assert(authorized_payload.get("package_execution_allowed") is False, "package execution allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_patchops_preflight_execution_added_by_l25_19") is True, "L25.19 should add no preflight execution", authorized_payload)
    _assert(authorized_payload.get("no_patchops_manifest_validation_added_by_l25_19") is True, "L25.19 should add no PatchOps validation", authorized_payload)
    _assert(authorized_payload.get("no_package_execution_added_by_l25_19") is True, "L25.19 should add no execution", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not forbidden_call_hits, "forbidden preflight/archive/parse/execution calls found: " + ", ".join(forbidden_call_hits), authorized_payload)
    _assert("It does not run PatchOps preflight on the archive manifest yet" in doc_text, "doc missing no-preflight-yet statement", authorized_payload)
    _assert("Archive manifest PatchOps-preflight authorization is readback-only" in doc_text, "doc missing readback-only boundary", authorized_payload)
    _assert("PatchOps check/inspect/plan/apply are not invoked against the archive manifest by the browser adapter" in doc_text, "doc missing no CLI invocation boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-extract/PatchOps-preflight/manifest-validation/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.19",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "default_future_patchops_preflight_authorized": default_payload.get("archive_manifest_patchops_preflight_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("archive_manifest_patchops_preflight_authorization_granted_for_future_patch"),
        "source_l25_18_ok": authorized_payload.get("source_l25_18_summary", {}).get("ok"),
        "source_l25_18_broad_checkpoint": authorized_payload.get("source_l25_18_summary", {}).get("broad_checkpoint"),
        "source_l25_18_schema_ladder_complete": authorized_payload.get("source_l25_18_summary", {}).get("schema_validation_ladder_complete"),
        "source_l25_18_manifest_schema_validated": authorized_payload.get("source_l25_18_summary", {}).get("manifest_schema_validated"),
        "source_l25_18_manifest_member_name_read": authorized_payload.get("source_l25_18_summary", {}).get("manifest_member_name_read"),
        "patchops_preflight_allowed": authorized_payload.get("archive_manifest_patchops_preflight_allowed"),
        "patchops_manifest_preflight_performed": authorized_payload.get("patchops_manifest_preflight_performed"),
        "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed"),
        "patchops_cli_check_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_check_invoked_for_archive_manifest"),
        "patchops_cli_inspect_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_inspect_invoked_for_archive_manifest"),
        "patchops_cli_plan_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest"),
        "patchops_cli_apply_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest"),
        "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
        "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
        "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.19 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
