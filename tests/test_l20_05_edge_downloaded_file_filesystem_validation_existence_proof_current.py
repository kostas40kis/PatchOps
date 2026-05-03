from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_existence_proof as l20_05

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-existence-proof"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-controlled-authorization-gate"
TOKEN = "PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_EXISTENCE_PROOF_AUTHORIZED"
FIXTURE_REL = "data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip"

SAFETY_FALSE_FIELDS = (
    "real_file_stat_performed",
    "real_file_hash_performed",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "downloaded_file_bytes_read",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
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
        fixture.write_text("L20.5 synthetic existence-only fixture. Do not read contents.\n", encoding="utf-8")
    return fixture


def _assert_no_forbidden_side_effects(payload: dict) -> None:
    for field in SAFETY_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l20_05_default_readback_is_passive() -> None:
    _ensure_fixture()
    payload = l20_05.build_edge_downloaded_file_filesystem_validation_existence_proof(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L20.5"
    assert payload["source_patch"] == "L20.4"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l20_4_controlled_authorization_gate_accepted"] is True
    assert payload["l20_4_complete"] is True
    assert payload["filesystem_validation_authorized_by_l20_4_for_future_phase"] is True
    assert payload["filesystem_existence_proof_requested"] is False
    assert payload["filesystem_existence_proof_authorized"] is False
    assert payload["filesystem_validation_performed"] is False
    assert payload["real_file_exists_check_performed"] is False
    assert payload["downloaded_file_exists_check_performed"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L20.6 Microsoft Edge downloaded-file filesystem validation broad checkpoint"
    _assert_no_forbidden_side_effects(payload)


def test_l20_05_authorized_existence_only_proof_checks_fixture_exists() -> None:
    fixture = _ensure_fixture()
    payload = l20_05.build_edge_downloaded_file_filesystem_validation_existence_proof(
        PROJECT_ROOT,
        allow_filesystem_existence_proof=True,
        authorization_token=TOKEN,
        candidate_path_metadata=FIXTURE_REL,
    )

    assert payload["ok"] is True
    assert payload["filesystem_existence_proof_requested"] is True
    assert payload["filesystem_existence_proof_authorization_token_present"] is True
    assert payload["filesystem_existence_proof_authorized"] is True
    assert payload["candidate_path_metadata"] == str(fixture.resolve())
    assert payload["candidate_safety"]["candidate_safe_for_l20_5_existence_only_proof"] is True
    result = payload["existence_validation_result"]
    assert result["existence_only_validation_performed"] is True
    assert result["candidate_exists"] is True
    assert result["candidate_validation_ready"] is True
    assert result["blocking_reasons"] == []
    assert payload["filesystem_validation_performed"] is True
    assert payload["real_file_exists_check_performed"] is True
    assert payload["downloaded_file_exists_check_performed"] is True
    assert payload["real_file_stat_performed"] is False
    assert payload["real_file_hash_performed"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["downloaded_manifest_read"] is False
    _assert_no_forbidden_side_effects(payload)


def test_l20_05_wrong_token_does_not_check_existence() -> None:
    _ensure_fixture()
    payload = l20_05.build_edge_downloaded_file_filesystem_validation_existence_proof(
        PROJECT_ROOT,
        allow_filesystem_existence_proof=True,
        authorization_token="wrong-token",
        candidate_path_metadata=FIXTURE_REL,
    )
    assert payload["ok"] is True
    assert payload["filesystem_existence_proof_requested"] is True
    assert payload["filesystem_existence_proof_authorization_token_present"] is False
    assert payload["filesystem_existence_proof_authorized"] is False
    assert payload["existence_validation_result"]["existence_only_validation_performed"] is False
    assert payload["real_file_exists_check_performed"] is False
    assert payload["downloaded_file_exists_check_performed"] is False
    _assert_no_forbidden_side_effects(payload)


def test_l20_05_rejects_unsafe_candidate_without_existence_check() -> None:
    _ensure_fixture()
    payload = l20_05.build_edge_downloaded_file_filesystem_validation_existence_proof(
        PROJECT_ROOT,
        allow_filesystem_existence_proof=True,
        authorization_token=TOKEN,
        candidate_path_metadata="docs/not_a_patchops_bundle.txt",
    )
    assert payload["ok"] is False
    assert payload["candidate_safety"]["candidate_safe_for_l20_5_existence_only_proof"] is False
    assert payload["filesystem_existence_proof_authorized"] is False
    assert payload["existence_validation_result"]["existence_only_validation_performed"] is False
    assert payload["real_file_exists_check_performed"] is False
    assert payload["downloaded_file_exists_check_performed"] is False
    _assert_no_forbidden_side_effects(payload)


def test_l20_05_cli_default_and_authorized_compact_json_smokes() -> None:
    _ensure_fixture()
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
    assert default_payload["patch"] == "L20.5"
    assert default_payload["filesystem_existence_proof_authorized"] is False
    assert default_payload["real_file_exists_check_performed"] is False
    _assert_no_forbidden_side_effects(default_payload)

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
            "--allow-filesystem-existence-proof",
            "--authorization-token",
            TOKEN,
            "--candidate-path-metadata",
            FIXTURE_REL,
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
    assert authorized_payload["patch"] == "L20.5"
    assert authorized_payload["filesystem_existence_proof_authorized"] is True
    assert authorized_payload["existence_validation_result"]["candidate_exists"] is True
    assert authorized_payload["real_file_exists_check_performed"] is True
    assert authorized_payload["downloaded_file_exists_check_performed"] is True
    assert authorized_payload["real_file_stat_performed"] is False
    assert authorized_payload["downloaded_file_bytes_read"] is False
    assert authorized_payload["downloaded_archive_opened"] is False
    assert authorized_payload["browser_started"] is False
    assert authorized_payload["edge_process_started"] is False
    _assert_no_forbidden_side_effects(authorized_payload)


def test_l20_05_rejects_disallowed_target_url_without_existence_check() -> None:
    _ensure_fixture()
    payload = l20_05.build_edge_downloaded_file_filesystem_validation_existence_proof(
        PROJECT_ROOT,
        target_url="http://example.test/",
        allow_filesystem_existence_proof=True,
        authorization_token=TOKEN,
        candidate_path_metadata=FIXTURE_REL,
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l20_4_controlled_authorization_gate_accepted"] is False
    assert payload["filesystem_existence_proof_authorized"] is False
    assert payload["real_file_exists_check_performed"] is False
    _assert_no_forbidden_side_effects(payload)


def test_l20_05_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l20_05_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_existence_proof.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L20.5 Microsoft Edge first controlled downloaded-file filesystem validation proof",
        COMMAND,
        SOURCE_COMMAND,
        "PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY",
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "first controlled downloaded-file filesystem validation proof",
        "existence-only filesystem validation proof",
        "synthetic PatchOps runtime fixture only",
        "L20.4 controlled authorization gate remains accepted",
        "explicit L20.5 existence proof authorization token",
        "controlled filesystem validation execution is limited to existence-only proof",
        "real file existence check may be performed only against the explicit synthetic fixture",
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
        "L20.6 Microsoft Edge downloaded-file filesystem validation broad checkpoint",
    ]:
        assert phrase in text
