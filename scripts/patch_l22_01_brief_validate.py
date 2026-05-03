from __future__ import annotations
import argparse, json, sys
from pathlib import Path
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate as l22_01

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Brief L22.1 validation')
    parser.add_argument('--repo-root', default=str(_REPO_ROOT))
    parser.add_argument('--target-url', default='https://chatgpt.com/')
    args = parser.parse_args(argv)
    default_payload = l22_01.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate(Path(args.repo_root).resolve(), target_url=args.target_url)
    authorized_payload = l22_01.build_edge_downloaded_archive_manifest_validation_passive_preflight_gate(Path(args.repo_root).resolve(), allow_manifest_validation_preflight=True, authorization_token=l22_01.REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN, target_url=args.target_url)
    ok = (default_payload.get('ok') is True and authorized_payload.get('ok') is True and default_payload.get('manifest_validation_preflight_authorized') is False and authorized_payload.get('manifest_validation_preflight_authorized') is True and authorized_payload.get('manifest_validation_execution_allowed') is False and authorized_payload.get('manifest_validation_active') is False and authorized_payload.get('manifest_validation_performed') is False and authorized_payload.get('downloaded_manifest_read') is False and authorized_payload.get('archive_member_bytes_read') is False and authorized_payload.get('downloaded_file_bytes_read') is False and authorized_payload.get('browser_started') is False and authorized_payload.get('edge_process_started') is False)
    summary = {
        'ok': ok,
        'patch': authorized_payload.get('patch'),
        'source_patch': authorized_payload.get('source_patch'),
        'source_l21_7a_archive_final_marker_repair_accepted': authorized_payload.get('source_l21_7a_archive_final_marker_repair_accepted'),
        'l21_downloaded_archive_validation_stream_complete': authorized_payload.get('l21_downloaded_archive_validation_stream_complete'),
        'l21_completion_means_metadata_only_archive_listing': authorized_payload.get('l21_completion_means_metadata_only_archive_listing'),
        'default_manifest_validation_preflight_authorized': default_payload.get('manifest_validation_preflight_authorized'),
        'authorized_manifest_validation_preflight_authorized': authorized_payload.get('manifest_validation_preflight_authorized'),
        'manifest_validation_preflight_authorization_is_readback_only_in_l22_1': authorized_payload.get('manifest_validation_preflight_authorization_is_readback_only_in_l22_1'),
        'manifest_validation_execution_allowed': authorized_payload.get('manifest_validation_execution_allowed'),
        'manifest_validation_active': authorized_payload.get('manifest_validation_active'),
        'manifest_validation_performed': authorized_payload.get('manifest_validation_performed'),
        'downloaded_manifest_read': authorized_payload.get('downloaded_manifest_read'),
        'downloaded_archive_opened_for_manifest_validation': authorized_payload.get('downloaded_archive_opened_for_manifest_validation'),
        'downloaded_archive_contents_listed_for_manifest_validation': authorized_payload.get('downloaded_archive_contents_listed_for_manifest_validation'),
        'downloaded_archive_extracted': authorized_payload.get('downloaded_archive_extracted'),
        'archive_member_bytes_read': authorized_payload.get('archive_member_bytes_read'),
        'downloaded_file_bytes_read': authorized_payload.get('downloaded_file_bytes_read'),
        'browser_started': authorized_payload.get('browser_started'),
        'edge_process_started': authorized_payload.get('edge_process_started'),
        'chatgpt_url_opened': authorized_payload.get('chatgpt_url_opened'),
        'package_run_performed_by_adapter': authorized_payload.get('package_run_performed_by_adapter'),
        'missing_commands': authorized_payload.get('missing_commands'),
        'missing_doc_phrases': authorized_payload.get('missing_doc_phrases'),
        'required_repo_paths_ok': (authorized_payload.get('required_repo_paths') or {}).get('ok'),
        'next_patch': authorized_payload.get('next_patch'),
    }
    print(json.dumps(summary, sort_keys=True, separators=(',', ':')))
    return 0 if summary['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
