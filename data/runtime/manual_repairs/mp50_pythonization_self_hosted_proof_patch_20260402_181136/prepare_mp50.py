from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    backup_root = Path(sys.argv[3]).resolve()
    inner_report_root = Path(sys.argv[4]).resolve()
    content_root = working_root / 'content'
    content_root.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)
    inner_report_root.mkdir(parents=True, exist_ok=True)

    marker_target = repo_root / 'data' / 'runtime' / 'self_hosted_proof' / 'mp50_existing_marker.txt'
    ensure_parent(marker_target)
    if not marker_target.exists():
        marker_target.write_text('pre-mp50 existing marker\n', encoding='utf-8')

    marker_content = content_root / 'data' / 'runtime' / 'self_hosted_proof' / 'mp50_existing_marker.txt'
    ensure_parent(marker_content)
    marker_content.write_text(
        'mp50 self-hosted proof written via PatchOps\n'
        'This existing file was intentionally rewritten to exercise backup and write helpers.\n',
        encoding='utf-8',
    )

    proof_test = content_root / 'tests' / 'test_pythonization_self_hosted_proof_current.py'
    ensure_parent(proof_test)
    proof_test.write_text(
        textwrap.dedent(
            '''
            from pathlib import Path


            def test_mp50_self_hosted_proof_marker_exists_and_is_current():
                marker_path = Path('data/runtime/self_hosted_proof/mp50_existing_marker.txt')
                assert marker_path.exists()
                text = marker_path.read_text(encoding='utf-8')
                assert 'mp50 self-hosted proof written via patchops' in text.lower()
                assert 'backup and write helpers' in text.lower()
            '''
        ).strip() + '\n',
        encoding='utf-8',
    )

    manifest_path = working_root / 'patch_manifest.json'
    manifest = {
        'manifest_version': '1',
        'patch_name': 'mp50_pythonization_self_hosted_proof',
        'active_profile': 'generic_python',
        'target_project_root': str(repo_root),
        'backup_root': str(backup_root),
        'files_to_write': [
            {
                'path': 'data/runtime/self_hosted_proof/mp50_existing_marker.txt',
                'content_path': str(marker_content.resolve()),
                'encoding': 'utf-8',
            },
            {
                'path': 'tests/test_pythonization_self_hosted_proof_current.py',
                'content_path': str(proof_test.resolve()),
                'encoding': 'utf-8',
            },
        ],
        'validation_commands': [
            {
                'name': 'mp50 self-hosted proof tests',
                'program': 'py',
                'args': [
                    '-m', 'pytest', '-q',
                    'tests/test_suspicious_run_rule_set_current.py',
                    'tests/test_suspicious_run_detector_current.py',
                    'tests/test_suspicious_bug_artifact_model_current.py',
                    'tests/test_suspicious_artifact_emission_current.py',
                    'tests/test_suspicious_artifact_report_mention_current.py',
                    'tests/test_suspicious_run_docs_current.py',
                    'tests/test_pythonization_docs_stop_current.py',
                    'tests/test_pythonization_examples_stop_current.py',
                    'tests/test_pythonization_self_hosted_proof_current.py',
                ],
                'working_directory': '.',
                'use_profile_runtime': False,
                'allowed_exit_codes': [0],
            }
        ],
        'report_preferences': {
            'report_dir': str(inner_report_root),
            'report_name_prefix': 'mp50',
            'write_to_desktop': False,
        },
        'tags': ['maintenance', 'pythonization', 'mp50', 'self_hosted', 'proof'],
        'notes': 'MP50 self-hosted proof patch for the Pythonization micro-patch stream.',
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    print(f'manifest_path={manifest_path}')
    print(f'marker_target={marker_target}')
    print(f'proof_test_target={repo_root / "tests" / "test_pythonization_self_hosted_proof_current.py"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())