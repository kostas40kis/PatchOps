from __future__ import annotations

from patchops.exceptions import PatchOpsError, WrapperExecutionError
from patchops.models import CommandResult, FailureInfo


def classify_exception(exc: Exception) -> FailureInfo:
    if isinstance(exc, WrapperExecutionError):
        return FailureInfo(category="wrapper_failure", message=str(exc))
    if isinstance(exc, PatchOpsError):
        return FailureInfo(category="wrapper_failure", message=str(exc))
    return FailureInfo(category="wrapper_failure", message=str(exc), details=exc.__class__.__name__)


def classify_command_failure(result: CommandResult, allowed_exit_codes: list[int]) -> FailureInfo | None:
    if result.exit_code in allowed_exit_codes:
        return None
    return FailureInfo(
        category="target_project_failure",
        message=(
            f"Command {result.name!r} failed during {result.phase} with exit code {result.exit_code}."
        ),
    )
