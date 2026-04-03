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
