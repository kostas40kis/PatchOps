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

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_plan_authorization_gate as gate
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_inspect_first_controlled_proof as inspect_proof
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_first_controlled_proof as preflight_proof

FALSE_FIELDS = (
    "archive_manifest_patchops_plan_authorization_executes_plan",
    "archive_manifest_patchops_plan_allowed",
    "patchops_manifest_plan_performed",
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
    "notes": "Synthetic manifest for L25.25 plan authorization gate. It remains inspect-only in the source chain and is never planned or applied by this patch.",
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
        if isinstance(node, ast.Call):
            qname = _qualified_call_name(node.func)
            name = qname.rsplit(".", 1)[-1]
            if name in FORBIDDEN_CALL_NAMES and qname not in {"json.dumps"}:
                hits.append(qname or name)
    return sorted(set(hits))


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
        root / inspect_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        INSPECT_MANIFEST_PAYLOAD,
        b"# synthetic launcher name only for L25.25 plan authorization source-chain readback\n",
    )


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    preflight_candidate = _refresh_preflight_zip_fixture(root)
    inspect_candidate = _refresh_inspect_zip_fixture(root)
    default_payload = gate.build_archive_manifest_patchops_plan_authorization_gate(root)
    authorized_payload = gate.build_archive_manifest_patchops_plan_authorization_gate(
        root,
        allow_archive_manifest_patchops_plan_authorization=True,
        authorization_token=gate.REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PLAN_AUTHORIZATION_TOKEN,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_manifest_patchops_plan_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_manifest_patchops_plan_authorization_gate.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_call_hits = _forbidden_call_hits(source_text)
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(preflight_candidate.exists(), "shared preflight source-chain zip fixture missing", authorized_payload)
    _assert(inspect_candidate.exists(), "isolated inspect source-chain zip fixture missing", authorized_payload)
    _assert(str(preflight_candidate.resolve()) != str(inspect_candidate.resolve()), "inspect fixture must be isolated from shared preflight fixture")
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("archive_manifest_patchops_plan_authorization_granted_for_future_patch") is False, "default should not grant future plan auth", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.25", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("ok") is True, "L25.24 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("broad_checkpoint") is True, "L25.24 broad checkpoint missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("inspect_ladder_complete") is True, "L25.24 inspect ladder completion missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_invoked_for_archive_manifest") is True, "L25.24 inspect-only proof missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_exit_code") == 0, "L25.24 inspect exit mismatch", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_timed_out") is False, "L25.24 inspect timed out", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_json_object") is True, "L25.24 inspect JSON marker missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_patch_name") == INSPECT_MANIFEST_OBJECT["patch_name"], "L25.24 inspect patch name mismatch", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_plan_invoked_for_archive_manifest") is False, "L25.24 plan must be false", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_apply_invoked_for_archive_manifest") is False, "L25.24 apply must be false", authorized_payload)
    _assert(authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_run_package_invoked_for_archive_manifest") is False, "L25.24 run-package must be false", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_patchops_plan_authorization_granted_for_future_patch") is True, "future plan auth should be granted by token", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_patchops_plan_authorization_readback_only") is True, "plan auth must be readback-only", authorized_payload)
    _assert(authorized_payload.get("archive_manifest_patchops_plan_allowed") is False, "plan allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_manifest_plan_performed") is False, "PatchOps plan must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest") is False, "PatchOps plan CLI must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest") is False, "PatchOps apply must remain false", authorized_payload)
    _assert(authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is False, "PatchOps run-package must remain false", authorized_payload)
    _assert(authorized_payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", authorized_payload)
    _assert(authorized_payload.get("package_execution_allowed") is False, "package execution allowed must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_patchops_plan_execution_added_by_l25_25") is True, "L25.25 should add no plan execution", authorized_payload)
    _assert(authorized_payload.get("no_patchops_apply_run_package_added_by_l25_25") is True, "L25.25 should add no apply/run-package", authorized_payload)
    _assert(authorized_payload.get("no_package_execution_added_by_l25_25") is True, "L25.25 should add no execution", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not forbidden_call_hits, "forbidden plan/inspect/archive/parse/execution calls found: " + ", ".join(forbidden_call_hits), authorized_payload)
    _assert("It does not run PatchOps plan on the archive manifest yet" in doc_text, "doc missing no-plan-yet statement", authorized_payload)
    _assert("Archive manifest PatchOps-plan authorization is readback-only" in doc_text, "doc missing readback-only boundary", authorized_payload)
    _assert("PatchOps plan is not invoked against the archive manifest copy" in doc_text, "doc missing no plan boundary", authorized_payload)
    _assert("PatchOps apply is not invoked against the archive manifest copy" in doc_text, "doc missing no apply boundary", authorized_payload)
    _assert("PatchOps run-package is not invoked against the archive manifest copy" in doc_text, "doc missing no run-package boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-extract/PatchOps-plan/PatchOps-apply/package-run/paste/send side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.25",
        "preflight_fixture_refreshed": True,
        "inspect_fixture_refreshed": True,
        "inspect_fixture_isolated_from_preflight_fixture": True,
        "preflight_fixture_path": str(preflight_candidate),
        "inspect_fixture_path": str(inspect_candidate),
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "default_future_patchops_plan_authorized": default_payload.get("archive_manifest_patchops_plan_authorization_granted_for_future_patch"),
        "authorized_readback": authorized_payload.get("archive_manifest_patchops_plan_authorization_granted_for_future_patch"),
        "source_l25_24_ok": authorized_payload.get("source_l25_24_summary", {}).get("ok"),
        "source_l25_24_broad_checkpoint": authorized_payload.get("source_l25_24_summary", {}).get("broad_checkpoint"),
        "source_l25_24_inspect_ladder_complete": authorized_payload.get("source_l25_24_summary", {}).get("inspect_ladder_complete"),
        "source_l25_24_patchops_cli_inspect_invoked_for_archive_manifest": authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_invoked_for_archive_manifest"),
        "source_l25_24_patchops_cli_inspect_exit_code": authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_exit_code"),
        "source_l25_24_patchops_cli_inspect_json_object": authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_json_object"),
        "source_l25_24_patchops_cli_inspect_patch_name": authorized_payload.get("source_l25_24_summary", {}).get("patchops_cli_inspect_patch_name"),
        "plan_authorization_readback_only": authorized_payload.get("archive_manifest_patchops_plan_authorization_readback_only"),
        "patchops_plan_allowed": authorized_payload.get("archive_manifest_patchops_plan_allowed"),
        "patchops_manifest_plan_performed": authorized_payload.get("patchops_manifest_plan_performed"),
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
    parser = argparse.ArgumentParser(description="L25.25 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
