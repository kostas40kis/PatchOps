from __future__ import annotations

import json
import textwrap
from pathlib import Path
import sys


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / 'content'
    inner_reports = working_root / 'inner_reports'
    content_root.mkdir(parents=True, exist_ok=True)
    inner_reports.mkdir(parents=True, exist_ok=True)

    rerun_path = repo_root / 'patchops' / 'rerun_decisions.py'
    test_path = repo_root / 'tests' / 'test_rerun_decision_matrix_current.py'

    helper_exists = rerun_path.exists()
    rerun_source = rerun_path.read_text(encoding='utf-8') if helper_exists else ''
    current_test_exists = test_path.exists()
    current_test_source = test_path.read_text(encoding='utf-8') if current_test_exists else ''

    required_test_fragments = [
        'continue_to_next_patch',
        'content_repair',
        'wrapper_only_repair',
        'authoring_repair',
        'stop_and_inspect_evidence',
    ]
    required_helpers_present = (
        'should_recommend_verify_only' in rerun_source
        and 'should_recommend_wrapper_only_repair' in rerun_source
    )
    required_fragments_present = all(fragment in current_test_source for fragment in required_test_fragments)

    if not helper_exists:
        raise SystemExit('MP38 prerequisite missing: patchops/rerun_decisions.py not found.')
    if not required_helpers_present:
        raise SystemExit('MP38 prerequisite shape missing from patchops/rerun_decisions.py.')

    decision = 'author_mp39'
    decision_reason = 'Prove the maintained rerun decision matrix with small executable examples.'
    if current_test_exists and required_fragments_present:
        decision = 'stop_mp39_already_present'
        decision_reason = 'The current rerun decision matrix test already exists.'

    state = {
        'decision': decision,
        'decision_reason': decision_reason,
        'helper_exists': helper_exists,
        'current_test_exists': current_test_exists,
        'required_fragments_present': required_fragments_present,
        'manifest_path': str(working_root / 'patch_manifest.json'),
        'inner_report_root': str(inner_reports),
    }

    if decision == 'author_mp39':
        current_test = textwrap.dedent('''
        from patchops.failure_categories import (
            AMBIGUOUS_OR_SUSPICIOUS_RUN,
            PATCH_AUTHORING_FAILURE,
            TARGET_PROJECT_FAILURE,
            WRAPPER_FAILURE,
        )
        from patchops.rerun_decisions import (
            VERIFY_ONLY,
            WRAPPER_ONLY_REPAIR,
            should_recommend_verify_only,
            should_recommend_wrapper_only_repair,
        )


        CONTINUE_TO_NEXT_PATCH = 'continue_to_next_patch'
        CONTENT_REPAIR = 'content_repair'
        AUTHORING_REPAIR = 'authoring_repair'
        STOP_AND_INSPECT_EVIDENCE = 'stop_and_inspect_evidence'


        def derive_next_mode(*, run_passed: bool, failure_class: str | None, target_content_already_present: bool, writes_applied_by_wrapper: bool) -> str:
            if run_passed:
                return CONTINUE_TO_NEXT_PATCH
            if should_recommend_verify_only(
                failure_class=failure_class,
                target_content_already_present=target_content_already_present,
                writes_applied_by_wrapper=writes_applied_by_wrapper,
            ):
                return VERIFY_ONLY
            if should_recommend_wrapper_only_repair(
                failure_class=failure_class,
                target_content_already_present=target_content_already_present,
                writes_applied_by_wrapper=writes_applied_by_wrapper,
            ):
                return WRAPPER_ONLY_REPAIR
            if failure_class == TARGET_PROJECT_FAILURE:
                return CONTENT_REPAIR
            if failure_class == PATCH_AUTHORING_FAILURE:
                return AUTHORING_REPAIR
            return STOP_AND_INSPECT_EVIDENCE


        def test_green_run_continues_to_next_patch():
            assert derive_next_mode(
                run_passed=True,
                failure_class=None,
                target_content_already_present=False,
                writes_applied_by_wrapper=False,
            ) == CONTINUE_TO_NEXT_PATCH


        def test_target_failure_without_already_present_content_recommends_content_repair():
            assert derive_next_mode(
                run_passed=False,
                failure_class=TARGET_PROJECT_FAILURE,
                target_content_already_present=False,
                writes_applied_by_wrapper=False,
            ) == CONTENT_REPAIR


        def test_wrapper_failure_with_clean_target_recommends_wrapper_only_repair():
            assert derive_next_mode(
                run_passed=False,
                failure_class=WRAPPER_FAILURE,
                target_content_already_present=True,
                writes_applied_by_wrapper=False,
            ) == WRAPPER_ONLY_REPAIR


        def test_patch_authoring_failure_recommends_authoring_repair():
            assert derive_next_mode(
                run_passed=False,
                failure_class=PATCH_AUTHORING_FAILURE,
                target_content_already_present=False,
                writes_applied_by_wrapper=False,
            ) == AUTHORING_REPAIR


        def test_ambiguous_run_recommends_stop_and_inspect():
            assert derive_next_mode(
                run_passed=False,
                failure_class=AMBIGUOUS_OR_SUSPICIOUS_RUN,
                target_content_already_present=False,
                writes_applied_by_wrapper=False,
            ) == STOP_AND_INSPECT_EVIDENCE


        def test_verify_only_case_remains_distinct_from_content_repair():
            assert derive_next_mode(
                run_passed=False,
                failure_class=TARGET_PROJECT_FAILURE,
                target_content_already_present=True,
                writes_applied_by_wrapper=False,
            ) == VERIFY_ONLY
        ''').strip() + '\n'

        out_test = content_root / 'tests' / 'test_rerun_decision_matrix_current.py'
        ensure_parent(out_test)
        out_test.write_text(current_test, encoding='utf-8')

        manifest = {
            'manifest_version': '1',
            'patch_name': 'mp39_rerun_decision_matrix_tests',
            'active_profile': 'generic_python',
            'target_project_root': str(repo_root),
            'files_to_write': [
                {
                    'path': 'tests/test_rerun_decision_matrix_current.py',
                    'content_path': str(out_test),
                    'encoding': 'utf-8',
                }
            ],
            'validation_commands': [
                {
                    'name': 'mp39 rerun decision matrix tests',
                    'program': 'py',
                    'args': ['-3','-m','pytest','-q','tests/test_rerun_decision_matrix_current.py','tests/test_wrapper_retry_decision_helper_current.py','tests/test_verify_only_decision_helper_current.py','tests/test_failure_classification_rules_current.py','tests/test_failure_category_model_current.py'],
                    'working_directory': '.',
                    'use_profile_runtime': False,
                    'allowed_exit_codes': [0],
                }
            ],
            'report_preferences': {
                'report_dir': str(inner_reports),
                'report_name_prefix': 'mp39',
                'write_to_desktop': False,
            },
            'tags': ['maintenance','pythonization','phase_f','mp39','self_hosted'],
            'notes': 'MP39 rerun decision matrix tests after confirmed MP38 completion.',
        }
        (working_root / 'patch_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    print(json.dumps(state, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())