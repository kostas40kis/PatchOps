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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_inspect_first_controlled_proof as proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_first_controlled_proof as preflight_proof

FALSE_FIELDS = (
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
)

FORBIDDEN_ARCHIVE_METHODS = {
    "extract",
    "extractall",
    "open",
    "testzip",
    "namelist",
    "infolist",
}

FORBIDDEN_EXECUTION_NAMES = {
    "run_package",
    "apply",
    "execute",
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
    "tags": ["synthetic", "l25_23", "inspect_only", "isolated_fixture"],
    "notes": "Synthetic manifest for L25.23 PatchOps inspect-only proof. It is never planned or applied.",
}
PREFLIGHT_MANIFEST_PAYLOAD = (json.dumps(PREFLIGHT_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
INSPECT_MANIFEST_PAYLOAD = (json.dumps(INSPECT_MANIFEST_OBJECT, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
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


def _subprocess_run_count(source_text: str) -> int:
    tree = ast.parse(source_text)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Call) and _qualified_call_name(node.func) == "subprocess.run")


def _write_zip(path: Path, payload: bytes, note: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(MANIFEST_MEMBER, payload)
        archive.writestr(NON_MANIFEST_MEMBER, note)
    return path


def _refresh_preflight_zip_fixture(root: Path) -> Path:
    return _write_zip(
        root / preflight_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        PREFLIGHT_MANIFEST_PAYLOAD,
        b"# synthetic launcher name only for shared L25.20/L25.21/L25.22 source chain\n",
    )


def _refresh_inspect_zip_fixture(root: Path) -> Path:
    return _write_zip(
        root / proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        INSPECT_MANIFEST_PAYLOAD,
        b"# synthetic launcher name only for isolated L25.23 PatchOps inspect proof\n",
    )


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    preflight_candidate = _refresh_preflight_zip_fixture(root)
    inspect_candidate = _refresh_inspect_zip_fixture(root)
    default_payload = proof.build_archive_manifest_patchops_inspect_first_controlled_proof(root)
    authorized_payload = proof.build_archive_manifest_patchops_inspect_first_controlled_proof(
        root,
        allow_archive_manifest_patchops_inspect_proof=True,
        authorization_token=proof.REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_INSPECT_PROOF_TOKEN,
        candidate_archive_path=str(inspect_candidate),
        member_name=MANIFEST_MEMBER,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_patchops_inspect_first_controlled_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_patchops_inspect_first_controlled_proof.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_call_hits = _forbidden_call_hits(source_text)
    read_call_hits = _read_call_hits(source_text)
    subprocess_run_count = _subprocess_run_count(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(preflight_candidate.exists(), "shared preflight source-chain zip fixture missing", authorized_payload)
    _assert(inspect_candidate.exists(), "isolated inspect proof zip fixture missing", authorized_payload)
    _assert(str(preflight_candidate.resolve()) != str(inspect_candidate.resolve()), "inspect fixture must be isolated from shared preflight fixture")
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("patchops_manifest_inspect_performed") is False, "default should not run inspect", default_payload)
    _assert(default_payload.get("inspect_fixture_isolated_from_preflight_fixture") is True, "default should report isolated fixture", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.23", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("repair_patch") == "L25.23a", "wrong repair patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_22_summary", {}).get("ok") is True, "L25.22 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_22_summary", {}).get("future_patchops_inspect_authorized") is True, "L25.22 future inspect authorization missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_22_summary", {}).get("patchops_manifest_inspect_performed") is False, "L25.22 must not have run inspect", authorized_payload)
    _assert(authorized_payload.get("source_l25_22_summary", {}).get("source_l25_21_check_invoked") is True, "L25.21 source check proof missing", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_patchops_inspect_allowed") is True, "PatchOps inspect should be allowed", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_read") is True, "manifest payload should be read", authorized_payload)
    _assert(authorized_payload.get("manifest_temp_file_written_for_inspect") is True, "temp manifest should be written for inspect", authorized_payload)
    _assert(authorized_payload.get("patchops_manifest_inspect_performed") is True, "PatchOps inspect should be performed", authorized_payload)
    _assert(authorized_payload.get("patchops_manifest_validation_performed") is False, "PatchOps validation should not be marked by inspect-only proof", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_inspect_invoked_for_archive_manifest") is True, "PatchOps inspect should be invoked", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_inspect_exit_code") == 0, "PatchOps inspect exit mismatch", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_inspect_timed_out") is False, "PatchOps inspect timed out", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_inspect_json_object") is True, "PatchOps inspect JSON object missing", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_inspect_patch_name") == INSPECT_MANIFEST_OBJECT["patch_name"], "PatchOps inspect patch name mismatch", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_inspect_active_profile") == "generic_python", "PatchOps inspect active profile mismatch", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_inspect_manifest_version") == "1", "PatchOps inspect manifest version mismatch", authorized_payload)
    _assert(authorized_payload.get("manifest_member_name_read") == MANIFEST_MEMBER, "wrong manifest member name read", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_byte_count") == len(INSPECT_MANIFEST_PAYLOAD), "manifest payload byte count mismatch", authorized_payload)
    _assert(authorized_payload.get("patchops_inspect_scope") == proof.PATCHOPS_INSPECT_SCOPE, "wrong PatchOps inspect scope", authorized_payload)
    _assert(authorized_payload.get("inspect_fixture_isolated_from_preflight_fixture") is True, "inspect fixture isolation marker missing", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest") is False, "PatchOps plan must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest") is False, "PatchOps apply must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is False, "PatchOps run-package must remain false", authorized_payload)
    _assert(authorized_payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", authorized_payload)
    _assert(authorized_payload.get("package_execution_allowed") is False, "package execution allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_patchops_plan_apply_run_package_added_by_l25_23") is True, "L25.23 should add no plan/apply/run-package", authorized_payload)
    _assert(authorized_payload.get("no_package_execution_added_by_l25_23") is True, "L25.23 should add no execution", authorized_payload)
    _assert(authorized_payload.get("no_archive_extraction_added_by_l25_23") is True, "L25.23 should add no extraction", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l25_23") is True, "L25.23 should add no browser permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not forbidden_call_hits, "forbidden archive/execution calls found: " + ", ".join(forbidden_call_hits), authorized_payload)
    _assert(read_call_hits == ["TARGET_MANIFEST_MEMBER_NAME"], "module must contain exactly one controlled manifest archive read call", authorized_payload)
    _assert(subprocess_run_count == 1, "module must contain exactly one subprocess.run call", authorized_payload)
    _assert("L25.23a repairs fixture isolation" in doc_text, "doc missing L25.23a repair note", authorized_payload)
    _assert("The inspect fixture is isolated from the shared L25.20/L25.21 preflight fixture" in doc_text, "doc missing fixture isolation boundary", authorized_payload)
    _assert("PatchOps inspect is the only new PatchOps CLI command invoked against the archive manifest copy" in doc_text, "doc missing inspect-only boundary", authorized_payload)
    _assert("PatchOps plan is not invoked against the archive manifest copy" in doc_text, "doc missing no plan boundary", authorized_payload)
    _assert("PatchOps apply is not invoked against the archive manifest copy" in doc_text, "doc missing no apply boundary", authorized_payload)
    _assert("PatchOps run-package is not invoked against the archive manifest copy" in doc_text, "doc missing no run-package boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-extract/PatchOps-plan/PatchOps-apply/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.23",
        "repair_patch": "L25.23a",
        "preflight_fixture_refreshed": True,
        "inspect_fixture_refreshed": True,
        "inspect_fixture_isolated_from_preflight_fixture": True,
        "preflight_fixture_path": str(preflight_candidate),
        "inspect_fixture_path": str(inspect_candidate),
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "default_patchops_manifest_inspect_performed": default_payload.get("patchops_manifest_inspect_performed"),
        "source_l25_22_ok": authorized_payload.get("source_l25_22_summary", {}).get("ok"),
        "source_l25_22_future_authorized": authorized_payload.get("source_l25_22_summary", {}).get("future_patchops_inspect_authorized"),
        "source_l25_22_source_l25_21_check_invoked": authorized_payload.get("source_l25_22_summary", {}).get("source_l25_21_check_invoked"),
        "patchops_inspect_allowed": authorized_payload.get("archive_manifest_patchops_inspect_allowed"),
        "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
        "manifest_temp_file_written_for_inspect": authorized_payload.get("manifest_temp_file_written_for_inspect"),
        "patchops_manifest_inspect_performed": authorized_payload.get("patchops_manifest_inspect_performed"),
        "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed"),
        "patchops_cli_inspect_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_inspect_invoked_for_archive_manifest"),
        "patchops_cli_inspect_exit_code": authorized_payload.get("patchops_cli_inspect_exit_code"),
        "patchops_cli_inspect_timed_out": authorized_payload.get("patchops_cli_inspect_timed_out"),
        "patchops_cli_inspect_json_object": authorized_payload.get("patchops_cli_inspect_json_object"),
        "patchops_cli_inspect_patch_name": authorized_payload.get("patchops_cli_inspect_patch_name"),
        "patchops_cli_inspect_active_profile": authorized_payload.get("patchops_cli_inspect_active_profile"),
        "patchops_cli_inspect_manifest_version": authorized_payload.get("patchops_cli_inspect_manifest_version"),
        "patchops_inspect_scope": authorized_payload.get("patchops_inspect_scope"),
        "patchops_cli_plan_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest"),
        "patchops_cli_apply_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest"),
        "patchops_cli_run_package_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest"),
        "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
        "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
        "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.23a brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
