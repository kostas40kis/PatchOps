"""Orchestration state model for the optional LLM browser runner.

This module describes the browser-runner loop without performing it.

It is intentionally passive:
- it imports no Selenium modules,
- it starts no browser driver,
- it does not click or download anything,
- it does not run PatchOps,
- it only validates state transitions and carries compact metadata.

The actual end-to-end runner can later compose:
page readiness -> artifact detection -> download bridge -> PatchOps runner ->
report locator -> pasteback summary -> composer helper.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence


class OrchestrationState(str, Enum):
    IDLE = "IDLE"
    WAITING_FOR_REPLY_STABLE = "WAITING_FOR_REPLY_STABLE"
    LOOKING_FOR_ARTIFACT = "LOOKING_FOR_ARTIFACT"
    DOWNLOADING = "DOWNLOADING"
    RUNNING_PATCHOPS = "RUNNING_PATCHOPS"
    SUMMARY_READY = "SUMMARY_READY"
    WAITING_FOR_USER_NEXT_REPLY = "WAITING_FOR_USER_NEXT_REPLY"

    BLOCKED_ARTIFACT_MISSING = "BLOCKED_ARTIFACT_MISSING"
    BLOCKED_DOWNLOAD_FAILED = "BLOCKED_DOWNLOAD_FAILED"
    BLOCKED_BAD_ZIP = "BLOCKED_BAD_ZIP"
    BLOCKED_PATCHOPS_RUN_FAILED = "BLOCKED_PATCHOPS_RUN_FAILED"
    BLOCKED_REPORT_MISSING = "BLOCKED_REPORT_MISSING"
    BLOCKED_SELECTOR_DRIFT = "BLOCKED_SELECTOR_DRIFT"
    BLOCKED_DRIVER_FAILURE = "BLOCKED_DRIVER_FAILURE"
    BLOCKED_RUN_LOCK_HELD = "BLOCKED_RUN_LOCK_HELD"
    BLOCKED_REPEATED_FAILURES = "BLOCKED_REPEATED_FAILURES"


TERMINAL_BLOCKED_STATES: frozenset[OrchestrationState] = frozenset(
    {
        OrchestrationState.BLOCKED_ARTIFACT_MISSING,
        OrchestrationState.BLOCKED_DOWNLOAD_FAILED,
        OrchestrationState.BLOCKED_BAD_ZIP,
        OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED,
        OrchestrationState.BLOCKED_REPORT_MISSING,
        OrchestrationState.BLOCKED_SELECTOR_DRIFT,
        OrchestrationState.BLOCKED_DRIVER_FAILURE,
        OrchestrationState.BLOCKED_RUN_LOCK_HELD,
        OrchestrationState.BLOCKED_REPEATED_FAILURES,
    }
)

ACTIVE_STATES: frozenset[OrchestrationState] = frozenset(
    {
        OrchestrationState.IDLE,
        OrchestrationState.WAITING_FOR_REPLY_STABLE,
        OrchestrationState.LOOKING_FOR_ARTIFACT,
        OrchestrationState.DOWNLOADING,
        OrchestrationState.RUNNING_PATCHOPS,
        OrchestrationState.SUMMARY_READY,
        OrchestrationState.WAITING_FOR_USER_NEXT_REPLY,
    }
)

LEGAL_TRANSITIONS: dict[OrchestrationState, frozenset[OrchestrationState]] = {
    OrchestrationState.IDLE: frozenset(
        {
            OrchestrationState.WAITING_FOR_REPLY_STABLE,
            OrchestrationState.BLOCKED_DRIVER_FAILURE,
            OrchestrationState.BLOCKED_RUN_LOCK_HELD,
        }
    ),
    OrchestrationState.WAITING_FOR_REPLY_STABLE: frozenset(
        {
            OrchestrationState.LOOKING_FOR_ARTIFACT,
            OrchestrationState.BLOCKED_SELECTOR_DRIFT,
            OrchestrationState.BLOCKED_DRIVER_FAILURE,
            OrchestrationState.BLOCKED_REPEATED_FAILURES,
        }
    ),
    OrchestrationState.LOOKING_FOR_ARTIFACT: frozenset(
        {
            OrchestrationState.DOWNLOADING,
            OrchestrationState.BLOCKED_ARTIFACT_MISSING,
            OrchestrationState.BLOCKED_SELECTOR_DRIFT,
            OrchestrationState.BLOCKED_REPEATED_FAILURES,
        }
    ),
    OrchestrationState.DOWNLOADING: frozenset(
        {
            OrchestrationState.RUNNING_PATCHOPS,
            OrchestrationState.BLOCKED_DOWNLOAD_FAILED,
            OrchestrationState.BLOCKED_BAD_ZIP,
            OrchestrationState.BLOCKED_REPEATED_FAILURES,
        }
    ),
    OrchestrationState.RUNNING_PATCHOPS: frozenset(
        {
            OrchestrationState.SUMMARY_READY,
            OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED,
            OrchestrationState.BLOCKED_REPORT_MISSING,
            OrchestrationState.BLOCKED_REPEATED_FAILURES,
        }
    ),
    OrchestrationState.SUMMARY_READY: frozenset(
        {
            OrchestrationState.WAITING_FOR_USER_NEXT_REPLY,
            OrchestrationState.BLOCKED_SELECTOR_DRIFT,
            OrchestrationState.BLOCKED_REPEATED_FAILURES,
        }
    ),
    OrchestrationState.WAITING_FOR_USER_NEXT_REPLY: frozenset(
        {
            OrchestrationState.WAITING_FOR_REPLY_STABLE,
            OrchestrationState.IDLE,
            OrchestrationState.BLOCKED_DRIVER_FAILURE,
            OrchestrationState.BLOCKED_REPEATED_FAILURES,
        }
    ),
}


class OrchestrationStateError(ValueError):
    """Raised when an illegal orchestration transition is requested."""


@dataclass(frozen=True)
class StateTransition:
    from_state: OrchestrationState
    to_state: OrchestrationState
    reason: str
    metadata: dict[str, object] = field(default_factory=dict)

    def to_payload(self) -> dict[str, object]:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class OrchestrationSnapshot:
    state: OrchestrationState
    artifact_filename: str | None = None
    artifact_sha256: str | None = None
    downloaded_path: str | None = None
    canonical_report_path: str | None = None
    browser: str | None = None
    failure_count: int = 0
    max_failures: int = 3
    last_error: str | None = None
    history: tuple[StateTransition, ...] = ()

    @property
    def blocked(self) -> bool:
        return self.state in TERMINAL_BLOCKED_STATES

    @property
    def active(self) -> bool:
        return self.state in ACTIVE_STATES

    @property
    def should_stop(self) -> bool:
        return self.blocked or self.failure_count >= self.max_failures

    def to_payload(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "artifact_filename": self.artifact_filename,
            "artifact_sha256": self.artifact_sha256,
            "downloaded_path": self.downloaded_path,
            "canonical_report_path": self.canonical_report_path,
            "browser": self.browser,
            "failure_count": self.failure_count,
            "max_failures": self.max_failures,
            "last_error": self.last_error,
            "blocked": self.blocked,
            "active": self.active,
            "should_stop": self.should_stop,
            "history": [transition.to_payload() for transition in self.history],
        }


def normalize_state(value: OrchestrationState | str) -> OrchestrationState:
    if isinstance(value, OrchestrationState):
        return value
    try:
        return OrchestrationState(str(value))
    except ValueError:
        upper = str(value).strip().upper()
        for state in OrchestrationState:
            if state.value == upper:
                return state
        raise


def can_transition(from_state: OrchestrationState | str, to_state: OrchestrationState | str) -> bool:
    source = normalize_state(from_state)
    destination = normalize_state(to_state)

    if source in TERMINAL_BLOCKED_STATES:
        return False

    return destination in LEGAL_TRANSITIONS.get(source, frozenset())


def legal_next_states(state: OrchestrationState | str) -> tuple[OrchestrationState, ...]:
    normalized = normalize_state(state)
    return tuple(sorted(LEGAL_TRANSITIONS.get(normalized, frozenset()), key=lambda item: item.value))


def transition(
    snapshot: OrchestrationSnapshot,
    to_state: OrchestrationState | str,
    *,
    reason: str,
    metadata: Mapping[str, object] | None = None,
    artifact_filename: str | None = None,
    artifact_sha256: str | None = None,
    downloaded_path: str | None = None,
    canonical_report_path: str | None = None,
    browser: str | None = None,
    last_error: str | None = None,
    failure_increment: int = 0,
) -> OrchestrationSnapshot:
    destination = normalize_state(to_state)

    if not can_transition(snapshot.state, destination):
        raise OrchestrationStateError(f"illegal transition: {snapshot.state.value} -> {destination.value}")

    if failure_increment < 0:
        raise ValueError("failure_increment must not be negative")

    next_failure_count = snapshot.failure_count + failure_increment
    final_state = destination
    final_error = last_error if last_error is not None else snapshot.last_error

    if final_state not in TERMINAL_BLOCKED_STATES and next_failure_count >= snapshot.max_failures:
        final_state = OrchestrationState.BLOCKED_REPEATED_FAILURES
        final_error = final_error or "repeated failure threshold reached"

    transition_record = StateTransition(
        from_state=snapshot.state,
        to_state=final_state,
        reason=reason,
        metadata=dict(metadata or {}),
    )

    return OrchestrationSnapshot(
        state=final_state,
        artifact_filename=artifact_filename if artifact_filename is not None else snapshot.artifact_filename,
        artifact_sha256=artifact_sha256 if artifact_sha256 is not None else snapshot.artifact_sha256,
        downloaded_path=downloaded_path if downloaded_path is not None else snapshot.downloaded_path,
        canonical_report_path=canonical_report_path if canonical_report_path is not None else snapshot.canonical_report_path,
        browser=browser if browser is not None else snapshot.browser,
        failure_count=next_failure_count,
        max_failures=snapshot.max_failures,
        last_error=final_error,
        history=snapshot.history + (transition_record,),
    )


def new_orchestration_snapshot(
    *,
    browser: str | None = None,
    max_failures: int = 3,
) -> OrchestrationSnapshot:
    if max_failures <= 0:
        raise ValueError("max_failures must be positive")
    return OrchestrationSnapshot(
        state=OrchestrationState.IDLE,
        browser=browser,
        max_failures=max_failures,
    )


def reset_for_next_reply(snapshot: OrchestrationSnapshot, *, reason: str = "waiting_for_next_reply") -> OrchestrationSnapshot:
    if snapshot.state != OrchestrationState.WAITING_FOR_USER_NEXT_REPLY:
        raise OrchestrationStateError("reset_for_next_reply requires WAITING_FOR_USER_NEXT_REPLY")
    return transition(snapshot, OrchestrationState.WAITING_FOR_REPLY_STABLE, reason=reason)


def status_from_patchops_result(ok: bool, *, report_path: str | None = None) -> OrchestrationState:
    if ok and report_path:
        return OrchestrationState.SUMMARY_READY
    if ok and not report_path:
        return OrchestrationState.BLOCKED_REPORT_MISSING
    return OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED
