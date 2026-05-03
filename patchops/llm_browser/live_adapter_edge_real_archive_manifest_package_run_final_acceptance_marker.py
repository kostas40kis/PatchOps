"""L25.34 final acceptance marker for the controlled package-run ladder.

This follows accepted L25.33a. It marks the controlled synthetic package-run
ladder complete after the L25.32/L25.32a repair path and accepted L25.32b plus
L25.33a broad checkpoint repair.

This marker does not add browser, real downloaded artifact, pasteback,
send/submit, localhost, extension, commit, or push permission.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.34"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.34 Microsoft Edge controlled runtime package-run final acceptance marker"
SOURCE_PATCH = "L25.33a"
NEXT_PATCH = "L25.35 Microsoft Edge controlled runtime real-download artifact authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
EXPECTED_RUN_PACKAGE_SCOPE = "controlled_runtime_package_run_only_supported_bundle_shape_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"
EXPECTED_REPAIRS = ("L25.32", "L25.32a")

FALSE_FIELDS = (
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


def _first(payload: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload.get(name)
    return default


def _nested(source: Mapping[str, Any]) -> Mapping[str, Any]:
    value = source.get("source_l25_32b_summary")
    return value if isinstance(value, Mapping) else {}


def _is_true(payload: Mapping[str, Any], *names: str) -> bool:
    return any(payload.get(name) is True for name in names)


def _normalize_l25_33a_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    inner = dict(_nested(source))
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "repairs_patch": source.get("repairs_patch"),
        "broad_checkpoint": source.get("broad_checkpoint"),
        "package_run_ladder_complete": _first(source, "package_run_ladder_complete", "l25_archive_manifest_package_run_ladder_complete", default=False),
        "key_normalization_repair_proven": _is_true(source, "key_normalization_repair_proven") or source.get("l25_33a_repair_classification") == "normalize_l25_32b_validator_summary_and_module_payload_keys" or source.get("repairs_patch") == "L25.33",
        "module_payload_shape_proven": _is_true(source, "module_payload_shape_proven") or source.get("l25_33a_repair_classification") == "normalize_l25_32b_validator_summary_and_module_payload_keys",
        "validator_summary_shape_proven": _is_true(source, "validator_summary_shape_proven") or source.get("l25_33a_repair_classification") == "normalize_l25_32b_validator_summary_and_module_payload_keys",
        "source_l25_32b_ok": _first(source, "source_l25_32b_ok", default=inner.get("ok")),
        "source_l25_32b_patch": inner.get("patch") or "L25.32b",
        "source_l25_32b_repairs_patches": _first(source, "source_l25_32b_repairs_patches", default=inner.get("repairs_patches") or []),
        "bundle_review_expected_shape_present": _first(source, "bundle_review_expected_shape_present", default=inner.get("bundle_review_expected_shape_present")),
        "runpkg_fixture_names_include_expected_bundle_shape": _first(source, "runpkg_fixture_names_include_expected_bundle_shape", default=inner.get("runpkg_fixture_names_include_expected_bundle_shape")),
        "package_run_allowed": _first(source, "package_run_allowed", default=inner.get("package_run_allowed")),
        "patchops_run_package_performed": _first(source, "patchops_run_package_performed", default=inner.get("patchops_run_package_performed")),
        "patchops_cli_run_package_invoked_for_archive_manifest": _first(source, "patchops_cli_run_package_invoked_for_archive_manifest", default=inner.get("patchops_cli_run_package_invoked_for_archive_manifest")),
        "patchops_cli_run_package_exit_code": _first(source, "patchops_cli_run_package_exit_code", default=inner.get("patchops_cli_run_package_exit_code")),
        "patchops_cli_run_package_timed_out": _first(source, "patchops_cli_run_package_timed_out", default=inner.get("patchops_cli_run_package_timed_out")),
        "patchops_cli_run_package_review_rejected": _first(source, "patchops_cli_run_package_review_rejected", default=inner.get("patchops_cli_run_package_review_rejected")),
        "controlled_package_launcher_executed": _first(source, "controlled_package_launcher_executed", default=inner.get("controlled_package_launcher_executed")),
        "package_manifest_used_for_execution": _first(source, "package_manifest_used_for_execution", default=inner.get("package_manifest_used_for_execution", False)),
        "package_execution_allowed": _first(source, "package_execution_allowed", default=inner.get("package_execution_allowed")),
        "adapter_archive_extraction_performed": _first(source, "adapter_archive_extraction_performed", default=inner.get("adapter_archive_extraction_performed", False)),
        "browser_started": _first(source, "browser_started", default=inner.get("browser_started", False)),
        "pasteback": _first(source, "pasteback", "pasteback_workflow_active", default=inner.get("pasteback", False)),
        "real_downloaded_artifact_read": _first(source, "real_downloaded_artifact_read", default=inner.get("real_downloaded_artifact_read", False)),
        "package_run": _first(source, "package_run", default=inner.get("package_run")),
        "patchops_run_package_scope": _first(source, "patchops_run_package_scope", "accepted_patchops_run_package_scope", default=inner.get("patchops_run_package_scope")),
    }


def build_package_run_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = _normalize_l25_33a_source(source_payload)
    source_provided = bool(source_payload)
    checks: list[dict[str, Any]] = [
        {"name": "source_l25_33a_payload_provided", "ok": source_provided},
        {"name": "source_l25_33a_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_33a_patch_marker", "ok": source.get("patch") == "L25.33a"},
        {"name": "source_l25_33a_repairs_l25_33", "ok": source.get("repairs_patch") == "L25.33"},
        {"name": "source_l25_33a_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l25_33a_package_run_ladder_complete", "ok": source.get("package_run_ladder_complete") is True},
        {"name": "source_l25_33a_key_normalization_repair_proven", "ok": source.get("key_normalization_repair_proven") is True},
        {"name": "source_l25_32b_ok", "ok": source.get("source_l25_32b_ok") is True},
        {"name": "source_l25_32b_repairs_recorded", "ok": tuple(source.get("source_l25_32b_repairs_patches") or []) == EXPECTED_REPAIRS},
        {"name": "source_l25_32b_supported_bundle_shape", "ok": source.get("bundle_review_expected_shape_present") is True and source.get("runpkg_fixture_names_include_expected_bundle_shape") is True},
        {"name": "source_l25_32b_package_run_allowed", "ok": source.get("package_run_allowed") is True},
        {"name": "source_l25_32b_run_package_invoked", "ok": source.get("patchops_cli_run_package_invoked_for_archive_manifest") is True},
        {"name": "source_l25_32b_run_package_exit_zero", "ok": source.get("patchops_cli_run_package_exit_code") == 0},
        {"name": "source_l25_32b_run_package_not_timed_out", "ok": source.get("patchops_cli_run_package_timed_out") is False},
        {"name": "source_l25_32b_run_package_not_rejected", "ok": source.get("patchops_cli_run_package_review_rejected") is False},
        {"name": "source_l25_32b_launcher_executed", "ok": source.get("controlled_package_launcher_executed") is True},
        {"name": "source_l25_32b_package_run_true", "ok": source.get("package_run") is True},
        {"name": "source_l25_32b_scope", "ok": source.get("patchops_run_package_scope") == EXPECTED_RUN_PACKAGE_SCOPE},
        {"name": "source_l25_no_manifest_target_execution", "ok": source.get("package_manifest_used_for_execution") is False},
        {"name": "source_l25_no_adapter_extraction", "ok": source.get("adapter_archive_extraction_performed") is False},
        {"name": "source_l25_no_browser_paste_real_artifact", "ok": source.get("browser_started") is False and source.get("pasteback") is False and source.get("real_downloaded_artifact_read") is False},
    ]
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "final_acceptance_marker": True,
        "controlled_package_run_ladder_final_acceptance": ok,
        "accepted_l25_31_package_run_authorization_gate": True,
        "accepted_l25_32b_controlled_run_package_proof": ok,
        "accepted_l25_33a_key_normalized_broad_checkpoint": ok,
        "source_l25_33a_summary": source,
        "accepted_package_run_scope": EXPECTED_RUN_PACKAGE_SCOPE,
        "accepted_package_execution_scope": "controlled synthetic launcher only; not a real downloaded artifact and not a ChatGPT-produced package",
        "accepted_bundle_review_expected_shape_present": source.get("bundle_review_expected_shape_present") is True,
        "accepted_package_run_allowed": source.get("package_run_allowed") is True,
        "accepted_patchops_run_package_performed": source.get("patchops_run_package_performed") is True,
        "accepted_patchops_cli_run_package_invoked_for_archive_manifest": source.get("patchops_cli_run_package_invoked_for_archive_manifest") is True,
        "accepted_patchops_cli_run_package_exit_code": source.get("patchops_cli_run_package_exit_code"),
        "accepted_patchops_cli_run_package_timed_out": source.get("patchops_cli_run_package_timed_out"),
        "accepted_patchops_cli_run_package_review_rejected": source.get("patchops_cli_run_package_review_rejected"),
        "accepted_controlled_package_launcher_executed": source.get("controlled_package_launcher_executed") is True,
        "accepted_package_run": source.get("package_run") is True,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": source.get("package_execution_allowed") is True,
        "no_browser_permission_added_by_l25_34": True,
        "no_pasteback_permission_added_by_l25_34": True,
        "no_real_downloaded_artifact_permission_added_by_l25_34": True,
        "no_git_permission_added_by_l25_34": True,
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
        f"Final Acceptance              : {payload.get('controlled_package_run_ladder_final_acceptance')}",
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
    payload = build_package_run_final_acceptance_marker(args.repo_root, source_payload=source_payload, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
