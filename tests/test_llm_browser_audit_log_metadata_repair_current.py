from __future__ import annotations

from datetime import datetime, timezone

from patchops.llm_browser.audit_log import build_audit_event, sanitize_metadata


def _clock() -> datetime:
    return datetime(2026, 4, 29, 19, 40, tzinfo=timezone.utc)


def test_audit_metadata_preserves_json_arrays_for_planned_actions() -> None:
    metadata = sanitize_metadata(
        {
            "planned_actions": ["would_acquire_run_lock", "would_paste_summary_without_submit"],
            "side_effects_performed": [],
        }
    )

    assert metadata["planned_actions"] == ["would_acquire_run_lock", "would_paste_summary_without_submit"]
    assert metadata["side_effects_performed"] == []


def test_audit_metadata_preserves_nested_json_shape_and_clamps_string_leaves() -> None:
    metadata = sanitize_metadata(
        {
            "nested": {
                "actions": ["download", "patchops"],
                "long": "x" * 12,
            },
            "tuple_value": ("a", "b"),
            "object_value": object(),
        },
        max_value_length=6,
    )

    assert metadata["nested"]["actions"] == ["downl…", "patch…"]
    assert metadata["nested"]["long"] == "xxxxx…"
    assert metadata["tuple_value"] == ["a", "b"]
    assert isinstance(metadata["object_value"], str)


def test_audit_event_payload_preserves_structured_metadata() -> None:
    event = build_audit_event(
        "integration_result",
        status="PASS",
        metadata={
            "planned_actions": ["would_acquire_run_lock"],
            "side_effects_performed": [],
            "details": {"ok": True},
        },
        event_id="fixed",
        clock=_clock,
    )

    payload = event.to_payload()

    assert payload["metadata"]["planned_actions"] == ["would_acquire_run_lock"]
    assert payload["metadata"]["side_effects_performed"] == []
    assert payload["metadata"]["details"] == {"ok": True}
