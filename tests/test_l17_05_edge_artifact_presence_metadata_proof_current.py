from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_artifact_presence_metadata_proof as l17_05

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-artifact-presence-metadata-proof"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-artifact-detection-controlled-live-authorization-gate"
TOKEN = "PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_METADATA_PROOF_AUTHORIZED"


def _assert_no_browser_download_content_side_effects(payload: dict) -> None:
    for field in [
        "real_page_inspection_performed",
        "live_browser_artifact_detection_active",
        "live_browser_artifact_detection_performed",
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
    ]:
        assert payload[field] is False, field


def test_l17_05_default_readback_does_not_classify() -> None:
    payload = l17_05.build_edge_artifact_presence_metadata_proof(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["patch"] == "L17.5"
    assert payload["source_patch"] == "L17.4"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l17_4_controlled_live_authorization_gate_accepted"] is True
    assert payload["l17_4_complete"] is True
    assert payload["artifact_presence_metadata_proof_requested"] is False
    assert payload["artifact_presence_metadata_proof_authorized"] is False
    assert payload["artifact_presence_metadata_classification_performed"] is False
    assert payload["artifact_presence_detected_from_metadata"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L17.6 Microsoft Edge artifact detection broad checkpoint"
    _assert_no_browser_download_content_side_effects(payload)


def test_l17_05_authorized_positive_metadata_detects_artifact_presence() -> None:
    payload = l17_05.build_edge_artifact_presence_metadata_proof(
        PROJECT_ROOT,
        allow_artifact_presence_metadata_proof=True,
        authorization_token=TOKEN,
        candidate_metadata=l17_05.positive_metadata_fixture(),
    )

    assert payload["ok"] is True
    assert payload["artifact_presence_metadata_proof_requested"] is True
    assert payload["artifact_presence_metadata_proof_token_present"] is True
    assert payload["artifact_presence_metadata_proof_authorized"] is True
    assert payload["artifact_presence_metadata_classification_performed"] is True
    assert payload["artifact_presence_detected_from_metadata"] is True
    classification = payload["artifact_presence_metadata_classification"]
    assert classification["metadata_only"] is True
    assert classification["artifact_presence_detected"] is True
    assert classification["candidate_filename"] == "patch_999_example_patchops_bundle.zip"
    assert classification["blocking_reasons"] == []
    assert classification["content_reading_performed"] is False
    assert classification["download_performed"] is False
    assert classification["click_performed"] is False
    assert classification["package_run_performed"] is False
    assert payload["artifact_detection_performed"] is True
    assert payload["artifact_presence_detection_performed"] is True
    _assert_no_browser_download_content_side_effects(payload)


def test_l17_05_authorized_negative_metadata_rejects_non_zip_without_side_effects() -> None:
    result = l17_05.classify_artifact_presence_from_metadata(l17_05.negative_metadata_fixture())
    assert result["artifact_presence_detected"] is False
    assert "filename_does_not_end_with_zip" in result["blocking_reasons"]
    assert result["content_reading_performed"] is False
    assert result["download_performed"] is False
    assert result["click_performed"] is False
    assert result["package_run_performed"] is False


def test_l17_05_forbidden_metadata_keys_block_positive_detection() -> None:
    data = l17_05.positive_metadata_fixture()
    data["artifact_content"] = "print('do not read me')"
    result = l17_05.classify_artifact_presence_from_metadata(data)
    assert result["artifact_presence_detected"] is False
    assert result["forbidden_metadata_keys_present"] == ["artifact_content"]
    assert "forbidden_metadata_keys_present" in result["blocking_reasons"]


def test_l17_05_rejects_disallowed_target_url_without_browser_side_effects() -> None:
    payload = l17_05.build_edge_artifact_presence_metadata_proof(
        PROJECT_ROOT,
        allow_artifact_presence_metadata_proof=True,
        authorization_token=TOKEN,
        candidate_metadata=l17_05.positive_metadata_fixture(),
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l17_4_controlled_live_authorization_gate_accepted"] is False
    _assert_no_browser_download_content_side_effects(payload)


def test_l17_05_cli_default_and_authorized_compact_json_smokes() -> None:
    default_completed = subprocess.run(
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
    assert default_completed.returncode == 0, default_completed.stderr
    default_payload = json.loads(default_completed.stdout)
    assert default_payload["ok"] is True
    assert default_payload["patch"] == "L17.5"
    assert default_payload["artifact_presence_metadata_classification_performed"] is False
    _assert_no_browser_download_content_side_effects(default_payload)

    authorized_completed = subprocess.run(
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
            "--allow-artifact-presence-metadata-proof",
            "--authorization-token",
            TOKEN,
            "--candidate-filename",
            "patch_999_example_patchops_bundle.zip",
            "--download-control-visible",
            "--download-control-enabled",
            "--latest-assistant-reply-scope",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert authorized_completed.returncode == 0, authorized_completed.stderr
    assert len(authorized_completed.stdout) < 90000
    authorized_payload = json.loads(authorized_completed.stdout)
    assert authorized_payload["ok"] is True
    assert authorized_payload["patch"] == "L17.5"
    assert authorized_payload["artifact_presence_metadata_proof_authorized"] is True
    assert authorized_payload["artifact_presence_metadata_classification_performed"] is True
    assert authorized_payload["artifact_presence_detected_from_metadata"] is True
    _assert_no_browser_download_content_side_effects(authorized_payload)


def test_l17_05_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l17_05_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_artifact_presence_metadata_proof.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L17.5 Microsoft Edge first controlled artifact-presence metadata proof",
        COMMAND,
        SOURCE_COMMAND,
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "controlled artifact-presence metadata proof",
        "metadata-only artifact-presence classification",
        "L17.4 controlled live authorization gate remains accepted",
        "metadata proof authorization token",
        "artifact presence metadata proof may classify synthetic metadata only",
        "artifact presence metadata proof does not inspect a real page",
        "artifact presence metadata proof does not read artifact content",
        "artifact presence metadata proof does not click a download control",
        "artifact presence metadata proof does not download a file",
        "artifact presence metadata proof does not run a package",
        "live browser artifact detection remains inactive",
        "download workflow active: false",
        "download workflow remains inactive",
        "PatchOps remains source of truth",
        "target URL allowlist remains enforced",
        "ChatGPT URL may be selected but not opened",
        "dedicated Microsoft Edge runtime profile remains required for future live phases",
        "never use the default Microsoft Edge profile",
        "no Microsoft Edge start",
        "no Selenium import",
        "no CDP use",
        "no DOM scraping",
        "no prompt text extraction",
        "no conversation reading",
        "no artifact content reading",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L17.6 Microsoft Edge artifact detection broad checkpoint",
    ]:
        assert phrase in text
