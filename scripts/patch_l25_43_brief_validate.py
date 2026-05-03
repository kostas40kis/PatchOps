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

from patchops.llm_browser import live_adapter_edge_real_download_artifact_package_execution_dry_run_broad_checkpoint as broad

FALSE_FIELDS = (
    "artifact_path_opened_by_l25_43",
    "artifact_bytes_read_by_l25_43",
    "zip_member_opened_by_l25_43",
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


def _source_l25_42_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "patch": "L25.42",
        "package_execution_first_controlled_dry_run_proof": True,
        "package_execution_dry_run_only": True,
        "package_execution_dry_run_from_source_payload_only": True,
        "package_execution_dry_run_allowed": True,
        "candidate_artifact_suffix_zip": True,
        "candidate_artifact_under_l25_42_runtime": True,
        "would_run_command_rendered": True,
        "would_run_command_program": "py",
        "would_invoke_patchops_run_package_in_future_patch": True,
        "dry_run_rejects_artifact_path_outside_l25_42_runtime": True,
        "artifact_path_opened_by_l25_42": False,
        "artifact_bytes_read_by_l25_42": False,
        "zip_member_opened_by_l25_42": False,
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
    _assert(payload.get("patch") == "L25.43", "wrong patch marker", payload)
    _assert(payload.get("package_execution_dry_run_broad_checkpoint") is True, "broad checkpoint marker missing", payload)
    _assert(payload.get("package_execution_dry_run_broad_checkpoint_from_source_payload_only") is True, "source-payload-only marker missing", payload)
    _assert(payload.get("package_execution_dry_run_broad_checkpoint_allowed") is True, "broad checkpoint not allowed", payload)
    _assert(payload.get("accepted_package_execution_dry_run_only") is True, "accepted dry-run-only marker missing", payload)
    _assert(payload.get("accepted_package_execution_dry_run_allowed") is True, "accepted dry-run allowed marker missing", payload)
    _assert(payload.get("accepted_candidate_artifact_suffix_zip") is True, "accepted zip suffix marker missing", payload)
    _assert(payload.get("accepted_candidate_artifact_under_l25_42_runtime") is True, "accepted runtime path marker missing", payload)
    _assert(payload.get("accepted_would_run_command_rendered") is True, "would-run render marker missing", payload)
    _assert(payload.get("accepted_would_run_command_program") == "py", "would-run program mismatch", payload)
    _assert(payload.get("accepted_would_invoke_patchops_run_package_in_future_patch") is True, "future run-package intent missing", payload)
    _assert(payload.get("accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime") is True, "outside-path rejection missing", payload)
    _assert(payload.get("artifact_path_opened_by_l25_43") is False, "L25.43 must not open artifact path", payload)
    _assert(payload.get("artifact_bytes_read_by_l25_43") is False, "L25.43 must not read artifact bytes", payload)
    _assert(payload.get("zip_member_opened_by_l25_43") is False, "L25.43 must not open zip members", payload)
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
    source = _source_l25_42_payload()

    default_payload = broad.build_real_download_artifact_package_execution_dry_run_broad_checkpoint(root, source_payload=source)
    _assert(default_payload.get("ok") is False, "default should not pass without token", default_payload)
    _assert(default_payload.get("package_execution_dry_run_broad_checkpoint_allowed") is False, "default must not allow broad checkpoint", default_payload)

    authorized_payload = broad.build_real_download_artifact_package_execution_dry_run_broad_checkpoint(
        root,
        source_payload=source,
        allow_dry_run_broad_checkpoint=True,
        authorization_token=broad.REQUIRED_DRY_RUN_BROAD_CHECKPOINT_TOKEN,
    )
    _validate_payload(authorized_payload)

    malformed_source = dict(source)
    malformed_source["patchops_cli_run_package_invoked_for_real_artifact"] = True
    malformed_payload = broad.build_real_download_artifact_package_execution_dry_run_broad_checkpoint(
        root,
        source_payload=malformed_source,
        allow_dry_run_broad_checkpoint=True,
        authorization_token=broad.REQUIRED_DRY_RUN_BROAD_CHECKPOINT_TOKEN,
    )
    _assert(malformed_payload.get("ok") is False, "broad checkpoint must reject source that invoked run-package", malformed_payload)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_download_artifact_package_execution_dry_run_broad_checkpoint.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_download_artifact_package_execution_dry_run_broad_checkpoint.md"
    module_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    _assert(not _forbidden_import_hits(module_text), "forbidden imports in L25.43 module", authorized_payload)
    _assert(not _forbidden_call_hits(module_text), "forbidden artifact/zip/execution calls in L25.43 module", authorized_payload)
    _assert("This broad checkpoint does not open an artifact path" in doc_text, "doc missing no artifact-open boundary", authorized_payload)
    _assert("No PatchOps run-package invocation" in doc_text, "doc missing no run-package invocation boundary", authorized_payload)
    _assert("No package execution" in doc_text, "doc missing no package execution boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.43",
        "package_execution_dry_run_broad_checkpoint": authorized_payload.get("package_execution_dry_run_broad_checkpoint"),
        "package_execution_dry_run_broad_checkpoint_from_source_payload_only": authorized_payload.get("package_execution_dry_run_broad_checkpoint_from_source_payload_only"),
        "package_execution_dry_run_broad_checkpoint_allowed": authorized_payload.get("package_execution_dry_run_broad_checkpoint_allowed"),
        "accepted_package_execution_dry_run_only": authorized_payload.get("accepted_package_execution_dry_run_only"),
        "accepted_package_execution_dry_run_allowed": authorized_payload.get("accepted_package_execution_dry_run_allowed"),
        "accepted_candidate_artifact_suffix_zip": authorized_payload.get("accepted_candidate_artifact_suffix_zip"),
        "accepted_candidate_artifact_under_l25_42_runtime": authorized_payload.get("accepted_candidate_artifact_under_l25_42_runtime"),
        "accepted_would_run_command_rendered": authorized_payload.get("accepted_would_run_command_rendered"),
        "accepted_would_run_command_program": authorized_payload.get("accepted_would_run_command_program"),
        "accepted_would_invoke_patchops_run_package_in_future_patch": authorized_payload.get("accepted_would_invoke_patchops_run_package_in_future_patch"),
        "accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime": authorized_payload.get("accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime"),
        "broad_checkpoint_rejects_source_that_invoked_run_package": malformed_payload.get("ok") is False,
        "artifact_path_opened_by_l25_43": authorized_payload.get("artifact_path_opened_by_l25_43"),
        "artifact_bytes_read_by_l25_43": authorized_payload.get("artifact_bytes_read_by_l25_43"),
        "zip_member_opened_by_l25_43": authorized_payload.get("zip_member_opened_by_l25_43"),
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
    parser = argparse.ArgumentParser(description="L25.43 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
