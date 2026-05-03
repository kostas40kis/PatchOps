from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, Mapping, Sequence
from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_metadata_proof as l21_05

PATCH='L21.6a'
NAME='L21.6a Microsoft Edge downloaded-archive validation broad checkpoint repair'
COMMAND_NAME='browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint-repair'
SOURCE_COMMAND_NAME='browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof'
NEXT_PATCH='L21.7 Microsoft Edge downloaded-archive validation final acceptance marker'
DEFAULT_TARGET_URL='https://chatgpt.com/'
TOKEN='PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED'
FIXTURE='data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip'
BLOCKED=('downloaded_archive_extracted','downloaded_manifest_read','archive_member_bytes_read','downloaded_file_bytes_read','downloaded_file_stat_performed','downloaded_file_hash_performed','browser_started','edge_process_started','chatgpt_url_opened','paste_performed','send_or_submit_performed','package_run_performed_by_adapter','selenium_imported_by_readback','cdp_used','git_commit_executed','git_push_executed')
REQUIRED=(
 'patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_metadata_proof.py',
 'patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair.py',
 'patchops/llm_browser/commands.py',
 'docs/llm_browser_live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair.md',
 'tests/test_l21_06a_edge_downloaded_archive_validation_broad_checkpoint_repair_current.py',
 'scripts/patch_l21_06a_brief_validate.py',
 FIXTURE,
)
PHRASES=(
 'L21.6a Microsoft Edge downloaded-archive validation broad checkpoint repair',
 COMMAND_NAME,
 SOURCE_COMMAND_NAME,
 'L21.5 metadata-only archive proof remains accepted',
 'metadata-only listing of the synthetic fixture',
 'downloaded archive is not extracted',
 'downloaded manifest is not read',
 'archive member bytes are not read',
 'no Microsoft Edge start',
 'no package-run from browser',
 'L21.7 Microsoft Edge downloaded-archive validation final acceptance marker',
)

def _root(x):
    return Path.cwd().resolve() if x in (None,'.') else Path(x).resolve()

def _safe_false(payload: Mapping[str, Any]) -> bool:
    return all(payload.get(k) in (False, None) for k in BLOCKED)

def _names():
    try:
        from patchops.llm_browser import commands
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()

def _read(path: Path) -> str:
    try: return path.read_text(encoding='utf-8')
    except FileNotFoundError: return ''

def _summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    result=payload.get('archive_metadata_validation_result') or {}
    return {
        'ok':payload.get('ok'),'patch':payload.get('patch'),
        'archive_metadata_proof_authorized':payload.get('archive_metadata_proof_authorized'),
        'archive_validation_performed':payload.get('archive_validation_performed'),
        'downloaded_archive_opened':payload.get('downloaded_archive_opened'),
        'downloaded_archive_contents_listed':payload.get('downloaded_archive_contents_listed'),
        'archive_entry_count':result.get('archive_entry_count'),
        'archive_metadata_validation_performed':result.get('archive_metadata_validation_performed'),
        'archive_validation_ready':result.get('archive_validation_ready'),
        'downloaded_archive_extracted':payload.get('downloaded_archive_extracted'),
        'downloaded_manifest_read':payload.get('downloaded_manifest_read'),
        'archive_member_bytes_read':payload.get('archive_member_bytes_read'),
        'downloaded_file_bytes_read':payload.get('downloaded_file_bytes_read'),
        'browser_started':payload.get('browser_started'),
        'edge_process_started':payload.get('edge_process_started'),
        'package_run_performed_by_adapter':payload.get('package_run_performed_by_adapter'),
    }

def build_edge_downloaded_archive_validation_broad_checkpoint_repair(repo_root: str|Path|None=None, *, target_url: str|None=None) -> dict[str, Any]:
    root=_root(repo_root); target=target_url or DEFAULT_TARGET_URL
    default=l21_05.build_edge_downloaded_archive_validation_metadata_proof(root,target_url=target)
    auth=l21_05.build_edge_downloaded_archive_validation_metadata_proof(root,allow_archive_metadata_proof=True,authorization_token=TOKEN,candidate_path_metadata=FIXTURE,target_url=target)
    result=auth.get('archive_metadata_validation_result') or {}
    names=_names()
    missing_commands=[n for n in (SOURCE_COMMAND_NAME,COMMAND_NAME) if n not in names]
    missing_paths=[p for p in REQUIRED if not (root/p).exists()]
    doc=_read(root/'docs/llm_browser_live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair.md')
    missing_phrases=[p for p in PHRASES if p not in doc]
    default_ok=default.get('ok') is True and default.get('patch')=='L21.5' and default.get('archive_metadata_proof_authorized') is False and default.get('downloaded_archive_opened') is False and _safe_false(default)
    auth_ok=auth.get('ok') is True and auth.get('patch')=='L21.5' and auth.get('archive_metadata_proof_authorized') is True and auth.get('archive_validation_performed') is True and auth.get('downloaded_archive_opened') is True and auth.get('downloaded_archive_contents_listed') is True and (result.get('archive_entry_count') or 0)>=1 and _safe_false(auth)
    target_ok=bool(auth.get('target_url_allowed'))
    ok=default_ok and auth_ok and target_ok and not missing_commands and not missing_paths and not missing_phrases
    payload={
      'ok':ok,'status':'PASS' if ok else 'FAIL','patch':PATCH,'phase':'L21','name':NAME,
      'command_name':COMMAND_NAME,'source_command_name':SOURCE_COMMAND_NAME,'source_patch':'L21.5','next_patch':NEXT_PATCH,
      'l21_5_metadata_only_archive_proof_remains_accepted':default_ok and auth_ok,
      'default_archive_metadata_proof_readback_remains_passive':default_ok,
      'authorized_archive_metadata_proof_readback_remains_metadata_only':auth_ok,
      'archive_validation_scope':'metadata_only_synthetic_patchops_runtime_archive_fixture',
      'archive_validation_performed': bool(auth.get('archive_validation_performed')) if auth_ok else False,
      'downloaded_archive_opened': bool(auth.get('downloaded_archive_opened')) if auth_ok else False,
      'downloaded_archive_contents_listed': bool(auth.get('downloaded_archive_contents_listed')) if auth_ok else False,
      'archive_entry_count': result.get('archive_entry_count',0) if auth_ok else 0,
      'metadata_only_listing_of_synthetic_fixture': True,
      'microsoft_edge_first': True,'opera_second': True,'opera_active_implementation_target': False,
      'target_url':target,'target_url_allowed':target_ok,
      'source_default_summary':_summary(default),'source_authorized_summary':_summary(auth),
      'missing_commands':missing_commands,'missing_doc_phrases':missing_phrases,
      'required_repo_paths':{'ok':not missing_paths,'missing':missing_paths,'checked':list(REQUIRED)},
      'l21_6a_complete':ok,'remaining_l21_6a_patches':[] if ok else [PATCH],
      'checks':[
        {'name':'default_readback_passive','ok':default_ok,'status':'PASS' if default_ok else 'FAIL'},
        {'name':'authorized_readback_metadata_only','ok':auth_ok,'status':'PASS' if auth_ok else 'FAIL'},
        {'name':'commands_registered','ok':not missing_commands,'status':'PASS' if not missing_commands else 'FAIL'},
        {'name':'docs_and_paths_present','ok':not missing_paths and not missing_phrases,'status':'PASS' if not missing_paths and not missing_phrases else 'FAIL'},
      ],
    }
    for k in BLOCKED:
        payload[k]=False
    payload.update({
      'download_workflow_active':False,'download_performed':False,'click_download_performed':False,
      'artifact_content_reading_performed':False,'pasteback_workflow_active':False,
      'launch_execution_allowed':False,'browser_process_launch_requested':False,
      'patchops_remains_source_of_truth':True,'default_microsoft_edge_profile_allowed':False,
      'requires_dedicated_edge_runtime_profile_in_future_live_phase':True,
      'real_browser_download_remains_inactive':True,'pasteback_remains_inactive':True,
      'package_run_from_browser_remains_inactive':True,
    })
    return payload

def render_text(payload: Mapping[str, Any]) -> str:
    return '\n'.join([
      NAME,'='*len(NAME),f"Patch : {payload.get('patch')}",f"Status: {payload.get('status')}",
      f"L21.5 Accepted: {payload.get('l21_5_metadata_only_archive_proof_remains_accepted')}",
      f"Archive Scope: {payload.get('archive_validation_scope')}",
      f"Archive Opened: {payload.get('downloaded_archive_opened')}",
      f"Archive Contents Listed: {payload.get('downloaded_archive_contents_listed')}",
      f"Archive Extracted: {payload.get('downloaded_archive_extracted')}",
      f"Manifest Read: {payload.get('downloaded_manifest_read')}",
      f"Member Bytes Read: {payload.get('archive_member_bytes_read')}",
      f"Browser Started: {payload.get('browser_started')}",
      f"Next Patch: {payload.get('next_patch')}",
    ])+'\n'

def main(argv: Sequence[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description=NAME)
    parser.add_argument('--repo-root',default='.')
    parser.add_argument('--target-url',default=DEFAULT_TARGET_URL)
    parser.add_argument('--json',action='store_true')
    parser.add_argument('--compact',action='store_true')
    args=parser.parse_args(argv)
    payload=build_edge_downloaded_archive_validation_broad_checkpoint_repair(args.repo_root,target_url=args.target_url)
    if args.json: print(json.dumps(payload,sort_keys=True,separators=(',',':') if args.compact else None,indent=None if args.compact else 2))
    else: print(render_text(payload),end='')
    return 0 if payload.get('ok') else 1

if __name__=='__main__':
    raise SystemExit(main())
