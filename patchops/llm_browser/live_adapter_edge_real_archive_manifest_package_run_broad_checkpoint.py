"""L25.33 broad checkpoint for controlled synthetic package-run proof.

This follows accepted L25.32b. It summarizes the package-run ladder after the
L25.32/L25.32a repair path and, when explicitly provided with an authorized
source payload, verifies the accepted signals from the controlled synthetic
run-package proof.

It does not start a browser, inspect pages, paste, send, use Selenium/CDP/DOM
scraping, use a real downloaded artifact, start localhost, commit, or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.33"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.33 Microsoft Edge controlled runtime archive manifest package-run broad checkpoint"
SOURCE_PATCH = "L25.32b"
SOURCE_LADDER = (
    "L25.31 package-run authorization gate",
    "L25.32 failed first controlled package-run proof because the synthetic ZIP had the wrong bundle shape",
    "L25.32a failed repair because a brittle upstream source-chain ok assertion blocked the proof",
    "L25.32b repaired package-run proof using direct supported bundle-shape checks and one controlled synthetic run-package call",
)
NEXT_PATCH = "L25.34 Microsoft Edge controlled runtime package-run final acceptance marker"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
EXPECTED_RUN_PACKAGE_SCOPE = "controlled_runtime_package_run_only_supported_bundle_shape_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"
EXPECTED_REPAIRS = ("L25.32", "L25.32a")

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


def _coerce_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(source_payload or {})


def build_archive_manifest_package_run_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _coerce_source(source_payload)
    source_provided = bool(source)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_32b_payload_provided", "ok": source_provided},
        {"name": "source_l25_32b_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_32b_patch_marker", "ok": source.get("patch") == "L25.32b"},
        {"name": "source_l25_32b_repairs_recorded", "ok": tuple(source.get("repairs_patches") or []) == EXPECTED_REPAIRS},
        {"name": "source_l25_32b_bundle_shape", "ok": source.get("bundle_review_expected_shape_present") is True and source.get("runpkg_fixture_names_include_expected_bundle_shape") is True},
        {"name": "source_l25_32b_package_run_allowed", "ok": source.get("package_run_allowed") is True},
        {"name": "source_l25_32b_run_package_invoked", "ok": source.get("patchops_cli_run_package_invoked_for_archive_manifest") is True},
        {"name": "source_l25_32b_run_package_exit_zero", "ok": source.get("patchops_cli_run_package_exit_code") == 0},
        {"name": "source_l25_32b_run_package_not_timed_out", "ok": source.get("patchops_cli_run_package_timed_out") is False},
        {"name": "source_l25_32b_run_package_not_rejected", "ok": source.get("patchops_cli_run_package_review_rejected") is False},
        {"name": "source_l25_32b_launcher_executed", "ok": source.get("controlled_package_launcher_executed") is True},
        {"name": "source_l25_32b_package_run_true", "ok": source.get("package_run") is True},
        {"name": "source_l25_32b_scope", "ok": source.get("patchops_run_package_scope") == EXPECTED_RUN_PACKAGE_SCOPE},
        {"name": "source_l25_32b_no_manifest_target_execution", "ok": source.get("package_manifest_used_for_execution") is False},
        {"name": "source_l25_32b_no_adapter_extraction", "ok": source.get("adapter_archive_extraction_performed") is False},
        {"name": "source_l25_32b_no_browser_paste_real_artifact", "ok": source.get("browser_started") is False and source.get("pasteback") is False and source.get("real_downloaded_artifact_read") is not True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_ladder": list(SOURCE_LADDER),
        "broad_checkpoint": True,
        "archive_manifest_package_run_ladder_checkpoint": True,
        "l25_archive_manifest_package_run_ladder_complete": ok,
        "source_l25_32b_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "repairs_patches": source.get("repairs_patches"),
            "bundle_review_expected_shape_present": source.get("bundle_review_expected_shape_present"),
            "runpkg_fixture_names_include_expected_bundle_shape": source.get("runpkg_fixture_names_include_expected_bundle_shape"),
            "package_run_allowed": source.get("package_run_allowed"),
            "patchops_run_package_performed": source.get("patchops_run_package_performed"),
            "patchops_cli_run_package_invoked_for_archive_manifest": source.get("patchops_cli_run_package_invoked_for_archive_manifest"),
            "patchops_cli_run_package_exit_code": source.get("patchops_cli_run_package_exit_code"),
            "patchops_cli_run_package_timed_out": source.get("patchops_cli_run_package_timed_out"),
            "patchops_cli_run_package_review_rejected": source.get("patchops_cli_run_package_review_rejected"),
            "controlled_package_launcher_executed": source.get("controlled_package_launcher_executed"),
            "package_manifest_used_for_execution": source.get("package_manifest_used_for_execution"),
            "package_execution_allowed": source.get("package_execution_allowed"),
            "adapter_archive_extraction_performed": source.get("adapter_archive_extraction_performed"),
            "browser_started": source.get("browser_started"),
            "pasteback": source.get("pasteback"),
            "package_run": source.get("package_run"),
            "patchops_run_package_scope": source.get("patchops_run_package_scope"),
            "next_patch": source.get("next_patch"),
        },
        "accepted_bundle_review_expected_shape_present": source.get("bundle_review_expected_shape_present") is True,
        "accepted_package_run_allowed": source.get("package_run_allowed") is True,
        "accepted_patchops_run_package_performed": source.get("patchops_run_package_performed") is True,
        "accepted_patchops_cli_run_package_invoked_for_archive_manifest": source.get("patchops_cli_run_package_invoked_for_archive_manifest") is True,
        "accepted_patchops_cli_run_package_exit_code": source.get("patchops_cli_run_package_exit_code"),
        "accepted_patchops_cli_run_package_timed_out": source.get("patchops_cli_run_package_timed_out"),
        "accepted_patchops_cli_run_package_review_rejected": source.get("patchops_cli_run_package_review_rejected"),
        "accepted_controlled_package_launcher_executed": source.get("controlled_package_launcher_executed") is True,
        "accepted_package_run": source.get("package_run") is True,
        "accepted_patchops_run_package_scope": source.get("patchops_run_package_scope"),
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": source.get("package_execution_allowed") is True,
        "package_execution_scope": "controlled synthetic launcher only; not a real downloaded artifact and not a ChatGPT-produced package",
        "run_package_broad_checkpoint_reuses_accepted_l25_32b_proof": True,
        "l25_32_failure_classification": "authoring_shape_rejection_before_launcher",
        "l25_32a_failure_classification": "brittle_upstream_source_ok_assertion_before_run_package_proof",
        "l25_32b_repair_classification": "supported_bundle_shape_plus_explicit_token_plus_one_bounded_controlled_run_package_call",
        "no_new_browser_permission_added_by_l25_33": True,
        "no_new_pasteback_or_real_artifact_permission_added_by_l25_33": True,
        "no_git_permission_added_by_l25_33": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.33 is the broad checkpoint over the accepted L25.32b controlled synthetic run-package proof.",
            "The only accepted package-run execution remains the synthetic launcher-only bundle. Real downloaded artifacts, browser activity, pasteback, send/submit, localhost, extension, commit, and push remain out of scope.",
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
        f"Ladder Complete               : {payload.get('l25_archive_manifest_package_run_ladder_complete')}",
        f"Run Package Invoked           : {payload.get('accepted_patchops_cli_run_package_invoked_for_archive_manifest')}",
        f"Run Package Exit              : {payload.get('accepted_patchops_cli_run_package_exit_code')}",
        f"Review Rejected               : {payload.get('accepted_patchops_cli_run_package_review_rejected')}",
        f"Package Run                   : {payload.get('accepted_package_run')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Pasteback                     : {payload.get('pasteback_workflow_active')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_archive_manifest_package_run_broad_checkpoint(args.repo_root, source_payload=source_payload, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
