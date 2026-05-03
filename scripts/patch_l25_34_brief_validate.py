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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_package_run_final_acceptance_marker as final_marker
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_package_run_broad_checkpoint_key_repair as broad33a
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_package_run_first_controlled_proof_shape_repair2 as proof32b

FALSE_FIELDS = (
    "real_downloaded_manifest_read",
    "real_downloaded_artifact_read",
    "adapter_archive_extraction_performed",
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
    "localhost_server_started",
    "browser_extension_used",
    "git_commit_performed",
    "git_push_performed",
)

RUNPKG_LAUNCHER = "bundle/run_with_patchops.ps1"
RUNPKG_META = "bundle/bundle_meta.json"
RUNPKG_README = "bundle/README.txt"
RUNPKG_MANIFEST = "bundle/manifest.json"
RUNPKG_CONTENT = "bundle/content/.keep"
REQUIRED_NAMES = [RUNPKG_LAUNCHER, RUNPKG_META, RUNPKG_README, RUNPKG_MANIFEST, RUNPKG_CONTENT]

RUN_WITH_PATCHOPS_PS1 = """param(
    [string]$WrapperRoot = '',
    [string]$WrapperRepoRoot = '',
    [string]$RepoRoot = '',
    [string]$PackageRoot = ''
)
$ErrorActionPreference = 'Stop'
$Desktop = [Environment]::GetFolderPath('Desktop')
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$ReportPath = Join-Path $Desktop ("synthetic_l25_34_run_package_launcher_{0}.txt" -f $Stamp)
$Lines = @(
    'L25.34 synthetic run-package final acceptance launcher proof',
    'Patch Name : synthetic_l25_34_run_package_fixture',
    'Scope : controlled synthetic launcher only',
    'Browser Started : false',
    'Pasteback : false',
    'Package writes : none',
    'ExitCode : 0',
    'Result : PASS',
    'L25_32B_RUN_PACKAGE_LAUNCHER_MARKER'
)
Set-Content -LiteralPath $ReportPath -Value $Lines -Encoding UTF8
Write-Host ('Report Path        : {0}' -f $ReportPath)
Write-Host 'L25_32B_RUN_PACKAGE_LAUNCHER_MARKER'
Write-Host 'Result : PASS'
exit 0
"""


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _qualified_call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _qualified_call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _forbidden_import_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    forbidden = {"selenium", "webdriver_manager", "pyperclip", "psutil", "subprocess", "zipfile"}
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in forbidden:
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".", 1)[0] in forbidden:
                hits.append(node.module or "")
    return sorted(set(hits))


def _forbidden_call_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    forbidden = {"extract", "extractall", "execute", "run", "Popen", "check_call", "check_output"}
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            qname = _qualified_call_name(node.func)
            method = qname.rsplit(".", 1)[-1]
            if method in forbidden:
                hits.append(qname or method)
    return sorted(set(hits))


def _manifest(root: Path) -> dict[str, Any]:
    return {
        "bundle_schema_version": "synthetic-l25",
        "manifest_version": "1",
        "patch_name": "synthetic_l25_34_run_package_fixture",
        "synthetic": True,
        "active_profile": "generic_python",
        "target_project_root": str(root),
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {"write_to_desktop": False},
    }


def _refresh_runpkg_zip_fixture(root: Path) -> Path:
    path = root / proof32b.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema_version": "1",
        "bundle_schema_version": "1",
        "patch_name": "synthetic_l25_34_run_package_fixture",
        "bundle_mode": "launcher_direct_synthetic_final_acceptance_marker",
        "wrapper_project_root": str(root),
        "target_project": "patchops",
        "target_project_root": str(root),
        "launcher_path": "run_with_patchops.ps1",
        "manifest_path": "manifest.json",
        "content_root": "content",
        "active_profile": "generic_python",
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(RUNPKG_LAUNCHER, RUN_WITH_PATCHOPS_PS1)
        archive.writestr(RUNPKG_META, json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        archive.writestr(RUNPKG_MANIFEST, json.dumps(_manifest(root), sort_keys=True, separators=(",", ":")) + "\n")
        archive.writestr(RUNPKG_README, "L25.34 controlled synthetic final acceptance marker. No target writes.\n")
        archive.writestr(RUNPKG_CONTENT, "synthetic content marker only\n")
    return path


def _zip_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path, "r") as archive:
        return sorted(archive.namelist())


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _validate_final_payload(payload: dict[str, Any]) -> None:
    _assert(payload.get("ok") is True, "final marker payload is not ok", payload)
    _assert(payload.get("patch") == "L25.34", "wrong patch marker", payload)
    _assert(payload.get("final_acceptance_marker") is True, "final acceptance marker missing", payload)
    _assert(payload.get("controlled_package_run_ladder_final_acceptance") is True, "final package-run ladder acceptance missing", payload)
    _assert(payload.get("accepted_l25_32b_controlled_run_package_proof") is True, "L25.32b accepted proof marker missing", payload)
    _assert(payload.get("accepted_l25_33a_key_normalized_broad_checkpoint") is True, "L25.33a accepted broad marker missing", payload)
    src = payload.get("source_l25_33a_summary", {})
    _assert(src.get("ok") is True, "source L25.33a ok missing", payload)
    _assert(src.get("patch") == "L25.33a", "source L25.33a patch mismatch", payload)
    _assert(src.get("repairs_patch") == "L25.33", "source repairs patch missing", payload)
    _assert(src.get("package_run_ladder_complete") is True, "source package-run ladder incomplete", payload)
    _assert(src.get("key_normalization_repair_proven") is True, "source key normalization marker missing", payload)
    _assert(src.get("source_l25_32b_ok") is True, "source L25.32b ok missing", payload)
    _assert(src.get("source_l25_32b_repairs_patches") == ["L25.32", "L25.32a"], "source L25.32b repair list mismatch", payload)
    _assert(src.get("bundle_review_expected_shape_present") is True, "bundle shape marker missing", payload)
    _assert(src.get("package_run_allowed") is True, "package-run allowed marker missing", payload)
    _assert(src.get("patchops_cli_run_package_invoked_for_archive_manifest") is True, "run-package invoked marker missing", payload)
    _assert(src.get("patchops_cli_run_package_exit_code") == 0, "run-package exit mismatch", payload)
    _assert(src.get("patchops_cli_run_package_timed_out") is False, "run-package timeout marker mismatch", payload)
    _assert(src.get("patchops_cli_run_package_review_rejected") is False, "review rejection marker mismatch", payload)
    _assert(src.get("controlled_package_launcher_executed") is True, "controlled launcher marker missing", payload)
    _assert(src.get("package_run") is True, "package run marker missing", payload)
    _assert(payload.get("accepted_package_run_scope") == final_marker.EXPECTED_RUN_PACKAGE_SCOPE, "wrong accepted package-run scope", payload)
    _assert(payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for target execution", payload)
    _assert(payload.get("adapter_archive_extraction_performed") is False, "adapter extraction must be false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("pasteback_workflow_active") is False, "pasteback must remain false", payload)
    _assert(payload.get("real_downloaded_artifact_read") is False, "real artifact read must remain false", payload)
    _assert(not _false_field_errors(payload), "non-false boundary fields: " + ", ".join(_false_field_errors(payload)), payload)


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    runpkg_candidate = _refresh_runpkg_zip_fixture(root)
    names = _zip_names(runpkg_candidate)
    missing = sorted(set(REQUIRED_NAMES).difference(names))
    _assert(not missing, "run-package final marker zip missing expected bundle-review paths: " + ", ".join(missing))

    source32b = proof32b.build_archive_manifest_package_run_first_controlled_proof_shape_repair2(
        root,
        allow_archive_manifest_package_run_proof=True,
        authorization_token=proof32b.REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_PROOF_TOKEN,
        candidate_package_path=str(runpkg_candidate),
        bundle_names=names,
    )
    source33a_module = broad33a.build_archive_manifest_package_run_broad_checkpoint_key_repair(root, source_payload=source32b)
    payload = final_marker.build_package_run_final_acceptance_marker(root, source_payload=source33a_module)
    _validate_final_payload(payload)

    # Also prove L25.34 accepts the L25.33a validator-summary shape seen in reports.
    source33a_summary_shape = {
        "ok": True,
        "patch": "L25.33a",
        "repairs_patch": "L25.33",
        "broad_checkpoint": True,
        "package_run_ladder_complete": True,
        "key_normalization_repair_proven": True,
        "module_payload_shape_proven": True,
        "validator_summary_shape_proven": True,
        "source_l25_32b_ok": True,
        "source_l25_32b_repairs_patches": ["L25.32", "L25.32a"],
        "bundle_review_expected_shape_present": True,
        "runpkg_fixture_names_include_expected_bundle_shape": True,
        "package_run_allowed": True,
        "patchops_run_package_performed": True,
        "patchops_cli_run_package_invoked_for_archive_manifest": True,
        "patchops_cli_run_package_exit_code": 0,
        "patchops_cli_run_package_timed_out": False,
        "patchops_cli_run_package_review_rejected": False,
        "controlled_package_launcher_executed": True,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": True,
        "adapter_archive_extraction_performed": False,
        "browser_started": False,
        "pasteback": False,
        "real_downloaded_artifact_read": False,
        "package_run": True,
        "patchops_run_package_scope": proof32b.PACKAGE_RUN_SCOPE,
    }
    summary_payload = final_marker.build_package_run_final_acceptance_marker(root, source_payload=source33a_summary_shape)
    _validate_final_payload(summary_payload)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_package_run_final_acceptance_marker.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_package_run_final_acceptance_marker.md"
    module_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    _assert(not _forbidden_import_hits(module_text), "forbidden imports in final acceptance marker module", payload)
    _assert(not _forbidden_call_hits(module_text), "forbidden calls in final acceptance marker module", payload)
    _assert("marks the controlled synthetic package-run ladder complete" in doc_text, "doc missing final marker wording", payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", payload)
    _assert("No click/download/paste/send side effect" in doc_text, "doc missing no click/download/paste/send boundary", payload)

    return {
        "ok": True,
        "patch": "L25.34",
        "final_acceptance_marker": payload.get("final_acceptance_marker"),
        "controlled_package_run_ladder_final_acceptance": payload.get("controlled_package_run_ladder_final_acceptance"),
        "source_l25_33a_ok": payload.get("source_l25_33a_summary", {}).get("ok"),
        "source_l25_33a_repairs_patch": payload.get("source_l25_33a_summary", {}).get("repairs_patch"),
        "source_l25_33a_package_run_ladder_complete": payload.get("source_l25_33a_summary", {}).get("package_run_ladder_complete"),
        "source_l25_33a_key_normalization_repair_proven": payload.get("source_l25_33a_summary", {}).get("key_normalization_repair_proven"),
        "source_l25_32b_ok": payload.get("source_l25_33a_summary", {}).get("source_l25_32b_ok"),
        "source_l25_32b_repairs_patches": payload.get("source_l25_33a_summary", {}).get("source_l25_32b_repairs_patches"),
        "bundle_review_expected_shape_present": payload.get("source_l25_33a_summary", {}).get("bundle_review_expected_shape_present"),
        "package_run_allowed": payload.get("source_l25_33a_summary", {}).get("package_run_allowed"),
        "patchops_run_package_performed": payload.get("source_l25_33a_summary", {}).get("patchops_run_package_performed"),
        "patchops_cli_run_package_invoked_for_archive_manifest": payload.get("source_l25_33a_summary", {}).get("patchops_cli_run_package_invoked_for_archive_manifest"),
        "patchops_cli_run_package_exit_code": payload.get("source_l25_33a_summary", {}).get("patchops_cli_run_package_exit_code"),
        "patchops_cli_run_package_timed_out": payload.get("source_l25_33a_summary", {}).get("patchops_cli_run_package_timed_out"),
        "patchops_cli_run_package_review_rejected": payload.get("source_l25_33a_summary", {}).get("patchops_cli_run_package_review_rejected"),
        "controlled_package_launcher_executed": payload.get("source_l25_33a_summary", {}).get("controlled_package_launcher_executed"),
        "package_run": payload.get("source_l25_33a_summary", {}).get("package_run"),
        "accepted_package_run_scope": payload.get("accepted_package_run_scope"),
        "package_manifest_used_for_execution": payload.get("package_manifest_used_for_execution"),
        "package_execution_allowed": payload.get("package_execution_allowed"),
        "adapter_archive_extraction_performed": payload.get("adapter_archive_extraction_performed"),
        "browser_started": payload.get("browser_started"),
        "pasteback": payload.get("pasteback_workflow_active"),
        "real_downloaded_artifact_read": payload.get("real_downloaded_artifact_read"),
        "summary_shape_proven": True,
        "module_shape_proven": True,
        "failed_checks": payload.get("failed_checks"),
        "next_patch": payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.34 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
