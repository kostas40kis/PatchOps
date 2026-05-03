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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_package_run_first_controlled_proof_shape_repair as proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_apply_first_controlled_proof as apply_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_plan_first_controlled_proof as plan_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_inspect_first_controlled_proof as inspect_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_first_controlled_proof as preflight_proof

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

MANIFEST_MEMBER = "bundle/manifest.json"
NON_MANIFEST_MEMBER = "bundle/run_with_patchops.ps1"
RUNPKG_LAUNCHER = "bundle/run_with_patchops.ps1"
RUNPKG_META = "bundle/bundle_meta.json"
RUNPKG_README = "bundle/README.txt"
RUNPKG_CONTENT = "bundle/content/.keep"
LAUNCHER_MARKER = "L25_32A_RUN_PACKAGE_LAUNCHER_MARKER"


def _manifest(patch_name: str, purpose: str, tags: list[str]) -> dict[str, Any]:
    return {
        "bundle_schema_version": "synthetic-l25",
        "manifest_version": "1",
        "patch_name": patch_name,
        "purpose": purpose,
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
        "tags": tags,
        "notes": "Synthetic controlled fixture. It has no target writes and no validation commands.",
    }

PREFLIGHT_MANIFEST_OBJECT = _manifest("synthetic_l25_20_patchops_check_fixture", "patchops-check-only-preflight-proof", ["synthetic", "l25_20"])
INSPECT_MANIFEST_OBJECT = _manifest("synthetic_l25_23_patchops_inspect_fixture", "patchops-inspect-only-proof", ["synthetic", "l25_23"])
PLAN_MANIFEST_OBJECT = _manifest("synthetic_l25_26_patchops_plan_fixture", "patchops-plan-only-proof", ["synthetic", "l25_26"])
APPLY_MANIFEST_OBJECT = _manifest("synthetic_l25_29_patchops_apply_fixture", "patchops-apply-only-zero-write-zero-validation-proof", ["synthetic", "l25_29"])
RUNPKG_MANIFEST_OBJECT = _manifest("synthetic_l25_32a_run_package_fixture", "patchops-run-package-only-supported-bundle-shape-proof", ["synthetic", "l25_32a", "run_package_only", "supported_bundle_shape"])


def _payload(obj: dict[str, Any]) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

PREFLIGHT_MANIFEST_PAYLOAD = _payload(PREFLIGHT_MANIFEST_OBJECT)
INSPECT_MANIFEST_PAYLOAD = _payload(INSPECT_MANIFEST_OBJECT)
PLAN_MANIFEST_PAYLOAD = _payload(PLAN_MANIFEST_OBJECT)
APPLY_MANIFEST_PAYLOAD = _payload(APPLY_MANIFEST_OBJECT)
RUNPKG_MANIFEST_PAYLOAD = _payload(RUNPKG_MANIFEST_OBJECT)

RUN_WITH_PATCHOPS_PS1 = """param(
    [string]$WrapperRoot = '',
    [string]$WrapperRepoRoot = '',
    [string]$RepoRoot = '',
    [string]$PackageRoot = ''
)
$ErrorActionPreference = 'Stop'
$Desktop = [Environment]::GetFolderPath('Desktop')
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$ReportPath = Join-Path $Desktop ("synthetic_l25_32a_run_package_launcher_{0}.txt" -f $Stamp)
$Lines = @(
    'L25.32a synthetic run-package launcher proof',
    'Patch Name : synthetic_l25_32a_run_package_fixture',
    'Scope : controlled synthetic launcher only',
    'Browser Started : false',
    'Pasteback : false',
    'Package writes : none',
    'ExitCode : 0',
    'Result : PASS',
    'L25_32A_RUN_PACKAGE_LAUNCHER_MARKER'
)
Set-Content -LiteralPath $ReportPath -Value $Lines -Encoding UTF8
Write-Host ('Report Path        : {0}' -f $ReportPath)
Write-Host 'L25_32A_RUN_PACKAGE_LAUNCHER_MARKER'
Write-Host 'Result : PASS'
exit 0
"""


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
        if method in FORBIDDEN_ARCHIVE_METHODS or method in FORBIDDEN_EXECUTION_NAMES:
            hits.append(qname or method)
    return sorted(set(hits))


def _subprocess_run_count(source_text: str) -> int:
    tree = ast.parse(source_text)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Call) and _qualified_call_name(node.func) == "subprocess.run")


def _write_manifest_zip(path: Path, payload: bytes, note: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("bundle/manifest.json", payload)
        archive.writestr("bundle/run_with_patchops.ps1", note)
        archive.writestr("bundle/README.txt", b"synthetic l25 source-chain fixture\n")
        archive.writestr("bundle/content/.keep", b"synthetic\n")
        archive.writestr("bundle/bundle_meta.json", b"{}\n")
    return path


def _refresh_preflight_zip_fixture(root: Path) -> Path:
    return _write_manifest_zip(root / preflight_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, PREFLIGHT_MANIFEST_PAYLOAD, b"# shared L25 source-chain fixture\n")


def _refresh_inspect_zip_fixture(root: Path) -> Path:
    return _write_manifest_zip(root / inspect_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, INSPECT_MANIFEST_PAYLOAD, b"# shared L25 inspect fixture\n")


def _refresh_plan_zip_fixture(root: Path) -> Path:
    return _write_manifest_zip(root / plan_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, PLAN_MANIFEST_PAYLOAD, b"# shared L25 plan fixture\n")


def _refresh_apply_zip_fixture(root: Path) -> Path:
    return _write_manifest_zip(root / apply_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH, APPLY_MANIFEST_PAYLOAD, b"# shared L25 apply fixture\n")


def _refresh_runpkg_zip_fixture(root: Path) -> Path:
    path = root / proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema_version": "1",
        "bundle_schema_version": "1",
        "patch_name": "synthetic_l25_32a_run_package_fixture",
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
        archive.writestr("bundle/manifest.json", RUNPKG_MANIFEST_PAYLOAD)
        archive.writestr(RUNPKG_README, "L25.32a controlled synthetic run-package proof. No target writes.\n")
        archive.writestr(RUNPKG_CONTENT, "synthetic content marker only\n")
    return path


def _zip_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path, "r") as archive:
        return sorted(archive.namelist())


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    preflight_candidate = _refresh_preflight_zip_fixture(root)
    inspect_candidate = _refresh_inspect_zip_fixture(root)
    plan_candidate = _refresh_plan_zip_fixture(root)
    apply_candidate = _refresh_apply_zip_fixture(root)
    runpkg_candidate = _refresh_runpkg_zip_fixture(root)
    runpkg_names = _zip_names(runpkg_candidate)

    required_names = {RUNPKG_LAUNCHER, RUNPKG_META, RUNPKG_README, RUNPKG_CONTENT, "bundle/manifest.json"}
    missing_names = sorted(required_names.difference(runpkg_names))

    default_payload = proof.build_archive_manifest_package_run_first_controlled_proof_shape_repair(root)
    authorized_payload = proof.build_archive_manifest_package_run_first_controlled_proof_shape_repair(
        root,
        allow_archive_manifest_package_run_proof=True,
        authorization_token=proof.REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_PROOF_TOKEN,
        candidate_package_path=str(runpkg_candidate),
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_package_run_first_controlled_proof_shape_repair.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_package_run_first_controlled_proof_shape_repair.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_call_hits = _forbidden_call_hits(source_text)
    subprocess_run_count = _subprocess_run_count(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(not missing_names, "run-package proof zip is missing expected bundle-review paths: " + ", ".join(missing_names))
    _assert(preflight_candidate.exists(), "shared preflight source-chain zip fixture missing", authorized_payload)
    _assert(inspect_candidate.exists(), "inspect source-chain zip fixture missing", authorized_payload)
    _assert(plan_candidate.exists(), "plan source-chain zip fixture missing", authorized_payload)
    _assert(apply_candidate.exists(), "apply source-chain zip fixture missing", authorized_payload)
    _assert(runpkg_candidate.exists(), "run-package proof zip fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("patchops_run_package_performed") is False, "default should not run package", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.32a", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("repairs_patch") == "L25.32", "repair patch marker missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_31_summary", {}).get("ok") is True, "L25.31 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_31_summary", {}).get("future_package_run_authorized") is True, "L25.31 future package-run authorization missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_31_summary", {}).get("patchops_run_package_performed") is False, "L25.31 must not have run package", authorized_payload)
    _assert(authorized_payload.get("source_l25_31_summary", {}).get("source_l25_30_apply_invoked") is True, "L25.30 source apply proof missing", authorized_payload)
    _assert(authorized_payload.get("bundle_shape_repaired") is True, "bundle shape repair marker missing", authorized_payload)
    _assert(authorized_payload.get("bundle_review_expected_shape_present") is True, "bundle review expected shape marker missing", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_package_run_allowed") is True, "package-run should be allowed", authorized_payload)
    _assert(authorized_payload.get("patchops_run_package_performed") is True, "PatchOps run-package should be performed", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is True, "PatchOps run-package should be invoked", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_exit_code") == 0, "PatchOps run-package exit mismatch", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_timed_out") is False, "PatchOps run-package timed out", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_review_rejected") is False, "PatchOps run-package was rejected by bundle review", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_stdout_has_pass") is True or authorized_payload.get("patchops_cli_run_package_stdout_has_ok_true") is True, "PatchOps run-package PASS/ok marker missing", authorized_payload)
    _assert(authorized_payload.get("controlled_package_launcher_executed") is True, "controlled package launcher should execute", authorized_payload)
    _assert(authorized_payload.get("package_run") is True, "package_run marker should be true", authorized_payload)
    _assert(authorized_payload.get("package_execution_allowed") is True, "controlled package execution should be allowed only for this proof", authorized_payload)
    _assert(authorized_payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for target execution", authorized_payload)
    _assert(authorized_payload.get("adapter_archive_extraction_performed") is False, "adapter must not manually extract archive", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("pasteback_workflow_active") is False, "pasteback must remain false", authorized_payload)
    _assert(authorized_payload.get("real_downloaded_artifact_read") is False, "real downloaded artifact read must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_run_package_scope") == proof.PACKAGE_RUN_SCOPE, "wrong package-run scope", authorized_payload)
    _assert(authorized_payload.get("run_package_fixture_isolated_from_preflight_inspect_plan_apply_fixtures") is True, "run-package fixture isolation marker missing", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden browser imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not forbidden_call_hits, "forbidden archive extraction/execution calls found: " + ", ".join(forbidden_call_hits), authorized_payload)
    _assert(subprocess_run_count == 1, "module must contain exactly one subprocess.run call", authorized_payload)
    _assert("bundle/run_with_patchops.ps1" in doc_text, "doc missing supported launcher path", authorized_payload)
    _assert("bundle/bundle_meta.json" in doc_text, "doc missing bundle_meta path", authorized_payload)
    _assert("It is not a real downloaded artifact and not a ChatGPT-produced package" in doc_text, "doc missing synthetic-only boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/paste/send side effect" in doc_text, "doc missing no click/download/paste/send boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.32a",
        "repairs_patch": "L25.32",
        "preflight_fixture_refreshed": True,
        "inspect_fixture_refreshed": True,
        "plan_fixture_refreshed": True,
        "apply_fixture_refreshed": True,
        "runpkg_fixture_refreshed": True,
        "runpkg_fixture_path": str(runpkg_candidate),
        "runpkg_fixture_names_include_expected_bundle_shape": True,
        "runpkg_fixture_required_names": sorted(required_names),
        "default_patchops_run_package_performed": default_payload.get("patchops_run_package_performed"),
        "source_l25_31_ok": authorized_payload.get("source_l25_31_summary", {}).get("ok"),
        "source_l25_31_future_authorized": authorized_payload.get("source_l25_31_summary", {}).get("future_package_run_authorized"),
        "source_l25_31_source_l25_30_apply_invoked": authorized_payload.get("source_l25_31_summary", {}).get("source_l25_30_apply_invoked"),
        "bundle_shape_repaired": authorized_payload.get("bundle_shape_repaired"),
        "bundle_review_expected_shape_present": authorized_payload.get("bundle_review_expected_shape_present"),
        "package_run_allowed": authorized_payload.get("archive_manifest_package_run_allowed"),
        "patchops_run_package_performed": authorized_payload.get("patchops_run_package_performed"),
        "patchops_cli_run_package_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest"),
        "patchops_cli_run_package_exit_code": authorized_payload.get("patchops_cli_run_package_exit_code"),
        "patchops_cli_run_package_timed_out": authorized_payload.get("patchops_cli_run_package_timed_out"),
        "patchops_cli_run_package_review_rejected": authorized_payload.get("patchops_cli_run_package_review_rejected"),
        "patchops_cli_run_package_stdout_has_pass": authorized_payload.get("patchops_cli_run_package_stdout_has_pass"),
        "patchops_cli_run_package_stdout_has_marker": authorized_payload.get("patchops_cli_run_package_stdout_has_marker"),
        "patchops_cli_run_package_stdout_has_report_path": authorized_payload.get("patchops_cli_run_package_stdout_has_report_path"),
        "controlled_package_launcher_executed": authorized_payload.get("controlled_package_launcher_executed"),
        "controlled_package_launcher_marker_seen": authorized_payload.get("controlled_package_launcher_marker_seen"),
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
    parser = argparse.ArgumentParser(description="L25.32a brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
