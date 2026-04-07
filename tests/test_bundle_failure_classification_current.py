from __future__ import annotations

from patchops.bundles.failure_classification import (
    AMBIGUOUS_EVIDENCE,
    ENVIRONMENT_FAILURE,
    PACKAGE_AUTHORING_FAILURE,
    TARGET_CONTENT_FAILURE,
    WRAPPER_FAILURE,
    BundleFailureEvidence,
    classify_bundle_run_failure,
)


def test_classify_bundle_run_failure_marks_missing_staged_file_as_package_authoring_failure() -> None:
    result = classify_bundle_run_failure(
        BundleFailureEvidence(
            launcher_started=False,
            inner_report_found=False,
            stderr="FileNotFoundError: [Errno 2] No such file or directory: '...\\content\\tests\\test_bundle_apply_coordinator_zip_source_current.py'",
            package_setup_error="(package setup failed before launcher invocation)",
        )
    )

    assert result.category == PACKAGE_AUTHORING_FAILURE
    assert "before launcher invocation" in result.reason


def test_classify_bundle_run_failure_prefers_inner_failure_category_when_present() -> None:
    result = classify_bundle_run_failure(
        BundleFailureEvidence(
            launcher_started=True,
            inner_report_found=True,
            inner_failure_category=TARGET_CONTENT_FAILURE,
            inner_exit_code=1,
            launcher_exit_code=0,
            stderr="",
        )
    )

    assert result.category == TARGET_CONTENT_FAILURE
    assert "Inner report" in result.reason


def test_classify_bundle_run_failure_marks_launcher_contract_break_as_wrapper_failure() -> None:
    result = classify_bundle_run_failure(
        BundleFailureEvidence(
            launcher_started=True,
            inner_report_found=False,
            launcher_exit_code=1,
            stderr="The property ArgumentList cannot be found on this object. Verify that the property exists.",
        )
    )

    assert result.category == WRAPPER_FAILURE
    assert "Launcher execution failed" in result.reason


def test_classify_bundle_run_failure_marks_environment_issues_explicitly() -> None:
    result = classify_bundle_run_failure(
        BundleFailureEvidence(
            launcher_started=False,
            inner_report_found=False,
            stderr="'py' is not recognized as an internal or external command",
        )
    )

    assert result.category == ENVIRONMENT_FAILURE
    assert "Environment prevented" in result.reason


def test_classify_bundle_run_failure_falls_back_to_ambiguous_evidence() -> None:
    result = classify_bundle_run_failure(
        BundleFailureEvidence(
            launcher_started=True,
            inner_report_found=False,
            launcher_exit_code=0,
            stderr="",
        )
    )

    assert result.category == AMBIGUOUS_EVIDENCE
    assert "not strong enough" in result.reason
