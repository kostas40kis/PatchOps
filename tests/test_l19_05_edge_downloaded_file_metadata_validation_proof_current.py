from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_file_metadata_validation_proof as l19_05

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-file-metadata-validation-proof"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-validation-controlled-authorization-gate"
TOKEN = "PATCHOPS_L19_EDGE_DOWNLOADED_FILE_METADATA_VALIDATION_PROOF_AUTHORIZED"

PASSIVE_FALSE_FIELDS = (
    "controlled_downloaded_file_validation_execution_allowed",
    "downloaded_file_metadata_validation_execution_allowed",
    "downloaded_file_metadata_validation_active",
    "downloaded_file_validation_execution_allowed",
    "downloaded_file_validation_active",
    "downloaded_file_validation_performed",
    "downloaded_file_exists_check_performed",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "downloaded_file_bytes_read",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "live_download_execution_allowed",
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "download_staging_directory_created",
    "click_download_performed",
    "artifact_content_reading_performed",
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_performed",
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


def test_l19_05_default_readback_does_not_classify() -> None:
    payload = l19_05.build_edge_downloaded_file_metadata_validation_proof(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["patch"] == "L19.5"
    assert payload["source_patch"] == "L19.4"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l19_4_controlled_authorization_gate_accepted"] is True
    assert payload["l19_4_complete"] is True
    assert payload["downloaded_file_metadata_validation_proof_requested"] is False
    assert payload["downloaded_file_metadata_validation_proof_authorized"] is False
    assert payload["downloaded_file_metadata_validation_classification_performed"] is False
    assert payload["downloaded_file_metadata_validation_ready"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L19.6 Microsoft Edge downloaded-file validation broad checkpoint"
    _assert_passive(payload)


def test_l19_05_authorized_positive_metadata_confirms_validation_readiness() -> None:
    payload = l19_05.build_edge_downloaded_file_metadata_validation_proof(
        PROJECT_ROOT,
        allow_downloaded_file_metadata_validation_proof=True,
        authorization_token=TOKEN,
        downloaded_file_metadata=l19_05.positive_downloaded_file_metadata_fixture(),
    )

    assert payload["ok"] is True
    assert payload["downloaded_file_metadata_validation_proof_requested"] is True
    assert payload["downloaded_file_metadata_validation_proof_token_present"] is True
    assert payload["downloaded_file_metadata_validation_proof_authorized"] is True
    assert payload["downloaded_file_metadata_validation_classification_performed"] is True
    assert payload["downloaded_file_metadata_validation_ready"] is True
    classification = payload["downloaded_file_metadata_validation_classification"]
    assert classification["metadata_only"] is True
    assert classification["downloaded_file_metadata_validation_ready"] is True
    assert classification["candidate_filename_metadata"] == "patch_999_example_patchops_bundle.zip"
    assert classification["blocking_reasons"] == []
    assert classification["file_exists_check_performed"] is False
    assert classification["file_stat_performed"] is False
    assert classification["file_hash_performed"] is False
    assert classification["file_bytes_read"] is False
    assert classification["archive_opened"] is False
    assert classification["archive_contents_listed"] is False
    assert classification["archive_extracted"] is False
    assert classification["manifest_read"] is False
    assert classification["package_run_performed"] is False
    _assert_passive(payload)


def test_l19_05_negative_metadata_rejects_non_zip_without_side_effects() -> None:
    result = l19_05.classify_downloaded_file_validation_from_metadata(l19_05.negative_downloaded_file_metadata_fixture())
    assert result["downloaded_file_metadata_validation_ready"] is False
    assert "candidate_extension_metadata_is_not_zip" in result["blocking_reasons"]
    assert "candidate_filename_does_not_end_with_zip" in result["blocking_reasons"]
    assert result["file_exists_check_performed"] is False
    assert result["file_stat_performed"] is False
    assert result["file_hash_performed"] is False
    assert result["file_bytes_read"] is False
    assert result["archive_opened"] is False
    assert result["manifest_read"] is False
    assert result["package_run_performed"] is False


def test_l19_05_forbidden_metadata_keys_block_positive_detection() -> None:
    data = l19_05.positive_downloaded_file_metadata_fixture()
    data["file_exists"] = True
    data["file_hash"] = "do-not-compute"
    result = l19_05.classify_downloaded_file_validation_from_metadata(data)
    assert result["downloaded_file_metadata_validation_ready"] is False
    assert result["forbidden_metadata_keys_present"] == ["file_exists", "file_hash"]
    assert "forbidden_metadata_keys_present" in result["blocking_reasons"]


def test_l19_05_rejects_disallowed_target_url_without_browser_or_file_side_effects() -> None:
    payload = l19_05.build_edge_downloaded_file_metadata_validation_proof(
        PROJECT_ROOT,
        allow_downloaded_file_metadata_validation_proof=True,
        authorization_token=TOKEN,
        downloaded_file_metadata=l19_05.positive_downloaded_file_metadata_fixture(),
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l19_4_controlled_authorization_gate_accepted"] is False
    _assert_passive(payload)


def test_l19_05_cli_default_and_authorized_compact_json_smokes() -> None:
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
    assert default_payload["patch"] == "L19.5"
    assert default_payload["downloaded_file_metadata_validation_classification_performed"] is False
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
            "--allow-downloaded-file-metadata-validation-proof",
            "--authorization-token",
            TOKEN,
            "--candidate-path-metadata",
            "data/runtime/browser_downloads/patch_999_example_patchops_bundle.zip",
            "--candidate-filename-metadata",
            "patch_999_example_patchops_bundle.zip",
            "--candidate-extension-metadata",
            ".zip",
            "--candidate-path-is-metadata-only",
            "--downloaded-file-validation-authorization-from-l19-4",
            "--download-metadata-proof-from-l18-5",
            "--download-workflow-complete-from-l18-7",
            "--target-url-allowed-metadata",
            "--operator-reviewed-metadata",
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
    assert authorized_payload["patch"] == "L19.5"
    assert authorized_payload["downloaded_file_metadata_validation_proof_authorized"] is True
    assert authorized_payload["downloaded_file_metadata_validation_classification_performed"] is True
    assert authorized_payload["downloaded_file_metadata_validation_ready"] is True
    _assert_passive(authorized_payload)


def test_l19_05_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l19_05_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_file_metadata_validation_proof.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L19.5 Microsoft Edge first controlled downloaded-file metadata validation proof",
        COMMAND,
        SOURCE_COMMAND,
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "controlled downloaded-file metadata validation proof",
        "metadata-only downloaded-file validation decision",
        "L19.4 controlled authorization gate remains accepted",
        "downloaded-file metadata validation proof authorization token",
        "downloaded-file metadata validation may classify synthetic metadata only",
        "downloaded-file metadata validation does not check whether a file exists",
        "downloaded-file metadata validation does not stat a file",
        "downloaded-file metadata validation does not hash a file",
        "downloaded-file metadata validation does not open a downloaded archive",
        "downloaded-file metadata validation does not list downloaded archive contents",
        "downloaded-file metadata validation does not extract a downloaded archive",
        "downloaded-file metadata validation does not read a downloaded manifest",
        "downloaded-file metadata validation does not read downloaded file bytes",
        "downloaded-file metadata validation does not run a package",
        "downloaded-file validation execution allowed: false",
        "downloaded-file validation active: false",
        "downloaded-file validation is not performed",
        "downloaded file bytes are not read",
        "downloaded archive is not opened",
        "downloaded manifest is not read",
        "download workflow remains inactive",
        "real browser download remains inactive",
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
        "no click/download/file-read/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L19.6 Microsoft Edge downloaded-file validation broad checkpoint",
    ]:
        assert phrase in text
