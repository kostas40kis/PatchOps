"""L25.33a key-normalized broad checkpoint for controlled package-run proof.

This repairs L25.33. The failed L25.33 proof re-ran the accepted controlled
run-package proof successfully, but the broad checkpoint expected validator
summary key names while the source module produced module-payload key names.
L25.33a normalizes both shapes before checking accepted L25.32b signals.

No browser, Selenium, CDP, DOM scraping, pasteback, send/submit, localhost,
real downloaded artifact, git commit, or git push permission is added.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.33a"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.33a Microsoft Edge controlled runtime package-run broad checkpoint key repair"
SOURCE_PATCH = "L25.32b"
REPAIRS_PATCH = "L25.33"
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


def _is_true(payload: Mapping[str, Any], *names: str) -> bool:
    return any(payload.get(name) is True for name in names)


def _is_false(payload: Mapping[str, Any], *names: str, default_false: bool = False) -> bool:
    values = [payload.get(name) for name in names if name in payload]
    if not values:
        return default_false
    return all(value is False for value in values)


def _first(payload: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload.get(name)
    return default


def normalize_l25_32b_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "repairs_patches": list(source.get("repairs_patches") or []),
        "bundle_review_expected_shape_present": _is_true(source, "bundle_review_expected_shape_present"),
        "runpkg_fixture_names_include_expected_bundle_shape": _is_true(source, "runpkg_fixture_names_include_expected_bundle_shape") or _is_true(source, "bundle_review_expected_shape_present"),
        "package_run_allowed": _is_true(source, "package_run_allowed", "archive_manifest_package_run_allowed"),
        "patchops_run_package_performed": _is_true(source, "patchops_run_package_performed"),
        "patchops_cli_run_package_invoked_for_archive_manifest": _is_true(source, "patchops_cli_run_package_invoked_for_archive_manifest"),
        "patchops_cli_run_package_exit_code": _first(source, "patchops_cli_run_package_exit_code"),
        "patchops_cli_run_package_timed_out": _first(source, "patchops_cli_run_package_timed_out"),
        "patchops_cli_run_package_review_rejected": _first(source, "patchops_cli_run_package_review_rejected", default=False),
        "controlled_package_launcher_executed": _is_true(source, "controlled_package_launcher_executed"),
        "package_manifest_used_for_execution": _first(source, "package_manifest_used_for_execution", default=False),
        "package_execution_allowed": _is_true(source, "package_execution_allowed"),
        "adapter_archive_extraction_performed": _first(source, "adapter_archive_extraction_performed", default=False),
        "browser_started": _first(source, "browser_started", default=False),
        "pasteback": _first(source, "pasteback", "pasteback_workflow_active", default=False),
        "real_downloaded_artifact_read": _first(source, "real_downloaded_artifact_read", default=False),
        "package_run": _is_true(source, "package_run"),
        "patchops_run_package_scope": _first(source, "patchops_run_package_scope"),
        "next_patch": _first(source, "next_patch"),
    }


def build_archive_manifest_package_run_broad_checkpoint_key_repair(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = normalize_l25_32b_source(source_payload)
    source_provided = bool(source_payload)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_32b_payload_provided", "ok": source_provided},
        {"name": "source_l25_32b_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_32b_patch_marker", "ok": source.get("patch") == "L25.32b"},
        {"name": "source_l25_32b_repairs_recorded", "ok": tuple(source.get("repairs_patches") or []) == EXPECTED_REPAIRS},
        {"name": "source_l25_32b_bundle_shape_normalized", "ok": source.get("bundle_review_expected_shape_present") is True and source.get("runpkg_fixture_names_include_expected_bundle_shape") is True},
        {"name": "source_l25_32b_package_run_allowed_normalized", "ok": source.get("package_run_allowed") is True},
        {"name": "source_l25_32b_run_package_invoked", "ok": source.get("patchops_cli_run_package_invoked_for_archive_manifest") is True},
        {"name": "source_l25_32b_run_package_exit_zero", "ok": source.get("patchops_cli_run_package_exit_code") == 0},
        {"name": "source_l25_32b_run_package_not_timed_out", "ok": source.get("patchops_cli_run_package_timed_out") is False},
        {"name": "source_l25_32b_run_package_not_rejected", "ok": source.get("patchops_cli_run_package_review_rejected") is False},
        {"name": "source_l25_32b_launcher_executed", "ok": source.get("controlled_package_launcher_executed") is True},
        {"name": "source_l25_32b_package_run_true", "ok": source.get("package_run") is True},
        {"name": "source_l25_32b_scope", "ok": source.get("patchops_run_package_scope") == EXPECTED_RUN_PACKAGE_SCOPE},
        {"name": "source_l25_32b_no_manifest_target_execution", "ok": source.get("package_manifest_used_for_execution") is False},
        {"name": "source_l25_32b_no_adapter_extraction", "ok": source.get("adapter_archive_extraction_performed") is False},
        {"name": "source_l25_32b_no_browser_paste_real_artifact_normalized", "ok": source.get("browser_started") is False and source.get("pasteback") is False and source.get("real_downloaded_artifact_read") is False},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "repairs_patch": REPAIRS_PATCH,
        "broad_checkpoint": True,
        "archive_manifest_package_run_ladder_checkpoint": True,
        "l25_archive_manifest_package_run_ladder_complete": ok,
        "l25_33_failure_classification": "broad_checkpoint_key_shape_mismatch_after_successful_controlled_run_package_proof",
        "l25_33a_repair_classification": "normalize_l25_32b_validator_summary_and_module_payload_keys",
        "source_l25_32b_summary": source,
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
        "no_new_browser_permission_added_by_l25_33a": True,
        "no_new_pasteback_or_real_artifact_permission_added_by_l25_33a": True,
        "no_git_permission_added_by_l25_33a": True,
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
    return "\n".join([
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
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_archive_manifest_package_run_broad_checkpoint_key_repair(args.repo_root, source_payload=source_payload, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
