from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint as l21_02

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-cli-readback-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-passive-preflight-gate"

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


def test_l21_02_builds_passive_cli_readback_checkpoint() -> None:
    payload = l21_02.build_edge_downloaded_archive_validation_cli_readback_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L21.2"
    assert payload["source_patch"] == "L21.1"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l21_1_passive_preflight_gate_accepted"] is True
    assert payload["l21_1_default_archive_preflight_readback_ok"] is True
    assert payload["l21_1_authorized_archive_preflight_readback_ok"] is True
    assert payload["default_archive_validation_preflight_authorized"] is False
    assert payload["authorized_archive_validation_preflight_authorized"] is True
    assert payload["archive_validation_preflight_authorization_remains_readback_only"] is True
    assert payload["avoid_nested_cli_validation_cascades"] is True
    assert payload["one_shallow_l21_2_compact_cli_smoke"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L21.3 Microsoft Edge downloaded-archive validation passive plan checkpoint"
    _assert_archive_blocked(payload)


def test_l21_02_source_readbacks_are_compact_and_passive() -> None:
    payload = l21_02.build_edge_downloaded_archive_validation_cli_readback_checkpoint(PROJECT_ROOT)
    default = payload["source_default_summary"]
    authorized = payload["source_authorized_summary"]

    assert default["ok"] is True
    assert default["patch"] == "L21.1"
    assert default["archive_validation_preflight_authorized"] is False
    assert default["archive_validation_execution_allowed"] is False
    assert default["archive_validation_active"] is False
    assert default["archive_validation_performed"] is False
    assert default["downloaded_archive_opened"] is False
    assert default["downloaded_archive_contents_listed"] is False
    assert default["downloaded_archive_extracted"] is False
    assert default["downloaded_manifest_read"] is False
    assert default["downloaded_file_bytes_read"] is False
    assert default["downloaded_file_stat_performed"] is False
    assert default["downloaded_file_hash_performed"] is False
    assert default["browser_started"] is False
    assert default["edge_process_started"] is False

    assert authorized["ok"] is True
    assert authorized["patch"] == "L21.1"
    assert authorized["archive_validation_preflight_authorized"] is True
    assert authorized["archive_validation_execution_allowed"] is False
    assert authorized["archive_validation_active"] is False
    assert authorized["archive_validation_performed"] is False
    assert authorized["downloaded_archive_opened"] is False
    assert authorized["downloaded_archive_contents_listed"] is False
    assert authorized["downloaded_archive_extracted"] is False
    assert authorized["downloaded_manifest_read"] is False
    assert authorized["downloaded_file_bytes_read"] is False
    assert authorized["downloaded_file_stat_performed"] is False
    assert authorized["downloaded_file_hash_performed"] is False
    assert authorized["browser_started"] is False
    assert authorized["edge_process_started"] is False


def test_l21_02_cli_compact_json_smoke_is_shallow() -> None:
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
    assert len(completed.stdout) < 90000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L21.2"
    assert payload["l21_1_default_archive_preflight_readback_ok"] is True
    assert payload["l21_1_authorized_archive_preflight_readback_ok"] is True
    assert payload["archive_validation_execution_allowed"] is False
    assert payload["archive_validation_active"] is False
    assert payload["archive_validation_performed"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["downloaded_manifest_read"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_archive_blocked(payload)


def test_l21_02_rejects_disallowed_target_url_without_archive_access() -> None:
    payload = l21_02.build_edge_downloaded_archive_validation_cli_readback_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["l21_1_passive_preflight_gate_accepted"] is False
    _assert_archive_blocked(payload)


def test_l21_02_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l21_02_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L21.2 Microsoft Edge downloaded-archive validation CLI/readback checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY",
        "Microsoft Edge first",
        "Opera second",
        "downloaded-archive validation CLI/readback checkpoint",
        "passive CLI/readback checkpoint",
        "L21.1 passive preflight gate remains accepted",
        "default archive preflight readback remains passive",
        "authorized archive preflight readback remains passive",
        "archive validation preflight authorization remains readback-only",
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
        "avoid nested CLI validation cascades",
        "one shallow L21.2 compact CLI smoke",
        "L21.3 Microsoft Edge downloaded-archive validation passive plan checkpoint",
    ]:
        assert phrase in text
