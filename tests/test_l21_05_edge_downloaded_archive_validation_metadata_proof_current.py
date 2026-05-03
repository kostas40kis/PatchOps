from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_metadata_proof as l21_05

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate"
TOKEN = "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED"
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
            zf.writestr("README.txt", "L21.5 synthetic archive fixture.\n")
            zf.writestr("content/payload.txt", "Do not read through adapter.\n")
    return fixture


def _assert_blocked(payload: dict) -> None:
    for field in ALWAYS_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l21_05_default_readback_is_passive() -> None:
    _ensure_fixture()
    payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L21.5"
    assert payload["source_patch"] == "L21.4"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l21_4_controlled_authorization_gate_accepted"] is True
    assert payload["l21_4_complete"] is True
    assert payload["archive_validation_authorized_by_l21_4_for_future_phase"] is True
    assert payload["archive_metadata_proof_requested"] is False
    assert payload["archive_metadata_proof_authorized"] is False
    assert payload["archive_validation_performed"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["downloaded_archive_contents_listed"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L21.6 Microsoft Edge downloaded-archive validation broad checkpoint"
    _assert_blocked(payload)


def test_l21_05_authorized_archive_metadata_proof_lists_fixture_names_only() -> None:
    fixture = _ensure_fixture()
    payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(
        PROJECT_ROOT,
        allow_archive_metadata_proof=True,
        authorization_token=TOKEN,
        candidate_path_metadata=FIXTURE_REL,
    )

    assert payload["ok"] is True
    assert payload["archive_metadata_proof_requested"] is True
    assert payload["archive_metadata_proof_authorization_token_present"] is True
    assert payload["archive_metadata_proof_authorized"] is True
    assert payload["candidate_path_metadata"] == str(fixture.resolve())
    assert payload["candidate_safety"]["candidate_safe_for_l21_5_metadata_only_proof"] is True
    result = payload["archive_metadata_validation_result"]
    assert result["archive_metadata_validation_performed"] is True
    assert result["archive_validation_ready"] is True
    assert result["downloaded_archive_opened"] is True
    assert result["downloaded_archive_contents_listed"] is True
    assert result["archive_entry_count"] >= 3
    assert result["manifest_entry_detected_from_listing"] is True
    assert "manifest.json" in result["archive_entry_names"]
    assert result["downloaded_archive_extracted"] is False
    assert result["downloaded_manifest_read"] is False
    assert result["archive_member_bytes_read"] is False
    assert payload["archive_validation_performed"] is True
    assert payload["downloaded_archive_opened"] is True
    assert payload["downloaded_archive_contents_listed"] is True
    assert payload["downloaded_archive_extracted"] is False
    assert payload["downloaded_manifest_read"] is False
    assert payload["archive_member_bytes_read"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["downloaded_file_stat_performed"] is False
    assert payload["downloaded_file_hash_performed"] is False
    _assert_blocked(payload)


def test_l21_05_wrong_token_does_not_open_archive() -> None:
    _ensure_fixture()
    payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(
        PROJECT_ROOT,
        allow_archive_metadata_proof=True,
        authorization_token="wrong-token",
        candidate_path_metadata=FIXTURE_REL,
    )
    assert payload["ok"] is True
    assert payload["archive_metadata_proof_requested"] is True
    assert payload["archive_metadata_proof_authorization_token_present"] is False
    assert payload["archive_metadata_proof_authorized"] is False
    assert payload["archive_metadata_validation_result"]["archive_metadata_validation_performed"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["downloaded_archive_contents_listed"] is False
    _assert_blocked(payload)


def test_l21_05_rejects_unsafe_candidate_without_archive_access() -> None:
    _ensure_fixture()
    payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(
        PROJECT_ROOT,
        allow_archive_metadata_proof=True,
        authorization_token=TOKEN,
        candidate_path_metadata="docs/not_a_patchops_bundle.txt",
    )
    assert payload["ok"] is False
    assert payload["candidate_safety"]["candidate_safe_for_l21_5_metadata_only_proof"] is False
    assert payload["archive_metadata_proof_authorized"] is False
    assert payload["archive_metadata_validation_result"]["archive_metadata_validation_performed"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["downloaded_archive_contents_listed"] is False
    _assert_blocked(payload)


def test_l21_05_cli_default_and_authorized_compact_json_smokes() -> None:
    _ensure_fixture()
    default_completed = subprocess.run(
        [
            sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND,
            "--repo-root", str(PROJECT_ROOT), "--target-url", "https://chatgpt.com/",
            "--json", "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert default_completed.returncode == 0, default_completed.stderr
    default_payload = json.loads(default_completed.stdout)
    assert default_payload["ok"] is True
    assert default_payload["patch"] == "L21.5"
    assert default_payload["archive_metadata_proof_authorized"] is False
    assert default_payload["downloaded_archive_opened"] is False
    _assert_blocked(default_payload)

    authorized_completed = subprocess.run(
        [
            sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND,
            "--repo-root", str(PROJECT_ROOT), "--target-url", "https://chatgpt.com/",
            "--allow-archive-metadata-proof", "--authorization-token", TOKEN,
            "--candidate-path-metadata", FIXTURE_REL,
            "--json", "--compact",
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
    assert authorized_payload["patch"] == "L21.5"
    assert authorized_payload["archive_metadata_proof_authorized"] is True
    assert authorized_payload["downloaded_archive_opened"] is True
    assert authorized_payload["downloaded_archive_contents_listed"] is True
    assert authorized_payload["downloaded_archive_extracted"] is False
    assert authorized_payload["downloaded_manifest_read"] is False
    assert authorized_payload["archive_member_bytes_read"] is False
    assert authorized_payload["downloaded_file_bytes_read"] is False
    assert authorized_payload["browser_started"] is False
    assert authorized_payload["edge_process_started"] is False
    _assert_blocked(authorized_payload)


def test_l21_05_rejects_disallowed_target_url_without_archive_access() -> None:
    _ensure_fixture()
    payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(
        PROJECT_ROOT,
        target_url="http://example.test/",
        allow_archive_metadata_proof=True,
        authorization_token=TOKEN,
        candidate_path_metadata=FIXTURE_REL,
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l21_4_controlled_authorization_gate_accepted"] is False
    assert payload["archive_metadata_proof_authorized"] is False
    assert payload["downloaded_archive_opened"] is False
    _assert_blocked(payload)


def test_l21_05_command_registered() -> None:
    from patchops.llm_browser import commands
    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l21_05_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_validation_metadata_proof.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L21.5 Microsoft Edge first controlled downloaded-archive validation proof",
        COMMAND,
        SOURCE_COMMAND,
        "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY",
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "first controlled downloaded-archive validation proof",
        "archive metadata-only validation proof",
        "synthetic PatchOps runtime archive fixture only",
        "L21.4 controlled authorization gate remains accepted",
        "explicit L21.5 archive metadata proof authorization token",
        "controlled archive validation execution is limited to metadata-only proof",
        "downloaded archive may be opened only for metadata listing of the explicit synthetic fixture",
        "downloaded archive contents may be listed as metadata only",
        "downloaded archive is not extracted",
        "downloaded manifest is not read",
        "archive member bytes are not read",
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
        "L21.6 Microsoft Edge downloaded-archive validation broad checkpoint",
    ]:
        assert phrase in text
