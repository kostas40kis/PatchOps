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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_apply_broad_checkpoint as broad
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_apply_first_controlled_proof as apply_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_plan_first_controlled_proof as plan_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_inspect_first_controlled_proof as inspect_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_first_controlled_proof as preflight_proof

FALSE_FIELDS = (
    "patchops_cli_run_package_invoked_for_archive_manifest",
    "package_manifest_used_for_execution",
    "package_execution_allowed",
    "archive_member_extracted_to_project",
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
    "notes": "Synthetic manifest for L25.25/L25.27 source-chain readback.",
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
    "tags": ["synthetic", "l25_28", "apply_auth_readback_only", "isolated_fixture"],
    "notes": "Synthetic manifest for L25.28 apply authorization source-chain readback.",
}
APPLY_MANIFEST_OBJECT = {
    "bundle_schema_version": "synthetic-l25",
    "manifest_version": "1",
    "patch_name": "synthetic_l25_29_patchops_apply_fixture",
    "purpose": "patchops-apply-only-zero-write-zero-validation-proof",
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
    "tags": ["synthetic", "l25_30", "apply_broad", "zero_write", "zero_validation", "isolated_fixture"],
    "notes": "Synthetic manifest for L25.30 PatchOps apply broad checkpoint. It has no writes or validations and is never run-package executed.",
}
PREFLIGHT_MANIFEST_PAYLOAD = (json.dumps(PREFLIGHT_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
INSPECT_MANIFEST_PAYLOAD = (json.dumps(INSPECT_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
PLAN_MANIFEST_PAYLOAD = (json.dumps(PLAN_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
APPLY_MANIFEST_PAYLOAD = (json.dumps(APPLY_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
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
    return _write_zip(root / inspect_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, INSPECT_MANIFEST_PAYLOAD, b"# L25.25/L25.27 source-chain inspect fixture\n")


def _refresh_plan_zip_fixture(root: Path) -> Path:
    return _write_zip(root / plan_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, PLAN_MANIFEST_PAYLOAD, b"# L25.28 apply authorization source-chain plan fixture\n")


def _refresh_apply_zip_fixture(root: Path) -> Path:
    return _write_zip(root / apply_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, APPLY_MANIFEST_PAYLOAD, b"# isolated L25.30 PatchOps apply broad checkpoint fixture\n")


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    preflight_candidate = _refresh_preflight_zip_fixture(root)
    inspect_candidate = _refresh_inspect_zip_fixture(root)
    plan_candidate = _refresh_plan_zip_fixture(root)
    apply_candidate = _refresh_apply_zip_fixture(root)
    payload = broad.build_archive_manifest_patchops_apply_broad_checkpoint(root)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_patchops_apply_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_patchops_apply_broad_checkpoint.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_direct_call_hits = _forbidden_direct_call_hits(source_text)
    false_errors = _false_field_errors(payload)

    _assert(preflight_candidate.exists(), "shared preflight source-chain zip fixture missing", payload)
    _assert(inspect_candidate.exists(), "inspect source-chain zip fixture missing", payload)
    _assert(plan_candidate.exists(), "plan source-chain zip fixture missing", payload)
    _assert(apply_candidate.exists(), "isolated apply broad zip fixture missing", payload)
    _assert(payload.get("ok") is True, "apply broad checkpoint payload is not ok", payload)
    _assert(payload.get("patch") == "L25.30", "wrong patch marker", payload)
    _assert(payload.get("broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("archive_manifest_patchops_apply_ladder_checkpoint") is True, "apply ladder marker missing", payload)
    _assert(payload.get("l25_archive_manifest_patchops_apply_ladder_complete") is True, "apply ladder completion missing", payload)
    _assert(payload.get("failed_checks") == [], "failed checks should be empty", payload)
    _assert(payload.get("source_l25_29_default_summary", {}).get("patchops_manifest_apply_performed") is False, "default L25.29 should remain passive", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("patchops_apply_allowed") is True, "authorized L25.29 apply missing", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("manifest_payload_read") is True, "authorized L25.29 manifest payload read missing", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("manifest_payload_json_parsed") is True, "authorized L25.29 manifest parse missing", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("manifest_zero_write_zero_validation") is True, "authorized L25.29 zero guard missing", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("manifest_temp_file_written_for_apply") is True, "authorized L25.29 temp manifest missing", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("patchops_manifest_apply_performed") is True, "authorized L25.29 apply marker missing", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("patchops_manifest_validation_performed") is False, "authorized L25.29 validation marker should be false", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("patchops_cli_apply_invoked_for_archive_manifest") is True, "PatchOps apply not invoked", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("patchops_cli_apply_exit_code") == 0, "PatchOps apply exit mismatch", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("patchops_cli_apply_timed_out") is False, "PatchOps apply timed out", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("patchops_cli_apply_stdout_result_pass") is True, "PatchOps apply PASS marker missing", payload)
    _assert(payload.get("source_l25_29_authorized_summary", {}).get("patchops_cli_apply_patch_name") == APPLY_MANIFEST_OBJECT["patch_name"], "PatchOps apply patch name mismatch", payload)
    _assert(payload.get("accepted_patchops_apply_scope") == apply_proof.PATCHOPS_APPLY_SCOPE, "wrong accepted apply scope", payload)
    _assert(payload.get("patchops_apply_scope") == apply_proof.PATCHOPS_APPLY_SCOPE, "wrong payload apply scope", payload)
    _assert(payload.get("patchops_cli_apply_invoked_for_archive_manifest") is True, "accepted PatchOps apply marker missing", payload)
    _assert(payload.get("patchops_cli_apply_exit_code") == 0, "accepted PatchOps apply exit mismatch", payload)
    _assert(payload.get("patchops_cli_apply_stdout_result_pass") is True, "accepted PatchOps apply PASS marker missing", payload)
    _assert(payload.get("patchops_cli_apply_patch_name") == APPLY_MANIFEST_OBJECT["patch_name"], "accepted PatchOps apply patch name mismatch", payload)
    _assert(payload.get("apply_fixture_isolated_from_preflight_inspect_and_plan_fixtures") is True, "apply fixture isolation marker missing", payload)
    _assert(payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is False, "PatchOps run-package must remain false", payload)
    _assert(payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", payload)
    _assert(payload.get("package_execution_allowed") is False, "package execution allowed must remain false", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("no_patchops_run_package_added_by_l25_30") is True, "L25.30 should add no run-package", payload)
    _assert(payload.get("no_package_execution_added_by_l25_30") is True, "L25.30 should add no execution", payload)
    _assert(payload.get("no_archive_extraction_added_by_l25_30") is True, "L25.30 should add no extraction", payload)
    _assert(payload.get("no_browser_permission_added_by_l25_30") is True, "L25.30 should add no browser permission", payload)
    _assert(not false_errors, "false fields are not false: " + ", ".join(false_errors), payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), payload)
    _assert(not forbidden_direct_call_hits, "forbidden direct apply/archive/parse/execution calls found: " + ", ".join(forbidden_direct_call_hits), payload)
    _assert("PatchOps apply is the only new PatchOps CLI command invoked against the archive manifest copy" in doc_text, "doc missing apply-only boundary", payload)
    _assert("PatchOps run-package is not invoked against the archive manifest copy" in doc_text, "doc missing no run-package boundary", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", payload)
    _assert("No click/download/archive-extract/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", payload)

    return {
        "ok": True,
        "patch": "L25.30",
        "preflight_fixture_refreshed": True,
        "inspect_fixture_refreshed": True,
        "plan_fixture_refreshed": True,
        "apply_fixture_refreshed": True,
        "apply_fixture_isolated_from_preflight_inspect_and_plan_fixtures": True,
        "preflight_fixture_path": str(preflight_candidate),
        "inspect_fixture_path": str(inspect_candidate),
        "plan_fixture_path": str(plan_candidate),
        "apply_fixture_path": str(apply_candidate),
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "broad_checkpoint": payload.get("broad_checkpoint"),
        "archive_manifest_patchops_apply_ladder_complete": payload.get("l25_archive_manifest_patchops_apply_ladder_complete"),
        "failed_checks": payload.get("failed_checks"),
        "default_patchops_manifest_apply_performed": payload.get("source_l25_29_default_summary", {}).get("patchops_manifest_apply_performed"),
        "authorized_patchops_apply_allowed": payload.get("source_l25_29_authorized_summary", {}).get("patchops_apply_allowed"),
        "manifest_payload_read": payload.get("manifest_payload_read"),
        "manifest_payload_json_parsed": payload.get("manifest_payload_json_parsed"),
        "manifest_zero_write_zero_validation": payload.get("manifest_zero_write_zero_validation"),
        "manifest_temp_file_written_for_apply": payload.get("manifest_temp_file_written_for_apply"),
        "patchops_manifest_apply_performed": payload.get("patchops_manifest_apply_performed"),
        "patchops_manifest_validation_performed": payload.get("patchops_manifest_validation_performed"),
        "patchops_cli_apply_invoked_for_archive_manifest": payload.get("patchops_cli_apply_invoked_for_archive_manifest"),
        "patchops_cli_apply_exit_code": payload.get("patchops_cli_apply_exit_code"),
        "patchops_cli_apply_timed_out": payload.get("patchops_cli_apply_timed_out"),
        "patchops_cli_apply_stdout_result_pass": payload.get("patchops_cli_apply_stdout_result_pass"),
        "patchops_cli_apply_patch_name": payload.get("patchops_cli_apply_patch_name"),
        "accepted_patchops_apply_scope": payload.get("accepted_patchops_apply_scope"),
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
    parser = argparse.ArgumentParser(description="L25.30 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
