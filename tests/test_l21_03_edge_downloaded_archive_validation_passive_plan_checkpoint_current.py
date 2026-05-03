from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint as l21_03

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-cli-readback-checkpoint"

ARCHIVE_FALSE_FIELDS = (
    "archive_validation_execution_allowed", "archive_validation_active", "archive_validation_performed",
    "downloaded_archive_opened", "downloaded_archive_contents_listed", "downloaded_archive_extracted",
    "downloaded_manifest_read", "downloaded_file_bytes_read", "downloaded_file_stat_performed",
    "downloaded_file_hash_performed", "browser_started", "edge_process_started", "chatgpt_url_opened",
    "paste_performed", "send_or_submit_performed", "package_run_performed_by_adapter",
    "selenium_imported_by_readback", "cdp_used", "git_commit_executed", "git_push_executed",
)


def _assert_archive_blocked(payload: dict) -> None:
    for field in ARCHIVE_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l21_03_builds_passive_plan_checkpoint() -> None:
    payload = l21_03.build_edge_downloaded_archive_validation_passive_plan_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L21.3"
    assert payload["source_patch"] == "L21.2"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l21_2_cli_readback_checkpoint_accepted"] is True
    assert payload["l21_2_complete"] is True
    assert payload["l21_1_passive_preflight_gate_accepted"] is True
    assert payload["archive_candidate_definition_blocks_l21_3_archive_execution"] is True
    assert payload["future_archive_validation_plan_is_planned_not_executed"] is True
    assert payload["future_archive_validation_plan_blocks_archive_execution"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L21.4 Microsoft Edge downloaded-archive validation controlled authorization gate"
    _assert_archive_blocked(payload)


def test_l21_03_candidate_definition_blocks_archive_execution() -> None:
    definition = l21_03.archive_validation_candidate_definition()
    assert "metadata-only path evidence" in definition["candidate_means"]
    assert definition["future_candidate_rules"]["extension_must_be"] == ".zip"
    assert definition["future_candidate_rules"]["recommended_pattern"] == "patch_*_patchops_bundle.zip"
    assert definition["future_candidate_rules"]["candidate_path_must_remain_metadata_only_in_l21_3"] is True
    assert all(value is False for value in definition["future_validation_stages"].values())


def test_l21_03_future_plan_blocks_archive_execution() -> None:
    plan = l21_03.future_archive_validation_plan()
    assert all(item["status"] == "planned_not_executed" for item in plan)
    assert plan[0]["name"] == "confirm_l21_2_cli_readback_checkpoint_accepted"
    assert plan[1]["name"] == "require_future_l21_4_archive_validation_authorization_token"
    assert plan[2]["metadata_only"] is True
    assert plan[3]["archive_open_allowed_in_l21_3"] is False
    assert plan[3]["archive_extract"] is False
    assert plan[3]["manifest_read"] is False
    assert plan[4]["archive_listing_allowed_in_l21_3"] is False
    assert plan[4]["file_payload_read"] is False
    assert plan[5]["manifest_read_allowed_in_l21_3"] is False
    assert plan[5]["file_byte_read_allowed_in_l21_3"] is False
    assert plan[5]["package_run_allowed_in_l21_3"] is False
    assert plan[-1]["archive_validation_execution_allowed"] is False
    assert plan[-1]["downloaded_archive_opened"] is False
    assert plan[-1]["downloaded_archive_contents_listed"] is False
    assert plan[-1]["downloaded_archive_extracted"] is False
    assert plan[-1]["downloaded_manifest_read"] is False
    assert plan[-1]["downloaded_file_bytes_read"] is False
    assert plan[-1]["package_run"] is False
    assert plan[-1]["pasteback"] is False
    assert plan[-1]["auto_send"] is False


def test_l21_03_cli_compact_json_smoke() -> None:
    completed = subprocess.run([
        sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND,
        "--repo-root", str(PROJECT_ROOT), "--target-url", "https://chatgpt.com/", "--json", "--compact",
    ], cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=30)
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 90000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L21.3"
    assert payload["source_l21_2_cli_readback_checkpoint_accepted"] is True
    assert payload["future_archive_validation_plan_blocks_archive_execution"] is True
    _assert_archive_blocked(payload)


def test_l21_03_rejects_disallowed_target_url_without_archive_access() -> None:
    payload = l21_03.build_edge_downloaded_archive_validation_passive_plan_checkpoint(PROJECT_ROOT, target_url="http://example.test/")
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l21_2_cli_readback_checkpoint_accepted"] is False
    _assert_archive_blocked(payload)


def test_l21_03_command_registered() -> None:
    from patchops.llm_browser import commands
    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l21_03_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in l21_03.SAFETY_PHRASES:
        assert phrase in text
