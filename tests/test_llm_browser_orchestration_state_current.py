from __future__ import annotations

import pytest

from patchops.llm_browser.orchestration_state import (
    OrchestrationSnapshot,
    OrchestrationState,
    OrchestrationStateError,
    can_transition,
    legal_next_states,
    new_orchestration_snapshot,
    normalize_state,
    reset_for_next_reply,
    status_from_patchops_result,
    transition,
)


def test_new_snapshot_defaults_to_idle() -> None:
    snapshot = new_orchestration_snapshot(browser="edge")

    assert snapshot.state == OrchestrationState.IDLE
    assert snapshot.browser == "edge"
    assert snapshot.failure_count == 0
    assert snapshot.max_failures == 3
    assert snapshot.active is True
    assert snapshot.blocked is False
    assert snapshot.should_stop is False


def test_new_snapshot_rejects_nonpositive_max_failures() -> None:
    with pytest.raises(ValueError, match="max_failures"):
        new_orchestration_snapshot(max_failures=0)


def test_normalize_state_accepts_enum_value_and_case_insensitive_string() -> None:
    assert normalize_state(OrchestrationState.IDLE) == OrchestrationState.IDLE
    assert normalize_state("IDLE") == OrchestrationState.IDLE
    assert normalize_state("waiting_for_reply_stable") == OrchestrationState.WAITING_FOR_REPLY_STABLE


def test_state_machine_happy_path() -> None:
    snapshot = new_orchestration_snapshot(browser="edge")
    snapshot = transition(snapshot, "WAITING_FOR_REPLY_STABLE", reason="tick")
    snapshot = transition(snapshot, OrchestrationState.LOOKING_FOR_ARTIFACT, reason="reply_stable")
    snapshot = transition(
        snapshot,
        OrchestrationState.DOWNLOADING,
        reason="artifact_found",
        artifact_filename="patch_d0_16_orchestration_state_model_patchops_bundle.zip",
    )
    snapshot = transition(
        snapshot,
        OrchestrationState.RUNNING_PATCHOPS,
        reason="download_ready",
        downloaded_path=r"C:\Users\kostas\Downloads\patch_d0_16_orchestration_state_model_patchops_bundle.zip",
    )
    snapshot = transition(
        snapshot,
        OrchestrationState.SUMMARY_READY,
        reason="patchops_done",
        canonical_report_path=r"C:\Users\kostas\Desktop\patchops_run_package_20260429_191600.txt",
    )
    snapshot = transition(snapshot, OrchestrationState.WAITING_FOR_USER_NEXT_REPLY, reason="summary_inserted")

    assert snapshot.state == OrchestrationState.WAITING_FOR_USER_NEXT_REPLY
    assert len(snapshot.history) == 6
    assert snapshot.artifact_filename == "patch_d0_16_orchestration_state_model_patchops_bundle.zip"
    assert snapshot.downloaded_path is not None
    assert snapshot.canonical_report_path is not None


def test_illegal_transition_is_rejected() -> None:
    snapshot = new_orchestration_snapshot()

    with pytest.raises(OrchestrationStateError, match="illegal transition"):
        transition(snapshot, OrchestrationState.RUNNING_PATCHOPS, reason="skip_everything")


def test_terminal_blocked_states_do_not_transition() -> None:
    snapshot = new_orchestration_snapshot()
    snapshot = transition(snapshot, OrchestrationState.WAITING_FOR_REPLY_STABLE, reason="tick")
    snapshot = transition(snapshot, OrchestrationState.BLOCKED_DRIVER_FAILURE, reason="driver_closed")

    assert snapshot.blocked is True
    assert snapshot.should_stop is True
    assert can_transition(snapshot.state, OrchestrationState.IDLE) is False

    with pytest.raises(OrchestrationStateError):
        transition(snapshot, OrchestrationState.IDLE, reason="try_reset")


def test_legal_next_states_are_stable_and_sorted() -> None:
    states = legal_next_states(OrchestrationState.LOOKING_FOR_ARTIFACT)

    assert states == tuple(sorted(states, key=lambda item: item.value))
    assert OrchestrationState.DOWNLOADING in states
    assert OrchestrationState.BLOCKED_ARTIFACT_MISSING in states


def test_failure_increment_can_block_repeated_failures() -> None:
    snapshot = new_orchestration_snapshot(max_failures=2)
    snapshot = transition(snapshot, OrchestrationState.WAITING_FOR_REPLY_STABLE, reason="tick")
    snapshot = transition(
        snapshot,
        OrchestrationState.LOOKING_FOR_ARTIFACT,
        reason="first_selector_retry",
        failure_increment=1,
        last_error="selector not ready",
    )
    snapshot = transition(
        snapshot,
        OrchestrationState.BLOCKED_SELECTOR_DRIFT,
        reason="selector drift confirmed",
        failure_increment=1,
        last_error="latest assistant container not found",
    )

    assert snapshot.state == OrchestrationState.BLOCKED_SELECTOR_DRIFT
    assert snapshot.failure_count == 2
    assert snapshot.should_stop is True
    assert snapshot.last_error == "latest assistant container not found"


def test_repeated_failure_threshold_blocks_active_transition() -> None:
    snapshot = new_orchestration_snapshot(max_failures=1)
    snapshot = transition(
        snapshot,
        OrchestrationState.WAITING_FOR_REPLY_STABLE,
        reason="tick_with_failure",
        failure_increment=1,
        last_error="driver hiccup",
    )

    assert snapshot.state == OrchestrationState.BLOCKED_REPEATED_FAILURES
    assert snapshot.should_stop is True
    assert snapshot.last_error == "driver hiccup"


def test_failure_increment_rejects_negative_values() -> None:
    snapshot = new_orchestration_snapshot()

    with pytest.raises(ValueError, match="failure_increment"):
        transition(snapshot, OrchestrationState.WAITING_FOR_REPLY_STABLE, reason="bad", failure_increment=-1)


def test_reset_for_next_reply_requires_waiting_state() -> None:
    snapshot = new_orchestration_snapshot()

    with pytest.raises(OrchestrationStateError):
        reset_for_next_reply(snapshot)


def test_reset_for_next_reply_transitions_to_waiting_for_stability() -> None:
    snapshot = new_orchestration_snapshot()
    snapshot = transition(snapshot, OrchestrationState.WAITING_FOR_REPLY_STABLE, reason="tick")
    snapshot = transition(snapshot, OrchestrationState.LOOKING_FOR_ARTIFACT, reason="stable")
    snapshot = transition(snapshot, OrchestrationState.DOWNLOADING, reason="found")
    snapshot = transition(snapshot, OrchestrationState.RUNNING_PATCHOPS, reason="downloaded")
    snapshot = transition(snapshot, OrchestrationState.SUMMARY_READY, reason="done")
    snapshot = transition(snapshot, OrchestrationState.WAITING_FOR_USER_NEXT_REPLY, reason="summary_inserted")

    reset = reset_for_next_reply(snapshot)

    assert reset.state == OrchestrationState.WAITING_FOR_REPLY_STABLE
    assert reset.history[-1].reason == "waiting_for_next_reply"


def test_status_from_patchops_result_maps_report_presence() -> None:
    assert status_from_patchops_result(True, report_path=r"C:\Users\kostas\Desktop\report.txt") == OrchestrationState.SUMMARY_READY
    assert status_from_patchops_result(True, report_path=None) == OrchestrationState.BLOCKED_REPORT_MISSING
    assert status_from_patchops_result(False, report_path=r"C:\Users\kostas\Desktop\report.txt") == OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED


def test_snapshot_payload_is_compact_and_stable() -> None:
    snapshot = new_orchestration_snapshot(browser="opera")
    snapshot = transition(
        snapshot,
        OrchestrationState.WAITING_FOR_REPLY_STABLE,
        reason="tick",
        metadata={"interval_seconds": 10},
    )

    payload = snapshot.to_payload()

    assert payload["state"] == "WAITING_FOR_REPLY_STABLE"
    assert payload["browser"] == "opera"
    assert payload["blocked"] is False
    assert payload["active"] is True
    assert payload["history"][0]["from_state"] == "IDLE"
    assert payload["history"][0]["to_state"] == "WAITING_FOR_REPLY_STABLE"
    assert payload["history"][0]["metadata"] == {"interval_seconds": 10}


def test_can_transition_covers_blocked_run_lock_from_idle() -> None:
    assert can_transition(OrchestrationState.IDLE, OrchestrationState.BLOCKED_RUN_LOCK_HELD) is True
    assert can_transition(OrchestrationState.RUNNING_PATCHOPS, OrchestrationState.BLOCKED_RUN_LOCK_HELD) is False


def test_orchestration_snapshot_can_be_constructed_for_reported_failure() -> None:
    snapshot = OrchestrationSnapshot(
        state=OrchestrationState.BLOCKED_REPORT_MISSING,
        artifact_filename="patch_missing_report_patchops_bundle.zip",
        failure_count=1,
        max_failures=3,
        last_error="canonical report was not found",
    )

    assert snapshot.blocked is True
    assert snapshot.active is False
    assert snapshot.should_stop is True
