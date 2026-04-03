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
