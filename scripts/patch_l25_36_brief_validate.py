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

from patchops.llm_browser import live_adapter_edge_real_download_artifact_first_readback_proof as proof

FALSE_FIELDS = (
    "real_downloaded_manifest_read",
    "real_downloaded_manifest_member_opened",
    "real_downloaded_manifest_bytes_read",
    "real_downloaded_manifest_json_parsed",
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

REQUIRED_NAMES = ["bundle/run_with_patchops.ps1", "bundle/bundle_meta.json", "bundle/README.txt", "bundle/manifest.json", "bundle/content/.keep"]


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
    forbidden = {"selenium", "webdriver_manager", "pyperclip", "psutil", "subprocess"}
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


def _source_l25_35_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "patch": "L25.35",
        "authorization_gate": True,
        "authorization_readback_only": True,
        "authorized_summary_shape": True,
        "source_l25_34_final_acceptance": True,
        "accepted_package_run_scope": proof.EXPECTED_PACKAGE_RUN_SCOPE,
        "real_downloaded_artifact_read": False,
        "real_downloaded_artifact_path_opened": False,
        "real_downloaded_artifact_bytes_read": False,
        "real_archive_candidate_extracted": False,
        "browser_started": False,
        "package_execution_allowed": False,
        "package_run": False,
        "pasteback": False,
        "git_commit_performed": False,
        "git_push_performed": False,
    }


def _write_controlled_artifact(root: Path) -> Path:
    path = root / proof.DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "manifest_version": "1",
        "patch_name": "synthetic_l25_36_real_artifact_readback_fixture",
        "active_profile": "generic_python",
        "target_project_root": str(root),
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": [],
    }
    metadata = {
        "schema_version": "1",
        "patch_name": "synthetic_l25_36_real_artifact_readback_fixture",
        "bundle_mode": "controlled_artifact_readback_only",
        "launcher_path": "run_with_patchops.ps1",
        "manifest_path": "manifest.json",
        "content_root": "content",
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("bundle/run_with_patchops.ps1", "Write-Host 'L25.36 controlled artifact only - not executed'\n")
        archive.writestr("bundle/bundle_meta.json", json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        archive.writestr("bundle/README.txt", "L25.36 controlled artifact readback fixture. Do not execute.\n")
        archive.writestr("bundle/manifest.json", json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n")
        archive.writestr("bundle/content/.keep", "controlled artifact marker\n")
    return path


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _validate_payload(payload: dict[str, Any]) -> None:
    _assert(payload.get("ok") is True, "payload is not ok", payload)
    _assert(payload.get("patch") == "L25.36", "wrong patch marker", payload)
    _assert(payload.get("first_real_download_artifact_readback_proof") is True, "proof marker missing", payload)
    _assert(payload.get("artifact_readback_allowed") is True, "artifact readback not allowed", payload)
    _assert(payload.get("candidate_artifact_under_runtime_downloads") is True, "artifact must stay under L25.36 runtime downloads", payload)
    _assert(payload.get("real_downloaded_artifact_read") is True, "artifact read missing", payload)
    _assert(payload.get("real_downloaded_artifact_path_opened") is True, "artifact path open missing", payload)
    _assert(payload.get("real_downloaded_artifact_bytes_read") is True, "artifact bytes read missing", payload)
    _assert(payload.get("real_downloaded_artifact_byte_count", 0) > 0, "artifact byte count missing", payload)
    _assert(payload.get("real_downloaded_artifact_hash_computed") is True, "hash marker missing", payload)
    _assert(isinstance(payload.get("real_downloaded_artifact_sha256"), str) and len(payload.get("real_downloaded_artifact_sha256")) == 64, "sha256 missing", payload)
    _assert(payload.get("artifact_zip_opened_for_member_names_only") is True, "zip name listing marker missing", payload)
    _assert(payload.get("artifact_zip_member_names_read") is True, "zip member names marker missing", payload)
    _assert(payload.get("artifact_required_member_names_present") is True, "required member names missing", payload)
    _assert(payload.get("real_downloaded_manifest_read") is False, "manifest read must remain false", payload)
    _assert(payload.get("real_downloaded_manifest_member_opened") is False, "manifest member open must remain false", payload)
    _assert(payload.get("real_downloaded_manifest_bytes_read") is False, "manifest bytes read must remain false", payload)
    _assert(payload.get("real_downloaded_manifest_json_parsed") is False, "manifest parse must remain false", payload)
    _assert(payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", payload)
    _assert(payload.get("adapter_archive_extraction_performed") is False, "adapter extraction must remain false", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("package_execution_allowed") is False, "package execution must remain false", payload)
    _assert(payload.get("package_run") is False, "package run must remain false", payload)
    _assert(payload.get("patchops_cli_run_package_invoked_for_real_artifact") is False, "run-package must remain false", payload)
    _assert(payload.get("pasteback_workflow_active") is False, "pasteback must remain false", payload)
    _assert(not _false_field_errors(payload), "non-false boundary fields: " + ", ".join(_false_field_errors(payload)), payload)


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    artifact_path = _write_controlled_artifact(root)
    source = _source_l25_35_payload()

    default_payload = proof.build_real_download_artifact_first_readback_proof(root, source_payload=source, candidate_artifact_path=str(artifact_path))
    _assert(default_payload.get("ok") is False, "default should not pass without token", default_payload)
    _assert(default_payload.get("real_downloaded_artifact_read") is False, "default must not read artifact", default_payload)

    authorized_payload = proof.build_real_download_artifact_first_readback_proof(
        root,
        source_payload=source,
        allow_real_download_artifact_readback=True,
        authorization_token=proof.REQUIRED_REAL_DOWNLOAD_ARTIFACT_READBACK_TOKEN,
        candidate_artifact_path=str(artifact_path),
    )
    _validate_payload(authorized_payload)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_download_artifact_first_readback_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_download_artifact_first_readback_proof.md"
    module_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    _assert(not _forbidden_import_hits(module_text), "forbidden browser/subprocess imports in L25.36 module", authorized_payload)
    _assert(not _forbidden_call_hits(module_text), "forbidden extraction/execution calls in L25.36 module", authorized_payload)
    _assert("No real downloaded manifest member is opened" in doc_text, "doc missing no manifest-open boundary", authorized_payload)
    _assert("No archive extraction" in doc_text, "doc missing no extraction boundary", authorized_payload)
    _assert("No PatchOps run-package against the artifact" in doc_text, "doc missing no run-package boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.36",
        "artifact_path": str(artifact_path),
        "first_real_download_artifact_readback_proof": authorized_payload.get("first_real_download_artifact_readback_proof"),
        "artifact_readback_allowed": authorized_payload.get("artifact_readback_allowed"),
        "candidate_artifact_under_runtime_downloads": authorized_payload.get("candidate_artifact_under_runtime_downloads"),
        "real_downloaded_artifact_read": authorized_payload.get("real_downloaded_artifact_read"),
        "real_downloaded_artifact_path_opened": authorized_payload.get("real_downloaded_artifact_path_opened"),
        "real_downloaded_artifact_bytes_read": authorized_payload.get("real_downloaded_artifact_bytes_read"),
        "real_downloaded_artifact_hash_computed": authorized_payload.get("real_downloaded_artifact_hash_computed"),
        "real_downloaded_artifact_byte_count": authorized_payload.get("real_downloaded_artifact_byte_count"),
        "artifact_zip_opened_for_member_names_only": authorized_payload.get("artifact_zip_opened_for_member_names_only"),
        "artifact_zip_member_names_read": authorized_payload.get("artifact_zip_member_names_read"),
        "artifact_required_member_names_present": authorized_payload.get("artifact_required_member_names_present"),
        "real_downloaded_manifest_read": authorized_payload.get("real_downloaded_manifest_read"),
        "real_downloaded_manifest_member_opened": authorized_payload.get("real_downloaded_manifest_member_opened"),
        "real_downloaded_manifest_bytes_read": authorized_payload.get("real_downloaded_manifest_bytes_read"),
        "real_downloaded_manifest_json_parsed": authorized_payload.get("real_downloaded_manifest_json_parsed"),
        "real_archive_candidate_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "adapter_archive_extraction_performed": authorized_payload.get("adapter_archive_extraction_performed"),
        "browser_started": authorized_payload.get("browser_started"),
        "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
        "package_run": authorized_payload.get("package_run"),
        "patchops_cli_run_package_invoked_for_real_artifact": authorized_payload.get("patchops_cli_run_package_invoked_for_real_artifact"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.36 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
