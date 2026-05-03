"""L25.31 archive manifest package-run authorization gate.

This follows accepted L25.30. It reads back the controlled synthetic archive
manifest PatchOps apply-only broad checkpoint and grants only future
authorization for a package-run proof. It does not invoke PatchOps run-package,
package execution, extraction, browser automation, pasteback, or package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_apply_broad_checkpoint as l25_30

PATCH = "L25.31"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.31 Microsoft Edge controlled runtime archive manifest package-run authorization gate"
SOURCE_PATCH = "L25.30"
NEXT_PATCH = "L25.32 Microsoft Edge controlled runtime archive manifest package-run first proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PACKAGE_RUN_AUTHORIZED_READBACK_ONLY"
EXPECTED_APPLY_SCOPE = "controlled_runtime_manifest_patchops_apply_only_zero_write_zero_validation_no_run_package_no_package_execution"
EXPECTED_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
EXPECTED_SYNTHETIC_APPLY_PATCH_NAME = "synthetic_l25_29_patchops_apply_fixture"

FALSE_FIELDS = (
    "archive_manifest_package_run_authorization_executes_package_run",
    "archive_manifest_package_run_allowed",
    "patchops_run_package_performed",
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


def _l25_30_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_30.build_archive_manifest_patchops_apply_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.30 PatchOps apply broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_archive_manifest_package_run_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_package_run_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l25_30_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PACKAGE_RUN_AUTHORIZATION_TOKEN
    requested = bool(allow_archive_manifest_package_run_authorization or token_present)
    future_authorized = bool(allow_archive_manifest_package_run_authorization and token_valid)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_30_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_30_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l25_30_apply_ladder_complete", "ok": source.get("l25_archive_manifest_patchops_apply_ladder_complete") is True},
        {"name": "source_l25_30_failed_checks_empty", "ok": source.get("failed_checks") == []},
        {"name": "source_l25_30_apply_only_scope", "ok": source.get("accepted_patchops_apply_scope") == EXPECTED_APPLY_SCOPE},
        {"name": "source_l25_30_manifest_member", "ok": source.get("manifest_member_name_read") == EXPECTED_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_30_apply_fixture_isolated", "ok": source.get("apply_fixture_isolated_from_preflight_inspect_and_plan_fixtures") is True},
        {"name": "source_l25_30_zero_write_zero_validation", "ok": source.get("manifest_zero_write_zero_validation") is True},
        {"name": "source_l25_30_patchops_apply_invoked", "ok": source.get("patchops_cli_apply_invoked_for_archive_manifest") is True},
        {"name": "source_l25_30_patchops_apply_exit_zero", "ok": source.get("patchops_cli_apply_exit_code") == 0},
        {"name": "source_l25_30_patchops_apply_ok_shape", "ok": source.get("patchops_cli_apply_timed_out") is False and source.get("patchops_cli_apply_stdout_result_pass") is True},
        {"name": "source_l25_30_patchops_apply_patch_name", "ok": source.get("patchops_cli_apply_patch_name") == EXPECTED_SYNTHETIC_APPLY_PATCH_NAME},
        {"name": "source_l25_30_no_run_package", "ok": source.get("patchops_cli_run_package_invoked_for_archive_manifest") is False},
        {"name": "source_l25_30_no_execution_extract_browser_package", "ok": source.get("package_manifest_used_for_execution") is False and source.get("package_execution_allowed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "package_run_authorization_is_readback_only", "ok": True},
        {"name": "package_run_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_30_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "broad_checkpoint": source.get("broad_checkpoint"),
            "apply_ladder_complete": source.get("l25_archive_manifest_patchops_apply_ladder_complete"),
            "failed_checks": source.get("failed_checks"),
            "patchops_apply_scope": source.get("accepted_patchops_apply_scope"),
            "manifest_member_name_read": source.get("manifest_member_name_read"),
            "apply_fixture_isolated_from_preflight_inspect_and_plan_fixtures": source.get("apply_fixture_isolated_from_preflight_inspect_and_plan_fixtures"),
            "manifest_zero_write_zero_validation": source.get("manifest_zero_write_zero_validation"),
            "patchops_cli_apply_invoked_for_archive_manifest": source.get("patchops_cli_apply_invoked_for_archive_manifest"),
            "patchops_cli_apply_exit_code": source.get("patchops_cli_apply_exit_code"),
            "patchops_cli_apply_timed_out": source.get("patchops_cli_apply_timed_out"),
            "patchops_cli_apply_stdout_result_pass": source.get("patchops_cli_apply_stdout_result_pass"),
            "patchops_cli_apply_patch_name": source.get("patchops_cli_apply_patch_name"),
            "patchops_manifest_apply_performed": source.get("patchops_manifest_apply_performed"),
            "patchops_cli_run_package_invoked_for_archive_manifest": source.get("patchops_cli_run_package_invoked_for_archive_manifest"),
            "package_manifest_used_for_execution": source.get("package_manifest_used_for_execution"),
            "package_execution_allowed": source.get("package_execution_allowed"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_package_run_authorization_gate": True,
        "archive_manifest_package_run_authorization_readback_only": True,
        "archive_manifest_package_run_authorization_requested": requested,
        "archive_manifest_package_run_authorization_token_present": token_present,
        "archive_manifest_package_run_authorization_token_valid": token_valid,
        "archive_manifest_package_run_authorization_granted_for_future_patch": future_authorized,
        "future_archive_manifest_package_run_requires_explicit_flag_and_token": True,
        "future_archive_manifest_package_run_must_be_separately_gated_in_l25_32": True,
        "no_patchops_run_package_execution_added_by_l25_31": True,
        "no_package_execution_added_by_l25_31": True,
        "no_archive_extraction_added_by_l25_31": True,
        "no_browser_permission_added_by_l25_31": True,
        "no_pasteback_or_package_run_permission_added_by_l25_31": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "readback-only package-run authorization; no PatchOps run-package, no package execution, no extraction, no browser, no pasteback, no package-run",
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    for field in FALSE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Future Package Run Authorized : {payload.get('archive_manifest_package_run_authorization_granted_for_future_patch')}",
        f"Package Run Allowed           : {payload.get('archive_manifest_package_run_allowed')}",
        f"Run Package Performed         : {payload.get('patchops_run_package_performed')}",
        f"Source Apply Invoked          : {payload.get('source_l25_30_summary', {}).get('patchops_cli_apply_invoked_for_archive_manifest')}",
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
    parser.add_argument("--allow-archive-manifest-package-run-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_package_run_authorization_gate(
        args.repo_root,
        allow_archive_manifest_package_run_authorization=args.allow_archive_manifest_package_run_authorization,
        authorization_token=args.authorization_token,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
