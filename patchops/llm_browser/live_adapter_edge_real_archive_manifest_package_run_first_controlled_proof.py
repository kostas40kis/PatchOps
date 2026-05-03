"""L25.32 first controlled archive manifest package-run proof.

This follows accepted L25.31. It invokes exactly one bounded
`py -m patchops.cli run-package <controlled_zip> --wrapper-root <repo>` command
against a synthetic package ZIP whose root launcher writes only a tiny Desktop
proof report and exits zero. It does not start a browser, inspect pages, paste,
send, use Selenium/CDP/DOM scraping, use a real downloaded artifact, or run a
package produced by ChatGPT.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_package_run_authorization_gate as l25_31

PATCH = "L25.32"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.32 Microsoft Edge controlled runtime archive manifest package-run first proof"
SOURCE_PATCH = "L25.31"
NEXT_PATCH = "L25.33 Microsoft Edge controlled runtime archive manifest package-run broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = "data/runtime/browser_downloads/l25_32_package_run/future_real_package_run_bundle.zip"
REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PACKAGE_RUN_FIRST_CONTROLLED_PROOF_AUTHORIZED"
RUN_PACKAGE_TIMEOUT_SECONDS = 75
LAUNCHER_MARKER = "L25_32_RUN_PACKAGE_LAUNCHER_MARKER"
PACKAGE_RUN_SCOPE = "controlled_runtime_package_run_only_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"

ALWAYS_FALSE_FIELDS = (
    "real_downloaded_manifest_read",
    "real_downloaded_artifact_read",
    "adapter_archive_extraction_performed",
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
    "git_commit_performed",
    "git_push_performed",
)


def _l25_31_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_31.build_archive_manifest_package_run_authorization_gate(
            repo_root,
            allow_archive_manifest_package_run_authorization=True,
            authorization_token=l25_31.REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.31 package-run authorization readback failed: {type(exc).__name__}: {exc}"}


def _compact_text(text: str, limit: int = 5000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def _run_patchops_run_package(repo_root: Path, package_path: Path) -> dict[str, Any]:
    command = ["py", "-m", "patchops.cli", "run-package", str(package_path), "--wrapper-root", str(repo_root)]
    try:
        result = subprocess.run(
            command,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=RUN_PACKAGE_TIMEOUT_SECONDS,
            check=False,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        stdout_lower = stdout.lower()
        return {
            "command": " ".join(command),
            "exit_code": int(result.returncode),
            "timed_out": False,
            "stdout": _compact_text(stdout),
            "stderr": _compact_text(stderr),
            "stdout_has_marker": LAUNCHER_MARKER in stdout,
            "stdout_has_ok_true": '"ok": true' in stdout_lower or '"ok":true' in stdout_lower,
            "stdout_has_pass": "PASS" in stdout,
            "stdout_has_report_path": "Report Path" in stdout or "report_path" in stdout_lower,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(command),
            "exit_code": 124,
            "timed_out": True,
            "stdout": _compact_text(exc.stdout or ""),
            "stderr": _compact_text((exc.stderr or "") + "\nTIMEOUT"),
            "stdout_has_marker": False,
            "stdout_has_ok_true": False,
            "stdout_has_pass": False,
            "stdout_has_report_path": False,
        }


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_31_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_31_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_31_future_package_run_authorized", "ok": source.get("archive_manifest_package_run_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_31_package_run_execution_false", "ok": source.get("archive_manifest_package_run_allowed") is False and source.get("patchops_run_package_performed") is False},
        {"name": "default_package_run_proof_is_passive", "ok": True},
    ]
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_31_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_package_run_authorized": source.get("archive_manifest_package_run_authorization_granted_for_future_patch"),
            "package_run_allowed": source.get("archive_manifest_package_run_allowed"),
            "patchops_run_package_performed": source.get("patchops_run_package_performed"),
            "source_l25_30_apply_invoked": source.get("source_l25_30_summary", {}).get("patchops_cli_apply_invoked_for_archive_manifest"),
        },
        "archive_manifest_package_run_proof_requested": False,
        "archive_manifest_package_run_proof_token_present": False,
        "archive_manifest_package_run_proof_token_valid": False,
        "archive_manifest_package_run_allowed": False,
        "patchops_run_package_performed": False,
        "patchops_cli_run_package_invoked_for_archive_manifest": False,
        "patchops_cli_run_package_exit_code": None,
        "patchops_cli_run_package_timed_out": None,
        "controlled_package_launcher_execution_allowed": False,
        "controlled_package_launcher_executed": False,
        "controlled_package_launcher_marker_seen": False,
        "controlled_package_launcher_report_path_seen": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_run_performed_by_adapter": False,
        "package_run": False,
        "patchops_run_package_scope": "default_readback_only_no_package_run",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "zipfile_import_allowed_by_validator_only": True,
        "subprocess_patchops_run_package_allowed_by_l25_32": True,
        "no_browser_permission_added_by_l25_32": True,
        "no_pasteback_or_real_artifact_permission_added_by_l25_32": True,
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


def build_archive_manifest_package_run_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_package_run_proof: bool = False,
    authorization_token: str | None = None,
    candidate_package_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_package_path) if candidate_package_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_manifest_package_run_proof:
        return _default_payload(root, target_url)

    source = _l25_31_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    candidate_text = str(candidate).replace("\\", "/")

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_31_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_31_future_package_run_authorized", "ok": source.get("archive_manifest_package_run_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_31_package_run_execution_false", "ok": source.get("archive_manifest_package_run_allowed") is False and source.get("patchops_run_package_performed") is False},
        {"name": "source_l25_31_no_execution_extract_browser", "ok": source.get("package_execution_allowed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "package_run_proof_token_present", "ok": token_present},
        {"name": "package_run_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_path_is_isolated_run_package_fixture", "ok": "l25_32_package_run" in candidate_text},
        {"name": "candidate_exists_before_run_package", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_run_package", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
    ]

    package_run_allowed = bool(all(check.get("ok") for check in checks))
    run_result: dict[str, Any] = {}
    if package_run_allowed:
        run_result = _run_patchops_run_package(root, candidate)
        checks.extend([
            {"name": "patchops_run_package_invoked_only", "ok": run_result.get("command", "").startswith("py -m patchops.cli run-package ")},
            {"name": "patchops_run_package_exit_zero", "ok": run_result.get("exit_code") == 0},
            {"name": "patchops_run_package_not_timed_out", "ok": run_result.get("timed_out") is False},
            {"name": "patchops_run_package_pass_or_ok_marker", "ok": run_result.get("stdout_has_pass") is True or run_result.get("stdout_has_ok_true") is True},
            {"name": "controlled_launcher_marker_or_report_seen", "ok": run_result.get("stdout_has_marker") is True or run_result.get("stdout_has_report_path") is True},
        ])

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_31_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_package_run_authorized": source.get("archive_manifest_package_run_authorization_granted_for_future_patch"),
            "package_run_allowed": source.get("archive_manifest_package_run_allowed"),
            "patchops_run_package_performed": source.get("patchops_run_package_performed"),
            "source_l25_30_apply_invoked": source.get("source_l25_30_summary", {}).get("patchops_cli_apply_invoked_for_archive_manifest"),
            "source_l25_30_apply_exit_code": source.get("source_l25_30_summary", {}).get("patchops_cli_apply_exit_code"),
            "source_l25_30_apply_pass": source.get("source_l25_30_summary", {}).get("patchops_cli_apply_stdout_result_pass"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_package_run_proof_requested": True,
        "archive_manifest_package_run_proof_token_present": token_present,
        "archive_manifest_package_run_proof_token_valid": token_valid,
        "archive_manifest_package_run_allowed": package_run_allowed,
        "patchops_run_package_performed": package_run_allowed and run_result.get("exit_code") == 0,
        "patchops_cli_run_package_invoked_for_archive_manifest": package_run_allowed,
        "patchops_cli_run_package_exit_code": run_result.get("exit_code"),
        "patchops_cli_run_package_timed_out": run_result.get("timed_out"),
        "patchops_cli_run_package_stdout_has_pass": run_result.get("stdout_has_pass"),
        "patchops_cli_run_package_stdout_has_ok_true": run_result.get("stdout_has_ok_true"),
        "patchops_cli_run_package_stdout_has_marker": run_result.get("stdout_has_marker"),
        "patchops_cli_run_package_stdout_has_report_path": run_result.get("stdout_has_report_path"),
        "patchops_run_package_command_summary": {
            "command_kind": "py -m patchops.cli run-package",
            "timeout_seconds": RUN_PACKAGE_TIMEOUT_SECONDS,
            "exit_code": run_result.get("exit_code"),
            "timed_out": run_result.get("timed_out"),
        },
        "controlled_package_launcher_execution_allowed": package_run_allowed,
        "controlled_package_launcher_executed": package_run_allowed and run_result.get("exit_code") == 0,
        "controlled_package_launcher_marker_seen": run_result.get("stdout_has_marker") is True,
        "controlled_package_launcher_report_path_seen": run_result.get("stdout_has_report_path") is True,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": package_run_allowed,
        "package_run_performed_by_adapter": False,
        "package_run": package_run_allowed and run_result.get("exit_code") == 0,
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_package_path": str(candidate),
        "run_package_fixture_isolated_from_preflight_inspect_plan_apply_fixtures": True,
        "patchops_run_package_scope": PACKAGE_RUN_SCOPE,
        "zipfile_import_allowed_by_validator_only": True,
        "subprocess_patchops_run_package_allowed_by_l25_32": True,
        "no_browser_permission_added_by_l25_32": True,
        "no_pasteback_or_real_artifact_permission_added_by_l25_32": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.32 invokes exactly one bounded PatchOps run-package command against a controlled synthetic package ZIP.",
            "The controlled root launcher writes only a tiny proof report and exits zero.",
            "No browser, Selenium, CDP, DOM scraping, pasteback, send/submit, real downloaded artifact, localhost server, extension, git commit, or git push permission is added.",
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
        f"Run Package Invoked           : {payload.get('patchops_cli_run_package_invoked_for_archive_manifest')}",
        f"Run Package Exit              : {payload.get('patchops_cli_run_package_exit_code')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Launcher Executed             : {payload.get('controlled_package_launcher_executed')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Pasteback                     : {payload.get('pasteback_workflow_active')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-archive-manifest-package-run-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-package-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_package_run_first_controlled_proof(
        args.repo_root,
        allow_archive_manifest_package_run_proof=args.allow_archive_manifest_package_run_proof,
        authorization_token=args.authorization_token,
        candidate_package_path=args.candidate_package_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
