from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from patchops.workflows.verify_only import resolve_verify_only_expected_target_files


DEFAULT_WRAPPER_ONLY_RETRY_REASON = (
    "wrapper/reporting failure after likely content success"
)
WRAPPER_ONLY_RETRY_KIND = "wrapper_only_retry"


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


def build_wrapper_only_retry_state(
    manifest: Mapping[str, Any],
    target_project_root: str | Path,
    reason: str | None = None,
) -> WrapperOnlyRetryState:
    expected = tuple(
        resolve_verify_only_expected_target_files(manifest, target_project_root)
    )
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


def render_wrapper_only_retry_scope_lines(
    state: WrapperOnlyRetryState,
) -> tuple[str, ...]:
    escalate = (
        "full apply review required"
        if state.missing_target_files
        else "stay narrow"
    )
    return (
        "Scope    : wrapper-only retry",
        f"Mode     : {state.mode}",
        f"Kind     : {state.retry_kind}",
        "Writes   : skipped",
        "Intent   : recover evidence/reporting after likely wrapper failure",
        f"Reason   : {state.reason}",
        f"Explicit : {'yes' if state.explicit_retry_required else 'no'}",
        f"Expected : {len(state.expected_target_files)}",
        f"Existing : {len(state.existing_target_files)}",
        f"Missing  : {len(state.missing_target_files)}",
        f"Validate : {state.validation_command_count}",
        f"Smoke    : {state.smoke_command_count}",
        f"Audit    : {state.audit_command_count}",
        f"Escalate : {escalate}",
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
    }