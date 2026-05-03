from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized as l22_01b

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND='browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate-stabilized'
TOKEN='PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY'
FALSE_FIELDS=(
 'manifest_validation_execution_allowed','manifest_validation_active','manifest_validation_performed','downloaded_manifest_read',
 'archive_member_bytes_read','downloaded_archive_opened','downloaded_archive_contents_listed','downloaded_archive_extracted',
 'downloaded_file_bytes_read','downloaded_file_stat_performed','downloaded_file_hash_performed','browser_started','edge_process_started',
 'chatgpt_url_opened','paste_performed','send_or_submit_performed','package_run_performed_by_adapter','selenium_imported_by_readback',
 'cdp_used','git_commit_executed','git_push_executed')

def _blocked(payload: dict) -> None:
    for field in FALSE_FIELDS:
        assert payload[field] is False, field

def test_l22_01b_default_readback_is_passive():
    p=l22_01b.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized(PROJECT_ROOT)
    assert p['ok'] is True
    assert p['patch']=='L22.1b'
    assert p['manifest_validation_preflight_authorized'] is False
    assert p['manifest_validation_preflight_authorization_is_readback_only_in_l22_1b'] is True
    assert p['missing_commands'] == []
    assert p['missing_doc_phrases'] == []
    assert p['required_repo_paths']['ok'] is True
    assert p['next_patch']=='L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint'
    _blocked(p)

def test_l22_01b_authorized_readback_still_does_not_read_manifest():
    p=l22_01b.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized(PROJECT_ROOT, allow_manifest_validation_preflight=True, authorization_token=TOKEN)
    assert p['ok'] is True
    assert p['manifest_validation_preflight_requested'] is True
    assert p['manifest_validation_preflight_authorized'] is True
    assert p['manifest_validation_execution_allowed'] is False
    assert p['downloaded_manifest_read'] is False
    assert p['archive_member_bytes_read'] is False
    assert p['downloaded_archive_opened'] is False
    _blocked(p)

def test_l22_01b_wrong_token_does_not_authorize():
    p=l22_01b.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized(PROJECT_ROOT, allow_manifest_validation_preflight=True, authorization_token='wrong')
    assert p['ok'] is True
    assert p['manifest_validation_preflight_requested'] is True
    assert p['manifest_validation_preflight_authorized'] is False
    _blocked(p)

def test_l22_01b_cli_default_and_authorized_smoke():
    default=subprocess.run([sys.executable,'-m','patchops.cli','llm-browser',COMMAND,'--repo-root',str(PROJECT_ROOT),'--target-url','https://chatgpt.com/','--json','--compact'],cwd=PROJECT_ROOT,text=True,capture_output=True,timeout=30)
    assert default.returncode==0, default.stderr
    p=json.loads(default.stdout)
    assert p['ok'] is True and p['patch']=='L22.1b'
    assert p['manifest_validation_preflight_authorized'] is False
    _blocked(p)
    auth=subprocess.run([sys.executable,'-m','patchops.cli','llm-browser',COMMAND,'--repo-root',str(PROJECT_ROOT),'--target-url','https://chatgpt.com/','--allow-manifest-validation-preflight','--authorization-token',TOKEN,'--json','--compact'],cwd=PROJECT_ROOT,text=True,capture_output=True,timeout=30)
    assert auth.returncode==0, auth.stderr
    assert len(auth.stdout)<90000
    p=json.loads(auth.stdout)
    assert p['ok'] is True and p['patch']=='L22.1b'
    assert p['manifest_validation_preflight_authorized'] is True
    assert p['downloaded_manifest_read'] is False
    _blocked(p)

def test_l22_01b_rejects_disallowed_target_url_without_side_effects():
    p=l22_01b.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized(PROJECT_ROOT, target_url='http://example.test/', allow_manifest_validation_preflight=True, authorization_token=TOKEN)
    assert p['ok'] is False
    assert p['target_url_allowed'] is False
    assert p['manifest_validation_preflight_authorized'] is True
    _blocked(p)

def test_l22_01b_command_registered():
    from patchops.llm_browser import commands
    assert COMMAND in tuple(commands.llm_browser_command_names())

def test_l22_01b_doc_mentions_safety_contract():
    text=(PROJECT_ROOT/'docs'/'llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized.md').read_text(encoding='utf-8')
    for phrase in ['L22.1b Microsoft Edge downloaded-archive manifest validation passive preflight stabilized repair', COMMAND, TOKEN, 'manifest validation passive preflight is readback-only', 'manifest validation execution allowed: false', 'downloaded manifest is not read', 'archive member bytes are not read', 'downloaded archive is not extracted', 'downloaded archive is not opened by L22.1b', 'no Microsoft Edge start', 'no Selenium import', 'no CDP use', 'no DOM scraping', 'no package-run from browser', 'L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint']:
        assert phrase in text
