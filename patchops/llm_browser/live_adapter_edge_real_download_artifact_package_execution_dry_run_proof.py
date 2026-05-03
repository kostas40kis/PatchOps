"""L25.42 first controlled package-execution dry-run proof.

This follows accepted L25.41. It validates the accepted L25.41 authorization
source payload and renders the PatchOps run-package command that a future patch
would execute against a controlled artifact path.

This is a dry-run only proof. It does not invoke PatchOps run-package, execute a
package, open artifact paths, read bytes, open ZIP members, extract archives,
start browsers, trigger downloads, paste/send, start localhost, use Selenium/CDP
or DOM scraping, commit, or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.42"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.42 Microsoft Edge controlled runtime real-download artifact package-execution first controlled dry-run proof"
SOURCE_PATCH = "L25.41"
NEXT_PATCH = "L25.43 Microsoft Edge controlled runtime real-download artifact package-execution dry-run broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH = "data/runtime/browser_downloads/l25_42_package_execution_dry_run/future_real_downloaded_package.zip"
REQUIRED_PACKAGE_EXECUTION_DRY_RUN_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_PACKAGE_EXECUTION_DRY_RUN_AUTHORIZED"
EXPECTED_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
EXPECTED_MANIFEST_PATCH_NAME = "synthetic_l25_37_manifest_readback_fixture"
EXPECTED_MANIFEST_VERSION = "1"

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


def _first(payload: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload.get(name)
    return default


def _normalize_l25_41_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "package_execution_authorization_gate": source.get("package_execution_authorization_gate"),
        "package_execution_authorization_from_source_payload_only": source.get("package_execution_authorization_from_source_payload_only"),
        "package_execution_authorization_granted_for_future_patch": source.get("package_execution_authorization_granted_for_future_patch"),
        "future_package_execution_requires_separate_l25_42_gate_and_token": source.get("future_package_execution_requires_separate_l25_42_gate_and_token"),
        "accepted_manifest_validation_ladder_final_acceptance": source.get("accepted_manifest_validation_ladder_final_acceptance"),
        "accepted_manifest_member_name": source.get("accepted_manifest_member_name"),
        "accepted_manifest_patch_name": source.get("accepted_manifest_patch_name"),
        "accepted_manifest_version": source.get("accepted_manifest_version"),
        "accepted_manifest_files_to_write_count": source.get("accepted_manifest_files_to_write_count"),
        "accepted_manifest_validation_commands_count": source.get("accepted_manifest_validation_commands_count"),
        "accepted_manifest_zero_writes": source.get("accepted_manifest_zero_writes"),
        "accepted_manifest_zero_validation_commands": source.get("accepted_manifest_zero_validation_commands"),
        "authorization_rejects_source_that_already_ran_package": source.get("authorization_rejects_source_that_already_ran_package"),
        "artifact_path_opened_by_l25_41": source.get("artifact_path_opened_by_l25_41", False),
        "artifact_bytes_read_by_l25_41": source.get("artifact_bytes_read_by_l25_41", False),
        "zip_member_opened_by_l25_41": source.get("zip_member_opened_by_l25_41", False),
        "real_archive_candidate_extracted": source.get("real_archive_candidate_extracted", False),
        "adapter_archive_extraction_performed": source.get("adapter_archive_extraction_performed", False),
        "archive_member_extracted_to_project": source.get("archive_member_extracted_to_project", False),
        "artifact_member_written_to_project": source.get("artifact_member_written_to_project", False),
        "browser_started": source.get("browser_started", False),
        "package_manifest_used_for_execution": source.get("package_manifest_used_for_execution", False),
        "package_execution_allowed": source.get("package_execution_allowed", False),
        "package_execution_performed_by_adapter": source.get("package_execution_performed_by_adapter", False),
        "package_run": source.get("package_run", False),
        "patchops_cli_run_package_invoked_for_real_artifact": source.get("patchops_cli_run_package_invoked_for_real_artifact", False),
        "pasteback": _first(source, "pasteback", "pasteback_workflow_active", default=False),
    }


def _artifact_under_l25_42_runtime(root: Path, artifact_path: Path) -> bool:
    try:
        base = (root / "data" / "runtime" / "browser_downloads" / "l25_42_package_execution_dry_run").resolve()
        return str(artifact_path.resolve()).startswith(str(base))
    except OSError:
        return False


def _render_run_package_command(root: Path, artifact_path: Path) -> dict[str, Any]:
    args = ["-m", "patchops.cli", "run-package", str(artifact_path), "--wrapper-root", str(root)]
    return {
        "program": "py",
        "args": args,
        "text": "py " + " ".join('"' + value + '"' if " " in value else value for value in args),
    }


def build_real_download_artifact_package_execution_dry_run_proof(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_package_execution_dry_run: bool = False,
    authorization_token: str | None = None,
    candidate_artifact_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _normalize_l25_41_source(source_payload)
    artifact_path = Path(candidate_artifact_path) if candidate_artifact_path else root / DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_PACKAGE_EXECUTION_DRY_RUN_TOKEN
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.41"
        and source.get("package_execution_authorization_gate") is True
        and source.get("package_execution_authorization_from_source_payload_only") is True
        and source.get("package_execution_authorization_granted_for_future_patch") is True
        and source.get("future_package_execution_requires_separate_l25_42_gate_and_token") is True
        and source.get("accepted_manifest_validation_ladder_final_acceptance") is True
        and source.get("accepted_manifest_member_name") == EXPECTED_MANIFEST_MEMBER_NAME
        and source.get("accepted_manifest_patch_name") == EXPECTED_MANIFEST_PATCH_NAME
        and source.get("accepted_manifest_version") == EXPECTED_MANIFEST_VERSION
        and source.get("accepted_manifest_files_to_write_count") == 0
        and source.get("accepted_manifest_validation_commands_count") == 0
        and source.get("accepted_manifest_zero_writes") is True
        and source.get("accepted_manifest_zero_validation_commands") is True
        and source.get("authorization_rejects_source_that_already_ran_package") is True
        and source.get("artifact_path_opened_by_l25_41") is False
        and source.get("artifact_bytes_read_by_l25_41") is False
        and source.get("zip_member_opened_by_l25_41") is False
        and source.get("real_archive_candidate_extracted") is False
        and source.get("adapter_archive_extraction_performed") is False
        and source.get("archive_member_extracted_to_project") is False
        and source.get("artifact_member_written_to_project") is False
        and source.get("browser_started") is False
        and source.get("package_manifest_used_for_execution") is False
        and source.get("package_execution_allowed") is False
        and source.get("package_execution_performed_by_adapter") is False
        and source.get("package_run") is False
        and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False
        and source.get("pasteback") is False
    )
    path_under_runtime = _artifact_under_l25_42_runtime(root, artifact_path)
    path_suffix_zip = artifact_path.suffix.lower() == ".zip"
    dry_run_allowed = bool(source_ok and allow_package_execution_dry_run and token_valid and path_under_runtime and path_suffix_zip)
    command = _render_run_package_command(root, artifact_path) if dry_run_allowed else {"program": None, "args": [], "text": None}
    checks: list[dict[str, Any]] = [
        {"name": "source_l25_41_payload_ok", "ok": source_ok},
        {"name": "dry_run_token_present", "ok": token_present},
        {"name": "dry_run_token_valid", "ok": token_valid},
        {"name": "dry_run_explicitly_allowed", "ok": allow_package_execution_dry_run is True},
        {"name": "candidate_artifact_suffix_zip", "ok": path_suffix_zip},
        {"name": "candidate_artifact_under_l25_42_runtime", "ok": path_under_runtime},
        {"name": "package_execution_dry_run_allowed", "ok": dry_run_allowed},
    ]
    if dry_run_allowed:
        checks.extend([
            {"name": "would_run_program_py", "ok": command.get("program") == "py"},
            {"name": "would_run_patchops_run_package", "ok": command.get("args", [])[0:3] == ["-m", "patchops.cli", "run-package"]},
            {"name": "would_run_wrapper_root_present", "ok": "--wrapper-root" in command.get("args", [])},
            {"name": "dry_run_did_not_invoke_run_package", "ok": True},
        ])
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "package_execution_first_controlled_dry_run_proof": True,
        "package_execution_dry_run_only": True,
        "package_execution_dry_run_from_source_payload_only": True,
        "package_execution_dry_run_requested": bool(allow_package_execution_dry_run or token_present),
        "package_execution_dry_run_token_present": token_present,
        "package_execution_dry_run_token_valid": token_valid,
        "package_execution_dry_run_allowed": dry_run_allowed,
        "source_l25_41_summary": source,
        "candidate_artifact_path": str(artifact_path),
        "candidate_artifact_relative_path": DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH,
        "candidate_artifact_suffix_zip": path_suffix_zip,
        "candidate_artifact_under_l25_42_runtime": path_under_runtime,
        "would_run_command_rendered": dry_run_allowed,
        "would_run_command_program": command.get("program"),
        "would_run_command_args": command.get("args"),
        "would_run_command_text": command.get("text"),
        "would_invoke_patchops_run_package_in_future_patch": dry_run_allowed,
        "artifact_path_opened_by_l25_42": False,
        "artifact_bytes_read_by_l25_42": False,
        "zip_member_opened_by_l25_42": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_execution_performed_by_adapter": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "no_browser_permission_added_by_l25_42": True,
        "no_download_permission_added_by_l25_42": True,
        "no_artifact_or_zip_read_permission_added_by_l25_42": True,
        "no_archive_extraction_permission_added_by_l25_42": True,
        "no_package_execution_performed_by_l25_42": True,
        "no_patchops_run_package_invocation_by_l25_42": True,
        "no_pasteback_permission_added_by_l25_42": True,
        "no_git_permission_added_by_l25_42": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    for field in FALSE_FIELDS:
        if field not in payload:
            payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Dry Run Allowed               : {payload.get('package_execution_dry_run_allowed')}",
        f"Would Run Rendered            : {payload.get('would_run_command_rendered')}",
        f"PatchOps Run-Package Invoked  : {payload.get('patchops_cli_run_package_invoked_for_real_artifact')}",
        f"Package Execution Allowed     : {payload.get('package_execution_allowed')}",
        f"Artifact Opened By L25.42     : {payload.get('artifact_path_opened_by_l25_42')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--allow-package-execution-dry-run", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-artifact-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_package_execution_dry_run_proof(
        args.repo_root,
        source_payload=source_payload,
        allow_package_execution_dry_run=args.allow_package_execution_dry_run,
        authorization_token=args.authorization_token,
        candidate_artifact_path=args.candidate_artifact_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
