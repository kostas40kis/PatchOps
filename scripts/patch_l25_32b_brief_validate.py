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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_package_run_first_controlled_proof_shape_repair2 as proof

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

FORBIDDEN_IMPORT_MODULES = ("selenium", "webdriver_manager", "pyperclip", "psutil")
FORBIDDEN_ARCHIVE_METHODS = {"extract", "extractall"}
FORBIDDEN_EXECUTION_NAMES = {"execute"}

RUNPKG_LAUNCHER = "bundle/run_with_patchops.ps1"
RUNPKG_META = "bundle/bundle_meta.json"
RUNPKG_README = "bundle/README.txt"
RUNPKG_MANIFEST = "bundle/manifest.json"
RUNPKG_CONTENT = "bundle/content/.keep"
LAUNCHER_MARKER = "L25_32B_RUN_PACKAGE_LAUNCHER_MARKER"
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
$ReportPath = Join-Path $Desktop ("synthetic_l25_32b_run_package_launcher_{0}.txt" -f $Stamp)
$Lines = @(
    'L25.32b synthetic run-package launcher proof',
    'Patch Name : synthetic_l25_32b_run_package_fixture',
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
    hits: list[str] = []
    forbidden = set(FORBIDDEN_IMPORT_MODULES)
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
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            qname = _qualified_call_name(node.func)
            method = qname.rsplit(".", 1)[-1]
            if method in FORBIDDEN_ARCHIVE_METHODS or method in FORBIDDEN_EXECUTION_NAMES:
                hits.append(qname or method)
    return sorted(set(hits))


def _subprocess_run_count(source_text: str) -> int:
    tree = ast.parse(source_text)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Call) and _qualified_call_name(node.func) == "subprocess.run")


def _manifest(root: Path) -> dict[str, Any]:
    return {
        "bundle_schema_version": "synthetic-l25",
        "manifest_version": "1",
        "patch_name": "synthetic_l25_32b_run_package_fixture",
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
    path = root / proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema_version": "1",
        "bundle_schema_version": "1",
        "patch_name": "synthetic_l25_32b_run_package_fixture",
        "bundle_mode": "launcher_direct_synthetic_proof",
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
        archive.writestr(RUNPKG_README, "L25.32b controlled synthetic run-package proof. No target writes.\n")
        archive.writestr(RUNPKG_CONTENT, "synthetic content marker only\n")
    return path


def _zip_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path, "r") as archive:
        return sorted(archive.namelist())


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    runpkg_candidate = _refresh_runpkg_zip_fixture(root)
    runpkg_names = _zip_names(runpkg_candidate)
    missing_names = sorted(set(REQUIRED_NAMES).difference(runpkg_names))
    _assert(not missing_names, "run-package proof zip is missing expected bundle-review paths: " + ", ".join(missing_names))

    default_payload = proof.build_archive_manifest_package_run_first_controlled_proof_shape_repair2(root)
    authorized_payload = proof.build_archive_manifest_package_run_first_controlled_proof_shape_repair2(
        root,
        allow_archive_manifest_package_run_proof=True,
        authorization_token=proof.REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_PROOF_TOKEN,
        candidate_package_path=str(runpkg_candidate),
        bundle_names=runpkg_names,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_package_run_first_controlled_proof_shape_repair2.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_package_run_first_controlled_proof_shape_repair2.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    false_errors = _false_field_errors(authorized_payload)

    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("patchops_run_package_performed") is False, "default should not run package", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.32b", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("bundle_review_expected_shape_present") is True, "bundle review expected shape missing", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_package_run_allowed") is True, "package-run should be allowed", authorized_payload)
    _assert(authorized_payload.get("patchops_run_package_performed") is True, "PatchOps run-package should be performed", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is True, "PatchOps run-package should be invoked", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_exit_code") == 0, "PatchOps run-package exit mismatch", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_timed_out") is False, "PatchOps run-package timed out", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_review_rejected") is False, "PatchOps run-package was rejected by bundle review", authorized_payload)
    _assert(authorized_payload.get("controlled_package_launcher_executed") is True, "controlled launcher should execute", authorized_payload)
    _assert(authorized_payload.get("package_run") is True, "package_run marker should be true", authorized_payload)
    _assert(authorized_payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for target execution", authorized_payload)
    _assert(authorized_payload.get("adapter_archive_extraction_performed") is False, "adapter must not manually extract archive", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("pasteback_workflow_active") is False, "pasteback must remain false", authorized_payload)
    _assert(authorized_payload.get("real_downloaded_artifact_read") is False, "real downloaded artifact read must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_run_package_scope") == proof.PACKAGE_RUN_SCOPE, "wrong package-run scope", authorized_payload)
    _assert(not false_errors, "non-false boundary fields: " + ", ".join(false_errors), authorized_payload)
    _assert(not _forbidden_import_hits(source_text), "forbidden browser imports found", authorized_payload)
    _assert(not _forbidden_call_hits(source_text), "forbidden extraction/execution calls found", authorized_payload)
    _assert(_subprocess_run_count(source_text) == 1, "module must contain exactly one subprocess.run call", authorized_payload)
    _assert("bundle/run_with_patchops.ps1" in doc_text, "doc missing supported launcher path", authorized_payload)
    _assert("It is not a real downloaded artifact and not a ChatGPT-produced package" in doc_text, "doc missing synthetic boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No click/download/paste/send side effect" in doc_text, "doc missing no click/download/paste/send boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.32b",
        "repairs_patches": ["L25.32", "L25.32a"],
        "runpkg_fixture_refreshed": True,
        "runpkg_fixture_path": str(runpkg_candidate),
        "runpkg_fixture_names_include_expected_bundle_shape": True,
        "bundle_review_expected_shape_present": authorized_payload.get("bundle_review_expected_shape_present"),
        "package_run_allowed": authorized_payload.get("archive_manifest_package_run_allowed"),
        "patchops_run_package_performed": authorized_payload.get("patchops_run_package_performed"),
        "patchops_cli_run_package_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest"),
        "patchops_cli_run_package_exit_code": authorized_payload.get("patchops_cli_run_package_exit_code"),
        "patchops_cli_run_package_timed_out": authorized_payload.get("patchops_cli_run_package_timed_out"),
        "patchops_cli_run_package_review_rejected": authorized_payload.get("patchops_cli_run_package_review_rejected"),
        "controlled_package_launcher_executed": authorized_payload.get("controlled_package_launcher_executed"),
        "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
        "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
        "adapter_archive_extraction_performed": authorized_payload.get("adapter_archive_extraction_performed"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "patchops_run_package_scope": authorized_payload.get("patchops_run_package_scope"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.32b brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
