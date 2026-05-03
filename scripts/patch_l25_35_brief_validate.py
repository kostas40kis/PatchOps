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

from patchops.llm_browser import live_adapter_edge_real_download_artifact_authorization_gate as gate

FALSE_FIELDS = (
    "real_downloaded_manifest_read",
    "real_downloaded_artifact_read",
    "real_downloaded_artifact_path_opened",
    "real_downloaded_artifact_bytes_read",
    "real_downloaded_artifact_hash_computed",
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
    "package_run_performed_by_adapter",
    "package_run",
    "patchops_cli_run_package_invoked_for_real_artifact",
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


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _l25_34_source_summary_shape() -> dict[str, Any]:
    return {
        "ok": True,
        "patch": "L25.34",
        "final_acceptance_marker": True,
        "controlled_package_run_ladder_final_acceptance": True,
        "source_l25_33a_ok": True,
        "source_l25_33a_repairs_patch": "L25.33",
        "source_l25_33a_package_run_ladder_complete": True,
        "source_l25_33a_key_normalization_repair_proven": True,
        "source_l25_32b_ok": True,
        "source_l25_32b_repairs_patches": ["L25.32", "L25.32a"],
        "bundle_review_expected_shape_present": True,
        "package_run_allowed": True,
        "patchops_run_package_performed": True,
        "patchops_cli_run_package_invoked_for_archive_manifest": True,
        "patchops_cli_run_package_exit_code": 0,
        "patchops_cli_run_package_timed_out": False,
        "patchops_cli_run_package_review_rejected": False,
        "controlled_package_launcher_executed": True,
        "package_run": True,
        "accepted_package_run_scope": gate.EXPECTED_RUN_PACKAGE_SCOPE,
        "package_manifest_used_for_execution": False,
        "adapter_archive_extraction_performed": False,
        "browser_started": False,
        "pasteback": False,
        "real_downloaded_artifact_read": False,
    }


def _l25_34_source_module_shape() -> dict[str, Any]:
    src = _l25_34_source_summary_shape()
    return {
        "ok": True,
        "patch": "L25.34",
        "final_acceptance_marker": True,
        "controlled_package_run_ladder_final_acceptance": True,
        "accepted_l25_32b_controlled_run_package_proof": True,
        "accepted_l25_33a_key_normalized_broad_checkpoint": True,
        "accepted_package_run_scope": gate.EXPECTED_RUN_PACKAGE_SCOPE,
        "package_manifest_used_for_execution": False,
        "adapter_archive_extraction_performed": False,
        "browser_started": False,
        "pasteback_workflow_active": False,
        "real_downloaded_artifact_read": False,
        "source_l25_33a_summary": {
            "ok": True,
            "patch": "L25.33a",
            "repairs_patch": "L25.33",
            "package_run_ladder_complete": True,
            "key_normalization_repair_proven": True,
            "source_l25_32b_ok": True,
            "source_l25_32b_repairs_patches": src["source_l25_32b_repairs_patches"],
            "bundle_review_expected_shape_present": True,
            "package_run_allowed": True,
            "patchops_run_package_performed": True,
            "patchops_cli_run_package_invoked_for_archive_manifest": True,
            "patchops_cli_run_package_exit_code": 0,
            "patchops_cli_run_package_timed_out": False,
            "patchops_cli_run_package_review_rejected": False,
            "controlled_package_launcher_executed": True,
            "package_manifest_used_for_execution": False,
            "adapter_archive_extraction_performed": False,
            "browser_started": False,
            "pasteback": False,
            "real_downloaded_artifact_read": False,
            "package_run": True,
            "patchops_run_package_scope": gate.EXPECTED_RUN_PACKAGE_SCOPE,
        },
    }


def _validate_authorized_payload(payload: dict[str, Any]) -> None:
    _assert(payload.get("ok") is True, "authorized payload is not ok", payload)
    _assert(payload.get("patch") == "L25.35", "wrong patch marker", payload)
    _assert(payload.get("real_download_artifact_authorization_gate") is True, "authorization gate marker missing", payload)
    _assert(payload.get("real_download_artifact_authorization_readback_only") is True, "readback-only marker missing", payload)
    _assert(payload.get("real_download_artifact_authorization_granted_for_future_patch") is True, "future authorization not granted", payload)
    _assert(payload.get("accepted_controlled_package_run_ladder_final_acceptance") is True, "L25.34 final acceptance marker missing", payload)
    _assert(payload.get("accepted_package_run_scope") == gate.EXPECTED_RUN_PACKAGE_SCOPE, "wrong source package-run scope", payload)
    _assert(payload.get("real_downloaded_artifact_read") is False, "real artifact read must remain false", payload)
    _assert(payload.get("real_downloaded_artifact_path_opened") is False, "real artifact path open must remain false", payload)
    _assert(payload.get("real_downloaded_artifact_bytes_read") is False, "real artifact bytes read must remain false", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "real archive extraction must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_execution_allowed") is False, "package execution must remain false", payload)
    _assert(payload.get("package_run") is False, "package run must remain false in L25.35", payload)
    _assert(payload.get("pasteback_workflow_active") is False, "pasteback must remain false", payload)
    _assert(not _false_field_errors(payload), "non-false boundary fields: " + ", ".join(_false_field_errors(payload)), payload)


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    summary_source = _l25_34_source_summary_shape()
    module_source = _l25_34_source_module_shape()

    default_payload = gate.build_real_download_artifact_authorization_gate(root, source_payload=summary_source)
    _assert(default_payload.get("ok") is False, "default should not be ok without token", default_payload)
    _assert(default_payload.get("real_download_artifact_authorization_granted_for_future_patch") is False, "default must not grant future authorization", default_payload)

    authorized_summary_payload = gate.build_real_download_artifact_authorization_gate(
        root,
        source_payload=summary_source,
        allow_real_download_artifact_authorization=True,
        authorization_token=gate.REQUIRED_REAL_DOWNLOAD_ARTIFACT_AUTHORIZATION_TOKEN,
    )
    _validate_authorized_payload(authorized_summary_payload)

    authorized_module_payload = gate.build_real_download_artifact_authorization_gate(
        root,
        source_payload=module_source,
        allow_real_download_artifact_authorization=True,
        authorization_token=gate.REQUIRED_REAL_DOWNLOAD_ARTIFACT_AUTHORIZATION_TOKEN,
    )
    _validate_authorized_payload(authorized_module_payload)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_download_artifact_authorization_gate.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_download_artifact_authorization_gate.md"
    module_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    _assert(not _forbidden_import_hits(module_text), "forbidden imports in L25.35 module", authorized_summary_payload)
    _assert(not _forbidden_call_hits(module_text), "forbidden calls in L25.35 module", authorized_summary_payload)
    _assert("does not read a real downloaded artifact yet" in doc_text, "doc missing readback-only artifact boundary", authorized_summary_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_summary_payload)
    _assert("No real downloaded artifact bytes are read" in doc_text, "doc missing no bytes-read boundary", authorized_summary_payload)
    _assert("No package execution" in doc_text, "doc missing no package execution boundary", authorized_summary_payload)

    return {
        "ok": True,
        "patch": "L25.35",
        "authorization_gate": authorized_summary_payload.get("real_download_artifact_authorization_gate"),
        "authorization_readback_only": authorized_summary_payload.get("real_download_artifact_authorization_readback_only"),
        "default_future_authorized": default_payload.get("real_download_artifact_authorization_granted_for_future_patch"),
        "authorized_summary_shape": authorized_summary_payload.get("real_download_artifact_authorization_granted_for_future_patch"),
        "authorized_module_shape": authorized_module_payload.get("real_download_artifact_authorization_granted_for_future_patch"),
        "source_l25_34_final_acceptance": authorized_summary_payload.get("accepted_controlled_package_run_ladder_final_acceptance"),
        "accepted_package_run_scope": authorized_summary_payload.get("accepted_package_run_scope"),
        "real_downloaded_artifact_read": authorized_summary_payload.get("real_downloaded_artifact_read"),
        "real_downloaded_artifact_path_opened": authorized_summary_payload.get("real_downloaded_artifact_path_opened"),
        "real_downloaded_artifact_bytes_read": authorized_summary_payload.get("real_downloaded_artifact_bytes_read"),
        "real_archive_candidate_extracted": authorized_summary_payload.get("real_archive_candidate_extracted"),
        "browser_started": authorized_summary_payload.get("browser_started"),
        "package_execution_allowed": authorized_summary_payload.get("package_execution_allowed"),
        "package_run": authorized_summary_payload.get("package_run"),
        "pasteback": authorized_summary_payload.get("pasteback_workflow_active"),
        "git_commit_performed": authorized_summary_payload.get("git_commit_performed"),
        "git_push_performed": authorized_summary_payload.get("git_push_performed"),
        "next_patch": authorized_summary_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.35 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
