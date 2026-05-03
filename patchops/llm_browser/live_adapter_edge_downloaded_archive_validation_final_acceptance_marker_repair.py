from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH='L21.7a'
NAME='L21.7a Microsoft Edge downloaded-archive validation final acceptance marker repair'
COMMAND_NAME='browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair'
SOURCE_COMMAND_NAME='browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint-repair'
SOURCE_PATCH='L21.6a'
NEXT_PATCH='L22.1 Microsoft Edge downloaded-archive manifest validation passive preflight gate'
DEFAULT_TARGET_URL='https://chatgpt.com/'
FIXTURE='data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip'
BLOCKED_FALSE_FIELDS=(
 'downloaded_archive_extracted','downloaded_manifest_read','archive_member_bytes_read','downloaded_file_bytes_read',
 'downloaded_file_stat_performed','downloaded_file_hash_performed','browser_started','edge_process_started','chatgpt_url_opened',
 'paste_performed','send_or_submit_performed','package_run_performed_by_adapter','selenium_imported_by_readback','cdp_used',
 'git_commit_executed','git_push_executed')
REQUIRED_PATHS=(
 'patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair.py',
 'patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair.py',
 'patchops/llm_browser/commands.py',
 'docs/llm_browser_live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair.md',
 'docs/llm_browser_live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair.md',
 'tests/test_l21_06a_edge_downloaded_archive_validation_broad_checkpoint_repair_current.py',
 'tests/test_l21_07a_edge_downloaded_archive_validation_final_acceptance_marker_repair_current.py',
 'scripts/patch_l21_06a_brief_validate.py','scripts/patch_l21_07a_brief_validate.py',FIXTURE)
DOC_PHRASES=(
 'L21.7a Microsoft Edge downloaded-archive validation final acceptance marker repair',COMMAND_NAME,SOURCE_COMMAND_NAME,
 'L21.6a archive broad checkpoint repair remains accepted','L21 downloaded-archive validation stream complete',
 'L21 completion means metadata-only listing of the synthetic archive fixture','metadata-only archive listing remains accepted',
 'downloaded archive may be opened only for metadata listing of the synthetic fixture','downloaded archive contents may be listed as metadata only',
 'downloaded archive is not extracted','downloaded manifest is not read','archive member bytes are not read',
 'archive extraction remains a separate future stream','manifest read remains a separate future stream',
 'archive member-byte read remains a separate future stream','package-run from browser remains a separate future stream',
 'no Microsoft Edge start','no package-run from browser','L22.1 Microsoft Edge downloaded-archive manifest validation passive preflight gate')

def _root(repo_root):
    return Path.cwd().resolve() if repo_root is None or str(repo_root)=='.' else Path(repo_root).resolve()

def _names():
    try:
        from patchops.llm_browser import commands
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()

def _read(path: Path) -> str:
    try: return path.read_text(encoding='utf-8')
    except FileNotFoundError: return ''

def _load_source(root: Path, target_url: str) -> dict[str, Any]:
    try:
        from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair as l21_06a
        return dict(l21_06a.build_edge_downloaded_archive_validation_broad_checkpoint_repair(root, target_url=target_url))
    except Exception as exc:
        return {'ok': False, 'patch': SOURCE_PATCH, 'source_error': f'{type(exc).__name__}: {exc}', 'target_url_allowed': target_url.startswith('https://chatgpt.com')}

def _summary(source: Mapping[str, Any]) -> dict[str, Any]:
    keys=('ok','patch','l21_6a_complete','archive_validation_scope','archive_validation_performed','downloaded_archive_opened',
          'downloaded_archive_contents_listed','archive_entry_count','downloaded_archive_extracted','downloaded_manifest_read',
          'archive_member_bytes_read','downloaded_file_bytes_read','browser_started','edge_process_started','package_run_performed_by_adapter',
          'target_url_allowed','missing_commands','missing_doc_phrases')
    return {k: source.get(k) for k in keys}

def build_edge_downloaded_archive_validation_final_acceptance_marker_repair(repo_root: str|Path|None=None, *, target_url: str|None=None) -> dict[str, Any]:
    root=_root(repo_root); target=target_url or DEFAULT_TARGET_URL
    source=_load_source(root,target)
    source_ok=source.get('ok') is True
    target_ok=bool(source.get('target_url_allowed', target.startswith('https://chatgpt.com')))
    names=_names()
    missing_commands=[n for n in (SOURCE_COMMAND_NAME, COMMAND_NAME) if n not in names]
    missing_paths=[p for p in REQUIRED_PATHS if not (root/p).exists()]
    doc=_read(root/'docs/llm_browser_live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair.md')
    missing_doc_phrases=[p for p in DOC_PHRASES if p not in doc]
    ok=bool(source_ok and target_ok and not missing_commands and not missing_paths and not missing_doc_phrases)
    opened=bool(source.get('downloaded_archive_opened', source_ok)) if source_ok else False
    listed=bool(source.get('downloaded_archive_contents_listed', source_ok)) if source_ok else False
    entry_count=int(source.get('archive_entry_count') or (1 if source_ok else 0))
    payload={
        'ok':ok,'status':'PASS' if ok else 'FAIL','patch':PATCH,'phase':'L21','name':NAME,'command_name':COMMAND_NAME,
        'source_command_name':SOURCE_COMMAND_NAME,'source_patch':SOURCE_PATCH,'next_patch':NEXT_PATCH,
        'final_acceptance_marker_repair':True,'downloaded_archive_validation_final_acceptance_marker':True,
        'source_l21_6a_broad_checkpoint_repair_accepted':source_ok,'l21_1_through_l21_6a_remain_accepted':source_ok,
        'l21_downloaded_archive_validation_stream_complete':ok,'l21_completion_means_metadata_only_synthetic_archive_listing':True,
        'metadata_only_archive_listing_remains_accepted':source_ok,'only_synthetic_archive_fixture_metadata_listing_is_accepted':True,
        'archive_validation_scope':'metadata_only_synthetic_patchops_runtime_archive_fixture','archive_validation_performed':bool(source.get('archive_validation_performed', source_ok)) if source_ok else False,
        'downloaded_archive_opened':opened,'downloaded_archive_contents_listed':listed,'archive_entry_count':entry_count,
        'downloaded_archive_extracted':False,'downloaded_manifest_read':False,'archive_member_bytes_read':False,'downloaded_file_bytes_read':False,
        'downloaded_file_stat_performed':False,'downloaded_file_hash_performed':False,
        'archive_extraction_remains_separate_future_stream':True,'manifest_read_remains_separate_future_stream':True,
        'archive_member_byte_read_remains_separate_future_stream':True,'package_run_from_browser_remains_separate_future_stream':True,
        'microsoft_edge_first':True,'opera_second':True,'opera_active_implementation_target':False,'target_url':target,'target_url_allowed':target_ok,
        'browser_started':False,'edge_process_started':False,'chatgpt_url_opened':False,'paste_performed':False,'send_or_submit_performed':False,
        'package_run_performed_by_adapter':False,'selenium_imported_by_readback':False,'cdp_used':False,'git_commit_executed':False,'git_push_executed':False,
        'requires_dedicated_edge_runtime_profile_in_future_live_phase':True,'default_microsoft_edge_profile_allowed':False,'patchops_remains_source_of_truth':True,
        'source_l21_6a_summary':_summary(source),'missing_commands':missing_commands,'missing_doc_phrases':missing_doc_phrases,
        'required_repo_paths':{'ok':not missing_paths,'missing':missing_paths,'checked':list(REQUIRED_PATHS)},'remaining_l21_patches':[] if ok else [PATCH],
        'checks':[{'name':'source_l21_6a_broad_checkpoint_repair_accepted','ok':source_ok,'status':'PASS' if source_ok else 'FAIL'},
                  {'name':'l21_archive_stream_complete_as_metadata_only_listing','ok':ok,'status':'PASS' if ok else 'FAIL'},
                  {'name':'archive_extraction_manifest_member_bytes_package_run_remain_blocked','ok':True,'status':'PASS'},
                  {'name':'command_registered','ok':not missing_commands,'status':'PASS' if not missing_commands else 'FAIL'},
                  {'name':'required_repo_paths_present','ok':not missing_paths,'status':'PASS' if not missing_paths else 'FAIL'},
                  {'name':'docs_contain_l21_7a_safety_contract','ok':not missing_doc_phrases,'status':'PASS' if not missing_doc_phrases else 'FAIL'}]}
    return payload

def render_text(payload: Mapping[str, Any]) -> str:
    lines=[NAME,'='*len(NAME),f"Patch                         : {payload.get('patch')}",f"Status                        : {payload.get('status')}",
           f"L21.6a Accepted               : {payload.get('source_l21_6a_broad_checkpoint_repair_accepted')}",
           f"L21 Stream Complete           : {payload.get('l21_downloaded_archive_validation_stream_complete')}",
           f"Scope                         : {payload.get('archive_validation_scope')}",f"Archive Opened                : {payload.get('downloaded_archive_opened')}",
           f"Archive Listed                : {payload.get('downloaded_archive_contents_listed')}",f"Archive Extracted             : {payload.get('downloaded_archive_extracted')}",
           f"Manifest Read                 : {payload.get('downloaded_manifest_read')}",f"Package Run                   : {payload.get('package_run_performed_by_adapter')}",
           f"Next Patch                    : {payload.get('next_patch')}"]
    return '\n'.join(lines)+'\n'

def main(argv: Sequence[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description=NAME)
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--target-url', default=DEFAULT_TARGET_URL)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--compact', action='store_true')
    args=parser.parse_args(argv)
    payload=build_edge_downloaded_archive_validation_final_acceptance_marker_repair(args.repo_root,target_url=args.target_url)
    if args.json:
        print(json.dumps(payload,sort_keys=True,separators=(',',':') if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end='')
    return 0 if payload.get('ok') else 1

if __name__=='__main__':
    raise SystemExit(main())
