from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate as l22_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = 'browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate'
SOURCE_COMMAND = 'browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair'
TOKEN = 'PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY'
FALSE_FIELDS = ('manifest_validation_execution_allowed','manifest_validation_active','manifest_validation_performed','downloaded_manifest_read','downloaded_archive_opened_for_manifest_validation','downloaded_archive_contents_listed_for_manifest_validation','downloaded_archive_extracted','archive_member_bytes_read','downloaded_file_bytes_read','downloaded_file_stat_performed','downloaded_file_hash_performed','browser_started','edge_process_started','chatgpt_url_opened','paste_performed','send_or_submit_performed','package_run_performed_by_adapter','selenium_imported_by_readback','cdp_used','git_commit_executed','git_push_executed')

def _assert_blocked(payload: dict) -> None:
    for field in FALSE_FIELDS:
        assert payload[field] is False, field

def test_l22_01_default_readback_is_passive() -> None:
    payload = l22_01.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate(PROJECT_ROOT)
    assert payload['ok'] is True
    assert payload['patch'] == 'L22.1'
    assert payload['source_patch'] == 'L21.7a'
    assert payload['command_name'] == COMMAND
    assert payload['source_command_name'] == SOURCE_COMMAND
    assert payload['source_l21_7a_archive_final_marker_repair_accepted'] is True
    assert payload['manifest_validation_preflight_requested'] is False
    assert payload['manifest_validation_preflight_authorized'] is False
    assert payload['manifest_validation_preflight_authorization_is_readback_only_in_l22_1'] is True
    assert payload['missing_commands'] == []
    assert payload['missing_doc_phrases'] == []
    assert payload['required_repo_paths']['ok'] is True
    assert payload['next_patch'] == 'L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint'
    _assert_blocked(payload)

def test_l22_01_authorized_readback_still_blocks_manifest_validation() -> None:
    payload = l22_01.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate(PROJECT_ROOT, allow_manifest_validation_preflight=True, authorization_token=TOKEN)
    assert payload['ok'] is True
    assert payload['manifest_validation_preflight_requested'] is True
    assert payload['manifest_validation_preflight_authorized'] is True
    assert payload['manifest_validation_preflight_readback']['manifest_validation_preflight_authorization_token_present'] is True
    assert payload['manifest_validation_execution_allowed'] is False
    assert payload['manifest_validation_active'] is False
    assert payload['manifest_validation_performed'] is False
    assert payload['downloaded_manifest_read'] is False
    assert payload['archive_member_bytes_read'] is False
    assert payload['downloaded_archive_extracted'] is False
    _assert_blocked(payload)

def test_l22_01_wrong_token_does_not_authorize() -> None:
    payload = l22_01.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate(PROJECT_ROOT, allow_manifest_validation_preflight=True, authorization_token='wrong-token')
    assert payload['ok'] is True
    assert payload['manifest_validation_preflight_requested'] is True
    assert payload['manifest_validation_preflight_authorized'] is False
    _assert_blocked(payload)

def test_l22_01_cli_default_and_authorized_compact_json_smokes() -> None:
    default_completed = subprocess.run([sys.executable, '-m', 'patchops.cli', 'llm-browser', COMMAND, '--repo-root', str(PROJECT_ROOT), '--target-url', 'https://chatgpt.com/', '--json', '--compact'], cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=30)
    assert default_completed.returncode == 0, default_completed.stderr
    default_payload = json.loads(default_completed.stdout)
    assert default_payload['ok'] is True
    assert default_payload['manifest_validation_preflight_authorized'] is False
    _assert_blocked(default_payload)
    authorized_completed = subprocess.run([sys.executable, '-m', 'patchops.cli', 'llm-browser', COMMAND, '--repo-root', str(PROJECT_ROOT), '--target-url', 'https://chatgpt.com/', '--allow-manifest-validation-preflight', '--authorization-token', TOKEN, '--json', '--compact'], cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=30)
    assert authorized_completed.returncode == 0, authorized_completed.stderr
    assert len(authorized_completed.stdout) < 90000
    authorized_payload = json.loads(authorized_completed.stdout)
    assert authorized_payload['ok'] is True
    assert authorized_payload['patch'] == 'L22.1'
    assert authorized_payload['manifest_validation_preflight_authorized'] is True
    assert authorized_payload['manifest_validation_execution_allowed'] is False
    assert authorized_payload['downloaded_manifest_read'] is False
    assert authorized_payload['archive_member_bytes_read'] is False
    assert authorized_payload['package_run_performed_by_adapter'] is False
    _assert_blocked(authorized_payload)

def test_l22_01_rejects_disallowed_target_url_without_manifest_access() -> None:
    payload = l22_01.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate(PROJECT_ROOT, target_url='http://example.test/', allow_manifest_validation_preflight=True, authorization_token=TOKEN)
    assert payload['ok'] is False
    assert payload['target_url_allowed'] is False
    assert payload['source_l21_7a_archive_final_marker_repair_accepted'] is False
    assert payload['manifest_validation_preflight_authorized'] is True
    _assert_blocked(payload)

def test_l22_01_command_registered() -> None:
    from patchops.llm_browser import commands
    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names

def test_l22_01_doc_mentions_safety_contract() -> None:
    text = (PROJECT_ROOT / 'docs' / 'llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate.md').read_text(encoding='utf-8')
    for phrase in ['L22.1 Microsoft Edge downloaded-archive manifest validation passive preflight gate', COMMAND, SOURCE_COMMAND, TOKEN, 'Microsoft Edge first','Opera second','downloaded-archive manifest validation passive preflight gate','manifest validation preflight authorization is readback-only','L21.7a archive final marker repair remains accepted','L21 completion means metadata-only listing of the synthetic archive fixture','manifest validation execution allowed: false','manifest validation active: false','manifest validation is not performed','downloaded manifest is not read','downloaded archive is not extracted','archive member bytes are not read','downloaded archive may not be opened for manifest validation in L22.1','downloaded archive contents are not listed for manifest validation in L22.1','downloaded file bytes are not read','downloaded file stat is not performed','downloaded file hash is not performed','package-run from browser remains inactive','pasteback remains inactive','download workflow remains inactive','real browser download remains inactive','PatchOps remains source of truth','target URL allowlist remains enforced','ChatGPT URL may be selected but not opened','dedicated Microsoft Edge runtime profile remains required for future live phases','never use the default Microsoft Edge profile','no Microsoft Edge start','no Selenium import','no CDP use','no DOM scraping','no prompt text extraction','no conversation reading','no artifact content reading','no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect','no localhost PatchOps server','no browser extension','no git commit or git push','L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint']:
        assert phrase in text
