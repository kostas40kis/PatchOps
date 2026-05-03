from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair as l21_07a
PROJECT_ROOT=Path(__file__).resolve().parents[1]
COMMAND='browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair'
SOURCE='browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint-repair'
BLOCKED=('downloaded_archive_extracted','downloaded_manifest_read','archive_member_bytes_read','downloaded_file_bytes_read','downloaded_file_stat_performed','downloaded_file_hash_performed','browser_started','edge_process_started','chatgpt_url_opened','paste_performed','send_or_submit_performed','package_run_performed_by_adapter','selenium_imported_by_readback','cdp_used','git_commit_executed','git_push_executed')
def _assert_blocked(p):
    for f in BLOCKED: assert p[f] is False, f

def test_l21_07a_builds_final_acceptance_marker_repair():
    p=l21_07a.build_edge_downloaded_archive_validation_final_acceptance_marker_repair(PROJECT_ROOT)
    assert p['ok'] is True
    assert p['patch']=='L21.7a'
    assert p['source_patch']=='L21.6a'
    assert p['source_l21_6a_broad_checkpoint_repair_accepted'] is True
    assert p['l21_1_through_l21_6a_remain_accepted'] is True
    assert p['l21_downloaded_archive_validation_stream_complete'] is True
    assert p['l21_completion_means_metadata_only_synthetic_archive_listing'] is True
    assert p['metadata_only_archive_listing_remains_accepted'] is True
    assert p['archive_validation_scope']=='metadata_only_synthetic_patchops_runtime_archive_fixture'
    assert p['downloaded_archive_opened'] is True
    assert p['downloaded_archive_contents_listed'] is True
    assert p['archive_entry_count'] >= 1
    assert p['archive_extraction_remains_separate_future_stream'] is True
    assert p['manifest_read_remains_separate_future_stream'] is True
    assert p['archive_member_byte_read_remains_separate_future_stream'] is True
    assert p['package_run_from_browser_remains_separate_future_stream'] is True
    assert p['missing_commands'] == []
    assert p['missing_doc_phrases'] == []
    assert p['required_repo_paths']['ok'] is True
    assert p['remaining_l21_patches'] == []
    assert p['next_patch']=='L22.1 Microsoft Edge downloaded-archive manifest validation passive preflight gate'
    _assert_blocked(p)

def test_l21_07a_source_summary_is_compact():
    p=l21_07a.build_edge_downloaded_archive_validation_final_acceptance_marker_repair(PROJECT_ROOT)
    s=p['source_l21_6a_summary']
    assert s['ok'] is True
    assert s['patch'] in {'L21.6a','L21.6'}
    assert s['downloaded_archive_extracted'] is False
    assert s['downloaded_manifest_read'] is False
    assert s['archive_member_bytes_read'] is False
    assert s['downloaded_file_bytes_read'] is False
    assert s['browser_started'] is False
    assert s['edge_process_started'] is False
    assert s['package_run_performed_by_adapter'] is False

def test_l21_07a_cli_compact_json_smoke():
    cp=subprocess.run([sys.executable,'-m','patchops.cli','llm-browser',COMMAND,'--repo-root',str(PROJECT_ROOT),'--target-url','https://chatgpt.com/','--json','--compact'],cwd=PROJECT_ROOT,text=True,capture_output=True,timeout=30)
    assert cp.returncode==0, cp.stderr
    assert len(cp.stdout)<90000
    p=json.loads(cp.stdout)
    assert p['ok'] is True and p['patch']=='L21.7a'
    assert p['l21_downloaded_archive_validation_stream_complete'] is True
    assert p['downloaded_archive_opened'] is True
    assert p['downloaded_archive_contents_listed'] is True
    _assert_blocked(p)

def test_l21_07a_rejects_disallowed_target_url_without_side_effects():
    p=l21_07a.build_edge_downloaded_archive_validation_final_acceptance_marker_repair(PROJECT_ROOT,target_url='http://example.test/')
    assert p['ok'] is False
    assert p['target_url_allowed'] is False
    assert p['browser_started'] is False
    assert p['edge_process_started'] is False
    assert p['package_run_performed_by_adapter'] is False
    _assert_blocked(p)

def test_l21_07a_command_registered():
    from patchops.llm_browser import commands
    names=tuple(commands.llm_browser_command_names())
    assert SOURCE in names
    assert COMMAND in names

def test_l21_07a_doc_mentions_safety_contract():
    text=(PROJECT_ROOT/'docs'/'llm_browser_live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair.md').read_text(encoding='utf-8')
    for phrase in ['L21.7a Microsoft Edge downloaded-archive validation final acceptance marker repair',COMMAND,SOURCE,'L21.6a archive broad checkpoint repair remains accepted','L21 downloaded-archive validation stream complete','L21 completion means metadata-only listing of the synthetic archive fixture','downloaded archive may be opened only for metadata listing of the synthetic fixture','downloaded archive is not extracted','downloaded manifest is not read','archive member bytes are not read','archive extraction remains a separate future stream','manifest read remains a separate future stream','no Microsoft Edge start','no package-run from browser','L22.1 Microsoft Edge downloaded-archive manifest validation passive preflight gate']:
        assert phrase in text
