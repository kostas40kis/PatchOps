from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_final_acceptance_marker as l20_07

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-broad-checkpoint"
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
        fixture.write_text("L20.7 synthetic existence-only fixture. Do not read contents.\n", encoding="utf-8")
    return fixture


def _assert_always_blocked(payload: dict) -> None:
    for field in ALWAYS_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l20_07_builds_final_acceptance_marker() -> None:
    _ensure_fixture()
    payload = l20_07.build_edge_downloaded_file_filesystem_validation_final_acceptance_marker(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L20.7"
    assert payload["source_patch"] == "L20.6"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l20_6_broad_checkpoint_accepted"] is True
    assert payload["l20_1_through_l20_6_remain_accepted"] is True
    assert payload["l20_downloaded_file_filesystem_validation_stream_complete"] is True
    assert payload["l20_completion_means_synthetic_fixture_existence_only_validation"] is True
    assert payload["existence_only_filesystem_validation_proof_remains_accepted"] is True
    assert payload["only_synthetic_patchops_runtime_fixture_existence_check_is_accepted"] is True
    assert payload["real_file_existence_check_accepted_only_for_synthetic_fixture"] is True
    assert payload["filesystem_validation_scope"] == "existence_only_synthetic_patchops_runtime_fixture"
    assert payload["filesystem_validation_performed"] is True
    assert payload["real_file_exists_check_performed"] is True
    assert payload["downloaded_file_exists_check_performed"] is True
    assert payload["archive_validation_remains_separate_future_stream"] is True
    assert payload["hash_validation_remains_separate_future_stream"] is True
    assert payload["file_byte_read_remains_separate_future_stream"] is True
    assert payload["manifest_read_remains_separate_future_stream"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["remaining_l20_patches"] == []
    assert payload["next_patch"] == "L21.1 Microsoft Edge downloaded-archive validation passive preflight gate"
    _assert_always_blocked(payload)


def test_l20_07_source_summary_remains_narrow() -> None:
    _ensure_fixture()
    payload = l20_07.build_edge_downloaded_file_filesystem_validation_final_acceptance_marker(PROJECT_ROOT)
    source = payload["source_l20_6_summary"]

    assert source["ok"] is True
    assert source["patch"] == "L20.6"
    assert source["l20_6_complete"] is True
    assert source["l20_1_through_l20_5_remain_accepted"] is True
    assert source["existence_only_filesystem_validation_proof_remains_accepted"] is True
    assert source["authorized_existence_proof_readback_remains_existence_only"] is True
    assert source["unsafe_candidate_remains_rejected_without_filesystem_access"] is True
    assert source["filesystem_validation_scope"] == "existence_only_synthetic_patchops_runtime_fixture"
    assert source["filesystem_validation_performed"] is True
    assert source["real_file_exists_check_performed"] is True
    assert source["downloaded_file_exists_check_performed"] is True
    assert source["real_file_stat_performed"] is False
    assert source["real_file_hash_performed"] is False
    assert source["downloaded_file_bytes_read"] is False
    assert source["downloaded_archive_opened"] is False
    assert source["downloaded_manifest_read"] is False
    assert source["browser_started"] is False
    assert source["edge_process_started"] is False
    assert source["package_run_performed_by_adapter"] is False


def test_l20_07_cli_compact_json_smoke() -> None:
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
    assert payload["patch"] == "L20.7"
    assert payload["l20_downloaded_file_filesystem_validation_stream_complete"] is True
    assert payload["l20_completion_means_synthetic_fixture_existence_only_validation"] is True
    assert payload["filesystem_validation_scope"] == "existence_only_synthetic_patchops_runtime_fixture"
    assert payload["real_file_exists_check_performed"] is True
    assert payload["downloaded_file_exists_check_performed"] is True
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_always_blocked(payload)


def test_l20_07_rejects_disallowed_target_url_without_archive_or_byte_read() -> None:
    _ensure_fixture()
    payload = l20_07.build_edge_downloaded_file_filesystem_validation_final_acceptance_marker(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l20_6_broad_checkpoint_accepted"] is False
    _assert_always_blocked(payload)


def test_l20_07_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l20_07_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_final_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L20.7 Microsoft Edge downloaded-file filesystem validation final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "downloaded-file filesystem validation final acceptance marker",
        "L20.1 through L20.6 remain accepted",
        "L20 downloaded-file filesystem validation stream complete",
        "L20 completion means synthetic-fixture existence-only validation",
        "existence-only filesystem validation proof remains accepted",
        "only the synthetic PatchOps runtime fixture existence check is accepted",
        "real file existence check is accepted only for the synthetic fixture",
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
        "archive validation remains a separate future stream",
        "hash validation remains a separate future stream",
        "file-byte read remains a separate future stream",
        "manifest read remains a separate future stream",
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
        "L21.1 Microsoft Edge downloaded-archive validation passive preflight gate",
    ]:
        assert phrase in text
