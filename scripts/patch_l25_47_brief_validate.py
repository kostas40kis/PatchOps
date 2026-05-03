from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Direct script execution puts scripts/ on sys.path. Bootstrap the repo root
# before importing patchops.* so this validator works through manifest commands.
REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT_STR = str(REPO_ROOT)
if REPO_ROOT_STR not in sys.path:
    sys.path.insert(0, REPO_ROOT_STR)

from patchops.llm_browser.live_adapter_edge_real_download_artifact_controlled_run_package_final_acceptance_marker import (
    TOKEN,
    FinalAcceptanceValidationError,
    validate_source_payload,
)


def _good_payload() -> dict[str, object]:
    return {
        "patch": "L25.46A",
        "l25_47_final_acceptance_token": TOKEN,
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
        "controlled_run_package_exit_code": 0,
        "controlled_run_package_exit_zero_plus_marker_pass_observed": True,
        "controlled_run_package_marker_observed": True,
        "controlled_package_target_write_marker_false": True,
        "controlled_package_browser_marker_false": True,
        "controlled_package_pasteback_marker_false": True,
        "good_payload_accepted": True,
        "malformed_payloads_rejected": 31,
        "module_cli_good_payload_passed": True,
        "source_payload_only_broad_checkpoint": True,
        "run_package_invoked_by_l25_46a": False,
        "run_package_invocation_scope": "validator_patchops_path_only",
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
        "page_inspection_performed": False,
        "prompt_text_extracted": False,
        "conversation_read": False,
        "download_performed": False,
        "click_download_performed": False,
        "artifact_content_reading_performed": False,
        "pasteback": False,
        "pasteback_workflow_active": False,
        "send_submit_performed": False,
        "localhost_server_started": False,
        "browser_extension_used": False,
        "adapter_driven_extraction_into_target_project": False,
        "package_execution_performed_by_adapter": False,
        "git_commit_performed": False,
        "git_push_performed": False,
    }


def _expect_rejected(label: str, payload: dict[str, object]) -> None:
    try:
        validate_source_payload(payload)
    except FinalAcceptanceValidationError:
        return
    raise AssertionError(f"malformed payload was accepted: {label}")


def _mutated(base: dict[str, object], **updates: object) -> dict[str, object]:
    data = copy.deepcopy(base)
    data.update(updates)
    return data


def run_validation() -> dict[str, object]:
    good = _good_payload()
    result = validate_source_payload(good)
    assert result["ok"] is True
    assert result["patch"] == "L25.47"
    assert result["controlled_run_package_final_acceptance_marker"] is True
    assert result["controlled_run_package_ladder_final_acceptance"] is True
    assert result["source_payload_only_final_acceptance"] is True
    assert result["run_package_invoked_by_l25_47"] is False
    assert result["browser_started"] is False
    assert result["pasteback"] is False

    bad_cases = {
        "wrong_patch": _mutated(good, patch="L25.45A"),
        "missing_token": _mutated(good, l25_47_final_acceptance_token="WRONG"),
        "l25_41_missing": _mutated(good, l25_41_authorized_future_package_execution_only=False),
        "l25_42_missing": _mutated(good, l25_42_rendered_would_run_command_only=False),
        "l25_43_missing": _mutated(good, l25_43_broad_checked_dry_run_behavior=False),
        "l25_44_missing": _mutated(good, l25_44_final_accepted_dry_run_ladder=False),
        "l25_45_missing": _mutated(good, l25_45_performed_one_controlled_run_package=False),
        "l25_45a_missing": _mutated(good, l25_45a_repaired_pass_detection=False),
        "l25_46_missing": _mutated(good, l25_46_broad_checkpoint_completed=False),
        "l25_46a_missing": _mutated(good, l25_46a_validator_import_bootstrap_repaired=False),
        "broad_checkpoint_missing": _mutated(good, controlled_run_package_broad_checkpoint_validator=False),
        "ladder_invalid": _mutated(good, controlled_run_package_ladder_valid=False),
        "pass_detection_missing": _mutated(good, controlled_run_package_pass_detection_repaired_by_l25_45a=False),
        "exit_code_nonzero": _mutated(good, controlled_run_package_exit_code=1),
        "exit_zero_marker_missing": _mutated(good, controlled_run_package_exit_zero_plus_marker_pass_observed=False),
        "marker_missing": _mutated(good, controlled_run_package_marker_observed=False),
        "target_write_marker_missing": _mutated(good, controlled_package_target_write_marker_false=False),
        "browser_marker_missing": _mutated(good, controlled_package_browser_marker_false=False),
        "pasteback_marker_missing": _mutated(good, controlled_package_pasteback_marker_false=False),
        "too_few_bad_payloads": _mutated(good, malformed_payloads_rejected=3),
        "module_cli_missing": _mutated(good, module_cli_good_payload_passed=False),
        "source_payload_not_broad": _mutated(good, source_payload_only_broad_checkpoint=False),
        "l25_46a_invoked_run_package": _mutated(good, run_package_invoked_by_l25_46a=True),
        "wrong_run_scope": _mutated(good, run_package_invocation_scope="browser_adapter"),
        "wrong_extraction_scope": _mutated(good, real_archive_candidate_extraction_scope="target_project"),
        "adapter_extraction_true": _mutated(good, adapter_archive_extraction_performed=True),
        "archive_member_extracted_true": _mutated(good, archive_member_extracted_to_project=True),
        "artifact_member_written_true": _mutated(good, artifact_member_written_to_project=True),
        "controlled_target_write_true": _mutated(good, target_project_file_write_performed_by_controlled_package=True),
        "browser_started_true": _mutated(good, browser_started=True),
        "real_download_true": _mutated(good, real_browser_download_triggered=True),
        "selenium_true": _mutated(good, selenium_used=True),
        "cdp_true": _mutated(good, cdp_used=True),
        "dom_true": _mutated(good, dom_scraping_used=True),
        "pasteback_true": _mutated(good, pasteback=True),
        "send_submit_true": _mutated(good, send_submit_performed=True),
        "localhost_true": _mutated(good, localhost_server_started=True),
        "extension_true": _mutated(good, browser_extension_used=True),
        "git_commit_true": _mutated(good, git_commit_performed=True),
        "git_push_true": _mutated(good, git_push_performed=True),
        "adapter_package_execution_true": _mutated(good, package_execution_performed_by_adapter=True),
    }
    for label, payload in bad_cases.items():
        _expect_rejected(label, payload)

    module_path = REPO_ROOT / "patchops" / "llm_browser" / "live_adapter_edge_real_download_artifact_controlled_run_package_final_acceptance_marker.py"
    with tempfile.TemporaryDirectory(prefix="patchops_l25_47_") as temp_dir:
        payload_path = Path(temp_dir) / "accepted_l25_46a_payload.json"
        payload_path.write_text(json.dumps(good, indent=2) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(module_path), "--source-payload", str(payload_path), "--compact"],
            cwd=str(REPO_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    cli_payload = json.loads(completed.stdout)
    assert cli_payload["ok"] is True
    assert cli_payload["patch"] == "L25.47"
    assert cli_payload["run_package_invoked_by_l25_47"] is False

    return {
        "ok": True,
        "patch": "L25.47",
        "controlled_run_package_final_acceptance_marker": True,
        "controlled_run_package_ladder_final_acceptance": True,
        "good_payload_accepted": True,
        "malformed_payloads_rejected": len(bad_cases),
        "module_cli_good_payload_passed": True,
        "source_payload_only_final_acceptance": True,
        "run_package_invoked_by_l25_47": False,
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief validator for PatchOps L25.47.")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    try:
        payload = run_validation()
    except Exception as exc:
        print(json.dumps({"ok": False, "patch": "L25.47", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

