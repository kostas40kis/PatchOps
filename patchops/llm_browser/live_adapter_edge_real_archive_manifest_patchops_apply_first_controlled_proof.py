"""L25.29 first controlled archive manifest PatchOps apply proof.

This follows accepted L25.28. It reads exactly one controlled synthetic archive
manifest member, verifies that the manifest is zero-write and zero-validation,
writes a bounded runtime temporary manifest copy, and invokes only
`py -m patchops.cli apply <temp_manifest>` with a short timeout. It does not
invoke run-package, package execution, extraction, browser automation, pasteback,
or package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_apply_authorization_gate as l25_28

PATCH = "L25.29"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.29 Microsoft Edge controlled runtime archive manifest PatchOps apply first proof"
SOURCE_PATCH = "L25.28"
NEXT_PATCH = "L25.30 Microsoft Edge controlled runtime archive manifest PatchOps apply broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = "data/runtime/browser_downloads/l25_29_patchops_apply/future_real_patchops_apply_bundle.zip"
REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_APPLY_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_APPLY_FIRST_CONTROLLED_PROOF_AUTHORIZED"
TARGET_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
PATCHOPS_APPLY_SCOPE = "controlled_runtime_manifest_patchops_apply_only_zero_write_zero_validation_no_run_package_no_package_execution"
APPLY_TIMEOUT_SECONDS = 45
TEMP_MANIFEST_RELATIVE_PATH = "data/runtime/browser_downloads/l25_29_patchops_apply/manifest_for_patchops_apply.json"

ALWAYS_FALSE_FIELDS = (
    "patchops_cli_run_package_invoked_for_archive_manifest",
    "package_manifest_used_for_execution",
    "package_execution_allowed",
    "archive_member_extracted_to_project",
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


def _l25_28_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_28.build_archive_manifest_patchops_apply_authorization_gate(
            repo_root,
            allow_archive_manifest_patchops_apply_authorization=True,
            authorization_token=l25_28.REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_APPLY_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.28 PatchOps apply authorization readback failed: {type(exc).__name__}: {exc}"}


def _compact_text(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def _run_patchops_apply(repo_root: Path, manifest_path: Path) -> dict[str, Any]:
    command = ["py", "-m", "patchops.cli", "apply", str(manifest_path)]
    try:
        result = subprocess.run(
            command,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=APPLY_TIMEOUT_SECONDS,
            check=False,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        return {
            "command": " ".join(command),
            "exit_code": int(result.returncode),
            "timed_out": False,
            "stdout": _compact_text(stdout),
            "stderr": _compact_text(stderr),
            "stdout_has_result_pass": "Result             : PASS" in stdout or "Result   : PASS" in stdout or "Result : PASS" in stdout,
            "stdout_has_exit_zero": "ExitCode           : 0" in stdout or "ExitCode : 0" in stdout,
            "stdout_has_patch_name": "Patch Name         : synthetic_l25_29_patchops_apply_fixture" in stdout or "Patch Name           : synthetic_l25_29_patchops_apply_fixture" in stdout,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(command),
            "exit_code": 124,
            "timed_out": True,
            "stdout": _compact_text(exc.stdout or ""),
            "stderr": _compact_text((exc.stderr or "") + "\nTIMEOUT"),
            "stdout_has_result_pass": False,
            "stdout_has_exit_zero": False,
            "stdout_has_patch_name": False,
        }


def _manifest_is_zero_write_zero_validation(manifest_obj: Mapping[str, Any]) -> bool:
    return (
        manifest_obj.get("files_to_write") == []
        and manifest_obj.get("backup_files") == []
        and manifest_obj.get("validation_commands") == []
        and manifest_obj.get("smoke_commands") == []
        and manifest_obj.get("audit_commands") == []
        and manifest_obj.get("cleanup_commands") == []
        and manifest_obj.get("archive_commands") == []
    )


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_28_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_28_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_28_future_patchops_apply_authorized", "ok": source.get("archive_manifest_patchops_apply_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_28_apply_execution_false", "ok": source.get("archive_manifest_patchops_apply_allowed") is False and source.get("patchops_manifest_apply_performed") is False},
        {"name": "default_patchops_apply_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_28_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_patchops_apply_authorized": source.get("archive_manifest_patchops_apply_authorization_granted_for_future_patch"),
            "patchops_apply_allowed": source.get("archive_manifest_patchops_apply_allowed"),
            "patchops_manifest_apply_performed": source.get("patchops_manifest_apply_performed"),
            "source_l25_27_plan_invoked": source.get("source_l25_27_summary", {}).get("patchops_cli_plan_invoked_for_archive_manifest"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_patchops_apply_proof_requested": False,
        "archive_manifest_patchops_apply_proof_token_present": False,
        "archive_manifest_patchops_apply_proof_token_valid": False,
        "archive_manifest_patchops_apply_allowed": False,
        "manifest_payload_read": False,
        "manifest_payload_bytes_read": False,
        "manifest_payload_json_parsed": False,
        "manifest_zero_write_zero_validation": False,
        "manifest_temp_file_written_for_apply": False,
        "patchops_manifest_apply_performed": False,
        "patchops_manifest_validation_performed": False,
        "patchops_cli_apply_invoked_for_archive_manifest": False,
        "patchops_cli_apply_exit_code": None,
        "patchops_cli_apply_result_pass": False,
        "patchops_cli_apply_patch_name": None,
        "patchops_apply_scope": "default_readback_only_no_patchops_apply",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "apply_fixture_isolated_from_preflight_inspect_and_plan_fixtures": True,
        "zipfile_import_allowed_by_l25_29": True,
        "subprocess_patchops_apply_allowed_by_l25_29": True,
        "no_patchops_run_package_added_by_l25_29": True,
        "no_package_execution_added_by_l25_29": True,
        "no_archive_extraction_added_by_l25_29": True,
        "no_browser_permission_added_by_l25_29": True,
        "no_pasteback_or_package_run_permission_added_by_l25_29": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def build_archive_manifest_patchops_apply_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_patchops_apply_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    member_name: str = TARGET_MANIFEST_MEMBER_NAME,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_manifest_patchops_apply_proof:
        return _default_payload(root, target_url)

    source = _l25_28_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_APPLY_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    candidate_text = str(candidate).replace("\\", "/")
    member_is_allowed = member_name == TARGET_MANIFEST_MEMBER_NAME

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_28_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_28_future_patchops_apply_authorized", "ok": source.get("archive_manifest_patchops_apply_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_28_apply_execution_false", "ok": source.get("archive_manifest_patchops_apply_allowed") is False and source.get("patchops_manifest_apply_performed") is False},
        {"name": "source_l25_28_no_run_package_execution_extract_browser", "ok": source.get("patchops_cli_run_package_invoked_for_archive_manifest") is False and source.get("package_execution_allowed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "patchops_apply_proof_token_present", "ok": token_present},
        {"name": "patchops_apply_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_path_is_isolated_apply_fixture", "ok": "l25_29_patchops_apply" in candidate_text},
        {"name": "candidate_exists_before_apply", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_apply", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
        {"name": "target_member_is_manifest_member", "ok": member_is_allowed},
    ]

    apply_allowed = bool(all(check.get("ok") for check in checks))
    data = b""
    manifest_obj: dict[str, Any] = {}
    temp_manifest_path = root / TEMP_MANIFEST_RELATIVE_PATH
    apply_result: dict[str, Any] = {}
    apply_error: str | None = None
    temp_written = False
    zero_write_zero_validation = False
    if apply_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                data = archive.read(TARGET_MANIFEST_MEMBER_NAME)
            loaded = json.loads(data.decode("utf-8"))
            if isinstance(loaded, dict):
                manifest_obj = loaded
            zero_write_zero_validation = _manifest_is_zero_write_zero_validation(manifest_obj)
            checks.extend([
                {"name": "manifest_payload_read_succeeded", "ok": len(data) > 0},
                {"name": "manifest_payload_json_parsed", "ok": bool(manifest_obj)},
                {"name": "manifest_patch_name_matches", "ok": manifest_obj.get("patch_name") == "synthetic_l25_29_patchops_apply_fixture"},
                {"name": "manifest_active_profile_matches", "ok": manifest_obj.get("active_profile") == "generic_python"},
                {"name": "manifest_is_zero_write_zero_validation", "ok": zero_write_zero_validation},
            ])
            if zero_write_zero_validation:
                temp_manifest_path.parent.mkdir(parents=True, exist_ok=True)
                temp_manifest_path.write_bytes(data)
                temp_written = True
                apply_result = _run_patchops_apply(root, temp_manifest_path)
                checks.extend([
                    {"name": "temp_manifest_written_for_apply", "ok": temp_written and temp_manifest_path.exists()},
                    {"name": "patchops_apply_invoked_only", "ok": apply_result.get("command", "").startswith("py -m patchops.cli apply ")},
                    {"name": "patchops_apply_exit_zero", "ok": apply_result.get("exit_code") == 0},
                    {"name": "patchops_apply_not_timed_out", "ok": apply_result.get("timed_out") is False},
                    {"name": "patchops_apply_stdout_result_pass", "ok": apply_result.get("stdout_has_result_pass") is True},
                    {"name": "patchops_apply_stdout_exit_zero", "ok": apply_result.get("stdout_has_exit_zero") is True},
                    {"name": "patchops_apply_stdout_patch_name_matches", "ok": apply_result.get("stdout_has_patch_name") is True},
                ])
            else:
                checks.append({"name": "patchops_apply_blocked_until_zero_write_zero_validation", "ok": False})
        except Exception as exc:
            apply_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "patchops_apply_attempt", "ok": False, "error": apply_error})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_28_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_patchops_apply_authorized": source.get("archive_manifest_patchops_apply_authorization_granted_for_future_patch"),
            "patchops_apply_allowed": source.get("archive_manifest_patchops_apply_allowed"),
            "patchops_manifest_apply_performed": source.get("patchops_manifest_apply_performed"),
            "source_l25_27_plan_invoked": source.get("source_l25_27_summary", {}).get("patchops_cli_plan_invoked_for_archive_manifest"),
            "source_l25_27_plan_exit_code": source.get("source_l25_27_summary", {}).get("patchops_cli_plan_exit_code"),
            "source_l25_27_plan_json_object": source.get("source_l25_27_summary", {}).get("patchops_cli_plan_json_object"),
            "patchops_cli_run_package_invoked_for_archive_manifest": source.get("patchops_cli_run_package_invoked_for_archive_manifest"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_patchops_apply_proof_requested": True,
        "archive_manifest_patchops_apply_proof_token_present": token_present,
        "archive_manifest_patchops_apply_proof_token_valid": token_valid,
        "archive_manifest_patchops_apply_allowed": apply_allowed,
        "manifest_payload_read": apply_allowed,
        "manifest_payload_bytes_read": apply_allowed,
        "manifest_payload_json_parsed": bool(manifest_obj),
        "manifest_member_name_read": TARGET_MANIFEST_MEMBER_NAME if apply_allowed else None,
        "manifest_payload_byte_count": len(data),
        "manifest_patch_name": manifest_obj.get("patch_name"),
        "manifest_files_to_write_count": len(manifest_obj.get("files_to_write") or []),
        "manifest_validation_commands_count": len(manifest_obj.get("validation_commands") or []),
        "manifest_zero_write_zero_validation": zero_write_zero_validation,
        "manifest_temp_file_written_for_apply": temp_written,
        "manifest_temp_file_path": str(temp_manifest_path) if temp_written else None,
        "patchops_manifest_apply_performed": apply_allowed and apply_result.get("exit_code") == 0,
        "patchops_manifest_validation_performed": False,
        "patchops_cli_apply_invoked_for_archive_manifest": apply_allowed and zero_write_zero_validation,
        "patchops_cli_apply_exit_code": apply_result.get("exit_code"),
        "patchops_cli_apply_timed_out": apply_result.get("timed_out"),
        "patchops_cli_apply_stdout_result_pass": apply_result.get("stdout_has_result_pass"),
        "patchops_cli_apply_stdout_exit_zero": apply_result.get("stdout_has_exit_zero"),
        "patchops_cli_apply_patch_name": manifest_obj.get("patch_name") if apply_result.get("stdout_has_patch_name") else None,
        "patchops_apply_error": apply_error,
        "patchops_apply_scope": PATCHOPS_APPLY_SCOPE,
        "patchops_apply_command_summary": {
            "command_kind": "py -m patchops.cli apply",
            "timeout_seconds": APPLY_TIMEOUT_SECONDS,
            "exit_code": apply_result.get("exit_code"),
            "timed_out": apply_result.get("timed_out"),
        },
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "apply_fixture_isolated_from_preflight_inspect_and_plan_fixtures": True,
        "zipfile_import_allowed_by_l25_29": True,
        "subprocess_patchops_apply_allowed_by_l25_29": True,
        "json_manifest_parse_allowed_by_l25_29_for_zero_write_guard": True,
        "no_patchops_run_package_added_by_l25_29": True,
        "no_package_execution_added_by_l25_29": True,
        "no_archive_extraction_added_by_l25_29": True,
        "no_browser_permission_added_by_l25_29": True,
        "no_pasteback_or_package_run_permission_added_by_l25_29": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.29 invokes exactly one bounded PatchOps apply on a temp copy of the isolated controlled synthetic archive manifest.",
            "The synthetic manifest is guarded as zero-write and zero-validation before PatchOps apply is invoked.",
            "PatchOps run-package, package execution, extraction, browser, pasteback, send/submit, and package-run remain disabled.",
        ],
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"PatchOps Apply Invoked        : {payload.get('patchops_cli_apply_invoked_for_archive_manifest')}",
        f"PatchOps Apply Exit           : {payload.get('patchops_cli_apply_exit_code')}",
        f"PatchOps Apply Patch          : {payload.get('patchops_cli_apply_patch_name')}",
        f"Zero Write/Validation         : {payload.get('manifest_zero_write_zero_validation')}",
        f"Run Package Invoked           : {payload.get('patchops_cli_run_package_invoked_for_archive_manifest')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-archive-manifest-patchops-apply-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--member-name", default=TARGET_MANIFEST_MEMBER_NAME)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_patchops_apply_first_controlled_proof(
        args.repo_root,
        allow_archive_manifest_patchops_apply_proof=args.allow_archive_manifest_patchops_apply_proof,
        authorization_token=args.authorization_token,
        candidate_archive_path=args.candidate_archive_path,
        member_name=args.member_name,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
