from __future__ import annotations
import argparse, json, sys
from pathlib import Path
_REPO_ROOT=Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path: sys.path.insert(0,str(_REPO_ROOT))
from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_broad_checkpoint_repair as l21_06a

def main(argv=None):
    parser=argparse.ArgumentParser(description='Brief L21.6a validation')
    parser.add_argument('--repo-root',default=str(_REPO_ROOT))
    parser.add_argument('--target-url',default='https://chatgpt.com/')
    args=parser.parse_args(argv)
    p=l21_06a.build_edge_downloaded_archive_validation_broad_checkpoint_repair(Path(args.repo_root).resolve(),target_url=args.target_url)
    keys=['ok','patch','source_patch','l21_5_metadata_only_archive_proof_remains_accepted','default_archive_metadata_proof_readback_remains_passive','authorized_archive_metadata_proof_readback_remains_metadata_only','archive_validation_scope','archive_validation_performed','downloaded_archive_opened','downloaded_archive_contents_listed','archive_entry_count','downloaded_archive_extracted','downloaded_manifest_read','archive_member_bytes_read','downloaded_file_bytes_read','downloaded_file_stat_performed','downloaded_file_hash_performed','browser_started','edge_process_started','chatgpt_url_opened','package_run_performed_by_adapter','missing_commands','missing_doc_phrases','next_patch']
    s={k:p.get(k) for k in keys}
    s['required_repo_paths_ok']=(p.get('required_repo_paths') or {}).get('ok')
    print(json.dumps(s,sort_keys=True,separators=(',',':')))
    return 0 if s['ok'] else 1
if __name__=='__main__': raise SystemExit(main())
