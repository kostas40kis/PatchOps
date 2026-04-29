"""Minimal audit log for the optional LLM browser runner.

The audit log records compact JSONL events for browser-runner decisions and
future operator-facing actions. It is deliberately passive:
- imports no Selenium modules,
- starts no browser driver,
- does not click or download anything,
- does not run PatchOps,
- does not paste or send anything,
- only appends compact JSON lines to a local file.

The log is intended to answer: what did the runner decide, what would it have
done, and where is the canonical evidence/report?
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
from typing import Callable, Mapping
import uuid


DEFAULT_AUDIT_FILENAME = "audit.jsonl"
DEFAULT_MAX_BYTES = 1024 * 1024
ClockFn = Callable[[], datetime]


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    event_id: str
    timestamp: str
    source: str
    status: str | None = None
    patch: str | None = None
    artifact_filename: str | None = None
    artifact_sha256: str | None = None
    report_path: str | None = None
    state: str | None = None
    reason: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "event_type": self.event_type,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "source": self.source,
        }
        optional = {
            "status": self.status,
            "patch": self.patch,
            "artifact_filename": self.artifact_filename,
            "artifact_sha256": self.artifact_sha256,
            "report_path": self.report_path,
            "state": self.state,
            "reason": self.reason,
        }
        for key, value in optional.items():
            if value is not None:
                payload[key] = value
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "AuditEvent":
        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {"value": metadata}
        return cls(
            event_type=str(payload.get("event_type", "")).strip(),
            event_id=str(payload.get("event_id", "")).strip(),
            timestamp=str(payload.get("timestamp", "")).strip(),
            source=str(payload.get("source", "")).strip(),
            status=_optional_str(payload.get("status")),
            patch=_optional_str(payload.get("patch")),
            artifact_filename=_optional_str(payload.get("artifact_filename")),
            artifact_sha256=_optional_str(payload.get("artifact_sha256")),
            report_path=_optional_str(payload.get("report_path")),
            state=_optional_str(payload.get("state")),
            reason=_optional_str(payload.get("reason")),
            metadata=dict(metadata),
        )


@dataclass(frozen=True)
class AuditWriteResult:
    written: bool
    path: Path
    event_id: str | None
    rotated: bool
    rotation_path: Path | None
    reason: str

    def to_payload(self) -> dict[str, object]:
        return {
            "written": self.written,
            "path": str(self.path),
            "event_id": self.event_id,
            "rotated": self.rotated,
            "rotation_path": None if self.rotation_path is None else str(self.rotation_path),
            "reason": self.reason,
        }


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now(clock: ClockFn | None = None) -> str:
    current = utc_now() if clock is None else clock()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).isoformat(timespec="seconds")


def default_audit_log_path(*, environ: Mapping[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ

    explicit = env.get("PATCHOPS_LLM_BROWSER_AUDIT_LOG")
    if explicit:
        return Path(explicit).expanduser()

    root = env.get("PATCHOPS_LLM_BROWSER_STORE_DIR")
    if root:
        return Path(root).expanduser() / DEFAULT_AUDIT_FILENAME

    local_app_data = env.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "PatchOps" / "llm_browser" / DEFAULT_AUDIT_FILENAME

    return Path.home() / ".patchops" / "llm_browser" / DEFAULT_AUDIT_FILENAME


def _sanitize_json_value(value: object, *, max_value_length: int, depth: int = 0) -> object:
    """Return a compact JSON-safe value while preserving JSON-native shape."""

    if depth > 8:
        return "…"

    if value is None or isinstance(value, (int, float, bool)):
        return value

    if isinstance(value, str):
        if len(value) > max_value_length:
            return value[: max_value_length - 1].rstrip() + "…"
        return value

    if isinstance(value, (list, tuple)):
        return [
            _sanitize_json_value(item, max_value_length=max_value_length, depth=depth + 1)
            for item in value
        ]

    if isinstance(value, dict):
        safe: dict[str, object] = {}
        for key, nested in value.items():
            key_text = str(key).strip()
            if not key_text:
                continue
            safe[key_text] = _sanitize_json_value(
                nested,
                max_value_length=max_value_length,
                depth=depth + 1,
            )
        return safe

    return _sanitize_json_value(str(value), max_value_length=max_value_length, depth=depth + 1)


def sanitize_metadata(metadata: Mapping[str, object] | None, *, max_value_length: int = 500) -> dict[str, object]:
    if not metadata:
        return {}
    if max_value_length <= 0:
        raise ValueError("max_value_length must be positive")

    safe: dict[str, object] = {}
    for key, value in metadata.items():
        key_text = str(key).strip()
        if not key_text:
            continue
        safe[key_text] = _sanitize_json_value(value, max_value_length=max_value_length)

    return safe


def build_audit_event(
    event_type: str,
    *,
    source: str = "llm_browser",
    status: str | None = None,
    patch: str | None = None,
    artifact_filename: str | None = None,
    artifact_sha256: str | None = None,
    report_path: str | Path | None = None,
    state: str | None = None,
    reason: str | None = None,
    metadata: Mapping[str, object] | None = None,
    event_id: str | None = None,
    timestamp: str | None = None,
    clock: ClockFn | None = None,
) -> AuditEvent:
    event_type_text = str(event_type).strip()
    if not event_type_text:
        raise ValueError("event_type must not be empty")
    source_text = str(source).strip()
    if not source_text:
        raise ValueError("source must not be empty")

    return AuditEvent(
        event_type=event_type_text,
        event_id=event_id or uuid.uuid4().hex,
        timestamp=timestamp or iso_now(clock),
        source=source_text,
        status=_optional_str(status),
        patch=_optional_str(patch),
        artifact_filename=_optional_str(artifact_filename),
        artifact_sha256=_optional_str(artifact_sha256),
        report_path=None if report_path is None else _optional_str(str(report_path)),
        state=_optional_str(state),
        reason=_optional_str(reason),
        metadata=sanitize_metadata(metadata),
    )


def event_from_summary(
    summary: object,
    *,
    event_type: str = "pasteback_summary",
    source: str = "llm_browser",
    metadata: Mapping[str, object] | None = None,
    clock: ClockFn | None = None,
) -> AuditEvent:
    return build_audit_event(
        event_type,
        source=source,
        status=getattr(summary, "status", None),
        patch=getattr(summary, "patch", None),
        report_path=getattr(summary, "report_path", None),
        reason=getattr(summary, "next_action", None),
        metadata=metadata,
        clock=clock,
    )


def event_from_dry_run_result(
    result: object,
    *,
    event_type: str = "dry_run_result",
    source: str = "llm_browser",
    clock: ClockFn | None = None,
) -> AuditEvent:
    snapshot = getattr(result, "snapshot", None)
    pasteback = getattr(result, "pasteback_summary", None)
    artifact_detection = getattr(result, "artifact_detection", None)
    planned_actions = getattr(result, "planned_actions", ())
    side_effects = getattr(result, "side_effects_performed", ())

    return build_audit_event(
        event_type,
        source=source,
        status=getattr(pasteback, "status", None),
        patch=getattr(pasteback, "patch", None),
        artifact_filename=getattr(snapshot, "artifact_filename", None)
        or getattr(getattr(artifact_detection, "candidate", None), "filename", None),
        artifact_sha256=getattr(snapshot, "artifact_sha256", None),
        report_path=getattr(pasteback, "report_path", None),
        state=None if snapshot is None else getattr(getattr(snapshot, "state", None), "value", str(getattr(snapshot, "state", ""))),
        reason=getattr(snapshot, "last_error", None) or getattr(pasteback, "next_action", None),
        metadata={
            "ok": bool(getattr(result, "ok", False)),
            "blocked": bool(getattr(result, "blocked", False)),
            "planned_actions": list(planned_actions),
            "side_effects_performed": list(side_effects),
        },
        clock=clock,
    )


def event_from_integration_result(
    result: object,
    *,
    event_type: str = "integration_result",
    source: str = "llm_browser",
    clock: ClockFn | None = None,
) -> AuditEvent:
    dry_run = getattr(result, "dry_run", None)
    snapshot = getattr(dry_run, "snapshot", None)
    pasteback = getattr(dry_run, "pasteback_summary", None)
    artifact_detection = getattr(dry_run, "artifact_detection", None)

    planned_actions = getattr(dry_run, "planned_actions", ())
    side_effects = getattr(result, "side_effects_performed", ())
    blocked_reason = getattr(result, "blocked_reason", None)

    return build_audit_event(
        event_type,
        source=source,
        status=getattr(pasteback, "status", None),
        patch=getattr(pasteback, "patch", None),
        artifact_filename=getattr(snapshot, "artifact_filename", None)
        or getattr(getattr(artifact_detection, "candidate", None), "filename", None),
        artifact_sha256=getattr(snapshot, "artifact_sha256", None),
        report_path=getattr(pasteback, "report_path", None),
        state=None if snapshot is None else getattr(getattr(snapshot, "state", None), "value", str(getattr(snapshot, "state", ""))),
        reason=blocked_reason or getattr(snapshot, "last_error", None) or getattr(pasteback, "next_action", None),
        metadata={
            "ok": bool(getattr(result, "ok", False)),
            "blocked": bool(getattr(result, "blocked", False)),
            "planned_actions": list(planned_actions),
            "side_effects_performed": list(side_effects),
        },
        clock=clock,
    )


class AuditLog:
    def __init__(
        self,
        path: str | Path | None = None,
        *,
        max_bytes: int = DEFAULT_MAX_BYTES,
        clock: ClockFn | None = None,
    ) -> None:
        if max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        self.path = default_audit_log_path() if path is None else Path(path)
        self.max_bytes = int(max_bytes)
        self.clock = clock or utc_now

    def append_event(self, event: AuditEvent) -> AuditWriteResult:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        rotated = False
        rotation_path: Path | None = None

        if self.path.exists() and self.path.stat().st_size >= self.max_bytes:
            rotation_path = self._rotate()
            rotated = True

        line = json.dumps(event.to_payload(), sort_keys=True, separators=(",", ":")) + "\n"
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)

        return AuditWriteResult(
            written=True,
            path=self.path,
            event_id=event.event_id,
            rotated=rotated,
            rotation_path=rotation_path,
            reason="event_written",
        )

    def append(
        self,
        event_type: str,
        *,
        source: str = "llm_browser",
        status: str | None = None,
        patch: str | None = None,
        artifact_filename: str | None = None,
        artifact_sha256: str | None = None,
        report_path: str | Path | None = None,
        state: str | None = None,
        reason: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> AuditWriteResult:
        return self.append_event(
            build_audit_event(
                event_type,
                source=source,
                status=status,
                patch=patch,
                artifact_filename=artifact_filename,
                artifact_sha256=artifact_sha256,
                report_path=report_path,
                state=state,
                reason=reason,
                metadata=metadata,
                clock=self.clock,
            )
        )

    def read_events(self, *, limit: int | None = None) -> tuple[AuditEvent, ...]:
        if limit is not None and limit < 0:
            raise ValueError("limit must not be negative")
        if not self.path.exists():
            return ()

        events: list[AuditEvent] = []
        for line in self.path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                events.append(AuditEvent.from_payload(payload))

        if limit is not None:
            events = events[-limit:]
        return tuple(events)

    def _rotate(self) -> Path:
        stamp = iso_now(self.clock).replace(":", "").replace("+", "_").replace("-", "").replace("T", "_")
        rotation_path = self.path.with_name(f"{self.path.name}.{stamp}.bak")
        rotation_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(self.path), str(rotation_path))
        return rotation_path


def append_audit_event(
    event_type: str,
    *,
    path: str | Path | None = None,
    metadata: Mapping[str, object] | None = None,
    **kwargs: object,
) -> AuditWriteResult:
    log = AuditLog(path)
    event = build_audit_event(event_type, metadata=metadata, **kwargs)
    return log.append_event(event)
