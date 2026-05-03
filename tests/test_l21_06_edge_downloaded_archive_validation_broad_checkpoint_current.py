from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_broad_checkpoint as l21_06

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof"
FIXTURE_REL = "data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip"

ALWAYS_FALSE_FIELDS = (
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "archive_member_bytes_read",
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


def _ensure_fixture() -> Path:
    fixture = PROJECT_ROOT / FIXTURE_REL
    fixture.parent.mkdir(parents=True, exist_ok=True)
    if not fixture.exists():
        with zipfile.ZipFile(fixture, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", "{}\n")
            zf.writestr("bundle_meta.json", "{}\n")
            zf.writestr("README.txt", "L21.6 synthetic archive fixture.\n")
            zf.writestr("content/payload.txt", "Do not read through adapter.\n")
    return fixture


def _assert_always_blocked(payload: dict) -> None:
    for field in ALWAYS_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l21_06_builds_broad_checkpoint() -> None:
    _ensure_fixture()
    payload = l21_06.build_edge_downloaded_archive_validation_broad_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L21.6"
    assert payload["source_patch"] == "L21.5"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l21_1_through_l21_5_remain_accepted"] is True
    assert payload["archive_metadata_only_validation_proof_remains_accepted"] is True
    assert payload["default_archive_metadata_proof_readback_remains_passive"] is True
    assert payload["authorized_archive_metadata_proof_readback_remains_metadata_only"] is True
    assert payload["unsafe_archive_candidate_remains_rejected_without_archive_access"] is True
    assert payload["only_synthetic_patchops_runtime_archive_metadata_listing_is_allowed"] is True
    assert payload["archive_validation_scope"] == "metadata_listing_only_synthetic_patchops_runtime_archive_fixture"
    assert payload["archive_validation_performed"] is True
    assert payload["downloaded_archive_opened"] is True
    assert payload["downloaded_archive_contents_listed"] is True
    assert payload["archive_entry_count"] >= 1
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L21.7 Microsoft Edge downloaded-archive validation final acceptance marker"
    _assert_always_blocked(payload)


def test_l21_06_source_summaries_cover_default_authorized_and_unsafe() -> None:
    _ensure_fixture()
    payload = l21_06.build_edge_downloaded_archive_validation_broad_checkpoint(PROJECT_ROOT)
    default = payload["source_default_summary"]
    authorized = payload["source_authorized_summary"]
    unsafe = payload["source_unsafe_summary"]

    assert default["ok"] is True
    assert default["patch"] == "L21.5"
    assert default["archive_metadata_proof_authorized"] is False
    assert default["archive_metadata_validation_performed"] is False
    assert default["downloaded_archive_opened"] is False
    assert default["downloaded_archive_contents_listed"] is False
    assert default["archive_member_bytes_read"] is False
    assert default["package_run_performed_by_adapter"] is False

    assert authorized["ok"] is True
    assert authorized["patch"] == "L21.5"
    assert authorized["archive_metadata_proof_authorized"] is True
    assert authorized["candidate_safe_for_l21_5_metadata_only_proof"] is True
    assert authorized["archive_metadata_validation_performed"] is True
    assert authorized["archive_entry_count"] >= 1
    assert authorized["downloaded_archive_opened"] is True
    assert authorized["downloaded_archive_contents_listed"] is True
    assert authorized["downloaded_archive_extracted"] is False
    assert authorized["downloaded_manifest_read"] is False
    assert authorized["archive_member_bytes_read"] is False
    assert authorized["downloaded_file_bytes_read"] is False
    assert authorized["package_run_performed_by_adapter"] is False

    assert unsafe["ok"] is False
    assert unsafe["archive_metadata_proof_authorized"] is False
    assert unsafe["candidate_safe_for_l21_5_metadata_only_proof"] is False
    assert unsafe["archive_metadata_validation_performed"] is False
    assert unsafe["downloaded_archive_opened"] is False
    assert unsafe["downloaded_archive_contents_listed"] is False
    assert unsafe["archive_member_bytes_read"] is False


def test_l21_06_cli_compact_json_smoke() -> None:
    _ensure_fixture()
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
    assert payload["patch"] == "L21.6"
    assert payload["l21_1_through_l21_5_remain_accepted"] is True
    assert payload["authorized_archive_metadata_proof_readback_remains_metadata_only"] is True
    assert payload["unsafe_archive_candidate_remains_rejected_without_archive_access"] is True
    assert payload["archive_validation_performed"] is True
    assert payload["downloaded_archive_opened"] is True
    assert payload["downloaded_archive_contents_listed"] is True
    assert payload["downloaded_archive_extracted"] is False
    assert payload["downloaded_manifest_read"] is False
    assert payload["archive_member_bytes_read"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_always_blocked(payload)


def test_l21_06_rejects_disallowed_target_url_without_archive_access() -> None:
    _ensure_fixture()
    payload = l21_06.build_edge_downloaded_archive_validation_broad_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["l21_1_through_l21_5_remain_accepted"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["downloaded_archive_contents_listed"] is False
    _assert_always_blocked(payload)


def test_l21_06_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l21_06_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_validation_broad_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L21.6 Microsoft Edge downloaded-archive validation broad checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED",
        "Microsoft Edge first",
        "Opera second",
        "downloaded-archive validation broad checkpoint",
        "broad archive validation checkpoint",
        "L21.1 through L21.5 remain accepted",
        "archive metadata-only validation proof remains accepted",
        "default archive metadata proof readback remains passive",
        "authorized archive metadata proof readback remains metadata-only",
        "unsafe archive candidate remains rejected without archive access",
        "only the synthetic PatchOps runtime archive metadata listing is allowed",
        "downloaded archive may be opened only for metadata listing of the synthetic fixture",
        "downloaded archive contents may be listed as metadata only",
        "downloaded archive is not extracted",
        "downloaded manifest is not read",
        "archive member bytes are not read",
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
        "no click/download/stat/hash/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L21.7 Microsoft Edge downloaded-archive validation final acceptance marker",
    ]:
        assert phrase in text
