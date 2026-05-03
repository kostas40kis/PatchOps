from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair as l21_06a
PROJECT_ROOT=Path(__file__).resolve().parents[1]
COMMAND='browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint-repair'
SOURCE='browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof'
BLOCKED=('downloaded_archive_extracted','downloaded_manifest_read','archive_member_bytes_read','downloaded_file_bytes_read','downloaded_file_stat_performed','downloaded_file_hash_performed','browser_started','edge_process_started','chatgpt_url_opened','paste_performed','send_or_submit_performed','package_run_performed_by_adapter','selenium_imported_by_readback','cdp_used','git_commit_executed','git_push_executed')
def _blocked(p):
    for k in BLOCKED: assert p[k] is False, k

def test_l21_06a_builds_repaired_broad_checkpoint():
    p=l21_06a.build_edge_downloaded_archive_validation_broad_checkpoint_repair(PROJECT_ROOT)
    assert p['ok'] is True
    assert p['patch']=='L21.6a'
    assert p['l21_5_metadata_only_archive_proof_remains_accepted'] is True
    assert p['default_archive_metadata_proof_readback_remains_passive'] is True
    assert p['authorized_archive_metadata_proof_readback_remains_metadata_only'] is True
    assert p['archive_validation_scope']=='metadata_only_synthetic_patchops_runtime_archive_fixture'
    assert p['archive_validation_performed'] is True
    assert p['downloaded_archive_opened'] is True
    assert p['downloaded_archive_contents_listed'] is True
    assert p['archive_entry_count'] >= 1
    assert p['missing_commands'] == []
    assert p['missing_doc_phrases'] == []
    assert p['required_repo_paths']['ok'] is True
    assert p['next_patch']=='L21.7 Microsoft Edge downloaded-archive validation final acceptance marker'
    _blocked(p)

def test_l21_06a_source_summaries_are_narrow():
    p=l21_06a.build_edge_downloaded_archive_validation_broad_checkpoint_repair(PROJECT_ROOT)
    d=p['source_default_summary']; a=p['source_authorized_summary']
    assert d['ok'] is True and d['archive_metadata_proof_authorized'] is False
    assert d['downloaded_archive_opened'] is False
    assert a['ok'] is True and a['archive_metadata_proof_authorized'] is True
    assert a['downloaded_archive_opened'] is True
    assert a['downloaded_archive_contents_listed'] is True
    assert a['archive_entry_count'] >= 1
    assert a['downloaded_archive_extracted'] is False
    assert a['downloaded_manifest_read'] is False
    assert a['archive_member_bytes_read'] is False
    assert a['package_run_performed_by_adapter'] is False

def test_l21_06a_cli_compact_json_smoke():
    cp=subprocess.run([sys.executable,'-m','patchops.cli','llm-browser',COMMAND,'--repo-root',str(PROJECT_ROOT),'--target-url','https://chatgpt.com/','--json','--compact'],cwd=PROJECT_ROOT,text=True,capture_output=True,timeout=30)
    assert cp.returncode==0, cp.stderr
    p=json.loads(cp.stdout)
    assert p['ok'] is True and p['patch']=='L21.6a'
    assert p['downloaded_archive_opened'] is True
    assert p['downloaded_archive_contents_listed'] is True
    _blocked(p)

def test_l21_06a_rejects_disallowed_target_url_without_browser_or_package_run():
    p=l21_06a.build_edge_downloaded_archive_validation_broad_checkpoint_repair(PROJECT_ROOT,target_url='http://example.test/')
    assert p['ok'] is False
    assert p['target_url_allowed'] is False
    assert p['browser_started'] is False
    assert p['edge_process_started'] is False
    assert p['package_run_performed_by_adapter'] is False
    _blocked(p)

def test_l21_06a_command_registered():
    from patchops.llm_browser import commands
    names=tuple(commands.llm_browser_command_names())
    assert SOURCE in names
    assert COMMAND in names

def test_l21_06a_doc_mentions_safety_contract():
    text=(PROJECT_ROOT/'docs'/'llm_browser_live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair.md').read_text(encoding='utf-8')
    for phrase in ['L21.6a Microsoft Edge downloaded-archive validation broad checkpoint repair',COMMAND,SOURCE,'L21.5 metadata-only archive proof remains accepted','metadata-only listing of the synthetic fixture','downloaded archive is not extracted','downloaded manifest is not read','archive member bytes are not read','no Microsoft Edge start','no package-run from browser','L21.7 Microsoft Edge downloaded-archive validation final acceptance marker']:
        assert phrase in text
