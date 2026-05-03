"""L25.35 real downloaded artifact authorization gate.

This follows accepted L25.34. It is a readback-only gate for the next phase:
handling a real downloaded PatchOps package artifact. It grants only future
authorization when the explicit token is supplied and the accepted L25.34
controlled synthetic package-run ladder is proven by source payload.

L25.35 does not start a browser, download anything, read a real downloaded
artifact, extract an archive, execute a package, paste/send, start localhost,
use Selenium/CDP/DOM scraping, commit, or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.35"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.35 Microsoft Edge controlled runtime real-download artifact authorization gate"
SOURCE_PATCH = "L25.34"
NEXT_PATCH = "L25.36 Microsoft Edge controlled runtime real-download artifact first readback proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_REAL_DOWNLOAD_ARTIFACT_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_AUTHORIZED_READBACK_ONLY"
EXPECTED_RUN_PACKAGE_SCOPE = "controlled_runtime_package_run_only_supported_bundle_shape_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"
EXPECTED_REPAIRS = ("L25.32", "L25.32a")

FALSE_FIELDS = (
    "real_downloaded_manifest_read",
    "real_downloaded_artifact_read",
    "real_downloaded_artifact_path_opened",
    "real_downloaded_artifact_bytes_read",
    "real_downloaded_artifact_hash_computed",
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
    "package_run_performed_by_adapter",
    "package_run",
    "patchops_cli_run_package_invoked_for_real_artifact",
    "git_commit_performed",
    "git_push_performed",
)


def _first(payload: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload.get(name)
    return default


def _nested(source: Mapping[str, Any]) -> Mapping[str, Any]:
    value = source.get("source_l25_33a_summary")
    return value if isinstance(value, Mapping) else {}


def _normalize_l25_34_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    inner = dict(_nested(source))
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "final_acceptance_marker": source.get("final_acceptance_marker"),
        "controlled_package_run_ladder_final_acceptance": source.get("controlled_package_run_ladder_final_acceptance"),
        "accepted_l25_32b_controlled_run_package_proof": source.get("accepted_l25_32b_controlled_run_package_proof", True if source.get("source_l25_32b_ok") is True else None),
        "accepted_l25_33a_key_normalized_broad_checkpoint": source.get("accepted_l25_33a_key_normalized_broad_checkpoint", True if source.get("source_l25_33a_ok") is True else None),
        "source_l25_33a_ok": _first(source, "source_l25_33a_ok", default=inner.get("ok")),
        "source_l25_33a_patch": inner.get("patch") or "L25.33a",
        "source_l25_33a_repairs_patch": _first(source, "source_l25_33a_repairs_patch", default=inner.get("repairs_patch")),
        "source_l25_33a_package_run_ladder_complete": _first(source, "source_l25_33a_package_run_ladder_complete", default=inner.get("package_run_ladder_complete")),
        "source_l25_33a_key_normalization_repair_proven": _first(source, "source_l25_33a_key_normalization_repair_proven", default=inner.get("key_normalization_repair_proven")),
        "source_l25_32b_ok": _first(source, "source_l25_32b_ok", default=inner.get("source_l25_32b_ok")),
        "source_l25_32b_repairs_patches": _first(source, "source_l25_32b_repairs_patches", default=inner.get("source_l25_32b_repairs_patches") or []),
        "bundle_review_expected_shape_present": _first(source, "bundle_review_expected_shape_present", default=inner.get("bundle_review_expected_shape_present")),
        "package_run_allowed": _first(source, "package_run_allowed", default=inner.get("package_run_allowed")),
        "patchops_run_package_performed": _first(source, "patchops_run_package_performed", default=inner.get("patchops_run_package_performed")),
        "patchops_cli_run_package_invoked_for_archive_manifest": _first(source, "patchops_cli_run_package_invoked_for_archive_manifest", default=inner.get("patchops_cli_run_package_invoked_for_archive_manifest")),
        "patchops_cli_run_package_exit_code": _first(source, "patchops_cli_run_package_exit_code", default=inner.get("patchops_cli_run_package_exit_code")),
        "patchops_cli_run_package_timed_out": _first(source, "patchops_cli_run_package_timed_out", default=inner.get("patchops_cli_run_package_timed_out")),
        "patchops_cli_run_package_review_rejected": _first(source, "patchops_cli_run_package_review_rejected", default=inner.get("patchops_cli_run_package_review_rejected")),
        "controlled_package_launcher_executed": _first(source, "controlled_package_launcher_executed", default=inner.get("controlled_package_launcher_executed")),
        "package_run": _first(source, "package_run", default=inner.get("package_run")),
        "accepted_package_run_scope": _first(source, "accepted_package_run_scope", default=inner.get("patchops_run_package_scope")),
        "package_manifest_used_for_execution": _first(source, "package_manifest_used_for_execution", default=inner.get("package_manifest_used_for_execution", False)),
        "adapter_archive_extraction_performed": _first(source, "adapter_archive_extraction_performed", default=inner.get("adapter_archive_extraction_performed", False)),
        "browser_started": _first(source, "browser_started", default=inner.get("browser_started", False)),
        "pasteback": _first(source, "pasteback", "pasteback_workflow_active", default=inner.get("pasteback", False)),
        "real_downloaded_artifact_read": _first(source, "real_downloaded_artifact_read", default=inner.get("real_downloaded_artifact_read", False)),
    }


def build_real_download_artifact_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_real_download_artifact_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = _normalize_l25_34_source(source_payload)
    source_provided = bool(source_payload)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_REAL_DOWNLOAD_ARTIFACT_AUTHORIZATION_TOKEN
    requested = bool(allow_real_download_artifact_authorization or token_present)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_34_payload_provided", "ok": source_provided},
        {"name": "source_l25_34_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_34_patch_marker", "ok": source.get("patch") == "L25.34"},
        {"name": "source_l25_34_final_acceptance_marker", "ok": source.get("final_acceptance_marker") is True},
        {"name": "source_l25_34_controlled_package_run_final_acceptance", "ok": source.get("controlled_package_run_ladder_final_acceptance") is True},
        {"name": "source_l25_33a_accepted", "ok": source.get("source_l25_33a_ok") is True and source.get("source_l25_33a_repairs_patch") == "L25.33"},
        {"name": "source_l25_33a_key_normalization_repair", "ok": source.get("source_l25_33a_key_normalization_repair_proven") is True},
        {"name": "source_l25_32b_accepted", "ok": source.get("source_l25_32b_ok") is True and tuple(source.get("source_l25_32b_repairs_patches") or []) == EXPECTED_REPAIRS},
        {"name": "source_l25_32b_bundle_shape", "ok": source.get("bundle_review_expected_shape_present") is True},
        {"name": "source_l25_32b_package_run_proof", "ok": source.get("package_run_allowed") is True and source.get("patchops_run_package_performed") is True and source.get("patchops_cli_run_package_invoked_for_archive_manifest") is True},
        {"name": "source_l25_32b_run_package_exit_zero", "ok": source.get("patchops_cli_run_package_exit_code") == 0},
        {"name": "source_l25_32b_run_package_not_timed_out", "ok": source.get("patchops_cli_run_package_timed_out") is False},
        {"name": "source_l25_32b_run_package_not_rejected", "ok": source.get("patchops_cli_run_package_review_rejected") is False},
        {"name": "source_l25_32b_launcher_executed", "ok": source.get("controlled_package_launcher_executed") is True},
        {"name": "source_l25_32b_package_run_scope", "ok": source.get("accepted_package_run_scope") == EXPECTED_RUN_PACKAGE_SCOPE},
        {"name": "source_l25_no_manifest_target_execution", "ok": source.get("package_manifest_used_for_execution") is False},
        {"name": "source_l25_no_adapter_extraction", "ok": source.get("adapter_archive_extraction_performed") is False},
        {"name": "source_l25_no_browser_paste_real_artifact", "ok": source.get("browser_started") is False and source.get("pasteback") is False and source.get("real_downloaded_artifact_read") is False},
        {"name": "real_download_artifact_authorization_token_present", "ok": token_present},
        {"name": "real_download_artifact_authorization_token_valid", "ok": token_valid},
    ]
    source_ok = bool(all(check.get("ok") for check in checks[:-2]))
    future_authorized = bool(source_ok and allow_real_download_artifact_authorization and token_valid)
    ok = bool(source_ok and token_present and token_valid)

    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "real_download_artifact_authorization_gate": True,
        "real_download_artifact_authorization_readback_only": True,
        "real_download_artifact_authorization_requested": requested,
        "real_download_artifact_authorization_token_present": token_present,
        "real_download_artifact_authorization_token_valid": token_valid,
        "real_download_artifact_authorization_granted_for_future_patch": future_authorized,
        "future_real_download_artifact_read_requires_explicit_flag_and_token": True,
        "future_real_download_artifact_read_must_be_separately_gated_in_l25_36": True,
        "source_l25_34_summary": source,
        "accepted_controlled_package_run_ladder_final_acceptance": source.get("controlled_package_run_ladder_final_acceptance") is True,
        "accepted_package_run_scope": source.get("accepted_package_run_scope"),
        "no_browser_permission_added_by_l25_35": True,
        "no_real_download_permission_added_by_l25_35": True,
        "no_real_artifact_read_permission_added_by_l25_35": True,
        "no_archive_extraction_permission_added_by_l25_35": True,
        "no_package_execution_permission_added_by_l25_35": True,
        "no_pasteback_permission_added_by_l25_35": True,
        "no_git_permission_added_by_l25_35": True,
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
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Future Real Artifact Auth     : {payload.get('real_download_artifact_authorization_granted_for_future_patch')}",
        f"Real Artifact Read            : {payload.get('real_downloaded_artifact_read')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Pasteback                     : {payload.get('pasteback_workflow_active')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--allow-real-download-artifact-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_authorization_gate(
        args.repo_root,
        source_payload=source_payload,
        allow_real_download_artifact_authorization=args.allow_real_download_artifact_authorization,
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
