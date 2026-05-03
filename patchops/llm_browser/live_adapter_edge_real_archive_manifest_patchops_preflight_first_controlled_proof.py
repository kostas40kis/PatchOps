"""L25.20 first controlled archive manifest PatchOps preflight proof.

This follows accepted L25.19. It reads exactly one controlled synthetic archive
manifest member, writes a bounded runtime temporary manifest copy, and invokes
only `py -m patchops.cli check <temp_manifest>` with a short timeout. It does not
invoke inspect, plan, apply, run-package, package execution, extraction, browser
automation, pasteback, or package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_authorization_gate as l25_19
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_schema_validation_first_controlled_proof as schema_proof

PATCH = "L25.20"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.20 Microsoft Edge controlled runtime archive manifest PatchOps preflight first proof"
SOURCE_PATCH = "L25.19"
NEXT_PATCH = "L25.21 Microsoft Edge controlled runtime archive manifest PatchOps preflight broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = schema_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_FIRST_CONTROLLED_PROOF_AUTHORIZED"
TARGET_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
PATCHOPS_PREFLIGHT_SCOPE = "controlled_runtime_manifest_patchops_check_only_no_inspect_plan_apply_no_execution"
PREFLIGHT_TIMEOUT_SECONDS = 30
TEMP_MANIFEST_RELATIVE_PATH = "data/runtime/browser_downloads/l25_20_patchops_preflight/manifest_for_patchops_check.json"

ALWAYS_FALSE_FIELDS = (
    "patchops_cli_inspect_invoked_for_archive_manifest",
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


def _l25_19_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_19.build_archive_manifest_patchops_preflight_authorization_gate(
            repo_root,
            allow_archive_manifest_patchops_preflight_authorization=True,
            authorization_token=l25_19.REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.19 PatchOps preflight authorization readback failed: {type(exc).__name__}: {exc}"}


def _compact_text(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def _run_patchops_check(repo_root: Path, manifest_path: Path) -> dict[str, Any]:
    command = ["py", "-m", "patchops.cli", "check", str(manifest_path)]
    try:
        result = subprocess.run(
            command,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=PREFLIGHT_TIMEOUT_SECONDS,
            check=False,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        parsed_stdout: dict[str, Any] | None = None
        try:
            loaded = json.loads(stdout) if stdout.strip() else None
            if isinstance(loaded, dict):
                parsed_stdout = loaded
        except Exception:
            parsed_stdout = None
        return {
            "command": " ".join(command),
            "exit_code": int(result.returncode),
            "timed_out": False,
            "stdout": _compact_text(stdout),
            "stderr": _compact_text(stderr),
            "parsed_stdout": parsed_stdout,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(command),
            "exit_code": 124,
            "timed_out": True,
            "stdout": _compact_text(exc.stdout or ""),
            "stderr": _compact_text((exc.stderr or "") + "\nTIMEOUT"),
            "parsed_stdout": None,
        }


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_19_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_19_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_19_future_patchops_preflight_authorized", "ok": source.get("archive_manifest_patchops_preflight_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_19_preflight_execution_false", "ok": source.get("archive_manifest_patchops_preflight_allowed") is False and source.get("patchops_manifest_preflight_performed") is False},
        {"name": "default_patchops_preflight_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_19_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_patchops_preflight_authorized": source.get("archive_manifest_patchops_preflight_authorization_granted_for_future_patch"),
            "patchops_preflight_allowed": source.get("archive_manifest_patchops_preflight_allowed"),
            "patchops_manifest_preflight_performed": source.get("patchops_manifest_preflight_performed"),
            "patchops_manifest_validation_performed": source.get("patchops_manifest_validation_performed"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_patchops_preflight_proof_requested": False,
        "archive_manifest_patchops_preflight_proof_token_present": False,
        "archive_manifest_patchops_preflight_proof_token_valid": False,
        "archive_manifest_patchops_preflight_allowed": False,
        "manifest_payload_read": False,
        "manifest_temp_file_written_for_preflight": False,
        "patchops_manifest_preflight_performed": False,
        "patchops_manifest_validation_performed": False,
        "patchops_cli_check_invoked_for_archive_manifest": False,
        "patchops_cli_check_exit_code": None,
        "patchops_cli_check_ok": False,
        "patchops_cli_check_issue_count": None,
        "patchops_preflight_scope": "default_readback_only_no_patchops_check",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "zipfile_import_allowed_by_l25_20": True,
        "subprocess_patchops_check_allowed_by_l25_20": True,
        "no_patchops_inspect_plan_apply_added_by_l25_20": True,
        "no_package_execution_added_by_l25_20": True,
        "no_archive_extraction_added_by_l25_20": True,
        "no_browser_permission_added_by_l25_20": True,
        "no_pasteback_or_package_run_permission_added_by_l25_20": True,
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


def build_archive_manifest_patchops_preflight_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_patchops_preflight_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    member_name: str = TARGET_MANIFEST_MEMBER_NAME,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_manifest_patchops_preflight_proof:
        return _default_payload(root, target_url)

    source = _l25_19_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    member_is_allowed = member_name == TARGET_MANIFEST_MEMBER_NAME

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_19_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_19_future_patchops_preflight_authorized", "ok": source.get("archive_manifest_patchops_preflight_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_19_preflight_execution_false", "ok": source.get("archive_manifest_patchops_preflight_allowed") is False and source.get("patchops_manifest_preflight_performed") is False},
        {"name": "source_l25_19_no_validation_execution_extract_browser_package", "ok": source.get("patchops_manifest_validation_performed") is False and source.get("package_execution_allowed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "patchops_preflight_proof_token_present", "ok": token_present},
        {"name": "patchops_preflight_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_exists_before_preflight", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_preflight", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
        {"name": "target_member_is_manifest_member", "ok": member_is_allowed},
    ]

    preflight_allowed = bool(all(check.get("ok") for check in checks))
    data = b""
    temp_manifest_path = root / TEMP_MANIFEST_RELATIVE_PATH
    preflight_result: dict[str, Any] = {}
    preflight_error: str | None = None
    temp_written = False
    if preflight_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                data = archive.read(TARGET_MANIFEST_MEMBER_NAME)
            temp_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            temp_manifest_path.write_bytes(data)
            temp_written = True
            preflight_result = _run_patchops_check(root, temp_manifest_path)
            parsed = preflight_result.get("parsed_stdout") or {}
            checks.extend([
                {"name": "manifest_payload_read_succeeded", "ok": len(data) > 0},
                {"name": "temp_manifest_written_for_preflight", "ok": temp_written and temp_manifest_path.exists()},
                {"name": "patchops_check_invoked_only", "ok": preflight_result.get("command", "").startswith("py -m patchops.cli check ")},
                {"name": "patchops_check_exit_zero", "ok": preflight_result.get("exit_code") == 0},
                {"name": "patchops_check_not_timed_out", "ok": preflight_result.get("timed_out") is False},
                {"name": "patchops_check_json_ok", "ok": parsed.get("ok") is True},
                {"name": "patchops_check_issue_count_zero", "ok": parsed.get("issue_count") == 0},
                {"name": "patchops_check_patch_name_matches", "ok": parsed.get("patch_name") == "synthetic_l25_20_patchops_check_fixture"},
            ])
        except Exception as exc:
            preflight_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "patchops_check_preflight_attempt", "ok": False, "error": preflight_error})

    parsed_stdout = preflight_result.get("parsed_stdout") if isinstance(preflight_result, dict) else None
    if not isinstance(parsed_stdout, dict):
        parsed_stdout = {}
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_19_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_patchops_preflight_authorized": source.get("archive_manifest_patchops_preflight_authorization_granted_for_future_patch"),
            "patchops_preflight_allowed": source.get("archive_manifest_patchops_preflight_allowed"),
            "patchops_manifest_preflight_performed": source.get("patchops_manifest_preflight_performed"),
            "patchops_manifest_validation_performed": source.get("patchops_manifest_validation_performed"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_patchops_preflight_proof_requested": True,
        "archive_manifest_patchops_preflight_proof_token_present": token_present,
        "archive_manifest_patchops_preflight_proof_token_valid": token_valid,
        "archive_manifest_patchops_preflight_allowed": preflight_allowed,
        "manifest_payload_read": preflight_allowed,
        "manifest_payload_bytes_read": preflight_allowed,
        "manifest_member_name_read": TARGET_MANIFEST_MEMBER_NAME if preflight_allowed else None,
        "manifest_payload_byte_count": len(data),
        "manifest_temp_file_written_for_preflight": temp_written,
        "manifest_temp_file_path": str(temp_manifest_path) if temp_written else None,
        "patchops_manifest_preflight_performed": preflight_allowed and preflight_result.get("exit_code") == 0,
        "patchops_manifest_validation_performed": preflight_allowed and preflight_result.get("exit_code") == 0,
        "patchops_cli_check_invoked_for_archive_manifest": preflight_allowed,
        "patchops_cli_check_exit_code": preflight_result.get("exit_code"),
        "patchops_cli_check_timed_out": preflight_result.get("timed_out"),
        "patchops_cli_check_ok": parsed_stdout.get("ok") is True,
        "patchops_cli_check_issue_count": parsed_stdout.get("issue_count"),
        "patchops_cli_check_patch_name": parsed_stdout.get("patch_name"),
        "patchops_cli_check_active_profile": parsed_stdout.get("active_profile"),
        "patchops_preflight_error": preflight_error,
        "patchops_preflight_scope": PATCHOPS_PREFLIGHT_SCOPE,
        "patchops_preflight_command_summary": {
            "command_kind": "py -m patchops.cli check",
            "timeout_seconds": PREFLIGHT_TIMEOUT_SECONDS,
            "exit_code": preflight_result.get("exit_code"),
            "timed_out": preflight_result.get("timed_out"),
        },
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "zipfile_import_allowed_by_l25_20": True,
        "subprocess_patchops_check_allowed_by_l25_20": True,
        "no_patchops_inspect_plan_apply_added_by_l25_20": True,
        "no_package_execution_added_by_l25_20": True,
        "no_archive_extraction_added_by_l25_20": True,
        "no_browser_permission_added_by_l25_20": True,
        "no_pasteback_or_package_run_permission_added_by_l25_20": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.20 invokes exactly one bounded PatchOps check preflight on a temp copy of the controlled synthetic archive manifest.",
            "PatchOps inspect/plan/apply, package execution, extraction, browser, pasteback, send/submit, and package-run remain disabled.",
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
        f"PatchOps Check Invoked        : {payload.get('patchops_cli_check_invoked_for_archive_manifest')}",
        f"PatchOps Check Exit           : {payload.get('patchops_cli_check_exit_code')}",
        f"PatchOps Check OK             : {payload.get('patchops_cli_check_ok')}",
        f"Inspect Invoked               : {payload.get('patchops_cli_inspect_invoked_for_archive_manifest')}",
        f"Plan Invoked                  : {payload.get('patchops_cli_plan_invoked_for_archive_manifest')}",
        f"Apply Invoked                 : {payload.get('patchops_cli_apply_invoked_for_archive_manifest')}",
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
    parser.add_argument("--allow-archive-manifest-patchops-preflight-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--member-name", default=TARGET_MANIFEST_MEMBER_NAME)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_patchops_preflight_first_controlled_proof(
        args.repo_root,
        allow_archive_manifest_patchops_preflight_proof=args.allow_archive_manifest_patchops_preflight_proof,
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
