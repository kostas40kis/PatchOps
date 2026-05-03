"""L25.45 first controlled run-package proof.

This follows accepted L25.44. It validates the accepted dry-run final marker and
validates evidence from one controlled PatchOps run-package invocation against a
synthetic no-write artifact under the L25.45 runtime browser-downloads folder.

L25.45A repaired the pass detection: the controlled run is accepted when
PatchOps run-package exits 0 and the controlled launcher marker is observed,
even if a particular textual `Result : PASS` spelling is not emitted in stdout.

The module itself is evidence-validation only. The validator creates the
synthetic artifact and invokes PatchOps run-package exactly once. No browser,
real browser download, pasteback, localhost server, extension, commit, or push is
allowed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.45"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.45 Microsoft Edge controlled runtime real-download artifact package-execution first controlled run-package proof"
SOURCE_PATCH = "L25.44"
NEXT_PATCH = "L25.46 Microsoft Edge controlled runtime real-download artifact package-execution run-package broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH = "data/runtime/browser_downloads/l25_45_controlled_run_package/future_real_downloaded_package.zip"
CONTROLLED_MARKER = "PATCHOPS_L25_45_CONTROLLED_RUN_PACKAGE_MARKER"

FALSE_FIELDS = (
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
    "artifact_member_written_to_project",
    "target_project_file_write_performed_by_controlled_package",
    "git_commit_performed",
    "git_push_performed",
)


def _first(payload: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload.get(name)
    return default


def _normalize_l25_44_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "package_execution_dry_run_final_acceptance_marker": source.get("package_execution_dry_run_final_acceptance_marker"),
        "package_execution_dry_run_ladder_final_acceptance": source.get("package_execution_dry_run_ladder_final_acceptance"),
        "package_execution_dry_run_final_acceptance_from_source_payload_only": source.get("package_execution_dry_run_final_acceptance_from_source_payload_only"),
        "accepted_l25_41_package_execution_authorization_gate": source.get("accepted_l25_41_package_execution_authorization_gate"),
        "accepted_l25_42_package_execution_dry_run_proof": source.get("accepted_l25_42_package_execution_dry_run_proof"),
        "accepted_l25_43_package_execution_dry_run_broad_checkpoint": source.get("accepted_l25_43_package_execution_dry_run_broad_checkpoint"),
        "accepted_package_execution_dry_run_only": source.get("accepted_package_execution_dry_run_only"),
        "accepted_package_execution_dry_run_allowed": source.get("accepted_package_execution_dry_run_allowed"),
        "accepted_candidate_artifact_suffix_zip": source.get("accepted_candidate_artifact_suffix_zip"),
        "accepted_candidate_artifact_under_l25_42_runtime": source.get("accepted_candidate_artifact_under_l25_42_runtime"),
        "accepted_would_run_command_rendered": source.get("accepted_would_run_command_rendered"),
        "accepted_would_run_command_program": source.get("accepted_would_run_command_program"),
        "accepted_would_invoke_patchops_run_package_in_future_patch": source.get("accepted_would_invoke_patchops_run_package_in_future_patch"),
        "accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime": source.get("accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime"),
        "accepted_broad_checkpoint_rejects_source_that_invoked_run_package": source.get("accepted_broad_checkpoint_rejects_source_that_invoked_run_package"),
        "final_marker_rejects_source_that_invoked_run_package": source.get("final_marker_rejects_source_that_invoked_run_package"),
        "artifact_path_opened_by_l25_44": source.get("artifact_path_opened_by_l25_44", False),
        "artifact_bytes_read_by_l25_44": source.get("artifact_bytes_read_by_l25_44", False),
        "zip_member_opened_by_l25_44": source.get("zip_member_opened_by_l25_44", False),
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


def _normalize_run_payload(run_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    run = dict(run_payload or {})
    stdout = str(run.get("stdout") or "")
    stderr = str(run.get("stderr") or "")
    combined = stdout + "\n" + stderr
    command_args = list(run.get("command_args") or [])
    exit_zero = run.get("exit_code") == 0
    marker_observed = CONTROLLED_MARKER in combined
    textual_pass_observed = (
        "Result             : PASS" in stdout
        or "Result   : PASS" in stdout
        or "Result : PASS" in stdout
        or "\"ok\": true" in stdout
        or "'ok': True" in stdout
    )
    result_pass_observed = textual_pass_observed or (exit_zero and marker_observed)
    return {
        "invoked": run.get("invoked"),
        "exit_code": run.get("exit_code"),
        "timed_out": run.get("timed_out", False),
        "command_program": run.get("command_program"),
        "command_args": command_args,
        "command_text": run.get("command_text"),
        "artifact_path": run.get("artifact_path"),
        "artifact_under_l25_45_runtime": run.get("artifact_under_l25_45_runtime"),
        "artifact_suffix_zip": run.get("artifact_suffix_zip"),
        "stdout": stdout,
        "stderr": stderr,
        "marker_observed": marker_observed,
        "textual_pass_observed": textual_pass_observed,
        "exit_zero_plus_controlled_marker_pass_observed": exit_zero and marker_observed,
        "result_pass_observed": result_pass_observed,
        "target_write_marker_false": "CONTROLLED_PACKAGE_WRITES_TO_TARGET:false" in combined,
        "browser_marker_false": "CONTROLLED_PACKAGE_BROWSER_STARTED:false" in combined,
        "pasteback_marker_false": "CONTROLLED_PACKAGE_PASTEBACK:false" in combined,
    }


def build_real_download_artifact_controlled_run_package_proof(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    run_payload: Mapping[str, Any] | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = _normalize_l25_44_source(source_payload)
    run = _normalize_run_payload(run_payload)
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.44"
        and source.get("package_execution_dry_run_final_acceptance_marker") is True
        and source.get("package_execution_dry_run_ladder_final_acceptance") is True
        and source.get("package_execution_dry_run_final_acceptance_from_source_payload_only") is True
        and source.get("accepted_l25_41_package_execution_authorization_gate") is True
        and source.get("accepted_l25_42_package_execution_dry_run_proof") is True
        and source.get("accepted_l25_43_package_execution_dry_run_broad_checkpoint") is True
        and source.get("accepted_would_run_command_rendered") is True
        and source.get("accepted_would_run_command_program") == "py"
        and source.get("accepted_would_invoke_patchops_run_package_in_future_patch") is True
        and source.get("accepted_broad_checkpoint_rejects_source_that_invoked_run_package") is True
        and source.get("final_marker_rejects_source_that_invoked_run_package") is True
        and source.get("package_execution_allowed") is False
        and source.get("package_execution_performed_by_adapter") is False
        and source.get("package_run") is False
        and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False
        and source.get("browser_started") is False
        and source.get("pasteback") is False
    )
    run_ok = bool(
        run.get("invoked") is True
        and run.get("exit_code") == 0
        and run.get("timed_out") is False
        and run.get("command_program") == "py"
        and run.get("command_args", [])[0:3] == ["-m", "patchops.cli", "run-package"]
        and "--wrapper-root" in run.get("command_args", [])
        and run.get("artifact_under_l25_45_runtime") is True
        and run.get("artifact_suffix_zip") is True
        and run.get("marker_observed") is True
        and run.get("result_pass_observed") is True
        and run.get("target_write_marker_false") is True
        and run.get("browser_marker_false") is True
        and run.get("pasteback_marker_false") is True
    )
    checks: list[dict[str, Any]] = [
        {"name": "source_l25_44_payload_ok", "ok": source_ok},
        {"name": "controlled_run_package_invoked", "ok": run.get("invoked") is True},
        {"name": "controlled_run_package_exit_zero", "ok": run.get("exit_code") == 0},
        {"name": "controlled_run_package_not_timed_out", "ok": run.get("timed_out") is False},
        {"name": "controlled_run_package_command_shape", "ok": run.get("command_program") == "py" and run.get("command_args", [])[0:3] == ["-m", "patchops.cli", "run-package"] and "--wrapper-root" in run.get("command_args", [])},
        {"name": "controlled_artifact_path_guard", "ok": run.get("artifact_under_l25_45_runtime") is True and run.get("artifact_suffix_zip") is True},
        {"name": "controlled_launcher_marker_observed", "ok": run.get("marker_observed") is True},
        {"name": "controlled_run_package_result_pass", "ok": run.get("result_pass_observed") is True},
        {"name": "controlled_run_package_exit_zero_plus_marker_pass", "ok": run.get("exit_zero_plus_controlled_marker_pass_observed") is True},
        {"name": "controlled_package_no_target_writes_marker", "ok": run.get("target_write_marker_false") is True},
        {"name": "controlled_package_no_browser_marker", "ok": run.get("browser_marker_false") is True},
        {"name": "controlled_package_no_pasteback_marker", "ok": run.get("pasteback_marker_false") is True},
    ]
    ok = bool(source_ok and run_ok and all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "controlled_run_package_first_proof": True,
        "controlled_run_package_pass_detection_repaired_by_l25_45a": True,
        "controlled_run_package_proof_from_l25_44_final_acceptance": source_ok,
        "source_l25_44_summary": source,
        "controlled_artifact_path": run.get("artifact_path"),
        "controlled_artifact_under_l25_45_runtime": run.get("artifact_under_l25_45_runtime") is True,
        "controlled_artifact_suffix_zip": run.get("artifact_suffix_zip") is True,
        "controlled_run_package_invoked": run.get("invoked") is True,
        "controlled_run_package_exit_code": run.get("exit_code"),
        "controlled_run_package_timed_out": run.get("timed_out") is True,
        "controlled_run_package_result_pass": run.get("result_pass_observed") is True,
        "controlled_run_package_textual_pass_observed": run.get("textual_pass_observed") is True,
        "controlled_run_package_exit_zero_plus_marker_pass_observed": run.get("exit_zero_plus_controlled_marker_pass_observed") is True,
        "controlled_run_package_marker_observed": run.get("marker_observed") is True,
        "controlled_run_package_command_program": run.get("command_program"),
        "controlled_run_package_command_args": run.get("command_args"),
        "controlled_run_package_command_text": run.get("command_text"),
        "controlled_package_target_write_marker_false": run.get("target_write_marker_false") is True,
        "controlled_package_browser_marker_false": run.get("browser_marker_false") is True,
        "controlled_package_pasteback_marker_false": run.get("pasteback_marker_false") is True,
        "package_execution_allowed": run_ok,
        "package_execution_performed_by_adapter": False,
        "controlled_package_run_performed_by_validator": run_ok,
        "package_run": run_ok,
        "patchops_cli_run_package_invoked_for_controlled_artifact": run_ok,
        "patchops_cli_run_package_invoked_for_real_artifact": run_ok,
        "real_archive_candidate_extracted": run_ok,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "target_project_file_write_performed_by_controlled_package": False,
        "real_browser_download_active": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "selenium_imported": False,
        "cdp_used": False,
        "dom_scraping_used": False,
        "page_inspection_performed": False,
        "conversation_text_read": False,
        "prompt_text_extracted": False,
        "chatgpt_url_opened": False,
        "pasteback_workflow_active": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "localhost_server_started": False,
        "browser_extension_used": False,
        "git_commit_performed": False,
        "git_push_performed": False,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Controlled Run-Package        : {payload.get('controlled_run_package_invoked')}",
        f"Exit Code                     : {payload.get('controlled_run_package_exit_code')}",
        f"Result PASS                   : {payload.get('controlled_run_package_result_pass')}",
        f"Exit0+Marker PASS             : {payload.get('controlled_run_package_exit_zero_plus_marker_pass_observed')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Pasteback                     : {payload.get('pasteback_workflow_active')}",
        f"Target Writes                 : {payload.get('target_project_file_write_performed_by_controlled_package')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--run-payload-json", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    run_payload = json.loads(args.run_payload_json) if args.run_payload_json else None
    payload = build_real_download_artifact_controlled_run_package_proof(
        args.repo_root,
        source_payload=source_payload,
        run_payload=run_payload,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
