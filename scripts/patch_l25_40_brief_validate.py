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

from patchops.llm_browser import live_adapter_edge_real_download_artifact_manifest_validation_final_acceptance_marker as final_marker

FALSE_FIELDS = (
    "artifact_path_opened_by_l25_40",
    "artifact_bytes_read_by_l25_40",
    "zip_member_opened_by_l25_40",
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


def _source_l25_39_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "patch": "L25.39",
        "manifest_validation_broad_checkpoint": True,
        "manifest_validation_broad_checkpoint_from_source_payload_only": True,
        "manifest_validation_broad_checkpoint_allowed": True,
        "accepted_manifest_member_name": "bundle/manifest.json",
        "accepted_manifest_patch_name": "synthetic_l25_37_manifest_readback_fixture",
        "accepted_manifest_version": "1",
        "accepted_manifest_files_to_write_count": 0,
        "accepted_manifest_validation_commands_count": 0,
        "accepted_manifest_zero_writes": True,
        "accepted_manifest_zero_validation_commands": True,
        "accepted_malformed_manifest_source_rejected": True,
        "broad_checkpoint_rejects_missing_malformed_source_rejection": True,
        "artifact_path_opened_by_l25_39": False,
        "artifact_bytes_read_by_l25_39": False,
        "zip_member_opened_by_l25_39": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "browser_started": False,
        "package_execution_allowed": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "pasteback": False,
    }


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _validate_payload(payload: dict[str, Any]) -> None:
    _assert(payload.get("ok") is True, "payload is not ok", payload)
    _assert(payload.get("patch") == "L25.40", "wrong patch marker", payload)
    _assert(payload.get("manifest_validation_final_acceptance_marker") is True, "final marker missing", payload)
    _assert(payload.get("manifest_validation_ladder_final_acceptance") is True, "final acceptance missing", payload)
    _assert(payload.get("manifest_validation_final_acceptance_from_source_payload_only") is True, "source-payload-only marker missing", payload)
    _assert(payload.get("accepted_l25_35_real_artifact_authorization_gate") is True, "L25.35 acceptance missing", payload)
    _assert(payload.get("accepted_l25_36_artifact_readback_proof") is True, "L25.36 acceptance missing", payload)
    _assert(payload.get("accepted_l25_37_manifest_member_readback_proof") is True, "L25.37 acceptance missing", payload)
    _assert(payload.get("accepted_l25_38_manifest_validation_checkpoint") is True, "L25.38 acceptance missing", payload)
    _assert(payload.get("accepted_l25_39_manifest_validation_broad_checkpoint") is True, "L25.39 acceptance missing", payload)
    _assert(payload.get("accepted_manifest_member_name") == "bundle/manifest.json", "manifest member mismatch", payload)
    _assert(payload.get("accepted_manifest_patch_name") == "synthetic_l25_37_manifest_readback_fixture", "manifest patch mismatch", payload)
    _assert(payload.get("accepted_manifest_version") == "1", "manifest version mismatch", payload)
    _assert(payload.get("accepted_manifest_files_to_write_count") == 0, "manifest should have zero writes", payload)
    _assert(payload.get("accepted_manifest_validation_commands_count") == 0, "manifest should have zero validation commands", payload)
    _assert(payload.get("accepted_manifest_zero_writes") is True, "zero-writes marker missing", payload)
    _assert(payload.get("accepted_manifest_zero_validation_commands") is True, "zero-validation marker missing", payload)
    _assert(payload.get("accepted_malformed_manifest_source_rejected") is True, "malformed-source rejection marker missing", payload)
    _assert(payload.get("accepted_broad_checkpoint_rejects_missing_malformed_source_rejection") is True, "broad malformed-source rejection marker missing", payload)
    _assert(payload.get("artifact_path_opened_by_l25_40") is False, "L25.40 must not open artifact path", payload)
    _assert(payload.get("artifact_bytes_read_by_l25_40") is False, "L25.40 must not read artifact bytes", payload)
    _assert(payload.get("zip_member_opened_by_l25_40") is False, "L25.40 must not open zip members", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("adapter_archive_extraction_performed") is False, "adapter extraction must remain false", payload)
    _assert(payload.get("archive_member_extracted_to_project") is False, "member extraction must remain false", payload)
    _assert(payload.get("artifact_member_written_to_project") is False, "artifact member write must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_execution_allowed") is False, "package execution must remain false", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("patchops_cli_run_package_invoked_for_real_artifact") is False, "run-package must remain false", payload)
    _assert(payload.get("pasteback_workflow_active") is False, "pasteback must remain false", payload)
    _assert(not _false_field_errors(payload), "non-false boundary fields: " + ", ".join(_false_field_errors(payload)), payload)


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    source = _source_l25_39_payload()

    default_payload = final_marker.build_real_download_artifact_manifest_validation_final_acceptance_marker(root, source_payload=source)
    _assert(default_payload.get("ok") is False, "default should not pass without token", default_payload)
    _assert(default_payload.get("manifest_validation_ladder_final_acceptance") is False, "default must not finalize acceptance", default_payload)

    authorized_payload = final_marker.build_real_download_artifact_manifest_validation_final_acceptance_marker(
        root,
        source_payload=source,
        allow_final_acceptance_marker=True,
        authorization_token=final_marker.REQUIRED_FINAL_MARKER_TOKEN,
    )
    _validate_payload(authorized_payload)

    malformed_source = dict(source)
    malformed_source["accepted_manifest_validation_commands_count"] = 1
    malformed_payload = final_marker.build_real_download_artifact_manifest_validation_final_acceptance_marker(
        root,
        source_payload=malformed_source,
        allow_final_acceptance_marker=True,
        authorization_token=final_marker.REQUIRED_FINAL_MARKER_TOKEN,
    )
    _assert(malformed_payload.get("ok") is False, "final marker must reject non-zero manifest validation commands", malformed_payload)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_download_artifact_manifest_validation_final_acceptance_marker.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_download_artifact_manifest_validation_final_acceptance_marker.md"
    module_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    _assert(not _forbidden_import_hits(module_text), "forbidden imports in L25.40 module", authorized_payload)
    _assert(not _forbidden_call_hits(module_text), "forbidden artifact/zip/execution calls in L25.40 module", authorized_payload)
    _assert("marks the real-download-artifact manifest-validation ladder complete" in doc_text, "doc missing final-acceptance wording", authorized_payload)
    _assert("This final marker does not open an artifact path" in doc_text, "doc missing no artifact-open boundary", authorized_payload)
    _assert("This final marker does not read artifact bytes" in doc_text, "doc missing no artifact-read boundary", authorized_payload)
    _assert("This final marker does not open ZIP members" in doc_text, "doc missing no zip-member boundary", authorized_payload)
    _assert("No PatchOps run-package against the artifact" in doc_text, "doc missing no run-package boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.40",
        "manifest_validation_final_acceptance_marker": authorized_payload.get("manifest_validation_final_acceptance_marker"),
        "manifest_validation_ladder_final_acceptance": authorized_payload.get("manifest_validation_ladder_final_acceptance"),
        "manifest_validation_final_acceptance_from_source_payload_only": authorized_payload.get("manifest_validation_final_acceptance_from_source_payload_only"),
        "accepted_l25_35_real_artifact_authorization_gate": authorized_payload.get("accepted_l25_35_real_artifact_authorization_gate"),
        "accepted_l25_36_artifact_readback_proof": authorized_payload.get("accepted_l25_36_artifact_readback_proof"),
        "accepted_l25_37_manifest_member_readback_proof": authorized_payload.get("accepted_l25_37_manifest_member_readback_proof"),
        "accepted_l25_38_manifest_validation_checkpoint": authorized_payload.get("accepted_l25_38_manifest_validation_checkpoint"),
        "accepted_l25_39_manifest_validation_broad_checkpoint": authorized_payload.get("accepted_l25_39_manifest_validation_broad_checkpoint"),
        "accepted_manifest_member_name": authorized_payload.get("accepted_manifest_member_name"),
        "accepted_manifest_patch_name": authorized_payload.get("accepted_manifest_patch_name"),
        "accepted_manifest_version": authorized_payload.get("accepted_manifest_version"),
        "accepted_manifest_files_to_write_count": authorized_payload.get("accepted_manifest_files_to_write_count"),
        "accepted_manifest_validation_commands_count": authorized_payload.get("accepted_manifest_validation_commands_count"),
        "accepted_manifest_zero_writes": authorized_payload.get("accepted_manifest_zero_writes"),
        "accepted_manifest_zero_validation_commands": authorized_payload.get("accepted_manifest_zero_validation_commands"),
        "accepted_malformed_manifest_source_rejected": authorized_payload.get("accepted_malformed_manifest_source_rejected"),
        "accepted_broad_checkpoint_rejects_missing_malformed_source_rejection": authorized_payload.get("accepted_broad_checkpoint_rejects_missing_malformed_source_rejection"),
        "final_marker_rejects_nonzero_manifest_validation_commands": malformed_payload.get("ok") is False,
        "artifact_path_opened_by_l25_40": authorized_payload.get("artifact_path_opened_by_l25_40"),
        "artifact_bytes_read_by_l25_40": authorized_payload.get("artifact_bytes_read_by_l25_40"),
        "zip_member_opened_by_l25_40": authorized_payload.get("zip_member_opened_by_l25_40"),
        "real_archive_candidate_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "adapter_archive_extraction_performed": authorized_payload.get("adapter_archive_extraction_performed"),
        "archive_member_extracted_to_project": authorized_payload.get("archive_member_extracted_to_project"),
        "artifact_member_written_to_project": authorized_payload.get("artifact_member_written_to_project"),
        "browser_started": authorized_payload.get("browser_started"),
        "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
        "package_run": authorized_payload.get("package_run"),
        "patchops_cli_run_package_invoked_for_real_artifact": authorized_payload.get("patchops_cli_run_package_invoked_for_real_artifact"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.40 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
