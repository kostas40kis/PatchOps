"""L25.23 first controlled archive manifest PatchOps inspect proof.

This follows accepted L25.22. It reads exactly one controlled synthetic archive
manifest member, writes a bounded runtime temporary manifest copy, and invokes
only `py -m patchops.cli inspect <temp_manifest>` with a short timeout. It does
not invoke plan, apply, run-package, package execution, extraction, browser
automation, pasteback, or package-run.

L25.23a repair note: the inspect proof uses its own isolated controlled archive
fixture path so it does not overwrite the shared L25.20/L25.21 preflight fixture
that the L25.22 source readback still depends on.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_inspect_authorization_gate as l25_22

PATCH = "L25.23"
PHASE = "L25"
REPAIR_PATCH = "L25.23a"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.23 Microsoft Edge controlled runtime archive manifest PatchOps inspect first proof"
SOURCE_PATCH = "L25.22"
NEXT_PATCH = "L25.24 Microsoft Edge controlled runtime archive manifest PatchOps inspect broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = "data/runtime/browser_downloads/l25_23_patchops_inspect/future_real_patchops_inspect_bundle.zip"
REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_INSPECT_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_INSPECT_FIRST_CONTROLLED_PROOF_AUTHORIZED"
TARGET_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
PATCHOPS_INSPECT_SCOPE = "controlled_runtime_manifest_patchops_inspect_only_no_plan_apply_run_package_no_execution"
INSPECT_TIMEOUT_SECONDS = 30
TEMP_MANIFEST_RELATIVE_PATH = "data/runtime/browser_downloads/l25_23_patchops_inspect/manifest_for_patchops_inspect.json"

ALWAYS_FALSE_FIELDS = (
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


def _l25_22_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_22.build_archive_manifest_patchops_inspect_authorization_gate(
            repo_root,
            allow_archive_manifest_patchops_inspect_authorization=True,
            authorization_token=l25_22.REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_INSPECT_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.22 PatchOps inspect authorization readback failed: {type(exc).__name__}: {exc}"}


def _compact_text(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def _run_patchops_inspect(repo_root: Path, manifest_path: Path) -> dict[str, Any]:
    command = ["py", "-m", "patchops.cli", "inspect", str(manifest_path)]
    try:
        result = subprocess.run(
            command,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=INSPECT_TIMEOUT_SECONDS,
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
    source = _l25_22_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_22_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_22_future_patchops_inspect_authorized", "ok": source.get("archive_manifest_patchops_inspect_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_22_inspect_execution_false", "ok": source.get("archive_manifest_patchops_inspect_allowed") is False and source.get("patchops_manifest_inspect_performed") is False},
        {"name": "default_patchops_inspect_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_22_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_patchops_inspect_authorized": source.get("archive_manifest_patchops_inspect_authorization_granted_for_future_patch"),
            "patchops_inspect_allowed": source.get("archive_manifest_patchops_inspect_allowed"),
            "patchops_manifest_inspect_performed": source.get("patchops_manifest_inspect_performed"),
            "patchops_cli_check_invoked_in_source": source.get("source_l25_21_summary", {}).get("patchops_cli_check_invoked_for_archive_manifest"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_patchops_inspect_proof_requested": False,
        "archive_manifest_patchops_inspect_proof_token_present": False,
        "archive_manifest_patchops_inspect_proof_token_valid": False,
        "archive_manifest_patchops_inspect_allowed": False,
        "manifest_payload_read": False,
        "manifest_payload_bytes_read": False,
        "manifest_temp_file_written_for_inspect": False,
        "patchops_manifest_inspect_performed": False,
        "patchops_manifest_validation_performed": False,
        "patchops_cli_inspect_invoked_for_archive_manifest": False,
        "patchops_cli_inspect_exit_code": None,
        "patchops_cli_inspect_json_object": False,
        "patchops_cli_inspect_patch_name": None,
        "patchops_inspect_scope": "default_readback_only_no_patchops_inspect",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "inspect_fixture_isolated_from_preflight_fixture": True,
        "zipfile_import_allowed_by_l25_23": True,
        "subprocess_patchops_inspect_allowed_by_l25_23": True,
        "no_patchops_plan_apply_run_package_added_by_l25_23": True,
        "no_package_execution_added_by_l25_23": True,
        "no_archive_extraction_added_by_l25_23": True,
        "no_browser_permission_added_by_l25_23": True,
        "no_pasteback_or_package_run_permission_added_by_l25_23": True,
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


def build_archive_manifest_patchops_inspect_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_patchops_inspect_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    member_name: str = TARGET_MANIFEST_MEMBER_NAME,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_manifest_patchops_inspect_proof:
        return _default_payload(root, target_url)

    source = _l25_22_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_INSPECT_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    member_is_allowed = member_name == TARGET_MANIFEST_MEMBER_NAME

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_22_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_22_future_patchops_inspect_authorized", "ok": source.get("archive_manifest_patchops_inspect_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_22_inspect_execution_false", "ok": source.get("archive_manifest_patchops_inspect_allowed") is False and source.get("patchops_manifest_inspect_performed") is False},
        {"name": "source_l25_22_no_plan_apply_run_package_execution_extract_browser", "ok": source.get("patchops_cli_plan_invoked_for_archive_manifest") is False and source.get("patchops_cli_apply_invoked_for_archive_manifest") is False and source.get("patchops_cli_run_package_invoked_for_archive_manifest") is False and source.get("package_execution_allowed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "patchops_inspect_proof_token_present", "ok": token_present},
        {"name": "patchops_inspect_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_path_is_isolated_from_preflight_fixture", "ok": "l25_23_patchops_inspect" in str(candidate).replace("\\", "/")},
        {"name": "candidate_exists_before_inspect", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_inspect", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
        {"name": "target_member_is_manifest_member", "ok": member_is_allowed},
    ]

    inspect_allowed = bool(all(check.get("ok") for check in checks))
    data = b""
    temp_manifest_path = root / TEMP_MANIFEST_RELATIVE_PATH
    inspect_result: dict[str, Any] = {}
    inspect_error: str | None = None
    temp_written = False
    if inspect_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                data = archive.read(TARGET_MANIFEST_MEMBER_NAME)
            temp_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            temp_manifest_path.write_bytes(data)
            temp_written = True
            inspect_result = _run_patchops_inspect(root, temp_manifest_path)
            parsed = inspect_result.get("parsed_stdout") or {}
            checks.extend([
                {"name": "manifest_payload_read_succeeded", "ok": len(data) > 0},
                {"name": "temp_manifest_written_for_inspect", "ok": temp_written and temp_manifest_path.exists()},
                {"name": "patchops_inspect_invoked_only", "ok": inspect_result.get("command", "").startswith("py -m patchops.cli inspect ")},
                {"name": "patchops_inspect_exit_zero", "ok": inspect_result.get("exit_code") == 0},
                {"name": "patchops_inspect_not_timed_out", "ok": inspect_result.get("timed_out") is False},
                {"name": "patchops_inspect_json_object", "ok": isinstance(parsed, dict)},
                {"name": "patchops_inspect_patch_name_matches", "ok": parsed.get("patch_name") == "synthetic_l25_23_patchops_inspect_fixture"},
                {"name": "patchops_inspect_active_profile_matches", "ok": parsed.get("active_profile") == "generic_python"},
                {"name": "patchops_inspect_manifest_version_matches", "ok": parsed.get("manifest_version") == "1"},
            ])
        except Exception as exc:
            inspect_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "patchops_inspect_attempt", "ok": False, "error": inspect_error})

    parsed_stdout = inspect_result.get("parsed_stdout") if isinstance(inspect_result, dict) else None
    if not isinstance(parsed_stdout, dict):
        parsed_stdout = {}
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_22_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_patchops_inspect_authorized": source.get("archive_manifest_patchops_inspect_authorization_granted_for_future_patch"),
            "patchops_inspect_allowed": source.get("archive_manifest_patchops_inspect_allowed"),
            "patchops_manifest_inspect_performed": source.get("patchops_manifest_inspect_performed"),
            "source_l25_21_check_invoked": source.get("source_l25_21_summary", {}).get("patchops_cli_check_invoked_for_archive_manifest"),
            "source_l25_21_check_exit_code": source.get("source_l25_21_summary", {}).get("patchops_cli_check_exit_code"),
            "source_l25_21_check_ok": source.get("source_l25_21_summary", {}).get("patchops_cli_check_ok"),
            "patchops_cli_plan_invoked_for_archive_manifest": source.get("patchops_cli_plan_invoked_for_archive_manifest"),
            "patchops_cli_apply_invoked_for_archive_manifest": source.get("patchops_cli_apply_invoked_for_archive_manifest"),
            "patchops_cli_run_package_invoked_for_archive_manifest": source.get("patchops_cli_run_package_invoked_for_archive_manifest"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_patchops_inspect_proof_requested": True,
        "archive_manifest_patchops_inspect_proof_token_present": token_present,
        "archive_manifest_patchops_inspect_proof_token_valid": token_valid,
        "archive_manifest_patchops_inspect_allowed": inspect_allowed,
        "manifest_payload_read": inspect_allowed,
        "manifest_payload_bytes_read": inspect_allowed,
        "manifest_member_name_read": TARGET_MANIFEST_MEMBER_NAME if inspect_allowed else None,
        "manifest_payload_byte_count": len(data),
        "manifest_temp_file_written_for_inspect": temp_written,
        "manifest_temp_file_path": str(temp_manifest_path) if temp_written else None,
        "patchops_manifest_inspect_performed": inspect_allowed and inspect_result.get("exit_code") == 0,
        "patchops_manifest_validation_performed": False,
        "patchops_cli_inspect_invoked_for_archive_manifest": inspect_allowed,
        "patchops_cli_inspect_exit_code": inspect_result.get("exit_code"),
        "patchops_cli_inspect_timed_out": inspect_result.get("timed_out"),
        "patchops_cli_inspect_json_object": isinstance(parsed_stdout, dict) and bool(parsed_stdout),
        "patchops_cli_inspect_patch_name": parsed_stdout.get("patch_name"),
        "patchops_cli_inspect_active_profile": parsed_stdout.get("active_profile"),
        "patchops_cli_inspect_manifest_version": parsed_stdout.get("manifest_version"),
        "patchops_cli_inspect_target_project_root_present": bool(parsed_stdout.get("target_project_root")),
        "patchops_inspect_error": inspect_error,
        "patchops_inspect_scope": PATCHOPS_INSPECT_SCOPE,
        "patchops_inspect_command_summary": {
            "command_kind": "py -m patchops.cli inspect",
            "timeout_seconds": INSPECT_TIMEOUT_SECONDS,
            "exit_code": inspect_result.get("exit_code"),
            "timed_out": inspect_result.get("timed_out"),
        },
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "inspect_fixture_isolated_from_preflight_fixture": True,
        "zipfile_import_allowed_by_l25_23": True,
        "subprocess_patchops_inspect_allowed_by_l25_23": True,
        "no_patchops_plan_apply_run_package_added_by_l25_23": True,
        "no_package_execution_added_by_l25_23": True,
        "no_archive_extraction_added_by_l25_23": True,
        "no_browser_permission_added_by_l25_23": True,
        "no_pasteback_or_package_run_permission_added_by_l25_23": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.23 invokes exactly one bounded PatchOps inspect on a temp copy of the isolated controlled synthetic archive manifest.",
            "PatchOps plan/apply/run-package, package execution, extraction, browser, pasteback, send/submit, and package-run remain disabled.",
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
        f"Repair Patch                  : {payload.get('repair_patch')}",
        f"Status                        : {payload.get('status')}",
        f"PatchOps Inspect Invoked      : {payload.get('patchops_cli_inspect_invoked_for_archive_manifest')}",
        f"PatchOps Inspect Exit         : {payload.get('patchops_cli_inspect_exit_code')}",
        f"PatchOps Inspect Patch        : {payload.get('patchops_cli_inspect_patch_name')}",
        f"Fixture Isolated              : {payload.get('inspect_fixture_isolated_from_preflight_fixture')}",
        f"Plan Invoked                  : {payload.get('patchops_cli_plan_invoked_for_archive_manifest')}",
        f"Apply Invoked                 : {payload.get('patchops_cli_apply_invoked_for_archive_manifest')}",
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
    parser.add_argument("--allow-archive-manifest-patchops-inspect-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--member-name", default=TARGET_MANIFEST_MEMBER_NAME)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_patchops_inspect_first_controlled_proof(
        args.repo_root,
        allow_archive_manifest_patchops_inspect_proof=args.allow_archive_manifest_patchops_inspect_proof,
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
