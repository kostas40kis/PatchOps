from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_download_artifact_package_execution_dry_run_proof as proof

FALSE_FIELDS = (
    "artifact_path_opened_by_l25_42",
    "artifact_bytes_read_by_l25_42",
    "zip_member_opened_by_l25_42",
    "real_archive_candidate_extracted",
    "adapter_archive_extraction_performed",
    "archive_member_extracted_to_project",
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
    "package_manifest_used_for_execution",
    "package_execution_allowed",
    "package_execution_performed_by_adapter",
    "package_run_performed_by_adapter",
    "package_run",
    "patchops_cli_run_package_invoked_for_real_artifact",
    "artifact_member_written_to_project",
    "git_commit_performed",
    "git_push_performed",
)


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
    forbidden = {"selenium", "webdriver_manager", "pyperclip", "psutil", "subprocess", "zipfile", "hashlib"}
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
    forbidden = {"open", "read", "read_bytes", "extract", "extractall", "execute", "run", "Popen", "check_call", "check_output"}
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            qname = _qualified_call_name(node.func)
            method = qname.rsplit(".", 1)[-1]
            if method in forbidden and qname not in {"json.loads", "json.dumps"}:
                hits.append(qname or method)
    return sorted(set(hits))


def _source_l25_41_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "patch": "L25.41",
        "package_execution_authorization_gate": True,
        "package_execution_authorization_from_source_payload_only": True,
        "package_execution_authorization_granted_for_future_patch": True,
        "future_package_execution_requires_separate_l25_42_gate_and_token": True,
        "accepted_manifest_validation_ladder_final_acceptance": True,
        "accepted_manifest_member_name": "bundle/manifest.json",
        "accepted_manifest_patch_name": "synthetic_l25_37_manifest_readback_fixture",
        "accepted_manifest_version": "1",
        "accepted_manifest_files_to_write_count": 0,
        "accepted_manifest_validation_commands_count": 0,
        "accepted_manifest_zero_writes": True,
        "accepted_manifest_zero_validation_commands": True,
        "authorization_rejects_source_that_already_ran_package": True,
        "artifact_path_opened_by_l25_41": False,
        "artifact_bytes_read_by_l25_41": False,
        "zip_member_opened_by_l25_41": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "browser_started": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_execution_performed_by_adapter": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "pasteback": False,
    }


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _validate_payload(payload: dict[str, Any]) -> None:
    _assert(payload.get("ok") is True, "payload is not ok", payload)
    _assert(payload.get("patch") == "L25.42", "wrong patch marker", payload)
    _assert(payload.get("package_execution_first_controlled_dry_run_proof") is True, "dry-run proof marker missing", payload)
    _assert(payload.get("package_execution_dry_run_only") is True, "dry-run-only marker missing", payload)
    _assert(payload.get("package_execution_dry_run_from_source_payload_only") is True, "source-payload-only marker missing", payload)
    _assert(payload.get("package_execution_dry_run_allowed") is True, "dry run not allowed", payload)
    _assert(payload.get("candidate_artifact_suffix_zip") is True, "candidate suffix must be zip", payload)
    _assert(payload.get("candidate_artifact_under_l25_42_runtime") is True, "candidate must stay under L25.42 runtime", payload)
    _assert(payload.get("would_run_command_rendered") is True, "would-run command missing", payload)
    _assert(payload.get("would_run_command_program") == "py", "would-run program mismatch", payload)
    args = payload.get("would_run_command_args") or []
    _assert(args[:3] == ["-m", "patchops.cli", "run-package"], "would-run command must target PatchOps run-package", payload)
    _assert("--wrapper-root" in args, "would-run command missing wrapper root", payload)
    _assert(payload.get("would_invoke_patchops_run_package_in_future_patch") is True, "future run-package intent missing", payload)
    _assert(payload.get("artifact_path_opened_by_l25_42") is False, "L25.42 must not open artifact path", payload)
    _assert(payload.get("artifact_bytes_read_by_l25_42") is False, "L25.42 must not read artifact bytes", payload)
    _assert(payload.get("zip_member_opened_by_l25_42") is False, "L25.42 must not open zip members", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("adapter_archive_extraction_performed") is False, "adapter extraction must remain false", payload)
    _assert(payload.get("archive_member_extracted_to_project") is False, "member extraction must remain false", payload)
    _assert(payload.get("artifact_member_written_to_project") is False, "artifact member write must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_manifest_used_for_execution") is False, "manifest must not be used for execution", payload)
    _assert(payload.get("package_execution_allowed") is False, "package execution must remain false", payload)
    _assert(payload.get("package_execution_performed_by_adapter") is False, "adapter execution must remain false", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("patchops_cli_run_package_invoked_for_real_artifact") is False, "run-package invocation must remain false", payload)
    _assert(payload.get("pasteback_workflow_active") is False, "pasteback must remain false", payload)
    _assert(not _false_field_errors(payload), "non-false boundary fields: " + ", ".join(_false_field_errors(payload)), payload)


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    source = _source_l25_41_payload()
    candidate = root / proof.DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH

    default_payload = proof.build_real_download_artifact_package_execution_dry_run_proof(root, source_payload=source, candidate_artifact_path=str(candidate))
    _assert(default_payload.get("ok") is False, "default should not pass without token", default_payload)
    _assert(default_payload.get("would_run_command_rendered") is False, "default must not render would-run command", default_payload)

    authorized_payload = proof.build_real_download_artifact_package_execution_dry_run_proof(
        root,
        source_payload=source,
        allow_package_execution_dry_run=True,
        authorization_token=proof.REQUIRED_PACKAGE_EXECUTION_DRY_RUN_TOKEN,
        candidate_artifact_path=str(candidate),
    )
    _validate_payload(authorized_payload)

    outside_payload = proof.build_real_download_artifact_package_execution_dry_run_proof(
        root,
        source_payload=source,
        allow_package_execution_dry_run=True,
        authorization_token=proof.REQUIRED_PACKAGE_EXECUTION_DRY_RUN_TOKEN,
        candidate_artifact_path=str(root / "data" / "runtime" / "browser_downloads" / "outside.zip"),
    )
    _assert(outside_payload.get("ok") is False, "dry-run must reject artifact path outside L25.42 runtime folder", outside_payload)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_download_artifact_package_execution_dry_run_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_download_artifact_package_execution_dry_run_proof.md"
    module_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    _assert(not _forbidden_import_hits(module_text), "forbidden imports in L25.42 module", authorized_payload)
    _assert(not _forbidden_call_hits(module_text), "forbidden artifact/zip/execution calls in L25.42 module", authorized_payload)
    _assert("does not invoke PatchOps `run-package`" in doc_text, "doc missing no run-package invocation statement", authorized_payload)
    _assert("This dry-run proof does not open an artifact path" in doc_text, "doc missing no artifact-open boundary", authorized_payload)
    _assert("No package execution" in doc_text, "doc missing no package execution boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.42",
        "package_execution_first_controlled_dry_run_proof": authorized_payload.get("package_execution_first_controlled_dry_run_proof"),
        "package_execution_dry_run_only": authorized_payload.get("package_execution_dry_run_only"),
        "package_execution_dry_run_from_source_payload_only": authorized_payload.get("package_execution_dry_run_from_source_payload_only"),
        "package_execution_dry_run_allowed": authorized_payload.get("package_execution_dry_run_allowed"),
        "candidate_artifact_suffix_zip": authorized_payload.get("candidate_artifact_suffix_zip"),
        "candidate_artifact_under_l25_42_runtime": authorized_payload.get("candidate_artifact_under_l25_42_runtime"),
        "would_run_command_rendered": authorized_payload.get("would_run_command_rendered"),
        "would_run_command_program": authorized_payload.get("would_run_command_program"),
        "would_invoke_patchops_run_package_in_future_patch": authorized_payload.get("would_invoke_patchops_run_package_in_future_patch"),
        "dry_run_rejects_artifact_path_outside_l25_42_runtime": outside_payload.get("ok") is False,
        "artifact_path_opened_by_l25_42": authorized_payload.get("artifact_path_opened_by_l25_42"),
        "artifact_bytes_read_by_l25_42": authorized_payload.get("artifact_bytes_read_by_l25_42"),
        "zip_member_opened_by_l25_42": authorized_payload.get("zip_member_opened_by_l25_42"),
        "real_archive_candidate_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "adapter_archive_extraction_performed": authorized_payload.get("adapter_archive_extraction_performed"),
        "archive_member_extracted_to_project": authorized_payload.get("archive_member_extracted_to_project"),
        "artifact_member_written_to_project": authorized_payload.get("artifact_member_written_to_project"),
        "browser_started": authorized_payload.get("browser_started"),
        "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
        "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
        "package_execution_performed_by_adapter": authorized_payload.get("package_execution_performed_by_adapter"),
        "package_run": authorized_payload.get("package_run"),
        "patchops_cli_run_package_invoked_for_real_artifact": authorized_payload.get("patchops_cli_run_package_invoked_for_real_artifact"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.42 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
