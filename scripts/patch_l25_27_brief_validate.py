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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_plan_broad_checkpoint as broad
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_plan_first_controlled_proof as plan_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_inspect_first_controlled_proof as inspect_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_first_controlled_proof as preflight_proof

FALSE_FIELDS = (
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
PREFLIGHT_MANIFEST_OBJECT = {
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
    "notes": "Synthetic manifest for shared L25.20/L25.21/L25.22 source chain. It is never applied.",
}
INSPECT_MANIFEST_OBJECT = {
    "bundle_schema_version": "synthetic-l25",
    "manifest_version": "1",
    "patch_name": "synthetic_l25_23_patchops_inspect_fixture",
    "purpose": "patchops-inspect-only-proof",
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
    "tags": ["synthetic", "l25_25", "plan_auth_readback_only", "isolated_fixture"],
    "notes": "Synthetic manifest for L25.25 plan authorization source-chain readback. It is never planned or applied by L25.25.",
}
PLAN_MANIFEST_OBJECT = {
    "bundle_schema_version": "synthetic-l25",
    "manifest_version": "1",
    "patch_name": "synthetic_l25_26_patchops_plan_fixture",
    "purpose": "patchops-plan-only-proof",
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
    "tags": ["synthetic", "l25_27", "plan_broad", "isolated_fixture"],
    "notes": "Synthetic manifest for L25.27 PatchOps plan broad checkpoint. It has no writes or validations and is never applied.",
}
PREFLIGHT_MANIFEST_PAYLOAD = (json.dumps(PREFLIGHT_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
INSPECT_MANIFEST_PAYLOAD = (json.dumps(INSPECT_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
PLAN_MANIFEST_PAYLOAD = (json.dumps(PLAN_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
EXPECTED_MEMBER_NAMES = [MANIFEST_MEMBER, NON_MANIFEST_MEMBER]


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


def _write_zip(path: Path, payload: bytes, note: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(MANIFEST_MEMBER, payload)
        archive.writestr(NON_MANIFEST_MEMBER, note)
    return path


def _refresh_preflight_zip_fixture(root: Path) -> Path:
    return _write_zip(root / preflight_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, PREFLIGHT_MANIFEST_PAYLOAD, b"# shared L25.20/L25.21/L25.22 source-chain fixture\n")


def _refresh_inspect_zip_fixture(root: Path) -> Path:
    return _write_zip(root / inspect_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, INSPECT_MANIFEST_PAYLOAD, b"# L25.25 plan authorization source-chain fixture\n")


def _refresh_plan_zip_fixture(root: Path) -> Path:
    return _write_zip(root / plan_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, PLAN_MANIFEST_PAYLOAD, b"# isolated L25.27 PatchOps plan broad checkpoint fixture\n")


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    preflight_candidate = _refresh_preflight_zip_fixture(root)
    inspect_candidate = _refresh_inspect_zip_fixture(root)
    plan_candidate = _refresh_plan_zip_fixture(root)
    payload = broad.build_archive_manifest_patchops_plan_broad_checkpoint(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_patchops_plan_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_patchops_plan_broad_checkpoint.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_direct_call_hits = _forbidden_direct_call_hits(source_text)
    false_errors = _false_field_errors(payload)

    _assert(preflight_candidate.exists(), "shared preflight source-chain zip fixture missing", payload)
    _assert(inspect_candidate.exists(), "inspect source-chain zip fixture missing", payload)
    _assert(plan_candidate.exists(), "isolated plan broad zip fixture missing", payload)
    _assert(str(plan_candidate.resolve()) != str(preflight_candidate.resolve()), "plan fixture must differ from preflight fixture")
    _assert(str(plan_candidate.resolve()) != str(inspect_candidate.resolve()), "plan fixture must differ from inspect fixture")
    _assert(payload.get("ok") is True, "plan broad checkpoint payload is not ok", payload)
    _assert(payload.get("patch") == "L25.27", "wrong patch marker", payload)
    _assert(payload.get("broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("archive_manifest_patchops_plan_ladder_checkpoint") is True, "plan ladder marker missing", payload)
    _assert(payload.get("l25_archive_manifest_patchops_plan_ladder_complete") is True, "plan ladder completion missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l25_26_default_summary", {}).get("patchops_manifest_plan_performed") is False, "default L25.26 should remain passive", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_plan_allowed") is True, "authorized L25.26 plan missing", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("manifest_payload_read") is True, "authorized L25.26 manifest payload read missing", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("manifest_temp_file_written_for_plan") is True, "authorized L25.26 temp manifest missing", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_manifest_plan_performed") is True, "authorized L25.26 plan marker missing", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_manifest_validation_performed") is False, "authorized L25.26 validation marker should be false", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_invoked_for_archive_manifest") is True, "PatchOps plan not invoked", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_exit_code") == 0, "PatchOps plan exit mismatch", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_timed_out") is False, "PatchOps plan timed out", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_json_object") is True, "PatchOps plan JSON object missing", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_patch_name") == PLAN_MANIFEST_OBJECT["patch_name"], "PatchOps plan patch name mismatch", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_active_profile") == "generic_python", "PatchOps plan active profile mismatch", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_manifest_version") == "1", "PatchOps plan manifest version mismatch", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_mode") == "apply", "PatchOps plan mode mismatch", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_target_files") == [], "PatchOps plan target files should be empty", payload)
    _assert(payload.get("source_l25_26_authorized_summary", {}).get("patchops_cli_plan_validation_commands") == [], "PatchOps plan validation commands should be empty", payload)
    _assert(payload.get("accepted_patchops_plan_scope") == plan_proof.PATCHOPS_PLAN_SCOPE, "wrong accepted plan scope", payload)
    _assert(payload.get("patchops_plan_scope") == plan_proof.PATCHOPS_PLAN_SCOPE, "wrong payload plan scope", payload)
    _assert(payload.get("patchops_cli_plan_invoked_for_archive_manifest") is True, "accepted PatchOps plan marker missing", payload)
    _assert(payload.get("patchops_cli_plan_exit_code") == 0, "accepted PatchOps plan exit mismatch", payload)
    _assert(payload.get("patchops_cli_plan_json_object") is True, "accepted PatchOps plan JSON marker missing", payload)
    _assert(payload.get("patchops_cli_plan_patch_name") == PLAN_MANIFEST_OBJECT["patch_name"], "accepted PatchOps plan patch name mismatch", payload)
    _assert(payload.get("plan_fixture_isolated_from_preflight_and_inspect_fixtures") is True, "plan fixture isolation marker missing", payload)
    _assert(payload.get("patchops_cli_apply_invoked_for_archive_manifest") is False, "PatchOps apply must remain false", payload)
    _assert(payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is False, "PatchOps run-package must remain false", payload)
    _assert(payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", payload)
    _assert(payload.get("package_execution_allowed") is False, "package execution allowed must remain false", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_patchops_apply_run_package_added_by_l25_27") is True, "L25.27 should add no apply/run-package", payload)
    _assert(payload.get("no_package_execution_added_by_l25_27") is True, "L25.27 should add no execution", payload)
    _assert(payload.get("no_archive_extraction_added_by_l25_27") is True, "L25.27 should add no extraction", payload)
    _assert(payload.get("no_browser_permission_added_by_l25_27") is True, "L25.27 should add no browser permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert(not forbidden_direct_call_hits, "forbidden direct plan/archive/parse/execution calls found: " + ", ".join(forbidden_direct_call_hits), payload)
    _assert("PatchOps plan is the only new PatchOps CLI command invoked against the archive manifest copy" in doc_text, "doc missing plan-only boundary", payload)
    _assert("PatchOps apply is not invoked against the archive manifest copy" in doc_text, "doc missing no apply boundary", payload)
    _assert("PatchOps run-package is not invoked against the archive manifest copy" in doc_text, "doc missing no run-package boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/archive-extract/PatchOps-apply/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L25.27",
        "preflight_fixture_refreshed": True,
        "inspect_fixture_refreshed": True,
        "plan_fixture_refreshed": True,
        "plan_fixture_isolated_from_preflight_and_inspect_fixtures": True,
        "preflight_fixture_path": str(preflight_candidate),
        "inspect_fixture_path": str(inspect_candidate),
        "plan_fixture_path": str(plan_candidate),
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "broad_checkpoint": payload.get("broad_checkpoint"),
        "archive_manifest_patchops_plan_ladder_complete": payload.get("l25_archive_manifest_patchops_plan_ladder_complete"),
        "failed_checks": payload.get("failed_checks"),
        "default_patchops_manifest_plan_performed": payload.get("source_l25_26_default_summary", {}).get("patchops_manifest_plan_performed"),
        "authorized_patchops_plan_allowed": payload.get("source_l25_26_authorized_summary", {}).get("patchops_plan_allowed"),
        "manifest_payload_read": payload.get("manifest_payload_read"),
        "manifest_temp_file_written_for_plan": payload.get("manifest_temp_file_written_for_plan"),
        "patchops_manifest_plan_performed": payload.get("patchops_manifest_plan_performed"),
        "patchops_manifest_validation_performed": payload.get("patchops_manifest_validation_performed"),
        "patchops_cli_plan_invoked_for_archive_manifest": payload.get("patchops_cli_plan_invoked_for_archive_manifest"),
        "patchops_cli_plan_exit_code": payload.get("patchops_cli_plan_exit_code"),
        "patchops_cli_plan_timed_out": payload.get("patchops_cli_plan_timed_out"),
        "patchops_cli_plan_json_object": payload.get("patchops_cli_plan_json_object"),
        "patchops_cli_plan_patch_name": payload.get("patchops_cli_plan_patch_name"),
        "patchops_cli_plan_active_profile": payload.get("accepted_patchops_cli_plan_active_profile"),
        "patchops_cli_plan_manifest_version": payload.get("accepted_patchops_cli_plan_manifest_version"),
        "patchops_cli_plan_mode": payload.get("accepted_patchops_cli_plan_mode"),
        "patchops_cli_plan_target_files": payload.get("accepted_patchops_cli_plan_target_files"),
        "patchops_cli_plan_validation_commands": payload.get("accepted_patchops_cli_plan_validation_commands"),
        "accepted_patchops_plan_scope": payload.get("accepted_patchops_plan_scope"),
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
    parser = argparse.ArgumentParser(description="L25.27 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
