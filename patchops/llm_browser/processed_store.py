"""Processed artifact store for the optional LLM browser runner.

The store prevents duplicate PatchOps bundle execution by remembering completed
download artifacts by sha256 and by useful lookup metadata such as filename,
href, local path, result, and report path.

It is intentionally passive:
- it imports no Selenium modules,
- it starts no browser driver,
- it does not run PatchOps,
- it does not click or download anything,
- it only reads/writes a small JSON state file.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Callable, Iterable, Mapping, Sequence

from .chat_page_contract import ArtifactCandidate


ClockFn = Callable[[], datetime]


STORE_SCHEMA_VERSION = "1"
DEFAULT_STORE_FILENAME = "processed_artifacts.json"


@dataclass(frozen=True)
class StoreRepairResult:
    repaired: bool
    reason: str
    backup_path: Path | None

    def to_payload(self) -> dict[str, object]:
        return {
            "repaired": self.repaired,
            "reason": self.reason,
            "backup_path": None if self.backup_path is None else str(self.backup_path),
        }


@dataclass(frozen=True)
class ProcessedArtifactRecord:
    sha256: str
    filename: str
    path: str
    processed_at: str
    result: str
    report_path: str | None = None
    href: str | None = None
    notes: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, object]:
        return {
            "sha256": self.sha256,
            "filename": self.filename,
            "path": self.path,
            "processed_at": self.processed_at,
            "result": self.result,
            "report_path": self.report_path,
            "href": self.href,
            "notes": list(self.notes),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "ProcessedArtifactRecord":
        notes_value = payload.get("notes", ())
        if isinstance(notes_value, list):
            notes = tuple(str(item) for item in notes_value)
        elif isinstance(notes_value, tuple):
            notes = tuple(str(item) for item in notes_value)
        elif notes_value:
            notes = (str(notes_value),)
        else:
            notes = ()

        return cls(
            sha256=str(payload.get("sha256", "")).strip().lower(),
            filename=str(payload.get("filename", "")).strip(),
            path=str(payload.get("path", "")).strip(),
            processed_at=str(payload.get("processed_at", "")).strip(),
            result=str(payload.get("result", "")).strip(),
            report_path=_optional_str(payload.get("report_path")),
            href=_optional_str(payload.get("href")),
            notes=notes,
        )


@dataclass(frozen=True)
class ProcessedArtifactDecision:
    should_process: bool
    reason: str
    sha256: str | None
    existing_record: ProcessedArtifactRecord | None
    filename_conflicts: tuple[ProcessedArtifactRecord, ...]

    @property
    def warning(self) -> str | None:
        if self.filename_conflicts and self.should_process:
            return "same_filename_different_hash"
        return None

    def to_payload(self) -> dict[str, object]:
        return {
            "should_process": self.should_process,
            "reason": self.reason,
            "sha256": self.sha256,
            "existing_record": None if self.existing_record is None else self.existing_record.to_payload(),
            "filename_conflicts": [record.to_payload() for record in self.filename_conflicts],
            "warning": self.warning,
        }


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_store_path(*, environ: Mapping[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ

    explicit = env.get("PATCHOPS_LLM_BROWSER_PROCESSED_STORE")
    if explicit:
        return Path(explicit).expanduser()

    root = env.get("PATCHOPS_LLM_BROWSER_STORE_DIR")
    if root:
        return Path(root).expanduser() / DEFAULT_STORE_FILENAME

    local_app_data = env.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "PatchOps" / "llm_browser" / DEFAULT_STORE_FILENAME

    return Path.home() / ".patchops" / "llm_browser" / DEFAULT_STORE_FILENAME


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    target = Path(path)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_key(value: str | None) -> str:
    return "" if value is None else str(value).strip().lower()


class ProcessedArtifactStore:
    def __init__(
        self,
        path: str | Path | None = None,
        *,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self.path = default_store_path() if path is None else Path(path)
        self.clock = clock or utc_now_iso
        self.last_repair = StoreRepairResult(False, "not_loaded", None)
        self._records: list[ProcessedArtifactRecord] | None = None

    def load(self) -> tuple[ProcessedArtifactRecord, ...]:
        if self._records is not None:
            return tuple(self._records)

        if not self.path.exists():
            self._records = []
            self.last_repair = StoreRepairResult(False, "missing_store", None)
            return ()

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            records_payload = payload.get("records", []) if isinstance(payload, dict) else []
            if not isinstance(records_payload, list):
                raise ValueError("processed artifact store records must be a list")

            records = [ProcessedArtifactRecord.from_payload(item) for item in records_payload if isinstance(item, dict)]
            self._records = self._dedupe_records(records)
            self.last_repair = StoreRepairResult(False, "loaded", None)
            return tuple(self._records)
        except Exception:
            backup = self._backup_corrupt_store()
            self._records = []
            self._write_payload([])
            self.last_repair = StoreRepairResult(True, "corrupt_store_repaired", backup)
            return ()

    def records(self) -> tuple[ProcessedArtifactRecord, ...]:
        return self.load()

    def to_payload(self) -> dict[str, object]:
        return {
            "schema_version": STORE_SCHEMA_VERSION,
            "store_path": str(self.path),
            "records": [record.to_payload() for record in self.records()],
            "last_repair": self.last_repair.to_payload(),
        }

    def processed_keys(self) -> set[str]:
        keys: set[str] = set()
        for record in self.records():
            for value in (record.sha256, record.filename, record.href, record.path):
                key = _canonical_key(value)
                if key:
                    keys.add(key)
        return keys

    def contains_sha256(self, sha256: str) -> bool:
        wanted = _canonical_key(sha256)
        return any(_canonical_key(record.sha256) == wanted for record in self.records())

    def find_by_sha256(self, sha256: str) -> ProcessedArtifactRecord | None:
        wanted = _canonical_key(sha256)
        for record in self.records():
            if _canonical_key(record.sha256) == wanted:
                return record
        return None

    def find_by_filename(self, filename: str) -> tuple[ProcessedArtifactRecord, ...]:
        wanted = _canonical_key(filename)
        return tuple(record for record in self.records() if _canonical_key(record.filename) == wanted)

    def decide_for_file(
        self,
        path: str | Path,
        *,
        candidate: ArtifactCandidate | None = None,
    ) -> ProcessedArtifactDecision:
        target = Path(path)
        if not target.exists() or not target.is_file():
            return ProcessedArtifactDecision(
                should_process=False,
                reason="artifact_file_missing",
                sha256=None,
                existing_record=None,
                filename_conflicts=(),
            )

        digest = sha256_file(target)
        existing = self.find_by_sha256(digest)
        if existing is not None:
            return ProcessedArtifactDecision(
                should_process=False,
                reason="sha256_already_processed",
                sha256=digest,
                existing_record=existing,
                filename_conflicts=(),
            )

        filename = candidate.filename if candidate is not None else target.name
        filename_conflicts = tuple(
            record for record in self.find_by_filename(filename)
            if _canonical_key(record.sha256) != _canonical_key(digest)
        )

        return ProcessedArtifactDecision(
            should_process=True,
            reason="new_artifact",
            sha256=digest,
            existing_record=None,
            filename_conflicts=filename_conflicts,
        )

    def mark_processed(
        self,
        path: str | Path,
        *,
        result: str,
        report_path: str | Path | None = None,
        candidate: ArtifactCandidate | None = None,
        notes: Iterable[str] = (),
        processed_at: str | None = None,
    ) -> ProcessedArtifactRecord:
        target = Path(path)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"processed artifact file does not exist: {target}")

        digest = sha256_file(target)
        filename = candidate.filename if candidate is not None else target.name
        href = candidate.href if candidate is not None else None

        record = ProcessedArtifactRecord(
            sha256=digest,
            filename=filename,
            path=str(target),
            processed_at=processed_at or self.clock(),
            result=str(result).strip(),
            report_path=None if report_path is None else str(report_path),
            href=href,
            notes=tuple(str(note) for note in notes),
        )

        records = list(self.records())
        records = [existing for existing in records if _canonical_key(existing.sha256) != _canonical_key(digest)]
        records.append(record)
        self._records = self._dedupe_records(records)
        self._write_payload(self._records)
        return record

    def _dedupe_records(self, records: Sequence[ProcessedArtifactRecord]) -> list[ProcessedArtifactRecord]:
        by_hash: dict[str, ProcessedArtifactRecord] = {}
        for record in records:
            key = _canonical_key(record.sha256)
            if not key:
                continue
            by_hash[key] = record
        return list(by_hash.values())

    def _write_payload(self, records: Sequence[ProcessedArtifactRecord]) -> None:
        payload = {
            "schema_version": STORE_SCHEMA_VERSION,
            "records": [record.to_payload() for record in records],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_name(self.path.name + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_path.replace(self.path)

    def _backup_corrupt_store(self) -> Path | None:
        if not self.path.exists():
            return None
        stamp = self.clock().replace(":", "").replace("+", "_").replace("-", "").replace("T", "_")
        backup_path = self.path.with_name(f"{self.path.name}.corrupt.{stamp}.bak")
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.path, backup_path)
        return backup_path
