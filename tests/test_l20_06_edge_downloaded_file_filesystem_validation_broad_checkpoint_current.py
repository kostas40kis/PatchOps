from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_broad_checkpoint as l20_06

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-broad-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-existence-proof"
FIXTURE_REL = "data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip"

ALWAYS_FALSE_FIELDS = (
    "real_file_stat_performed",
    "real_file_hash_performed",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "downloaded_file_bytes_read",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "archive_validation_active",
    "archive_validation_performed",
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
        fixture.write_text("L20.6 synthetic existence-only fixture. Do not read contents.\n", encoding="utf-8")
    return fixture


def _assert_always_blocked(payload: dict) -> None:
    for field in ALWAYS_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l20_06_builds_broad_checkpoint() -> None:
    _ensure_fixture()
    payload = l20_06.build_edge_downloaded_file_filesystem_validation_broad_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L20.6"
    assert payload["source_patch"] == "L20.5"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l20_1_through_l20_5_remain_accepted"] is True
    assert payload["existence_only_filesystem_validation_proof_remains_accepted"] is True
    assert payload["default_existence_proof_readback_remains_passive"] is True
    assert payload["authorized_existence_proof_readback_remains_existence_only"] is True
    assert payload["unsafe_candidate_remains_rejected_without_filesystem_access"] is True
    assert payload["only_synthetic_fixture_existence_check_is_allowed"] is True
    assert payload["filesystem_validation_scope"] == "existence_only_synthetic_patchops_runtime_fixture"
    assert payload["filesystem_validation_performed"] is True
    assert payload["real_file_exists_check_performed"] is True
    assert payload["downloaded_file_exists_check_performed"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L20.7 Microsoft Edge downloaded-file filesystem validation final acceptance marker"
    _assert_always_blocked(payload)


def test_l20_06_source_summaries_cover_default_authorized_and_unsafe() -> None:
    _ensure_fixture()
    payload = l20_06.build_edge_downloaded_file_filesystem_validation_broad_checkpoint(PROJECT_ROOT)
    default = payload["source_default_summary"]
    authorized = payload["source_authorized_summary"]
    unsafe = payload["source_unsafe_summary"]

    assert default["ok"] is True
    assert default["patch"] == "L20.5"
    assert default["filesystem_existence_proof_authorized"] is False
    assert default["existence_only_validation_performed"] is False
    assert default["real_file_exists_check_performed"] is False
    assert default["downloaded_file_exists_check_performed"] is False
    assert default["downloaded_file_bytes_read"] is False
    assert default["downloaded_archive_opened"] is False

    assert authorized["ok"] is True
    assert authorized["patch"] == "L20.5"
    assert authorized["filesystem_existence_proof_authorized"] is True
    assert authorized["candidate_safe_for_l20_5_existence_only_proof"] is True
    assert authorized["existence_only_validation_performed"] is True
    assert authorized["candidate_exists"] is True
    assert authorized["real_file_exists_check_performed"] is True
    assert authorized["downloaded_file_exists_check_performed"] is True
    assert authorized["real_file_stat_performed"] is False
    assert authorized["downloaded_file_bytes_read"] is False
    assert authorized["downloaded_archive_opened"] is False
    assert authorized["package_run_performed_by_adapter"] is False

    assert unsafe["ok"] is False
    assert unsafe["filesystem_existence_proof_authorized"] is False
    assert unsafe["candidate_safe_for_l20_5_existence_only_proof"] is False
    assert unsafe["existence_only_validation_performed"] is False
    assert unsafe["real_file_exists_check_performed"] is False
    assert unsafe["downloaded_file_exists_check_performed"] is False
    assert unsafe["downloaded_file_bytes_read"] is False
    assert unsafe["downloaded_archive_opened"] is False


def test_l20_06_cli_compact_json_smoke() -> None:
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
    assert payload["patch"] == "L20.6"
    assert payload["l20_1_through_l20_5_remain_accepted"] is True
    assert payload["existence_only_filesystem_validation_proof_remains_accepted"] is True
    assert payload["authorized_existence_proof_readback_remains_existence_only"] is True
    assert payload["unsafe_candidate_remains_rejected_without_filesystem_access"] is True
    assert payload["filesystem_validation_performed"] is True
    assert payload["real_file_exists_check_performed"] is True
    assert payload["downloaded_file_exists_check_performed"] is True
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_always_blocked(payload)


def test_l20_06_rejects_disallowed_target_url_without_existence_check() -> None:
    _ensure_fixture()
    payload = l20_06.build_edge_downloaded_file_filesystem_validation_broad_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["l20_1_through_l20_5_remain_accepted"] is False
    _assert_always_blocked(payload)


def test_l20_06_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l20_06_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_broad_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L20.6 Microsoft Edge downloaded-file filesystem validation broad checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_EXISTENCE_PROOF_AUTHORIZED",
        "Microsoft Edge first",
        "Opera second",
        "downloaded-file filesystem validation broad checkpoint",
        "broad filesystem validation checkpoint",
        "L20.1 through L20.5 remain accepted",
        "existence-only filesystem validation proof remains accepted",
        "default existence proof readback remains passive",
        "authorized existence proof readback remains existence-only",
        "unsafe candidate remains rejected without filesystem access",
        "only the synthetic PatchOps runtime fixture existence check is allowed",
        "real file existence check is allowed only for the synthetic fixture",
        "real file stat remains inactive",
        "real file hash remains inactive",
        "downloaded file stat is not performed",
        "downloaded file hash is not performed",
        "downloaded file bytes are not read",
        "downloaded archive is not opened",
        "downloaded archive contents are not listed",
        "downloaded archive is not extracted",
        "downloaded manifest is not read",
        "archive validation remains inactive",
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
        "no click/download/stat/hash/archive/manifest/byte-read/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L20.7 Microsoft Edge downloaded-file filesystem validation final acceptance marker",
    ]:
        assert phrase in text
