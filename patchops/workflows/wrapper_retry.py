from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterator, Mapping

from patchops.manifest_loader import load_manifest
from patchops.profiles.base import resolve_profile


DEFAULT_WRAPPER_ONLY_RETRY_REASON = (
    "wrapper/reporting failure after likely content success"
)
WRAPPER_ONLY_RETRY_KIND = "wrapper_only_retry"
_ACTIVE_WRAPPER_ONLY_RETRY_REASON: str | None = None



def verify_only(manifest_path, wrapper_project_root=None):
    from patchops.workflows.verify_only import verify_only as _verify_only
    return _verify_only(manifest_path, wrapper_project_root=wrapper_project_root)
@dataclass(frozen=True)
class WrapperOnlyRetryState:
    mode: str
    retry_kind: str
    reason: str
    writes_skipped: bool
    explicit_retry_required: bool
    expected_target_files: tuple[str, ...]
    existing_target_files: tuple[str, ...]
    missing_target_files: tuple[str, ...]
    validation_command_count: int
    smoke_command_count: int
    audit_command_count: int


def normalize_wrapper_only_retry_reason(reason: str | None) -> str:
    if reason is None:
        return DEFAULT_WRAPPER_ONLY_RETRY_REASON

    normalized = " ".join(str(reason).split())
    if not normalized:
        return DEFAULT_WRAPPER_ONLY_RETRY_REASON
    return normalized


@contextmanager
def active_wrapper_only_retry_context(reason: str | None) -> Iterator[str]:
    global _ACTIVE_WRAPPER_ONLY_RETRY_REASON
    previous = _ACTIVE_WRAPPER_ONLY_RETRY_REASON
    _ACTIVE_WRAPPER_ONLY_RETRY_REASON = normalize_wrapper_only_retry_reason(reason)
    try:
        yield _ACTIVE_WRAPPER_ONLY_RETRY_REASON
    finally:
        _ACTIVE_WRAPPER_ONLY_RETRY_REASON = previous


def get_active_wrapper_only_retry_reason() -> str | None:
    return _ACTIVE_WRAPPER_ONLY_RETRY_REASON


def _resolve_expected_target_files(
    manifest: Mapping[str, Any],
    target_project_root: str | Path,
) -> tuple[str, ...]:
    from patchops.workflows.verify_only import (
        resolve_verify_only_expected_target_files,
    )

    return tuple(
        resolve_verify_only_expected_target_files(manifest, target_project_root)
    )


def build_wrapper_only_retry_state(
    manifest: Mapping[str, Any],
    target_project_root: str | Path,
    reason: str | None = None,
) -> WrapperOnlyRetryState:
    expected = _resolve_expected_target_files(manifest, target_project_root)
    existing = tuple(path for path in expected if Path(path).exists())
    missing = tuple(path for path in expected if not Path(path).exists())

    validation_commands = manifest.get("validation_commands") or []
    smoke_commands = manifest.get("smoke_commands") or []
    audit_commands = manifest.get("audit_commands") or []

    return WrapperOnlyRetryState(
        mode="verify",
        retry_kind=WRAPPER_ONLY_RETRY_KIND,
        reason=normalize_wrapper_only_retry_reason(reason),
        writes_skipped=True,
        explicit_retry_required=True,
        expected_target_files=expected,
        existing_target_files=existing,
        missing_target_files=missing,
        validation_command_count=len(validation_commands),
        smoke_command_count=len(smoke_commands),
        audit_command_count=len(audit_commands),
    )


def wrapper_only_retry_escalation_label(state: WrapperOnlyRetryState) -> str:
    return (
        "full apply review required"
        if state.missing_target_files
        else "stay narrow"
    )


def render_wrapper_only_retry_scope_lines(
    state: WrapperOnlyRetryState,
) -> tuple[str, ...]:
    return (
        "Scope    : wrapper-only retry",
        f"Mode     : {state.mode}",
        f"Kind     : {state.retry_kind}",
        "Writes Skipped : yes",
        "Intent   : recover evidence/reporting after likely wrapper failure",
        f"Reason   : {state.reason}",
        f"Explicit : {'yes' if state.explicit_retry_required else 'no'}",
        f"Expected : {len(state.expected_target_files)}",
        f"Existing : {len(state.existing_target_files)}",
        f"Missing  : {len(state.missing_target_files)}",
        f"Validate : {state.validation_command_count}",
        f"Smoke    : {state.smoke_command_count}",
        f"Audit    : {state.audit_command_count}",
        f"Escalate : {wrapper_only_retry_escalation_label(state)}",
    )


def render_wrapper_only_retry_report_lines(
    state: WrapperOnlyRetryState,
) -> tuple[str, ...]:
    return (
        f"Retry Kind       : {state.retry_kind}",
        f"Retry Reason     : {state.reason}",
        f"Writes Skipped   : {'yes' if state.writes_skipped else 'no'}",
        f"Explicit Retry   : {'yes' if state.explicit_retry_required else 'no'}",
        f"Expected Targets : {len(state.expected_target_files)}",
        f"Existing Targets : {len(state.existing_target_files)}",
        f"Missing Targets  : {len(state.missing_target_files)}",
        f"Validation Count : {state.validation_command_count}",
        f"Smoke Count      : {state.smoke_command_count}",
        f"Audit Count      : {state.audit_command_count}",
        f"Escalation       : {wrapper_only_retry_escalation_label(state)}",
    )


def wrapper_only_retry_needs_escalation(state: WrapperOnlyRetryState) -> bool:
    return bool(state.missing_target_files)


def wrapper_only_retry_allows_writes(state: WrapperOnlyRetryState) -> bool:
    _ = state
    return False


def wrapper_only_retry_state_as_dict(
    state: WrapperOnlyRetryState,
) -> dict[str, Any]:
    return {
        "mode": state.mode,
        "retry_kind": state.retry_kind,
        "reason": state.reason,
        "writes_skipped": state.writes_skipped,
        "explicit_retry_required": state.explicit_retry_required,
        "expected_target_files": list(state.expected_target_files),
        "existing_target_files": list(state.existing_target_files),
        "missing_target_files": list(state.missing_target_files),
        "validation_command_count": state.validation_command_count,
        "smoke_command_count": state.smoke_command_count,
        "audit_command_count": state.audit_command_count,
        "needs_escalation": wrapper_only_retry_needs_escalation(state),
        "allows_writes": wrapper_only_retry_allows_writes(state),
        "scope_lines": list(render_wrapper_only_retry_scope_lines(state)),
        "report_lines": list(render_wrapper_only_retry_report_lines(state)),
    }



def execute_wrapper_only_retry(
    manifest_path,
    wrapper_project_root=None,
    reason=None,
):
    _ = reason
    result = verify_only(
        manifest_path,
        wrapper_project_root=wrapper_project_root,
    )
    result.mode="wrapper_only_retry"
    return result
