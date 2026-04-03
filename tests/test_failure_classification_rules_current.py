from pathlib import Path

from patchops.execution.failure_classifier import classify_command_failure
from patchops.failure_categories import (
    AMBIGUOUS_OR_SUSPICIOUS_RUN,
    PATCH_AUTHORING_FAILURE,
    TARGET_PROJECT_FAILURE,
    WRAPPER_FAILURE,
    normalize_failure_category,
)
from patchops.models import CommandResult



def _command_result(*, exit_code: int, phase: str = "validation") -> CommandResult:
    return CommandResult(
        name="pytest",
        program="python",
        args=["-m", "pytest", "-q"],
        working_directory=Path("."),
        exit_code=exit_code,
        stdout="",
        stderr="",
        display_command="python -m pytest -q",
        phase=phase,
    )



def test_required_target_validation_failure_classifies_as_target_project_failure() -> None:
    failure = classify_command_failure(_command_result(exit_code=1), [0])
    assert failure is not None
    assert normalize_failure_category(getattr(failure, "category", None)) == TARGET_PROJECT_FAILURE



def test_allowed_success_does_not_classify_as_target_project_failure() -> None:
    failure = classify_command_failure(_command_result(exit_code=0), [0])
    assert failure is None



def test_launcher_report_contradiction_maps_to_wrapper_failure_vocabulary() -> None:
    assert normalize_failure_category(WRAPPER_FAILURE) == WRAPPER_FAILURE



def test_malformed_manifest_maps_to_patch_authoring_failure_vocabulary() -> None:
    assert normalize_failure_category(PATCH_AUTHORING_FAILURE) == PATCH_AUTHORING_FAILURE



def test_unclear_contradictory_evidence_falls_back_to_ambiguous_or_suspicious() -> None:
    assert normalize_failure_category(None) == AMBIGUOUS_OR_SUSPICIOUS_RUN
    assert (
        normalize_failure_category("contradictory_evidence_without_clear_class")
        == AMBIGUOUS_OR_SUSPICIOUS_RUN
    )
