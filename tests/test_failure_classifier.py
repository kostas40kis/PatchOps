from patchops.execution.failure_classifier import classify_command_failure
from patchops.models import CommandResult
from pathlib import Path


def test_failure_classifier_marks_nonzero_command_as_target_failure():
    result = CommandResult(
        name="pytest",
        program="python",
        args=["-m", "pytest"],
        working_directory=Path("."),
        exit_code=1,
        stdout="",
        stderr="",
        display_command="python -m pytest",
        phase="validation",
    )
    failure = classify_command_failure(result, [0])
    assert failure is not None
    assert failure.category == "target_project_failure"
