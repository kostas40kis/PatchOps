from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_download_metadata_proof as l18_05

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-download-metadata-proof"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-download-workflow-controlled-live-authorization-gate"
TOKEN = "PATCHOPS_L18_EDGE_DOWNLOAD_METADATA_PROOF_AUTHORIZED"

PASSIVE_FALSE_FIELDS = (
    "live_download_execution_allowed",
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "downloaded_file_bytes_read",
    "download_staging_directory_created",
    "click_download_performed",
    "artifact_content_reading_performed",
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "real_page_inspection_performed",
    "live_browser_artifact_detection_active",
    "live_browser_artifact_detection_performed",
    "live_browser_download_workflow_active",
    "live_browser_download_workflow_performed",
    "pasteback_workflow_active",
    "auto_send_allowed",
    "launch_execution_allowed",
    "browser_process_launch_requested",
    "browser_started",
    "edge_process_started",
    "chatgpt_url_opened",
    "page_inspection_performed",
    "page_metadata_detection_performed",
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


def test_l18_05_default_readback_does_not_classify() -> None:
    payload = l18_05.build_edge_download_metadata_proof(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["patch"] == "L18.5"
    assert payload["source_patch"] == "L18.4"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l18_4_controlled_live_authorization_gate_accepted"] is True
    assert payload["l18_4_complete"] is True
    assert payload["download_metadata_proof_requested"] is False
    assert payload["download_metadata_proof_authorized"] is False
    assert payload["download_metadata_classification_performed"] is False
    assert payload["download_readiness_confirmed_from_metadata"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L18.6 Microsoft Edge download workflow broad checkpoint"
    _assert_passive(payload)


def test_l18_05_authorized_positive_metadata_confirms_download_readiness() -> None:
    payload = l18_05.build_edge_download_metadata_proof(
        PROJECT_ROOT,
        allow_download_metadata_proof=True,
        authorization_token=TOKEN,
        download_metadata=l18_05.positive_download_metadata_fixture(),
    )

    assert payload["ok"] is True
    assert payload["download_metadata_proof_requested"] is True
    assert payload["download_metadata_proof_token_present"] is True
    assert payload["download_metadata_proof_authorized"] is True
    assert payload["download_metadata_classification_performed"] is True
    assert payload["download_readiness_confirmed_from_metadata"] is True
    classification = payload["download_metadata_classification"]
    assert classification["metadata_only"] is True
    assert classification["download_readiness_confirmed_from_metadata"] is True
    assert classification["candidate_filename"] == "patch_999_example_patchops_bundle.zip"
    assert classification["blocking_reasons"] == []
    assert classification["real_page_inspection_performed"] is False
    assert classification["click_download_performed"] is False
    assert classification["download_performed"] is False
    assert classification["downloaded_file_bytes_read"] is False
    assert classification["download_staging_directory_created"] is False
    assert classification["artifact_content_reading_performed"] is False
    assert classification["package_run_performed"] is False
    _assert_passive(payload)


def test_l18_05_negative_metadata_rejects_non_zip_without_side_effects() -> None:
    result = l18_05.classify_download_readiness_from_metadata(l18_05.negative_download_metadata_fixture())
    assert result["download_readiness_confirmed_from_metadata"] is False
    assert "candidate_filename_does_not_end_with_zip" in result["blocking_reasons"]
    assert result["click_download_performed"] is False
    assert result["download_performed"] is False
    assert result["downloaded_file_bytes_read"] is False
    assert result["download_staging_directory_created"] is False
    assert result["artifact_content_reading_performed"] is False
    assert result["package_run_performed"] is False


def test_l18_05_forbidden_metadata_keys_block_positive_detection() -> None:
    data = l18_05.positive_download_metadata_fixture()
    data["downloaded_file_bytes"] = "do-not-read"
    result = l18_05.classify_download_readiness_from_metadata(data)
    assert result["download_readiness_confirmed_from_metadata"] is False
    assert result["forbidden_metadata_keys_present"] == ["downloaded_file_bytes"]
    assert "forbidden_metadata_keys_present" in result["blocking_reasons"]


def test_l18_05_rejects_disallowed_target_url_without_browser_side_effects() -> None:
    payload = l18_05.build_edge_download_metadata_proof(
        PROJECT_ROOT,
        allow_download_metadata_proof=True,
        authorization_token=TOKEN,
        download_metadata=l18_05.positive_download_metadata_fixture(),
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l18_4_controlled_live_authorization_gate_accepted"] is False
    _assert_passive(payload)


def test_l18_05_cli_default_and_authorized_compact_json_smokes() -> None:
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
    assert default_payload["patch"] == "L18.5"
    assert default_payload["download_metadata_classification_performed"] is False
    _assert_passive(default_payload)

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
            "--allow-download-metadata-proof",
            "--authorization-token",
            TOKEN,
            "--candidate-filename",
            "patch_999_example_patchops_bundle.zip",
            "--artifact-presence-from-l17-metadata",
            "--download-control-visible-metadata",
            "--download-control-enabled-metadata",
            "--download-authorization-from-l18-4",
            "--target-url-allowed-metadata",
            "--staging-path-is-metadata-only",
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
    assert authorized_payload["patch"] == "L18.5"
    assert authorized_payload["download_metadata_proof_authorized"] is True
    assert authorized_payload["download_metadata_classification_performed"] is True
    assert authorized_payload["download_readiness_confirmed_from_metadata"] is True
    _assert_passive(authorized_payload)


def test_l18_05_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l18_05_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_download_metadata_proof.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L18.5 Microsoft Edge first controlled download metadata proof",
        COMMAND,
        SOURCE_COMMAND,
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "controlled download metadata proof",
        "metadata-only download readiness classification",
        "L18.4 controlled live authorization gate remains accepted",
        "download metadata proof authorization token",
        "download metadata proof may classify synthetic metadata only",
        "download metadata proof does not inspect a real page",
        "download metadata proof does not click a download control",
        "download metadata proof does not download a file",
        "download metadata proof does not create a staging directory",
        "download metadata proof does not read downloaded file bytes",
        "download metadata proof does not read artifact content",
        "download metadata proof does not run a package",
        "live browser download workflow remains inactive",
        "download workflow active: false",
        "download workflow execution allowed: false",
        "download is not performed",
        "downloaded file bytes are not read",
        "download staging directory is not created",
        "pasteback remains inactive",
        "package-run from browser remains inactive",
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
        "L18.6 Microsoft Edge download workflow broad checkpoint",
    ]:
        assert phrase in text
