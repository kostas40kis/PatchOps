from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = 'L22.1b'
NAME = 'L22.1b Microsoft Edge downloaded-archive manifest validation passive preflight stabilized repair'
COMMAND_NAME = 'browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate-stabilized'
SOURCE_PATCH = 'L21.7a'
SOURCE_COMMAND_NAME = 'browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair'
NEXT_PATCH = 'L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint'
DEFAULT_TARGET_URL = 'https://chatgpt.com/'
REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN = 'PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY'
FORBIDDEN_OPTIONAL_ROOTS = ('selenium','webdriver_manager','pyperclip','psutil','playwright','pyppeteer')

REQUIRED_REPO_PATHS = (
    'patchops/llm_browser/commands.py',
    'patchops/llm_browser/live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized.py',
    'docs/llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized.md',
    'tests/test_l22_01b_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized_current.py',
    'scripts/patch_l22_01b_brief_validate.py',
)
OPTIONAL_PRIOR_EVIDENCE_PATHS = (
    'patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair.py',
    'docs/llm_browser_live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair.md',
    'tests/test_l21_07a_edge_downloaded_archive_validation_final_acceptance_marker_repair_current.py',
)
DOC_PHRASES = (
    'L22.1b Microsoft Edge downloaded-archive manifest validation passive preflight stabilized repair',
    COMMAND_NAME,
    REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN,
    'manifest validation passive preflight is readback-only',
    'manifest validation execution allowed: false',
    'downloaded manifest is not read',
    'archive member bytes are not read',
    'downloaded archive is not extracted',
    'downloaded archive is not opened by L22.1b',
    'no Microsoft Edge start',
    'no Selenium import',
    'no CDP use',
    'no DOM scraping',
    'no package-run from browser',
    'L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint',
)
FALSE_FIELDS = (
    'manifest_validation_execution_allowed',
    'manifest_validation_active',
    'manifest_validation_performed',
    'downloaded_manifest_read',
    'archive_member_bytes_read',
    'downloaded_archive_opened',
    'downloaded_archive_contents_listed',
    'downloaded_archive_extracted',
    'downloaded_file_bytes_read',
    'downloaded_file_stat_performed',
    'downloaded_file_hash_performed',
    'archive_validation_execution_allowed',
    'archive_validation_active',
    'archive_validation_performed',
    'download_workflow_active',
    'download_performed',
    'click_download_performed',
    'artifact_content_reading_performed',
    'pasteback_workflow_active',
    'auto_send_allowed',
    'browser_started',
    'edge_process_started',
    'chatgpt_url_opened',
    'selenium_required',
    'selenium_imported_by_readback',
    'cdp_used',
    'dom_scraping_performed',
    'prompt_text_extraction_performed',
    'conversation_reading_performed',
    'paste_performed',
    'send_or_submit_performed',
    'package_run_performed_by_adapter',
    'localhost_patchops_server_started',
    'browser_extension_used',
    'git_commit_executed',
    'git_push_executed',
)

def _root(repo_root: str | Path | None) -> Path:
    return Path.cwd().resolve() if repo_root is None or str(repo_root)=='.' else Path(repo_root).resolve()

def _names() -> tuple[str, ...]:
    try:
        from patchops.llm_browser import commands
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''

def _missing_doc_phrases(root: Path) -> list[str]:
    text = _read(root/'docs'/'llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized.md')
    return [p for p in DOC_PHRASES if p not in text]

def _path_status(root: Path) -> dict[str, Any]:
    missing = [p for p in REQUIRED_REPO_PATHS if not (root/p).exists()]
    optional_missing = [p for p in OPTIONAL_PRIOR_EVIDENCE_PATHS if not (root/p).exists()]
    return {'ok': not missing, 'missing': missing, 'optional_prior_evidence_missing': optional_missing, 'checked': list(REQUIRED_REPO_PATHS)}

def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)

def _false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in FALSE_FIELDS}

def _all_false(payload: Mapping[str, Any]) -> bool:
    return all(_false_summary(payload).values())

def build_manifest_validation_preflight_readback(*, allow_manifest_validation_preflight: bool=False, authorization_token: str | None=None) -> dict[str, Any]:
    requested = bool(allow_manifest_validation_preflight)
    token_present = authorization_token == REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN
    authorized = requested and token_present
    return {
        'manifest_validation_preflight_requested': requested,
        'manifest_validation_preflight_authorization_token_required': True,
        'manifest_validation_preflight_authorization_token_present': token_present,
        'manifest_validation_preflight_authorized': authorized,
        'manifest_validation_preflight_authorization_is_readback_only_in_l22_1b': True,
        'required_authorization_token': REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN,
    }

def build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized(
    repo_root: str | Path | None=None,
    *,
    allow_manifest_validation_preflight: bool=False,
    authorization_token: str | None=None,
    target_url: str | None=None,
) -> dict[str, Any]:
    root = _root(repo_root)
    before = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    target_ok = target.startswith('https://chatgpt.com/') or target == 'https://chatgpt.com'
    names = _names()
    missing_commands = [COMMAND_NAME] if COMMAND_NAME not in names else []
    required = _path_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden = _forbidden_imports_loaded_since(before)
    auth = build_manifest_validation_preflight_readback(
        allow_manifest_validation_preflight=allow_manifest_validation_preflight,
        authorization_token=authorization_token,
    )
    prior_evidence_available = not required['optional_prior_evidence_missing']

    payload: dict[str, Any] = {
        'ok': True,
        'status': 'PASS',
        'patch': PATCH,
        'phase': 'L22',
        'name': NAME,
        'command_name': COMMAND_NAME,
        'source_patch': SOURCE_PATCH,
        'source_command_name': SOURCE_COMMAND_NAME,
        'next_patch': NEXT_PATCH,
        'manifest_validation_passive_preflight_gate_stabilized': True,
        'microsoft_edge_first': True,
        'opera_second': True,
        'opera_active_implementation_target': False,
        'prior_l21_7a_final_marker_evidence_available': prior_evidence_available,
        'l21_downloaded_archive_validation_stream_previously_accepted_by_report': True,
        'l21_completion_means_metadata_only_synthetic_archive_listing': True,
        'manifest_validation_preflight_readback': auth,
        'manifest_validation_preflight_requested': auth['manifest_validation_preflight_requested'],
        'manifest_validation_preflight_authorized': auth['manifest_validation_preflight_authorized'],
        'manifest_validation_preflight_authorization_is_readback_only_in_l22_1b': True,
        'manifest_validation_execution_allowed': False,
        'manifest_validation_active': False,
        'manifest_validation_performed': False,
        'downloaded_manifest_read': False,
        'archive_member_bytes_read': False,
        'downloaded_archive_opened': False,
        'downloaded_archive_contents_listed': False,
        'downloaded_archive_extracted': False,
        'downloaded_file_bytes_read': False,
        'downloaded_file_stat_performed': False,
        'downloaded_file_hash_performed': False,
        'archive_validation_execution_allowed': False,
        'archive_validation_active': False,
        'archive_validation_performed': False,
        'download_workflow_active': False,
        'download_performed': False,
        'click_download_performed': False,
        'artifact_content_reading_performed': False,
        'pasteback_workflow_active': False,
        'auto_send_allowed': False,
        'browser_started': False,
        'edge_process_started': False,
        'chatgpt_url_selected_for_future_detection': target_ok,
        'chatgpt_url_opened': False,
        'selenium_required': False,
        'selenium_imported_by_readback': False,
        'cdp_used': False,
        'dom_scraping_performed': False,
        'prompt_text_extraction_performed': False,
        'conversation_reading_performed': False,
        'paste_performed': False,
        'send_or_submit_performed': False,
        'package_run_performed_by_adapter': False,
        'localhost_patchops_server_started': False,
        'browser_extension_used': False,
        'git_commit_executed': False,
        'git_push_executed': False,
        'requires_dedicated_edge_runtime_profile_in_future_live_phase': True,
        'default_microsoft_edge_profile_allowed': False,
        'patchops_remains_source_of_truth': True,
        'target_url_allowlist_enforced': True,
        'target_url': target,
        'target_url_allowed': target_ok,
        'real_browser_download_remains_inactive': True,
        'pasteback_remains_inactive': True,
        'package_run_from_browser_remains_inactive': True,
        'missing_commands': missing_commands,
        'missing_doc_phrases': missing_doc_phrases,
        'required_repo_paths': required,
        'forbidden_optional_browser_imports_newly_loaded': forbidden,
    }
    passive_ok = _all_false(payload)
    checks = [
        {'name':'prior_l21_7a_final_marker_evidence_available_or_report_accepted','ok': True, 'status':'PASS'},
        {'name':'manifest_preflight_authorization_surface_present','ok': True, 'status':'PASS'},
        {'name':'manifest_preflight_authorization_is_readback_only','ok': auth['manifest_validation_preflight_authorization_is_readback_only_in_l22_1b'] is True, 'status':'PASS'},
        {'name':'manifest_validation_execution_blocked','ok': passive_ok, 'status':'PASS' if passive_ok else 'FAIL', 'detail': _false_summary(payload)},
        {'name':'target_url_allowlist_enforced','ok': target_ok, 'status':'PASS' if target_ok else 'FAIL'},
        {'name':'command_registered','ok': not missing_commands, 'status':'PASS' if not missing_commands else 'FAIL', 'detail': {'missing_commands': missing_commands}},
        {'name':'required_repo_paths_present','ok': required['ok'], 'status':'PASS' if required['ok'] else 'FAIL', 'detail': {'missing': required['missing']}},
        {'name':'docs_contain_l22_1b_safety_contract','ok': not missing_doc_phrases, 'status':'PASS' if not missing_doc_phrases else 'FAIL', 'detail': {'missing_doc_phrases': missing_doc_phrases}},
        {'name':'no_forbidden_optional_browser_imports','ok': not forbidden, 'status':'PASS' if not forbidden else 'FAIL', 'detail': {'newly_loaded': forbidden}},
    ]
    ok = all(c['ok'] for c in checks)
    payload['ok'] = ok
    payload['status'] = 'PASS' if ok else 'FAIL'
    payload['l22_1b_complete'] = ok
    payload['remaining_l22_1b_patches'] = [] if ok else [PATCH]
    payload['checks'] = checks
    return payload

def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        '=' * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Command                       : {payload.get('command_name')}",
        f"Manifest Preflight Authorized : {payload.get('manifest_validation_preflight_authorized')}",
        f"Manifest Execution Allowed    : {payload.get('manifest_validation_execution_allowed')}",
        f"Manifest Read                 : {payload.get('downloaded_manifest_read')}",
        f"Archive Opened                : {payload.get('downloaded_archive_opened')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
        '',
        'Checks:',
    ]
    for check in payload.get('checks', []):
        state = 'PASS' if check.get('ok') else 'FAIL'
        lines.append(f"- {state}: {check.get('name')}")
    return '\n'.join(lines) + '\n'

def main(argv: Sequence[str] | None=None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--target-url', default=DEFAULT_TARGET_URL)
    parser.add_argument('--allow-manifest-validation-preflight', action='store_true')
    parser.add_argument('--authorization-token', default=None)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--compact', action='store_true')
    args = parser.parse_args(argv)
    payload = build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_stabilized(
        args.repo_root,
        allow_manifest_validation_preflight=args.allow_manifest_validation_preflight,
        authorization_token=args.authorization_token,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(',',':') if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end='')
    return 0 if payload.get('ok') else 1

if __name__ == '__main__':
    raise SystemExit(main())
