from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate as l21_04

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint"
TOKEN = "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY"

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


def test_l21_04_default_authorization_gate_is_passive() -> None:
    payload = l21_04.build_edge_downloaded_archive_validation_controlled_authorization_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L21.4"
    assert payload["source_patch"] == "L21.3"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l21_3_passive_plan_checkpoint_accepted"] is True
    assert payload["archive_validation_authorization_requested"] is False
    assert payload["archive_validation_authorization_token_present"] is False
    assert payload["archive_validation_authorized_for_future_phase"] is False
    assert payload["archive_validation_authorization_is_readback_only_in_l21_4"] is True
    assert payload["future_authorization_gate_plan_blocks_archive_execution"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L21.5 Microsoft Edge first controlled downloaded-archive validation proof"
    _assert_archive_blocked(payload)


def test_l21_04_authorized_readback_still_blocks_archive_validation() -> None:
    payload = l21_04.build_edge_downloaded_archive_validation_controlled_authorization_gate(
        PROJECT_ROOT,
        allow_archive_validation_authorization=True,
        authorization_token=TOKEN,
    )
    assert payload["ok"] is True
    assert payload["archive_validation_authorization_requested"] is True
    assert payload["archive_validation_authorization_token_present"] is True
    assert payload["archive_validation_authorized_for_future_phase"] is True
    assert payload["archive_validation_authorization_is_readback_only_in_l21_4"] is True
    _assert_archive_blocked(payload)


def test_l21_04_wrong_token_does_not_authorize_future_phase() -> None:
    payload = l21_04.build_edge_downloaded_archive_validation_controlled_authorization_gate(
        PROJECT_ROOT,
        allow_archive_validation_authorization=True,
        authorization_token="wrong-token",
    )
    assert payload["ok"] is True
    assert payload["archive_validation_authorization_requested"] is True
    assert payload["archive_validation_authorization_token_present"] is False
    assert payload["archive_validation_authorized_for_future_phase"] is False
    _assert_archive_blocked(payload)


def test_l21_04_authorization_gate_plan_blocks_archive_execution() -> None:
    plan = l21_04.future_archive_validation_authorization_gate_plan()
    assert all(item["status"] == "planned_not_executed" for item in plan)
    assert plan[0]["name"] == "confirm_l21_3_passive_plan_checkpoint_accepted"
    assert plan[1]["name"] == "require_explicit_archive_validation_authorization_flag"
    assert plan[2]["required_authorization_token"] == TOKEN
    assert plan[3]["archive_open_in_l21_4"] is False
    assert plan[3]["archive_listing_in_l21_4"] is False
    assert plan[3]["archive_extract_in_l21_4"] is False
    assert plan[3]["manifest_read_in_l21_4"] is False
    assert plan[3]["file_byte_read_in_l21_4"] is False
    assert plan[3]["package_run_in_l21_4"] is False
    assert plan[-1]["archive_validation_execution_allowed"] is False
    assert plan[-1]["downloaded_archive_opened"] is False
    assert plan[-1]["downloaded_manifest_read"] is False
    assert plan[-1]["downloaded_file_bytes_read"] is False
    assert plan[-1]["package_run"] is False
    assert plan[-1]["pasteback"] is False
    assert plan[-1]["auto_send"] is False


def test_l21_04_cli_default_and_authorized_compact_json_smokes() -> None:
    default_completed = subprocess.run([
        sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND,
        "--repo-root", str(PROJECT_ROOT), "--target-url", "https://chatgpt.com/", "--json", "--compact",
    ], cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=30)
    assert default_completed.returncode == 0, default_completed.stderr
    default_payload = json.loads(default_completed.stdout)
    assert default_payload["ok"] is True
    assert default_payload["patch"] == "L21.4"
    assert default_payload["archive_validation_authorized_for_future_phase"] is False
    _assert_archive_blocked(default_payload)

    authorized_completed = subprocess.run([
        sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND,
        "--repo-root", str(PROJECT_ROOT), "--target-url", "https://chatgpt.com/",
        "--allow-archive-validation-authorization", "--authorization-token", TOKEN,
        "--json", "--compact",
    ], cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=30)
    assert authorized_completed.returncode == 0, authorized_completed.stderr
    assert len(authorized_completed.stdout) < 90000
    authorized_payload = json.loads(authorized_completed.stdout)
    assert authorized_payload["ok"] is True
    assert authorized_payload["patch"] == "L21.4"
    assert authorized_payload["archive_validation_authorized_for_future_phase"] is True
    assert authorized_payload["archive_validation_execution_allowed"] is False
    assert authorized_payload["downloaded_archive_opened"] is False
    assert authorized_payload["downloaded_manifest_read"] is False
    assert authorized_payload["downloaded_file_bytes_read"] is False
    _assert_archive_blocked(authorized_payload)


def test_l21_04_rejects_disallowed_target_url_without_archive_access() -> None:
    payload = l21_04.build_edge_downloaded_archive_validation_controlled_authorization_gate(
        PROJECT_ROOT,
        target_url="http://example.test/",
        allow_archive_validation_authorization=True,
        authorization_token=TOKEN,
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l21_3_passive_plan_checkpoint_accepted"] is False
    assert payload["archive_validation_authorized_for_future_phase"] is True
    _assert_archive_blocked(payload)


def test_l21_04_command_registered() -> None:
    from patchops.llm_browser import commands
    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l21_04_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in l21_04.SAFETY_PHRASES:
        assert phrase in text
