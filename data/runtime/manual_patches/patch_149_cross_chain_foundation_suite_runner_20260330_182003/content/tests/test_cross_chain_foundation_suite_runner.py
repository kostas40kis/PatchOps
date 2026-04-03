import pytest

from src.trader.execution.cross_chain_foundation_suite_runner import (
    PHASE_1_FOUNDATION_TEST_PATHS,
    CrossChainFoundationSuiteRunnerError,
    build_cross_chain_foundation_suite_definition,
    build_cross_chain_foundation_suite_summary,
    render_cross_chain_foundation_suite_summary_text,
)


def test_definition_contains_phase_1_foundation_modules() -> None:
    definition = build_cross_chain_foundation_suite_definition()

    assert definition.suite_name == "cross_chain_foundation_suite"
    assert definition.phase_name == "Phase 1 - Cross-chain execution substrate"
    assert definition.test_paths == PHASE_1_FOUNDATION_TEST_PATHS
    assert "phase-1 cross-chain substrate" in definition.purpose.lower()


def test_summary_passes_when_no_failed_modules_are_supplied() -> None:
    summary = build_cross_chain_foundation_suite_summary()

    assert summary.total_test_modules == len(PHASE_1_FOUNDATION_TEST_PATHS)
    assert summary.passed_test_modules == len(PHASE_1_FOUNDATION_TEST_PATHS)
    assert summary.failed_test_modules == 0
    assert summary.result == "PASS"


def test_summary_fails_when_failed_modules_are_supplied() -> None:
    summary = build_cross_chain_foundation_suite_summary(
        failed_test_paths=("tests/test_connector_selection_policy.py",)
    )

    assert summary.total_test_modules == len(PHASE_1_FOUNDATION_TEST_PATHS)
    assert summary.passed_test_modules == len(PHASE_1_FOUNDATION_TEST_PATHS) - 1
    assert summary.failed_test_modules == 1
    assert summary.result == "FAIL"


def test_summary_blocks_unknown_failed_module_paths() -> None:
    with pytest.raises(
        CrossChainFoundationSuiteRunnerError,
        match="failed_test_paths must be members of the suite",
    ):
        build_cross_chain_foundation_suite_summary(
            failed_test_paths=("tests/test_not_in_suite.py",)
        )


def test_rendered_summary_text_mentions_named_suite_and_result() -> None:
    summary = build_cross_chain_foundation_suite_summary()
    rendered = render_cross_chain_foundation_suite_summary_text(summary)

    assert "CROSS CHAIN FOUNDATION SUITE" in rendered
    assert "Suite name: cross_chain_foundation_suite" in rendered
    assert "Result: PASS" in rendered
    assert "tests/test_chain_execution_context.py" in rendered
    assert "tests/test_chain_support_validation.py" in rendered