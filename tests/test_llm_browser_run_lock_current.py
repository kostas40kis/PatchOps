from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from patchops.llm_browser.run_lock import (
    RunLock,
    RunLockRecord,
    default_lock_path,
    parse_iso_datetime,
    process_exists,
)


def _dt(hour: int = 12, minute: int = 0) -> datetime:
    return datetime(2026, 4, 29, hour, minute, tzinfo=timezone.utc)


def test_default_lock_path_uses_explicit_lock_path(tmp_path: Path) -> None:
    explicit = tmp_path / "custom.lock"

    assert default_lock_path(environ={"PATCHOPS_LLM_BROWSER_RUN_LOCK": str(explicit)}) == explicit


def test_default_lock_path_uses_store_dir(tmp_path: Path) -> None:
    root = tmp_path / "state"

    assert default_lock_path(environ={"PATCHOPS_LLM_BROWSER_STORE_DIR": str(root)}) == root / "run.lock"


def test_default_lock_path_uses_localappdata(tmp_path: Path) -> None:
    local = tmp_path / "LocalAppData"

    assert default_lock_path(environ={"LOCALAPPDATA": str(local)}) == local / "PatchOps" / "llm_browser" / "run.lock"


def test_acquire_creates_lock_file_with_metadata(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    lock = RunLock(path, owner="unit-test", clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=123)

    decision = lock.acquire(metadata={"artifact": "patch_d0_14_run_lock_patchops_bundle.zip"})

    assert decision.locked is True
    assert decision.reason == "lock_acquired"
    assert decision.record is not None
    assert decision.record.pid == 123
    assert decision.record.owner == "unit-test"
    assert decision.record.metadata["artifact"] == "patch_d0_14_run_lock_patchops_bundle.zip"
    assert path.exists()

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1"
    assert payload["lock"]["pid"] == 123


def test_second_runner_exits_cleanly_when_lock_is_live(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    first = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=111)
    first.acquire()

    second = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=222)
    decision = second.acquire()

    assert decision.locked is False
    assert decision.reason == "lock_already_held"
    assert decision.existing_record is not None
    assert decision.existing_record.pid == 111


def test_stale_lock_recovered_when_pid_no_longer_exists(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    first = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=111)
    first.acquire()

    second = RunLock(path, clock=lambda: _dt(12, 1), process_exists_fn=lambda _pid: False, pid=222)
    decision = second.acquire()

    assert decision.locked is True
    assert decision.recovered_stale is True
    assert decision.backup_path is not None
    assert decision.backup_path.exists()
    assert decision.record is not None
    assert decision.record.pid == 222


def test_stale_lock_recovered_when_heartbeat_is_too_old(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    first = RunLock(path, clock=lambda: _dt(12, 0), process_exists_fn=lambda _pid: True, pid=111, stale_after_seconds=60)
    first.acquire()

    second = RunLock(path, clock=lambda: _dt(12, 2), process_exists_fn=lambda _pid: True, pid=222, stale_after_seconds=60)
    decision = second.acquire()

    assert decision.locked is True
    assert decision.reason == "lock_acquired"
    assert decision.recovered_stale is True
    assert decision.existing_record is not None
    assert decision.existing_record.pid == 111
    assert decision.record is not None
    assert decision.record.pid == 222


def test_stale_lock_can_be_reported_without_recovery(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    first = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: False, pid=111)
    first.acquire()

    second = RunLock(path, clock=lambda: _dt(12, 1), process_exists_fn=lambda _pid: False, pid=222)
    decision = second.acquire(recover_stale=False)

    assert decision.locked is False
    assert decision.reason == "stale_lock_present"


def test_corrupt_lock_is_backed_up_and_recovered(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    path.write_text("{not-json", encoding="utf-8")
    lock = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=123)

    decision = lock.acquire()

    assert decision.locked is True
    assert decision.recovered_stale is True
    assert decision.backup_path is not None
    assert decision.backup_path.exists()
    assert "{not-json" in decision.backup_path.read_text(encoding="utf-8")


def test_corrupt_lock_can_block_when_recovery_disabled(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    path.write_text("{not-json", encoding="utf-8")
    lock = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=123)

    decision = lock.acquire(recover_stale=False)

    assert decision.locked is False
    assert decision.reason == "corrupt_lock_present"


def test_heartbeat_updates_owned_lock(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    moments = iter([_dt(12, 0), _dt(12, 5)])
    lock = RunLock(path, clock=lambda: next(moments), process_exists_fn=lambda _pid: True, pid=123)
    lock.acquire()

    decision = lock.heartbeat()

    assert decision.locked is True
    assert decision.reason == "heartbeat_updated"
    assert decision.record is not None
    assert decision.record.heartbeat_at == "2026-04-29T12:05:00+00:00"


def test_heartbeat_refuses_foreign_lock(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=111).acquire()

    second = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=222)
    decision = second.heartbeat()

    assert decision.locked is False
    assert decision.reason == "lock_owned_by_another_pid"


def test_release_removes_owned_lock_and_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    lock = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=123)
    lock.acquire()

    first = lock.release()
    second = lock.release()

    assert first.locked is True
    assert first.reason == "lock_released"
    assert second.locked is True
    assert second.reason == "lock_already_missing"
    assert path.exists() is False


def test_release_refuses_foreign_lock(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=111).acquire()

    second = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=222)
    decision = second.release()

    assert decision.locked is False
    assert decision.reason == "lock_owned_by_another_pid"
    assert path.exists()


def test_context_manager_releases_lock_on_exit(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    with RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=123) as lock:
        assert path.exists()
        assert lock.record is not None

    assert path.exists() is False


def test_context_manager_releases_lock_on_exception(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    with pytest.raises(RuntimeError, match="boom"):
        with RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=123):
            raise RuntimeError("boom")

    assert path.exists() is False


def test_context_manager_raises_when_lock_cannot_be_acquired(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=111).acquire()

    with pytest.raises(RuntimeError, match="unable to acquire run lock"):
        with RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=222):
            pass


def test_parse_iso_datetime_handles_empty_and_bad_values() -> None:
    assert parse_iso_datetime("") is None
    assert parse_iso_datetime("not-a-date") is None
    assert parse_iso_datetime("2026-04-29T12:00:00+00:00") is not None


def test_record_payload_roundtrip() -> None:
    record = RunLockRecord(
        pid=123,
        owner="unit-test",
        acquired_at="2026-04-29T12:00:00+00:00",
        heartbeat_at="2026-04-29T12:00:00+00:00",
        metadata={"artifact": "patch.zip"},
    )

    loaded = RunLockRecord.from_payload(record.to_payload())

    assert loaded == record


def test_decision_payload_is_compact(tmp_path: Path) -> None:
    path = tmp_path / "run.lock"
    lock = RunLock(path, clock=lambda: _dt(), process_exists_fn=lambda _pid: True, pid=123)
    decision = lock.acquire(metadata={"artifact": "patch.zip"})

    payload = decision.to_payload()

    assert payload["locked"] is True
    assert payload["reason"] == "lock_acquired"
    assert payload["path"] == str(path)
    assert payload["record"]["pid"] == 123
    assert payload["existing_record"] is None


def test_process_exists_returns_false_for_invalid_pid() -> None:
    assert process_exists(0) is False
    assert process_exists(-10) is False
