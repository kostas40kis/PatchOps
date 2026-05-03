from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_passive_preflight_gate as l21_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-passive-preflight-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-final-acceptance-marker"
TOKEN = "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY"

ARCHIVE_FALSE_FIELDS = (
    "archive_validation_execution_allowed",
    "archive_validation_active",
    "archive_validation_performed",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "browser_started",
    "edge_process_started",
    "chatgpt_url_opened",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "selenium_imported_by_readback",
    "cdp_used",
    "git_commit_executed",
    "git_push_executed",
)


def _assert_archive_blocked(payload: dict) -> None:
    for field in ARCHIVE_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l21_01_default_readback_is_passive() -> None:
    payload = l21_01.build_edge_downloaded_archive_validation_passive_preflight_gate(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L21.1"
    assert payload["source_patch"] == "L20.7"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l20_7_final_marker_accepted"] is True
    assert payload["l20_downloaded_file_filesystem_validation_stream_complete"] is True
    assert payload["l20_completion_means_synthetic_fixture_existence_only_validation"] is True
    assert payload["archive_validation_preflight_requested"] is False
    assert payload["archive_validation_preflight_authorized"] is False
    assert payload["archive_validation_preflight_authorization_is_readback_only_in_l21_1"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L21.2 Microsoft Edge downloaded-archive validation CLI/readback checkpoint"
    _assert_archive_blocked(payload)


def test_l21_01_authorized_readback_still_blocks_archive_validation() -> None:
    payload = l21_01.build_edge_downloaded_archive_validation_passive_preflight_gate(
        PROJECT_ROOT,
        allow_archive_validation_preflight=True,
        authorization_token=TOKEN,
    )

    assert payload["ok"] is True
    assert payload["archive_validation_preflight_requested"] is True
    assert payload["archive_validation_preflight_authorized"] is True
    assert payload["archive_validation_preflight_readback"]["archive_validation_preflight_authorization_token_present"] is True
    assert payload["archive_validation_execution_allowed"] is False
    assert payload["archive_validation_active"] is False
    assert payload["archive_validation_performed"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["downloaded_archive_contents_listed"] is False
    assert payload["downloaded_archive_extracted"] is False
    assert payload["downloaded_manifest_read"] is False
    assert payload["downloaded_file_bytes_read"] is False
    _assert_archive_blocked(payload)


def test_l21_01_wrong_token_does_not_authorize() -> None:
    payload = l21_01.build_edge_downloaded_archive_validation_passive_preflight_gate(
        PROJECT_ROOT,
        allow_archive_validation_preflight=True,
        authorization_token="wrong-token",
    )
    assert payload["ok"] is True
    assert payload["archive_validation_preflight_requested"] is True
    assert payload["archive_validation_preflight_authorized"] is False
    _assert_archive_blocked(payload)


def test_l21_01_cli_default_and_authorized_compact_json_smokes() -> None:
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
    assert default_payload["patch"] == "L21.1"
    assert default_payload["archive_validation_preflight_authorized"] is False
    _assert_archive_blocked(default_payload)

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
            "--allow-archive-validation-preflight",
            "--authorization-token",
            TOKEN,
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
    assert authorized_payload["patch"] == "L21.1"
    assert authorized_payload["archive_validation_preflight_authorized"] is True
    assert authorized_payload["archive_validation_execution_allowed"] is False
    assert authorized_payload["downloaded_archive_opened"] is False
    assert authorized_payload["downloaded_manifest_read"] is False
    assert authorized_payload["downloaded_file_bytes_read"] is False
    _assert_archive_blocked(authorized_payload)


def test_l21_01_rejects_disallowed_target_url_without_archive_access() -> None:
    payload = l21_01.build_edge_downloaded_archive_validation_passive_preflight_gate(
        PROJECT_ROOT,
        target_url="http://example.test/",
        allow_archive_validation_preflight=True,
        authorization_token=TOKEN,
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l20_7_final_marker_accepted"] is False
    assert payload["archive_validation_preflight_authorized"] is True
    _assert_archive_blocked(payload)


def test_l21_01_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l21_01_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L21.1 Microsoft Edge downloaded-archive validation passive preflight gate",
        COMMAND,
        SOURCE_COMMAND,
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "downloaded-archive validation passive preflight gate",
        "archive validation preflight authorization is readback-only",
        "L20.7 filesystem validation final marker remains accepted",
        "L20 completion means synthetic-fixture existence-only validation",
        "archive validation execution allowed: false",
        "archive validation active: false",
        "archive validation is not performed",
        "downloaded archive is not opened",
        "downloaded archive contents are not listed",
        "downloaded archive is not extracted",
        "downloaded manifest is not read",
        "downloaded file bytes are not read",
        "downloaded file stat is not performed",
        "downloaded file hash is not performed",
        "package-run from browser remains inactive",
        "pasteback remains inactive",
        "download workflow remains inactive",
        "real browser download remains inactive",
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
        "no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest/byte-read/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L21.2 Microsoft Edge downloaded-archive validation CLI/readback checkpoint",
    ]:
        assert phrase in text
