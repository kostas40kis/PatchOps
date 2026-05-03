from __future__ import annotations

import argparse
import json
from typing import Any, Mapping


PATCH = "L25.47"
SOURCE_PATCHES = ("L25.46", "L25.46A")
TOKEN = "PATCHOPS_L25_47_CONTROLLED_RUN_PACKAGE_FINAL_ACCEPTANCE_MARKER"

TRUE_REQUIREMENTS = {
    "ok": True,
    "l25_41_authorized_future_package_execution_only": True,
    "l25_42_rendered_would_run_command_only": True,
    "l25_43_broad_checked_dry_run_behavior": True,
    "l25_44_final_accepted_dry_run_ladder": True,
    "l25_45_performed_one_controlled_run_package": True,
    "l25_45a_repaired_pass_detection": True,
    "l25_46_broad_checkpoint_completed": True,
    "l25_46a_validator_import_bootstrap_repaired": True,
    "controlled_run_package_broad_checkpoint_validator": True,
    "controlled_run_package_ladder_valid": True,
    "controlled_run_package_pass_detection_repaired_by_l25_45a": True,
    "controlled_run_package_exit_zero_plus_marker_pass_observed": True,
    "controlled_run_package_marker_observed": True,
    "controlled_package_target_write_marker_false": True,
    "controlled_package_browser_marker_false": True,
    "controlled_package_pasteback_marker_false": True,
    "good_payload_accepted": True,
    "module_cli_good_payload_passed": True,
    "source_payload_only_broad_checkpoint": True,
}

FALSE_REQUIREMENTS = {
    "run_package_invoked_by_l25_46a": False,
    "adapter_archive_extraction_performed": False,
    "archive_member_extracted_to_project": False,
    "artifact_member_written_to_project": False,
    "target_project_file_write_performed_by_controlled_package": False,
    "browser_started": False,
    "real_browser_download_triggered": False,
    "selenium_used": False,
    "cdp_used": False,
    "dom_scraping_used": False,
    "pasteback": False,
    "send_submit_performed": False,
    "localhost_server_started": False,
    "browser_extension_used": False,
    "git_commit_performed": False,
    "git_push_performed": False,
}

OPTIONAL_FORBIDDEN_TRUE_KEYS = (
    "page_inspection_performed",
    "prompt_text_extracted",
    "conversation_read",
    "package_execution_performed_by_adapter",
    "pasteback_workflow_active",
    "adapter_driven_extraction_into_target_project",
    "edge_process_started",
    "chatgpt_url_opened",
    "browser_opened",
    "download_performed",
    "click_download_performed",
    "artifact_content_reading_performed",
)


class FinalAcceptanceValidationError(ValueError):
    """Raised when the L25.47 final-acceptance source payload is malformed."""


def _strict_bool(value: Any, *, key: str) -> bool:
    if not isinstance(value, bool):
        raise FinalAcceptanceValidationError(f"{key}: expected boolean, got {type(value).__name__}")
    return value


def _require_bool(payload: Mapping[str, Any], key: str, expected: bool) -> None:
    if key not in payload:
        raise FinalAcceptanceValidationError(f"{key}: missing required key")
    actual = _strict_bool(payload[key], key=key)
    if actual is not expected:
        raise FinalAcceptanceValidationError(f"{key}: expected {expected!r}, got {actual!r}")


def _require_optional_false(payload: Mapping[str, Any], key: str) -> None:
    if key in payload:
        _require_bool(payload, key, False)


def _require_exit_zero(payload: Mapping[str, Any]) -> None:
    key = "controlled_run_package_exit_code"
    if key not in payload:
        raise FinalAcceptanceValidationError(f"{key}: missing required key")
    if payload[key] != 0:
        raise FinalAcceptanceValidationError(f"{key}: expected 0, got {payload[key]!r}")


def _require_token(payload: Mapping[str, Any]) -> None:
    token = payload.get("l25_47_final_acceptance_token")
    if token != TOKEN:
        raise FinalAcceptanceValidationError(
            "l25_47_final_acceptance_token: expected "
            f"{TOKEN!r}, got {token!r}"
        )


def _require_int_min(payload: Mapping[str, Any], key: str, minimum: int) -> None:
    if key not in payload:
        raise FinalAcceptanceValidationError(f"{key}: missing required key")
    value = payload[key]
    if not isinstance(value, int) or value < minimum:
        raise FinalAcceptanceValidationError(f"{key}: expected integer >= {minimum}, got {value!r}")


def validate_source_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate accepted L25.46A evidence and emit the L25.47 final marker."""

    if not isinstance(payload, Mapping):
        raise FinalAcceptanceValidationError("source payload must be a JSON object")

    patch = payload.get("patch")
    if patch not in SOURCE_PATCHES:
        raise FinalAcceptanceValidationError(f"patch: expected one of {SOURCE_PATCHES!r}, got {patch!r}")

    _require_token(payload)
    _require_exit_zero(payload)
    _require_int_min(payload, "malformed_payloads_rejected", 20)

    for key, expected in TRUE_REQUIREMENTS.items():
        _require_bool(payload, key, expected)

    for key, expected in FALSE_REQUIREMENTS.items():
        _require_bool(payload, key, expected)

    for key in OPTIONAL_FORBIDDEN_TRUE_KEYS:
        _require_optional_false(payload, key)

    if payload.get("run_package_invocation_scope") != "validator_patchops_path_only":
        raise FinalAcceptanceValidationError(
            "run_package_invocation_scope: expected 'validator_patchops_path_only'"
        )

    if payload.get("real_archive_candidate_extraction_scope") != "patchops_owned_runtime_only":
        raise FinalAcceptanceValidationError(
            "real_archive_candidate_extraction_scope: expected 'patchops_owned_runtime_only'"
        )

    return {
        "ok": True,
        "patch": PATCH,
        "source_patch": patch,
        "controlled_run_package_final_acceptance_marker": True,
        "controlled_run_package_ladder_final_acceptance": True,
        "controlled_run_package_final_acceptance_from_source_payload_only": True,
        "accepted_l25_41_package_execution_authorization_gate": True,
        "accepted_l25_42_package_execution_dry_run_proof": True,
        "accepted_l25_43_package_execution_dry_run_broad_checkpoint": True,
        "accepted_l25_44_package_execution_dry_run_final_marker": True,
        "accepted_l25_45_first_controlled_run_package_proof": True,
        "accepted_l25_45a_pass_detection_repair": True,
        "accepted_l25_46_controlled_run_package_broad_checkpoint": True,
        "accepted_l25_46a_validator_import_bootstrap_repair": True,
        "controlled_run_package_exit_code": 0,
        "controlled_run_package_exit_zero_plus_marker_pass_observed": True,
        "controlled_run_package_marker_observed": True,
        "controlled_run_package_run_scope": "validator_patchops_path_only",
        "real_archive_candidate_extraction_scope": "patchops_owned_runtime_only",
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "target_project_file_write_performed_by_controlled_package": False,
        "browser_started": False,
        "real_browser_download_triggered": False,
        "selenium_used": False,
        "cdp_used": False,
        "dom_scraping_used": False,
        "pasteback": False,
        "send_submit_performed": False,
        "localhost_server_started": False,
        "browser_extension_used": False,
        "git_commit_performed": False,
        "git_push_performed": False,
        "run_package_invoked_by_l25_47": False,
        "source_payload_only_final_acceptance": True,
    }


def load_source_payload(path: str) -> Mapping[str, Any]:
    return json.loads(open(path, "r", encoding="utf-8").read())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the L25.47 controlled run-package final acceptance marker.")
    parser.add_argument("--source-payload", help="JSON file containing accepted L25.46A source evidence.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    args = parser.parse_args(argv)

    if not args.source_payload:
        print(json.dumps({
            "ok": False,
            "patch": PATCH,
            "error": "source payload required",
            "default_without_source_payload_rejected": True,
            "run_package_invoked_by_l25_47": False,
        }, sort_keys=True))
        return 1

    try:
        result = validate_source_payload(load_source_payload(args.source_payload))
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "patch": PATCH,
            "error": str(exc),
            "run_package_invoked_by_l25_47": False,
        }, sort_keys=True))
        return 1

    print(json.dumps(result, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

