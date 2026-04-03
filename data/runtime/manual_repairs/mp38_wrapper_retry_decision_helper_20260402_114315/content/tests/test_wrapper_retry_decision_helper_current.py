from patchops.failure_categories import PATCH_AUTHORING_FAILURE, TARGET_PROJECT_FAILURE, WRAPPER_FAILURE
from patchops.rerun_decisions import (
    WRAPPER_ONLY_REPAIR,
    should_recommend_verify_only,
    should_recommend_wrapper_only_repair,
)


def test_wrapper_retry_constant_is_stable():
    assert WRAPPER_ONLY_REPAIR == 'wrapper_only_repair'


def test_wrapper_retry_helper_accepts_wrapper_failure_when_target_already_present_and_no_writes():
    assert should_recommend_wrapper_only_repair(
        failure_class=WRAPPER_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is True


def test_wrapper_retry_helper_rejects_when_writes_were_applied_by_wrapper():
    assert should_recommend_wrapper_only_repair(
        failure_class=WRAPPER_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=True,
    ) is False


def test_wrapper_retry_helper_rejects_when_target_content_is_not_already_present():
    assert should_recommend_wrapper_only_repair(
        failure_class=WRAPPER_FAILURE,
        target_content_already_present=False,
        writes_applied_by_wrapper=False,
    ) is False


def test_wrapper_retry_helper_rejects_target_failure():
    assert should_recommend_wrapper_only_repair(
        failure_class=TARGET_PROJECT_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is False


def test_wrapper_retry_helper_rejects_patch_authoring_failure():
    assert should_recommend_wrapper_only_repair(
        failure_class=PATCH_AUTHORING_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is False


def test_wrapper_retry_and_verify_only_helpers_remain_separate():
    assert should_recommend_verify_only(
        failure_class=TARGET_PROJECT_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is True
    assert should_recommend_wrapper_only_repair(
        failure_class=WRAPPER_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is True
