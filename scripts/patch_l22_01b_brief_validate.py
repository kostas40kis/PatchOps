from __future__ import annotations
import argparse, json, sys
from pathlib import Path
_REPO_ROOT=Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path: sys.path.insert(0,str(_REPO_ROOT))
from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized as l22_01b

def main(argv=None):
    parser=argparse.ArgumentParser(description='Brief L22.1b validation')
    parser.add_argument('--repo-root', default=str(_REPO_ROOT))
    parser.add_argument('--target-url', default='https://chatgpt.com/')
    args=parser.parse_args(argv)
    root=Path(args.repo_root).resolve()
    default=l22_01b.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized(root,target_url=args.target_url)
    auth=l22_01b.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized(root,target_url=args.target_url,allow_manifest_validation_preflight=True,authorization_token=l22_01b.REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN)
    ok=(default.get('ok') is True and auth.get('ok') is True and default.get('manifest_validation_preflight_authorized') is False and auth.get('manifest_validation_preflight_authorized') is True and auth.get('manifest_validation_execution_allowed') is False and auth.get('downloaded_manifest_read') is False and auth.get('archive_member_bytes_read') is False and auth.get('downloaded_archive_opened') is False and auth.get('browser_started') is False and auth.get('package_run_performed_by_adapter') is False)
    summary={
      'ok': ok,
      'patch': auth.get('patch'),
      'source_patch': auth.get('source_patch'),
      'default_manifest_validation_preflight_authorized': default.get('manifest_validation_preflight_authorized'),
      'authorized_manifest_validation_preflight_authorized': auth.get('manifest_validation_preflight_authorized'),
      'manifest_validation_preflight_authorization_is_readback_only_in_l22_1b': auth.get('manifest_validation_preflight_authorization_is_readback_only_in_l22_1b'),
      'manifest_validation_execution_allowed': auth.get('manifest_validation_execution_allowed'),
      'manifest_validation_active': auth.get('manifest_validation_active'),
      'manifest_validation_performed': auth.get('manifest_validation_performed'),
      'downloaded_manifest_read': auth.get('downloaded_manifest_read'),
      'archive_member_bytes_read': auth.get('archive_member_bytes_read'),
      'downloaded_archive_opened': auth.get('downloaded_archive_opened'),
      'downloaded_archive_extracted': auth.get('downloaded_archive_extracted'),
      'downloaded_file_bytes_read': auth.get('downloaded_file_bytes_read'),
      'browser_started': auth.get('browser_started'),
      'edge_process_started': auth.get('edge_process_started'),
      'package_run_performed_by_adapter': auth.get('package_run_performed_by_adapter'),
      'missing_commands': auth.get('missing_commands'),
      'missing_doc_phrases': auth.get('missing_doc_phrases'),
      'required_repo_paths_ok': (auth.get('required_repo_paths') or {}).get('ok'),
      'next_patch': auth.get('next_patch'),
    }
    print(json.dumps(summary, sort_keys=True, separators=(',',':')))
    return 0 if summary['ok'] else 1
if __name__=='__main__': raise SystemExit(main())
