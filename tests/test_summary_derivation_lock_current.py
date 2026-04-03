from pathlib import Path

from patchops.reporting.renderer import render_workflow_report
from tests.test_summary_integrity_current import _build_result, _command_result, _command_spec


def test_summary_lock_rejects_required_smoke_failure_even_when_result_label_claims_pass(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        smoke_specs=[_command_spec("required_smoke", [0])],
        smoke_results=[_command_result("required_smoke", 7, "smoke")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "SMOKE COMMANDS" in report
    assert "NAME    : required_smoke" in report
    assert "EXIT    : 7" in report
    assert "ExitCode : 7" in report
    assert "Result   : FAIL" in report


def test_summary_lock_keeps_required_failure_sticky_even_when_later_non_zero_is_tolerated(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        validation_specs=[_command_spec("required_validation", [0])],
        validation_results=[_command_result("required_validation", 4, "validation")],
        smoke_specs=[_command_spec("tolerated_smoke", [0, 3])],
        smoke_results=[_command_result("tolerated_smoke", 3, "smoke")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "NAME    : required_validation" in report
    assert "NAME    : tolerated_smoke" in report
    assert "EXIT    : 4" in report
    assert "EXIT    : 3" in report
    assert "ExitCode : 4" in report
    assert "Result   : FAIL" in report


def test_summary_lock_preserves_pass_when_only_explicitly_tolerated_non_zero_exists(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        smoke_specs=[_command_spec("tolerated_smoke", [0, 5])],
        smoke_results=[_command_result("tolerated_smoke", 5, "smoke")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "NAME    : tolerated_smoke" in report
    assert "EXIT    : 5" in report
    assert "ExitCode : 0" in report
    assert "Result   : PASS" in report
