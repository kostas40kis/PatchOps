from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from patchops.llm_browser.audit_log import (
    AuditEvent,
    AuditLog,
    append_audit_event,
    build_audit_event,
    default_audit_log_path,
    event_from_integration_result,
    event_from_summary,
    sanitize_metadata,
)


def _clock() -> datetime:
    return datetime(2026, 4, 29, 19, 36, tzinfo=timezone.utc)


class SummaryLike:
    status = "PASS"
    patch = "D0.24 minimal audit log"
    report_path = r"C:\Users\kostas\Desktop\patchops_run_package_20260429_193600.txt"
    next_action = "Continue with the next patch."


class StateValue:
    value = "SUMMARY_READY"


class SnapshotLike:
    state = StateValue()
    artifact_filename = "patch_d0_24_minimal_audit_log_patchops_bundle.zip"
    artifact_sha256 = "abc123"
    last_error = None


class DryRunLike:
    snapshot = SnapshotLike()
    pasteback_summary = SummaryLike()
    artifact_detection = None
    planned_actions = ("would_acquire_run_lock", "would_paste_summary_without_submit")


class IntegrationLike:
    dry_run = DryRunLike()
    side_effects_performed = ()
    blocked_reason = None
    ok = True
    blocked = False


def test_default_audit_log_path_uses_explicit_path(tmp_path: Path) -> None:
    explicit = tmp_path / "audit.jsonl"

    assert default_audit_log_path(environ={"PATCHOPS_LLM_BROWSER_AUDIT_LOG": str(explicit)}) == explicit


def test_default_audit_log_path_uses_store_dir(tmp_path: Path) -> None:
    root = tmp_path / "state"

    assert default_audit_log_path(environ={"PATCHOPS_LLM_BROWSER_STORE_DIR": str(root)}) == root / "audit.jsonl"


def test_default_audit_log_path_uses_localappdata(tmp_path: Path) -> None:
    local = tmp_path / "LocalAppData"

    assert default_audit_log_path(environ={"LOCALAPPDATA": str(local)}) == local / "PatchOps" / "llm_browser" / "audit.jsonl"


def test_sanitize_metadata_keeps_scalars_arrays_and_clamps_long_values() -> None:
    metadata = sanitize_metadata(
        {
            "ok": True,
            "count": 3,
            "long": "x" * 20,
            "list": [1, 2],
            "empty key after strip": None,
        },
        max_value_length=8,
    )

    assert metadata["ok"] is True
    assert metadata["count"] == 3
    assert metadata["long"] == "xxxxxxx…"
    assert metadata["list"] == [1, 2]

    with pytest.raises(ValueError, match="max_value_length"):
        sanitize_metadata({"a": "b"}, max_value_length=0)


def test_build_audit_event_requires_event_type_and_source() -> None:
    with pytest.raises(ValueError, match="event_type"):
        build_audit_event("", clock=_clock)

    with pytest.raises(ValueError, match="source"):
        build_audit_event("event", source="", clock=_clock)


def test_build_audit_event_payload_omits_none_fields() -> None:
    event = build_audit_event(
        "integration_result",
        source="unit-test",
        status="PASS",
        patch="D0.24 minimal audit log",
        report_path=r"C:\Users\kostas\Desktop\report.txt",
        state="SUMMARY_READY",
        reason=None,
        event_id="fixed-id",
        clock=_clock,
    )

    payload = event.to_payload()

    assert payload["event_type"] == "integration_result"
    assert payload["event_id"] == "fixed-id"
    assert payload["timestamp"] == "2026-04-29T19:36:00+00:00"
    assert payload["source"] == "unit-test"
    assert payload["status"] == "PASS"
    assert payload["patch"] == "D0.24 minimal audit log"
    assert payload["report_path"] == r"C:\Users\kostas\Desktop\report.txt"
    assert payload["state"] == "SUMMARY_READY"
    assert "reason" not in payload


def test_audit_event_roundtrip_from_payload() -> None:
    event = AuditEvent.from_payload(
        {
            "event_type": "run",
            "event_id": "id1",
            "timestamp": "now",
            "source": "unit",
            "status": "PASS",
            "metadata": {"a": 1},
        }
    )

    assert event.event_type == "run"
    assert event.event_id == "id1"
    assert event.status == "PASS"
    assert event.metadata == {"a": 1}


def test_audit_log_append_and_read_events(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, clock=_clock)

    result = log.append(
        "dry_run_result",
        status="FAIL",
        state="BLOCKED_ARTIFACT_MISSING",
        reason="no_patchops_bundle_candidates",
        metadata={"planned_actions": ["scan"]},
    )

    assert result.written is True
    assert result.path == path
    assert result.event_id is not None
    assert result.rotated is False

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["event_type"] == "dry_run_result"
    assert payload["status"] == "FAIL"
    assert payload["metadata"]["planned_actions"] == ["scan"]

    events = log.read_events()
    assert len(events) == 1
    assert events[0].reason == "no_patchops_bundle_candidates"


def test_audit_log_read_limit_returns_latest_events(tmp_path: Path) -> None:
    log = AuditLog(tmp_path / "audit.jsonl", clock=_clock)

    log.append_event(build_audit_event("one", event_id="1", clock=_clock))
    log.append_event(build_audit_event("two", event_id="2", clock=_clock))
    log.append_event(build_audit_event("three", event_id="3", clock=_clock))

    events = log.read_events(limit=2)

    assert [event.event_id for event in events] == ["2", "3"]

    with pytest.raises(ValueError, match="limit"):
        log.read_events(limit=-1)


def test_audit_log_ignores_corrupt_json_lines(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    path.write_text('{"event_type":"ok","event_id":"1","timestamp":"now","source":"unit"}\nnot-json\n', encoding="utf-8")
    log = AuditLog(path)

    events = log.read_events()

    assert len(events) == 1
    assert events[0].event_type == "ok"


def test_audit_log_rotates_when_file_is_too_large(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    path.write_text("x" * 20, encoding="utf-8")
    log = AuditLog(path, max_bytes=10, clock=_clock)

    result = log.append_event(build_audit_event("rotated", event_id="rotated-id", clock=_clock))

    assert result.rotated is True
    assert result.rotation_path is not None
    assert result.rotation_path.exists()
    assert result.rotation_path.read_text(encoding="utf-8") == "x" * 20
    assert path.exists()
    assert "rotated-id" in path.read_text(encoding="utf-8")


def test_append_audit_event_helper_writes_event(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"

    result = append_audit_event(
        "helper_event",
        path=path,
        status="PASS",
        metadata={"source_test": True},
    )

    assert result.written is True
    assert "helper_event" in path.read_text(encoding="utf-8")


def test_event_from_summary_uses_summary_fields() -> None:
    event = event_from_summary(SummaryLike(), metadata={"note": "ok"}, clock=_clock)

    assert event.event_type == "pasteback_summary"
    assert event.status == "PASS"
    assert event.patch == "D0.24 minimal audit log"
    assert event.report_path == r"C:\Users\kostas\Desktop\patchops_run_package_20260429_193600.txt"
    assert event.reason == "Continue with the next patch."
    assert event.metadata == {"note": "ok"}


def test_event_from_integration_result_is_compact() -> None:
    event = event_from_integration_result(IntegrationLike(), clock=_clock)
    payload = event.to_payload()

    assert payload["event_type"] == "integration_result"
    assert payload["status"] == "PASS"
    assert payload["patch"] == "D0.24 minimal audit log"
    assert payload["artifact_filename"] == "patch_d0_24_minimal_audit_log_patchops_bundle.zip"
    assert payload["artifact_sha256"] == "abc123"
    assert payload["state"] == "SUMMARY_READY"
    assert payload["metadata"]["ok"] is True
    assert payload["metadata"]["blocked"] is False
    assert payload["metadata"]["planned_actions"] == ["would_acquire_run_lock", "would_paste_summary_without_submit"]
    assert payload["metadata"]["side_effects_performed"] == []
    assert "text" not in payload
