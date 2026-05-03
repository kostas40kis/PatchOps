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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_broad_checkpoint as broad
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_first_controlled_proof as proof

FALSE_FIELDS = (
    "patchops_cli_inspect_invoked_for_archive_manifest",
    "patchops_cli_plan_invoked_for_archive_manifest",
    "patchops_cli_apply_invoked_for_archive_manifest",
    "patchops_cli_run_package_invoked_for_archive_manifest",
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
    "subprocess",
    "zipfile",
)

FORBIDDEN_DIRECT_CALLS = {
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
}

MANIFEST_MEMBER = "bundle/manifest.json"
NON_MANIFEST_MEMBER = "bundle/run_with_patchops.ps1"
MANIFEST_OBJECT = {
    "bundle_schema_version": "synthetic-l25",
    "manifest_version": "1",
    "patch_name": "synthetic_l25_20_patchops_check_fixture",
    "purpose": "patchops-check-only-preflight-proof",
    "synthetic": True,
    "active_profile": "generic_python",
    "target_project_root": str(REPO_ROOT),
    "backup_files": [],
    "files_to_write": [],
    "validation_commands": [],
    "smoke_commands": [],
    "audit_commands": [],
    "cleanup_commands": [],
    "archive_commands": [],
    "failure_policy": {},
    "report_preferences": {"write_to_desktop": False},
    "tags": ["synthetic", "l25_20", "check_only", "dual_compatible"],
    "notes": "Synthetic manifest for L25.21 PatchOps preflight broad checkpoint. It remains compatible with the earlier tiny schema and is never applied.",
}
MANIFEST_PAYLOAD = (json.dumps(MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
CONTROLLED_MEMBERS = {
    MANIFEST_MEMBER: MANIFEST_PAYLOAD,
    NON_MANIFEST_MEMBER: b"# synthetic launcher name only for L25.21 PatchOps preflight broad checkpoint\n",
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
    payload = broad.build_archive_manifest_patchops_preflight_broad_checkpoint(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_patchops_preflight_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_patchops_preflight_broad_checkpoint.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_direct_call_hits = _forbidden_direct_call_hits(source_text)
    false_errors = _false_field_errors(payload)

    _assert(candidate.exists(), "controlled preflight broad zip fixture missing", payload)
    _assert(payload.get("ok") is True, "preflight broad checkpoint payload is not ok", payload)
    _assert(payload.get("patch") == "L25.21", "wrong patch marker", payload)
    _assert(payload.get("broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("archive_manifest_patchops_preflight_ladder_checkpoint") is True, "preflight ladder marker missing", payload)
    _assert(payload.get("l25_archive_manifest_patchops_preflight_ladder_complete") is True, "preflight ladder completion missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l25_20_default_summary", {}).get("patchops_manifest_preflight_performed") is False, "default L25.20 should remain passive", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_preflight_allowed") is True, "authorized L25.20 preflight missing", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("manifest_payload_read") is True, "authorized L25.20 manifest payload read missing", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("manifest_temp_file_written_for_preflight") is True, "authorized L25.20 temp manifest missing", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_manifest_preflight_performed") is True, "authorized L25.20 preflight marker missing", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_manifest_validation_performed") is True, "authorized L25.20 check marker missing", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_cli_check_invoked_for_archive_manifest") is True, "PatchOps check not invoked", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_cli_check_exit_code") == 0, "PatchOps check exit mismatch", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_cli_check_timed_out") is False, "PatchOps check timed out", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_cli_check_ok") is True, "PatchOps check ok missing", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_cli_check_issue_count") == 0, "PatchOps check issue count mismatch", payload)
    _assert(payload.get("source_l25_20_authorized_summary", {}).get("patchops_cli_check_patch_name") == MANIFEST_OBJECT["patch_name"], "PatchOps check patch name mismatch", payload)
    _assert(payload.get("accepted_patchops_preflight_scope") == proof.PATCHOPS_PREFLIGHT_SCOPE, "wrong accepted preflight scope", payload)
    _assert(payload.get("patchops_preflight_scope") == proof.PATCHOPS_PREFLIGHT_SCOPE, "wrong payload preflight scope", payload)
    _assert(payload.get("patchops_cli_check_invoked_for_archive_manifest") is True, "accepted PatchOps check marker missing", payload)
    _assert(payload.get("patchops_cli_check_exit_code") == 0, "accepted PatchOps check exit mismatch", payload)
    _assert(payload.get("patchops_cli_check_ok") is True, "accepted PatchOps check ok missing", payload)
    _assert(payload.get("patchops_cli_check_issue_count") == 0, "accepted PatchOps check issue count mismatch", payload)
    _assert(payload.get("patchops_cli_inspect_invoked_for_archive_manifest") is False, "PatchOps inspect must remain false", payload)
    _assert(payload.get("patchops_cli_plan_invoked_for_archive_manifest") is False, "PatchOps plan must remain false", payload)
    _assert(payload.get("patchops_cli_apply_invoked_for_archive_manifest") is False, "PatchOps apply must remain false", payload)
    _assert(payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is False, "PatchOps run-package must remain false", payload)
    _assert(payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", payload)
    _assert(payload.get("package_execution_allowed") is False, "package execution allowed must remain false", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_patchops_inspect_plan_apply_run_package_added_by_l25_21") is True, "L25.21 should add no inspect/plan/apply/run-package", payload)
    _assert(payload.get("no_package_execution_added_by_l25_21") is True, "L25.21 should add no execution", payload)
    _assert(payload.get("no_archive_extraction_added_by_l25_21") is True, "L25.21 should add no extraction", payload)
    _assert(payload.get("no_browser_permission_added_by_l25_21") is True, "L25.21 should add no browser permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert(not forbidden_direct_call_hits, "forbidden direct preflight/archive/parse/execution calls found: " + ", ".join(forbidden_direct_call_hits), payload)
    _assert("L25.20a dual-compatible controlled fixture repair" in doc_text, "doc missing L25.20a ladder item", payload)
    _assert("PatchOps check is the only PatchOps CLI command invoked against the archive manifest copy" in doc_text, "doc missing check-only boundary", payload)
    _assert("PatchOps inspect is not invoked against the archive manifest copy" in doc_text, "doc missing no inspect boundary", payload)
    _assert("PatchOps plan is not invoked against the archive manifest copy" in doc_text, "doc missing no plan boundary", payload)
    _assert("PatchOps apply is not invoked against the archive manifest copy" in doc_text, "doc missing no apply boundary", payload)
    _assert("PatchOps run-package is not invoked against the archive manifest copy" in doc_text, "doc missing no run-package boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/archive-extract/PatchOps-inspect/PatchOps-plan/PatchOps-apply/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L25.21",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "broad_checkpoint": payload.get("broad_checkpoint"),
        "archive_manifest_patchops_preflight_ladder_complete": payload.get("l25_archive_manifest_patchops_preflight_ladder_complete"),
        "failed_checks": payload.get("failed_checks"),
        "default_patchops_manifest_preflight_performed": payload.get("source_l25_20_default_summary", {}).get("patchops_manifest_preflight_performed"),
        "authorized_patchops_preflight_allowed": payload.get("source_l25_20_authorized_summary", {}).get("patchops_preflight_allowed"),
        "manifest_payload_read": payload.get("manifest_payload_read"),
        "manifest_temp_file_written_for_preflight": payload.get("manifest_temp_file_written_for_preflight"),
        "patchops_manifest_preflight_performed": payload.get("patchops_manifest_preflight_performed"),
        "patchops_manifest_validation_performed": payload.get("patchops_manifest_validation_performed"),
        "patchops_cli_check_invoked_for_archive_manifest": payload.get("patchops_cli_check_invoked_for_archive_manifest"),
        "patchops_cli_check_exit_code": payload.get("patchops_cli_check_exit_code"),
        "patchops_cli_check_timed_out": payload.get("patchops_cli_check_timed_out"),
        "patchops_cli_check_ok": payload.get("patchops_cli_check_ok"),
        "patchops_cli_check_issue_count": payload.get("patchops_cli_check_issue_count"),
        "patchops_cli_check_patch_name": payload.get("patchops_cli_check_patch_name"),
        "accepted_patchops_preflight_scope": payload.get("accepted_patchops_preflight_scope"),
        "patchops_cli_inspect_invoked_for_archive_manifest": payload.get("patchops_cli_inspect_invoked_for_archive_manifest"),
        "patchops_cli_plan_invoked_for_archive_manifest": payload.get("patchops_cli_plan_invoked_for_archive_manifest"),
        "patchops_cli_apply_invoked_for_archive_manifest": payload.get("patchops_cli_apply_invoked_for_archive_manifest"),
        "patchops_cli_run_package_invoked_for_archive_manifest": payload.get("patchops_cli_run_package_invoked_for_archive_manifest"),
        "package_manifest_used_for_execution": payload.get("package_manifest_used_for_execution"),
        "package_execution_allowed": payload.get("package_execution_allowed"),
        "archive_extracted": payload.get("real_archive_candidate_extracted"),
        "browser_started": payload.get("browser_started"),
        "pasteback": payload.get("pasteback_workflow_active"),
        "package_run": payload.get("package_run"),
        "next_patch": payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.21 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
