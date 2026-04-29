"""Run lock for the optional LLM browser runner.

The lock prevents overlapping browser-runner driven PatchOps executions.
It is deliberately passive and filesystem-based:
- it imports no Selenium modules,
- it starts no browser driver,
- it does not run PatchOps,
- it does not click or download anything,
- it only reads/writes/removes a small JSON lock file.

The default stale-lock rule is conservative:
- if the recorded PID no longer exists, the lock is stale;
- if heartbeat age exceeds stale_after_seconds, the lock is stale.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import errno
import json
import os
from pathlib import Path
import shutil
from typing import Callable, Mapping


STORE_SCHEMA_VERSION = "1"
DEFAULT_LOCK_FILENAME = "run.lock"
DEFAULT_STALE_AFTER_SECONDS = 60 * 60


ClockFn = Callable[[], datetime]
ProcessExistsFn = Callable[[int], bool]


@dataclass(frozen=True)
class RunLockRecord:
    pid: int
    owner: str
    acquired_at: str
    heartbeat_at: str
    metadata: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "pid": self.pid,
            "owner": self.owner,
            "acquired_at": self.acquired_at,
            "heartbeat_at": self.heartbeat_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "RunLockRecord":
        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        return cls(
            pid=int(payload.get("pid", 0)),
            owner=str(payload.get("owner", "")).strip(),
            acquired_at=str(payload.get("acquired_at", "")).strip(),
            heartbeat_at=str(payload.get("heartbeat_at", "")).strip(),
            metadata=dict(metadata),
        )


@dataclass(frozen=True)
class RunLockDecision:
    locked: bool
    reason: str
    path: Path
    record: RunLockRecord | None
    existing_record: RunLockRecord | None = None
    recovered_stale: bool = False
    backup_path: Path | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "locked": self.locked,
            "reason": self.reason,
            "path": str(self.path),
            "record": None if self.record is None else self.record.to_payload(),
            "existing_record": None if self.existing_record is None else self.existing_record.to_payload(),
            "recovered_stale": self.recovered_stale,
            "backup_path": None if self.backup_path is None else str(self.backup_path),
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now(clock: ClockFn | None = None) -> str:
    current = utc_now() if clock is None else clock()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).isoformat(timespec="seconds")


def parse_iso_datetime(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def default_lock_path(*, environ: Mapping[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ

    explicit = env.get("PATCHOPS_LLM_BROWSER_RUN_LOCK")
    if explicit:
        return Path(explicit).expanduser()

    root = env.get("PATCHOPS_LLM_BROWSER_STORE_DIR")
    if root:
        return Path(root).expanduser() / DEFAULT_LOCK_FILENAME

    local_app_data = env.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "PatchOps" / "llm_browser" / DEFAULT_LOCK_FILENAME

    return Path.home() / ".patchops" / "llm_browser" / DEFAULT_LOCK_FILENAME


def process_exists(pid: int) -> bool:
    """Return whether pid appears alive.

    This avoids requiring psutil. Tests inject their own ProcessExistsFn.
    """

    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False

    if pid <= 0:
        return False
    if pid == os.getpid():
        return True

    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, wintypes.DWORD(pid))
            if not handle:
                return False
            kernel32.CloseHandle(handle)
            return True
        except Exception:
            return False

    try:
        os.kill(pid, 0)
    except OSError as exc:
        return exc.errno == errno.EPERM
    return True


class RunLock:
    def __init__(
        self,
        path: str | Path | None = None,
        *,
        owner: str = "patchops-llm-browser",
        stale_after_seconds: float = DEFAULT_STALE_AFTER_SECONDS,
        clock: ClockFn | None = None,
        process_exists_fn: ProcessExistsFn = process_exists,
        pid: int | None = None,
    ) -> None:
        if stale_after_seconds <= 0:
            raise ValueError("stale_after_seconds must be positive")

        self.path = default_lock_path() if path is None else Path(path)
        self.owner = owner
        self.stale_after_seconds = float(stale_after_seconds)
        self.clock = clock or utc_now
        self.process_exists_fn = process_exists_fn
        self.pid = os.getpid() if pid is None else int(pid)
        self.record: RunLockRecord | None = None

    def read_record(self) -> RunLockRecord | None:
        if not self.path.exists():
            return None
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("run lock payload must be a JSON object")
        if str(payload.get("schema_version", "")).strip() != STORE_SCHEMA_VERSION:
            raise ValueError("run lock schema_version is unsupported")
        lock_payload = payload.get("lock")
        if not isinstance(lock_payload, dict):
            raise ValueError("run lock payload missing lock object")
        return RunLockRecord.from_payload(lock_payload)

    def is_stale(self, record: RunLockRecord) -> bool:
        if not self.process_exists_fn(record.pid):
            return True

        heartbeat = parse_iso_datetime(record.heartbeat_at)
        if heartbeat is None:
            return True

        now = self.clock()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        age = (now.astimezone(timezone.utc) - heartbeat).total_seconds()
        return age > self.stale_after_seconds

    def acquire(
        self,
        *,
        metadata: Mapping[str, object] | None = None,
        recover_stale: bool = True,
    ) -> RunLockDecision:
        existing_record: RunLockRecord | None = None
        backup_path: Path | None = None
        recovered_stale = False

        if self.path.exists():
            try:
                existing_record = self.read_record()
            except Exception:
                if not recover_stale:
                    return RunLockDecision(
                        locked=False,
                        reason="corrupt_lock_present",
                        path=self.path,
                        record=None,
                        existing_record=None,
                    )
                backup_path = self._backup_existing_lock("corrupt")
                self._remove_lock_file()
                recovered_stale = True
            else:
                if existing_record is not None and not self.is_stale(existing_record):
                    return RunLockDecision(
                        locked=False,
                        reason="lock_already_held",
                        path=self.path,
                        record=None,
                        existing_record=existing_record,
                    )

                if not recover_stale:
                    return RunLockDecision(
                        locked=False,
                        reason="stale_lock_present",
                        path=self.path,
                        record=None,
                        existing_record=existing_record,
                    )

                backup_path = self._backup_existing_lock("stale")
                self._remove_lock_file()
                recovered_stale = True

        record = self._build_record(metadata=metadata)
        self._write_record(record)
        self.record = record
        return RunLockDecision(
            locked=True,
            reason="lock_acquired",
            path=self.path,
            record=record,
            existing_record=existing_record,
            recovered_stale=recovered_stale,
            backup_path=backup_path,
        )

    def heartbeat(self) -> RunLockDecision:
        current = self.read_record()
        if current is None:
            return RunLockDecision(False, "lock_missing", self.path, None)

        if current.pid != self.pid:
            return RunLockDecision(False, "lock_owned_by_another_pid", self.path, None, existing_record=current)

        updated = RunLockRecord(
            pid=current.pid,
            owner=current.owner,
            acquired_at=current.acquired_at,
            heartbeat_at=iso_now(self.clock),
            metadata=current.metadata,
        )
        self._write_record(updated)
        self.record = updated
        return RunLockDecision(True, "heartbeat_updated", self.path, updated)

    def release(self) -> RunLockDecision:
        if not self.path.exists():
            self.record = None
            return RunLockDecision(True, "lock_already_missing", self.path, None)

        try:
            current = self.read_record()
        except Exception:
            return RunLockDecision(False, "lock_corrupt_not_released", self.path, None)

        if current is not None and current.pid != self.pid:
            return RunLockDecision(False, "lock_owned_by_another_pid", self.path, None, existing_record=current)

        self._remove_lock_file()
        self.record = None
        return RunLockDecision(True, "lock_released", self.path, current)

    def __enter__(self) -> "RunLock":
        decision = self.acquire()
        if not decision.locked:
            raise RuntimeError(f"unable to acquire run lock: {decision.reason}")
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self.release()
        return False

    def _build_record(self, *, metadata: Mapping[str, object] | None = None) -> RunLockRecord:
        timestamp = iso_now(self.clock)
        return RunLockRecord(
            pid=self.pid,
            owner=self.owner,
            acquired_at=timestamp,
            heartbeat_at=timestamp,
            metadata=dict(metadata or {}),
        )

    def _write_record(self, record: RunLockRecord) -> None:
        payload = {
            "schema_version": STORE_SCHEMA_VERSION,
            "lock": record.to_payload(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_name(self.path.name + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_path.replace(self.path)

    def _remove_lock_file(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    def _backup_existing_lock(self, reason: str) -> Path | None:
        if not self.path.exists():
            return None
        stamp = iso_now(self.clock).replace(":", "").replace("+", "_").replace("-", "").replace("T", "_")
        backup_path = self.path.with_name(f"{self.path.name}.{reason}.{stamp}.bak")
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.path, backup_path)
        return backup_path
