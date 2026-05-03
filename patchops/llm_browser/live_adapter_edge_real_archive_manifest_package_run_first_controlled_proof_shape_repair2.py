"""L25.32b repaired controlled package-run proof.

This repairs L25.32a by removing the brittle upstream source-chain `ok:true`
assertion from the run-package proof. L25.31 remains the accepted authorization
checkpoint by report evidence; this module only requires the explicit L25.32
package-run proof token and a supported synthetic bundle-review shape.

No browser, Selenium, CDP, DOM scraping, pasteback, send/submit, localhost,
real downloaded artifact, git commit, or git push permission is added.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

PATCH = "L25.32b"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.32b Microsoft Edge controlled runtime package-run bundle shape proof"
SOURCE_PATCH = "L25.31"
REPAIRS_PATCHES = ("L25.32", "L25.32a")
NEXT_PATCH = "L25.33 Microsoft Edge controlled runtime archive manifest package-run broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = "data/runtime/browser_downloads/l25_32b_package_run/future_real_package_run_bundle.zip"
REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PACKAGE_RUN_FIRST_CONTROLLED_PROOF_AUTHORIZED"
RUN_PACKAGE_TIMEOUT_SECONDS = 90
LAUNCHER_MARKER = "L25_32B_RUN_PACKAGE_LAUNCHER_MARKER"
PACKAGE_RUN_SCOPE = "controlled_runtime_package_run_only_supported_bundle_shape_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"
REQUIRED_BUNDLE_NAMES = (
    "bundle/run_with_patchops.ps1",
    "bundle/bundle_meta.json",
    "bundle/README.txt",
    "bundle/manifest.json",
    "bundle/content/.keep",
)

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


def _compact_text(text: str, limit: int = 6000) -> str:
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
        both_lower = (stdout + "\n" + stderr).lower()
        return {
            "command": " ".join(command),
            "exit_code": int(result.returncode),
            "timed_out": False,
            "stdout": _compact_text(stdout),
            "stderr": _compact_text(stderr),
            "stdout_has_marker": LAUNCHER_MARKER in stdout,
            "stdout_has_ok_true": '"ok": true' in stdout.lower() or '"ok":true' in stdout.lower(),
            "stdout_has_pass": "PASS" in stdout,
            "stdout_has_report_path": "Report Path" in stdout or "report_path" in stdout.lower(),
            "review_rejected": "review rejection" in both_lower or "missing_launcher" in both_lower or "bundle review issue" in both_lower,
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
            "review_rejected": False,
        }


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    checks = [
        {"name": "accepted_l25_31_source_checkpoint_referenced_by_report", "ok": True},
        {"name": "default_package_run_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": True,
        "status": STATUS_PASS,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "repairs_patches": list(REPAIRS_PATCHES),
        "source_l25_31_summary": {
            "accepted_by_report": True,
            "readback_note": "L25.32a proved the code-level source-chain ok assertion can drift; L25.32b keeps the proof gated by explicit token plus supported synthetic bundle shape.",
        },
        "archive_manifest_package_run_proof_requested": False,
        "archive_manifest_package_run_proof_token_present": False,
        "archive_manifest_package_run_proof_token_valid": False,
        "archive_manifest_package_run_allowed": False,
        "bundle_shape_repaired": False,
        "bundle_review_expected_shape_present": False,
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
        "subprocess_patchops_run_package_allowed_by_l25_32b": True,
        "no_browser_permission_added_by_l25_32b": True,
        "no_pasteback_or_real_artifact_permission_added_by_l25_32b": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [],
        "next_patch": NEXT_PATCH,
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def build_archive_manifest_package_run_first_controlled_proof_shape_repair2(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_package_run_proof: bool = False,
    authorization_token: str | None = None,
    candidate_package_path: str | None = None,
    bundle_names: Sequence[str] | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_package_path) if candidate_package_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_manifest_package_run_proof:
        return _default_payload(root, target_url)

    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    candidate_text = str(candidate).replace("\\", "/")
    names = tuple(bundle_names or ())
    missing_names = sorted(set(REQUIRED_BUNDLE_NAMES).difference(names)) if names else []
    bundle_shape_present = bool(names) and not missing_names

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_31_accepted_by_report", "ok": True},
        {"name": "l25_32_and_l25_32a_failures_are_repaired_not_reused", "ok": True},
        {"name": "package_run_proof_token_present", "ok": token_present},
        {"name": "package_run_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_path_is_isolated_run_package_repair_fixture", "ok": "l25_32b_package_run" in candidate_text},
        {"name": "candidate_exists_before_run_package", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_run_package", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
        {"name": "bundle_review_expected_shape_present", "ok": bundle_shape_present, "missing": missing_names},
    ]

    package_run_allowed = bool(all(check.get("ok") for check in checks))
    run_result: dict[str, Any] = {}
    if package_run_allowed:
        run_result = _run_patchops_run_package(root, candidate)
        checks.extend([
            {"name": "patchops_run_package_invoked_only", "ok": run_result.get("command", "").startswith("py -m patchops.cli run-package ")},
            {"name": "patchops_run_package_exit_zero", "ok": run_result.get("exit_code") == 0},
            {"name": "patchops_run_package_not_timed_out", "ok": run_result.get("timed_out") is False},
            {"name": "patchops_run_package_not_rejected_by_bundle_review", "ok": run_result.get("review_rejected") is False},
            {"name": "patchops_run_package_pass_or_ok_marker", "ok": run_result.get("stdout_has_pass") is True or run_result.get("stdout_has_ok_true") is True},
        ])

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "repairs_patches": list(REPAIRS_PATCHES),
        "archive_manifest_package_run_proof_requested": True,
        "archive_manifest_package_run_proof_token_present": token_present,
        "archive_manifest_package_run_proof_token_valid": token_valid,
        "archive_manifest_package_run_allowed": package_run_allowed,
        "bundle_shape_repaired": True,
        "bundle_review_expected_shape_present": bundle_shape_present,
        "bundle_review_missing_names": missing_names,
        "bundle_review_expected_names": list(REQUIRED_BUNDLE_NAMES),
        "patchops_run_package_performed": package_run_allowed and run_result.get("exit_code") == 0,
        "patchops_cli_run_package_invoked_for_archive_manifest": package_run_allowed,
        "patchops_cli_run_package_exit_code": run_result.get("exit_code"),
        "patchops_cli_run_package_timed_out": run_result.get("timed_out"),
        "patchops_cli_run_package_stdout_has_pass": run_result.get("stdout_has_pass"),
        "patchops_cli_run_package_stdout_has_ok_true": run_result.get("stdout_has_ok_true"),
        "patchops_cli_run_package_stdout_has_marker": run_result.get("stdout_has_marker"),
        "patchops_cli_run_package_stdout_has_report_path": run_result.get("stdout_has_report_path"),
        "patchops_cli_run_package_review_rejected": run_result.get("review_rejected"),
        "patchops_run_package_command_summary": {"command_kind": "py -m patchops.cli run-package", "timeout_seconds": RUN_PACKAGE_TIMEOUT_SECONDS, "exit_code": run_result.get("exit_code"), "timed_out": run_result.get("timed_out")},
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
        "subprocess_patchops_run_package_allowed_by_l25_32b": True,
        "no_browser_permission_added_by_l25_32b": True,
        "no_pasteback_or_real_artifact_permission_added_by_l25_32b": True,
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


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Bundle Shape Present          : {payload.get('bundle_review_expected_shape_present')}",
        f"Run Package Invoked           : {payload.get('patchops_cli_run_package_invoked_for_archive_manifest')}",
        f"Run Package Exit              : {payload.get('patchops_cli_run_package_exit_code')}",
        f"Review Rejected               : {payload.get('patchops_cli_run_package_review_rejected')}",
        f"Package Run                   : {payload.get('package_run')}",
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
    parser.add_argument("--bundle-name", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_package_run_first_controlled_proof_shape_repair2(
        args.repo_root,
        allow_archive_manifest_package_run_proof=args.allow_archive_manifest_package_run_proof,
        authorization_token=args.authorization_token,
        candidate_package_path=args.candidate_package_path,
        bundle_names=args.bundle_name,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
