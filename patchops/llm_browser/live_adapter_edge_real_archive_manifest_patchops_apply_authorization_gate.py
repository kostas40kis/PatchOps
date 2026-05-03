"""L25.28 archive manifest PatchOps apply authorization gate.

This follows accepted L25.27. It reads back the controlled synthetic archive
manifest PatchOps plan-only broad checkpoint and grants only future
authorization for a PatchOps apply proof. It does not invoke PatchOps apply,
run-package, package execution, extraction, browser automation, pasteback, or
package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_plan_broad_checkpoint as l25_27

PATCH = "L25.28"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.28 Microsoft Edge controlled runtime archive manifest PatchOps apply authorization gate"
SOURCE_PATCH = "L25.27"
NEXT_PATCH = "L25.29 Microsoft Edge controlled runtime archive manifest PatchOps apply first proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_APPLY_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_APPLY_AUTHORIZED_READBACK_ONLY"
EXPECTED_PLAN_SCOPE = "controlled_runtime_manifest_patchops_plan_only_no_apply_run_package_no_execution"
EXPECTED_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
EXPECTED_SYNTHETIC_PLAN_PATCH_NAME = "synthetic_l25_26_patchops_plan_fixture"

FALSE_FIELDS = (
    "archive_manifest_patchops_apply_authorization_executes_apply",
    "archive_manifest_patchops_apply_allowed",
    "patchops_manifest_apply_performed",
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


def _l25_27_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_27.build_archive_manifest_patchops_plan_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.27 PatchOps plan broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_archive_manifest_patchops_apply_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_patchops_apply_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l25_27_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_APPLY_AUTHORIZATION_TOKEN
    requested = bool(allow_archive_manifest_patchops_apply_authorization or token_present)
    future_authorized = bool(allow_archive_manifest_patchops_apply_authorization and token_valid)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_27_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_27_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l25_27_plan_ladder_complete", "ok": source.get("l25_archive_manifest_patchops_plan_ladder_complete") is True},
        {"name": "source_l25_27_failed_checks_empty", "ok": source.get("failed_checks") == []},
        {"name": "source_l25_27_plan_only_scope", "ok": source.get("accepted_patchops_plan_scope") == EXPECTED_PLAN_SCOPE},
        {"name": "source_l25_27_manifest_member", "ok": source.get("manifest_member_name_read") == EXPECTED_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_27_plan_fixture_isolated", "ok": source.get("plan_fixture_isolated_from_preflight_and_inspect_fixtures") is True},
        {"name": "source_l25_27_patchops_plan_invoked", "ok": source.get("patchops_cli_plan_invoked_for_archive_manifest") is True},
        {"name": "source_l25_27_patchops_plan_exit_zero", "ok": source.get("patchops_cli_plan_exit_code") == 0},
        {"name": "source_l25_27_patchops_plan_ok_shape", "ok": source.get("patchops_cli_plan_timed_out") is False and source.get("patchops_cli_plan_json_object") is True},
        {"name": "source_l25_27_patchops_plan_patch_name", "ok": source.get("patchops_cli_plan_patch_name") == EXPECTED_SYNTHETIC_PLAN_PATCH_NAME},
        {"name": "source_l25_27_patchops_plan_empty_payload", "ok": source.get("accepted_patchops_cli_plan_target_files") == [] and source.get("accepted_patchops_cli_plan_validation_commands") == []},
        {"name": "source_l25_27_no_apply_run_package", "ok": source.get("patchops_cli_apply_invoked_for_archive_manifest") is False and source.get("patchops_cli_run_package_invoked_for_archive_manifest") is False},
        {"name": "source_l25_27_no_execution_extract_browser_package", "ok": source.get("package_manifest_used_for_execution") is False and source.get("package_execution_allowed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "patchops_apply_authorization_is_readback_only", "ok": True},
        {"name": "patchops_apply_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_27_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "broad_checkpoint": source.get("broad_checkpoint"),
            "plan_ladder_complete": source.get("l25_archive_manifest_patchops_plan_ladder_complete"),
            "failed_checks": source.get("failed_checks"),
            "patchops_plan_scope": source.get("accepted_patchops_plan_scope"),
            "manifest_member_name_read": source.get("manifest_member_name_read"),
            "plan_fixture_isolated_from_preflight_and_inspect_fixtures": source.get("plan_fixture_isolated_from_preflight_and_inspect_fixtures"),
            "patchops_cli_plan_invoked_for_archive_manifest": source.get("patchops_cli_plan_invoked_for_archive_manifest"),
            "patchops_cli_plan_exit_code": source.get("patchops_cli_plan_exit_code"),
            "patchops_cli_plan_timed_out": source.get("patchops_cli_plan_timed_out"),
            "patchops_cli_plan_json_object": source.get("patchops_cli_plan_json_object"),
            "patchops_cli_plan_patch_name": source.get("patchops_cli_plan_patch_name"),
            "patchops_cli_plan_mode": source.get("accepted_patchops_cli_plan_mode"),
            "patchops_cli_plan_target_files": source.get("accepted_patchops_cli_plan_target_files"),
            "patchops_cli_plan_validation_commands": source.get("accepted_patchops_cli_plan_validation_commands"),
            "patchops_manifest_plan_performed": source.get("patchops_manifest_plan_performed"),
            "patchops_cli_apply_invoked_for_archive_manifest": source.get("patchops_cli_apply_invoked_for_archive_manifest"),
            "patchops_cli_run_package_invoked_for_archive_manifest": source.get("patchops_cli_run_package_invoked_for_archive_manifest"),
            "package_manifest_used_for_execution": source.get("package_manifest_used_for_execution"),
            "package_execution_allowed": source.get("package_execution_allowed"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_patchops_apply_authorization_gate": True,
        "archive_manifest_patchops_apply_authorization_readback_only": True,
        "archive_manifest_patchops_apply_authorization_requested": requested,
        "archive_manifest_patchops_apply_authorization_token_present": token_present,
        "archive_manifest_patchops_apply_authorization_token_valid": token_valid,
        "archive_manifest_patchops_apply_authorization_granted_for_future_patch": future_authorized,
        "future_archive_manifest_patchops_apply_requires_explicit_flag_and_token": True,
        "future_archive_manifest_patchops_apply_must_be_separately_gated_in_l25_29": True,
        "no_patchops_apply_execution_added_by_l25_28": True,
        "no_patchops_run_package_added_by_l25_28": True,
        "no_package_execution_added_by_l25_28": True,
        "no_archive_extraction_added_by_l25_28": True,
        "no_browser_permission_added_by_l25_28": True,
        "no_pasteback_or_package_run_permission_added_by_l25_28": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "readback-only PatchOps-apply authorization; no PatchOps apply/run-package on archive manifest, no execution, no extraction, no browser, no pasteback, no package-run",
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
        f"Future Apply Authorized       : {payload.get('archive_manifest_patchops_apply_authorization_granted_for_future_patch')}",
        f"Apply Allowed                 : {payload.get('archive_manifest_patchops_apply_allowed')}",
        f"Apply Performed               : {payload.get('patchops_manifest_apply_performed')}",
        f"Source Plan Invoked           : {payload.get('source_l25_27_summary', {}).get('patchops_cli_plan_invoked_for_archive_manifest')}",
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
    parser.add_argument("--allow-archive-manifest-patchops-apply-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_patchops_apply_authorization_gate(
        args.repo_root,
        allow_archive_manifest_patchops_apply_authorization=args.allow_archive_manifest_patchops_apply_authorization,
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
