from pathlib import Path
import json
import textwrap
import sys

repo_root = Path(sys.argv[1])
working_root = Path(sys.argv[2])
content_root = working_root / 'content'
(content_root / 'patchops').mkdir(parents=True, exist_ok=True)
(content_root / 'tests').mkdir(parents=True, exist_ok=True)
inner_report_root = working_root / 'inner_reports'
inner_report_root.mkdir(parents=True, exist_ok=True)

helper_path = repo_root / 'patchops' / 'rerun_decisions.py'
test_path = repo_root / 'tests' / 'test_verify_only_decision_helper_current.py'

required_fragments = [
    'VERIFY_ONLY',
    'def should_recommend_verify_only(',
    'failure_class',
    'target_content_already_present',
    'writes_applied_by_wrapper',
]
existing = helper_path.read_text(encoding='utf-8') if helper_path.exists() else ''
required_present = helper_path.exists() and all(fragment in existing for fragment in required_fragments) and test_path.exists()

decision = 'stop_mp37_already_present' if required_present else 'author_mp37'
decision_reason = 'verify-only decision helper already present.' if required_present else 'Create a pure helper that decides whether verify-only is the correct next mode.'

state = {
    'decision': decision,
    'decision_reason': decision_reason,
    'helper_exists': helper_path.exists(),
    'current_test_exists': test_path.exists(),
    'required_fragments_present': required_present,
    'manifest_path': str(working_root / 'patch_manifest.json'),
    'inner_report_root': str(inner_report_root),
}

if decision == 'author_mp37':
    helper_text = textwrap.dedent('''
    """Pure rerun-decision helpers for maintenance-grade next-mode guidance."""

    VERIFY_ONLY = 'verify_only'


    def should_recommend_verify_only(*, failure_class: str | None, target_content_already_present: bool, writes_applied_by_wrapper: bool) -> bool:
        """Return True when the next truthful move is verify-only.

        The helper stays intentionally narrow. It only answers whether a run already
        matches the verify-only pattern based on already-known classification and evidence.
        """
        if failure_class != 'target_project_failure':
            return False
        if not target_content_already_present:
            return False
        if writes_applied_by_wrapper:
            return False
        return True
    ''').strip() + '\n'

    test_text = textwrap.dedent('''
    from patchops.rerun_decisions import VERIFY_ONLY, should_recommend_verify_only


    def test_verify_only_constant_is_stable():
        assert VERIFY_ONLY == 'verify_only'


    def test_verify_only_recommended_for_target_failure_when_content_already_present_and_no_writes():
        assert should_recommend_verify_only(
            failure_class='target_project_failure',
            target_content_already_present=True,
            writes_applied_by_wrapper=False,
        ) is True


    def test_verify_only_not_recommended_when_writes_were_applied_by_wrapper():
        assert should_recommend_verify_only(
            failure_class='target_project_failure',
            target_content_already_present=True,
            writes_applied_by_wrapper=True,
        ) is False


    def test_verify_only_not_recommended_for_non_target_failure():
        assert should_recommend_verify_only(
            failure_class='wrapper_failure',
            target_content_already_present=True,
            writes_applied_by_wrapper=False,
        ) is False


    def test_verify_only_not_recommended_when_target_content_not_already_present():
        assert should_recommend_verify_only(
            failure_class='target_project_failure',
            target_content_already_present=False,
            writes_applied_by_wrapper=False,
        ) is False
    ''').strip() + '\n'

    (content_root / 'patchops' / 'rerun_decisions.py').write_text(helper_text, encoding='utf-8')
    (content_root / 'tests' / 'test_verify_only_decision_helper_current.py').write_text(test_text, encoding='utf-8')

    manifest = {
        'manifest_version': '1',
        'patch_name': 'mp37_verify_only_decision_helper',
        'active_profile': 'generic_python',
        'target_project_root': str(repo_root),
        'backup_files': [],
        'files_to_write': [
            {
                'path': 'patchops/rerun_decisions.py',
                'content_path': str(content_root / 'patchops' / 'rerun_decisions.py'),
                'encoding': 'utf-8',
            },
            {
                'path': 'tests/test_verify_only_decision_helper_current.py',
                'content_path': str(content_root / 'tests' / 'test_verify_only_decision_helper_current.py'),
                'encoding': 'utf-8',
            },
        ],
        'validation_commands': [
            {
                'name': 'mp37 verify-only decision helper tests',
                'program': 'py',
                'args': ['-3','-m','pytest','-q','tests/test_verify_only_decision_helper_current.py','tests/test_failure_classification_rules_current.py','tests/test_failure_category_model_current.py'],
                'working_directory': '.',
                'use_profile_runtime': False,
                'allowed_exit_codes': [0],
            }
        ],
        'failure_policy': {},
        'report_preferences': {
            'report_dir': str(inner_report_root),
            'report_name_prefix': 'mp37',
            'write_to_desktop': False,
        },
        'tags': ['maintenance','pythonization','phase_f','mp37','self_hosted'],
        'notes': 'MP37 verify-only decision helper after confirmed MP36 completion.',
    }
    (working_root / 'patch_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

for key, value in state.items():
    print(f"{key}={value}")