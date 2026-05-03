from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_artifact_detection_cli_readback_checkpoint as l17_02

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-artifact-detection-cli-readback-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-artifact-detection-passive-preflight-gate"

PASSIVE_FALSE_FIELDS = (
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_allowed",
    "artifact_detection_performed",
    "artifact_content_reading_performed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_performed",
    "click_download_performed",
    "pasteback_workflow_active",
    "auto_send_allowed",
    "launch_execution_allowed",
    "browser_process_launch_requested",
    "browser_started",
    "edge_process_started",
    "chatgpt_url_opened",
    "page_inspection_performed",
    "page_metadata_detection_performed",
    "page_metadata_detection_proven",
    "selenium_required",
    "selenium_imported_by_readback",
    "cdp_used",
    "remote_debugging_port_used",
    "browser_session_created",
    "driver_created",
    "dom_scraping_performed",
    "prompt_text_extraction_performed",
    "conversation_reading_performed",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "localhost_patchops_server_started",
    "browser_extension_used",
    "git_commit_executed",
    "git_push_executed",
)


def _assert_passive(payload: dict) -> None:
    for field in PASSIVE_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l17_02_builds_passive_cli_readback_checkpoint() -> None:
    payload = l17_02.build_edge_artifact_detection_cli_readback_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L17.2"
    assert payload["source_patch"] == "L17.1"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l17_1_passive_preflight_gate_accepted"] is True
    assert payload["l17_1_default_compact_readback_ok"] is True
    assert payload["l17_1_authorized_compact_readback_ok"] is True
    assert payload["default_artifact_preflight_authorized"] is False
    assert payload["authorized_artifact_preflight_authorized"] is True
    assert payload["artifact_detection_preflight_is_readback_only"] is True
    assert payload["planned_cli_readbacks_are_passive"] is True
    assert payload["avoid_nested_cli_validation_cascades"] is True
    assert payload["one_shallow_cli_smoke_recommended"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L17.3 Microsoft Edge artifact detection passive plan checkpoint"
    _assert_passive(payload)


def test_l17_02_source_readbacks_are_compact_and_passive() -> None:
    payload = l17_02.build_edge_artifact_detection_cli_readback_checkpoint(PROJECT_ROOT)
    default = payload["source_default_summary"]
    authorized = payload["source_authorized_summary"]

    assert default["ok"] is True
    assert default["patch"] == "L17.1"
    assert default["artifact_detection_preflight_authorized"] is False
    assert default["artifact_detection_execution_allowed"] is False
    assert default["artifact_detection_active"] is False
    assert default["artifact_detection_performed"] is False
    assert default["download_workflow_active"] is False
    assert default["download_performed"] is False
    assert default["browser_started"] is False
    assert default["edge_process_started"] is False
    assert default["chatgpt_url_opened"] is False

    assert authorized["ok"] is True
    assert authorized["patch"] == "L17.1"
    assert authorized["artifact_detection_preflight_authorized"] is True
    assert authorized["artifact_detection_execution_allowed"] is False
    assert authorized["artifact_detection_active"] is False
    assert authorized["artifact_detection_performed"] is False
    assert authorized["download_workflow_active"] is False
    assert authorized["download_performed"] is False
    assert authorized["browser_started"] is False
    assert authorized["edge_process_started"] is False
    assert authorized["chatgpt_url_opened"] is False


def test_l17_02_cli_compact_json_smoke_is_shallow() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-url",
            "https://chatgpt.com/",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 80000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L17.2"
    assert payload["l17_1_default_compact_readback_ok"] is True
    assert payload["l17_1_authorized_compact_readback_ok"] is True
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["chatgpt_url_opened"] is False
    _assert_passive(payload)


def test_l17_02_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l17_02.build_edge_artifact_detection_cli_readback_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["l17_1_authorized_compact_readback_ok"] is False
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l17_02_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l17_02_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_artifact_detection_cli_readback_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L17.2 Microsoft Edge artifact detection CLI/readback checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "passive CLI/readback checkpoint",
        "L17.1 passive preflight gate remains accepted",
        "default compact readback remains passive",
        "authorized compact readback remains passive",
        "artifact detection preflight authorization is still readback-only",
        "artifact detection execution allowed: false",
        "artifact detection is not performed",
        "download workflow is not active",
        "PatchOps remains source of truth",
        "target URL allowlist remains enforced",
        "ChatGPT URL may be selected but not opened",
        "no Microsoft Edge start",
        "no Selenium import",
        "no CDP use",
        "no DOM scraping",
        "no prompt text extraction",
        "no conversation reading",
        "no artifact detection",
        "no artifact content reading",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "avoid nested CLI validation cascades",
        "one shallow L17.2 compact CLI smoke",
        "L17.3 Microsoft Edge artifact detection passive plan checkpoint",
    ]:
        assert phrase in text

# PATCHOPS L17.2A VALIDATOR IMPORT REPAIR START

def test_l17_02_brief_validator_runs_as_script_path() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/patch_l17_02_brief_validate.py",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L17.2"
    assert payload["validator_import_context_repaired"] is True
    assert payload["artifact_detection_execution_allowed"] is False
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["chatgpt_url_opened"] is False
# PATCHOPS L17.2A VALIDATOR IMPORT REPAIR END
