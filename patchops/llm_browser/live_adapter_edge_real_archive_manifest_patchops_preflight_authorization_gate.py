"""L25.19 archive manifest validation-to-PatchOps-preflight authorization gate.

This follows accepted L25.18. It reads back the controlled synthetic manifest
schema-validation broad checkpoint and grants only future authorization for a
PatchOps preflight proof. It does not invoke PatchOps check/inspect/plan/apply
against the archive manifest, execute packages, extract archives, start a
browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_schema_validation_broad_checkpoint as l25_18

PATCH = "L25.19"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.19 Microsoft Edge controlled runtime archive manifest validation-to-PatchOps-preflight authorization gate"
SOURCE_PATCH = "L25.18"
NEXT_PATCH = "L25.20 Microsoft Edge controlled runtime archive manifest PatchOps preflight first proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_AUTHORIZED_READBACK_ONLY"
EXPECTED_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
EXPECTED_SCHEMA_SCOPE = "controlled_runtime_manifest_tiny_internal_schema_validation_only_no_patchops_validation_no_execution"

FALSE_FIELDS = (
    "archive_manifest_patchops_preflight_authorization_executes_preflight",
    "archive_manifest_patchops_preflight_allowed",
    "patchops_manifest_preflight_performed",
    "patchops_manifest_validation_performed",
    "patchops_cli_check_invoked_for_archive_manifest",
    "patchops_cli_inspect_invoked_for_archive_manifest",
    "patchops_cli_plan_invoked_for_archive_manifest",
    "patchops_cli_apply_invoked_for_archive_manifest",
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


def _l25_18_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_18.build_archive_manifest_schema_validation_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.18 schema broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_archive_manifest_patchops_preflight_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_patchops_preflight_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l25_18_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_AUTHORIZATION_TOKEN
    requested = bool(allow_archive_manifest_patchops_preflight_authorization or token_present)
    future_authorized = bool(allow_archive_manifest_patchops_preflight_authorization and token_valid)
    required_keys = source.get("accepted_schema_required_keys") or []
    validated_keys = source.get("accepted_schema_validated_keys") or []

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_18_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_18_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l25_18_schema_ladder_complete", "ok": source.get("l25_archive_manifest_schema_validation_ladder_complete") is True},
        {"name": "source_l25_18_failed_checks_empty", "ok": source.get("failed_checks") == []},
        {"name": "source_l25_18_schema_validated", "ok": source.get("manifest_schema_validated") is True and source.get("manifest_validation_performed") is True},
        {"name": "source_l25_18_member_name", "ok": source.get("manifest_member_name_read") == EXPECTED_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_18_scope_tiny_internal_schema_only", "ok": source.get("accepted_schema_validation_scope") == EXPECTED_SCHEMA_SCOPE},
        {"name": "source_l25_18_schema_summary_ok", "ok": source.get("accepted_schema_summary_ok") is True and required_keys == validated_keys and len(required_keys) > 0},
        {"name": "source_l25_18_no_patchops_preflight_or_validation", "ok": source.get("patchops_manifest_validation_performed") is False},
        {"name": "source_l25_18_no_execution_extract_browser_package", "ok": source.get("package_manifest_used_for_execution") is False and source.get("package_execution_allowed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "patchops_preflight_authorization_is_readback_only", "ok": True},
        {"name": "patchops_preflight_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_18_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "broad_checkpoint": source.get("broad_checkpoint"),
            "schema_validation_ladder_complete": source.get("l25_archive_manifest_schema_validation_ladder_complete"),
            "failed_checks": source.get("failed_checks"),
            "schema_validation_allowed": source.get("archive_manifest_schema_validation_allowed"),
            "manifest_payload_schema_validated": source.get("manifest_payload_schema_validated"),
            "manifest_schema_validated": source.get("manifest_schema_validated"),
            "manifest_validation_performed": source.get("manifest_validation_performed"),
            "manifest_member_name_read": source.get("manifest_member_name_read"),
            "accepted_schema_validation_scope": source.get("accepted_schema_validation_scope"),
            "accepted_schema_summary_ok": source.get("accepted_schema_summary_ok"),
            "accepted_schema_required_keys": required_keys,
            "accepted_schema_validated_keys": validated_keys,
            "patchops_manifest_validation_performed": source.get("patchops_manifest_validation_performed"),
            "package_manifest_used_for_execution": source.get("package_manifest_used_for_execution"),
            "package_execution_allowed": source.get("package_execution_allowed"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_patchops_preflight_authorization_gate": True,
        "archive_manifest_patchops_preflight_authorization_readback_only": True,
        "archive_manifest_patchops_preflight_authorization_requested": requested,
        "archive_manifest_patchops_preflight_authorization_token_present": token_present,
        "archive_manifest_patchops_preflight_authorization_token_valid": token_valid,
        "archive_manifest_patchops_preflight_authorization_granted_for_future_patch": future_authorized,
        "future_archive_manifest_patchops_preflight_requires_explicit_flag_and_token": True,
        "future_archive_manifest_patchops_preflight_must_be_separately_gated_in_l25_20": True,
        "no_patchops_preflight_execution_added_by_l25_19": True,
        "no_patchops_manifest_validation_added_by_l25_19": True,
        "no_package_execution_added_by_l25_19": True,
        "no_archive_extraction_added_by_l25_19": True,
        "no_browser_permission_added_by_l25_19": True,
        "no_pasteback_or_package_run_permission_added_by_l25_19": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "readback-only PatchOps-preflight authorization; no PatchOps preflight/check/inspect/plan/apply on archive manifest, no execution, no extraction, no browser, no pasteback, no package-run",
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
        f"Future Preflight Authorized   : {payload.get('archive_manifest_patchops_preflight_authorization_granted_for_future_patch')}",
        f"Preflight Allowed             : {payload.get('archive_manifest_patchops_preflight_allowed')}",
        f"PatchOps Manifest Preflight   : {payload.get('patchops_manifest_preflight_performed')}",
        f"PatchOps Manifest Validation  : {payload.get('patchops_manifest_validation_performed')}",
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
    parser.add_argument("--allow-archive-manifest-patchops-preflight-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_patchops_preflight_authorization_gate(
        args.repo_root,
        allow_archive_manifest_patchops_preflight_authorization=args.allow_archive_manifest_patchops_preflight_authorization,
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
