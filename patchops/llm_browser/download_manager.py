"""Download manager helpers for the optional LLM browser runner.

This module validates and observes downloaded PatchOps bundle files on disk.

It is intentionally passive:
- it imports no Selenium modules,
- it starts no browser driver,
- it does not click/download anything,
- it does not run PatchOps,
- it only inspects local filesystem state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import time
from typing import Callable, Iterable

from .artifact_detector import is_patchops_bundle_filename
from .chat_page_contract import ArtifactCandidate


NowFn = Callable[[], float]
SleepFn = Callable[[float], None]


PARTIAL_SUFFIXES: tuple[str, ...] = (
    ".crdownload",
    ".part",
    ".tmp",
)


@dataclass(frozen=True)
class DownloadState:
    path: Path
    exists: bool
    complete: bool
    stable: bool
    size_bytes: int | None
    age_seconds: float | None
    partial_paths: tuple[Path, ...]
    reason: str

    @property
    def ready(self) -> bool:
        return self.exists and self.complete and self.stable

    def to_payload(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "complete": self.complete,
            "stable": self.stable,
            "size_bytes": self.size_bytes,
            "age_seconds": self.age_seconds,
            "partial_paths": [str(path) for path in self.partial_paths],
            "reason": self.reason,
            "ready": self.ready,
        }


@dataclass(frozen=True)
class DownloadWaitResult:
    state: DownloadState
    attempts: int
    elapsed_seconds: float
    timed_out: bool

    @property
    def ready(self) -> bool:
        return self.state.ready

    def to_payload(self) -> dict[str, object]:
        return {
            "ready": self.ready,
            "attempts": self.attempts,
            "elapsed_seconds": self.elapsed_seconds,
            "timed_out": self.timed_out,
            "state": self.state.to_payload(),
        }


@dataclass(frozen=True)
class PreparedDownloadArtifact:
    source_path: Path
    prepared_path: Path
    filename: str
    copied: bool
    size_bytes: int

    def to_payload(self) -> dict[str, object]:
        return {
            "source_path": str(self.source_path),
            "prepared_path": str(self.prepared_path),
            "filename": self.filename,
            "copied": self.copied,
            "size_bytes": self.size_bytes,
        }


def validate_download_filename(filename: str) -> str:
    cleaned = (filename or "").strip()
    if not cleaned:
        raise ValueError("download filename must not be empty")
    if Path(cleaned).name != cleaned:
        raise ValueError("download filename must be a single path segment")
    if cleaned in {".", ".."} or ".." in Path(cleaned).parts:
        raise ValueError("download filename must not contain traversal")
    if not is_patchops_bundle_filename(cleaned):
        raise ValueError("download filename must match patch_*_patchops_bundle.zip")
    return cleaned


def expected_download_path(download_dir: str | Path, filename: str) -> Path:
    safe_filename = validate_download_filename(filename)
    root = Path(download_dir).expanduser()
    return root / safe_filename


def expected_download_path_for_candidate(download_dir: str | Path, candidate: ArtifactCandidate) -> Path:
    return expected_download_path(download_dir, candidate.filename)


def partial_download_paths(path: str | Path) -> tuple[Path, ...]:
    target = Path(path)
    return tuple(target.with_name(target.name + suffix) for suffix in PARTIAL_SUFFIXES)


def _existing_partial_paths(path: Path) -> tuple[Path, ...]:
    return tuple(partial for partial in partial_download_paths(path) if partial.exists())


def inspect_download_state(
    path: str | Path,
    *,
    min_stable_age_seconds: float = 1.0,
    now: NowFn | None = None,
) -> DownloadState:
    if min_stable_age_seconds < 0:
        raise ValueError("min_stable_age_seconds must not be negative")

    clock = time.time if now is None else now
    target = Path(path)
    partials = _existing_partial_paths(target)

    if partials:
        return DownloadState(
            path=target,
            exists=target.exists(),
            complete=False,
            stable=False,
            size_bytes=target.stat().st_size if target.exists() else None,
            age_seconds=None,
            partial_paths=partials,
            reason="partial_download_present",
        )

    if not target.exists():
        return DownloadState(
            path=target,
            exists=False,
            complete=False,
            stable=False,
            size_bytes=None,
            age_seconds=None,
            partial_paths=(),
            reason="missing",
        )

    if not target.is_file():
        return DownloadState(
            path=target,
            exists=True,
            complete=False,
            stable=False,
            size_bytes=None,
            age_seconds=None,
            partial_paths=(),
            reason="not_a_file",
        )

    stat = target.stat()
    age = max(0.0, float(clock()) - float(stat.st_mtime))
    stable = age >= float(min_stable_age_seconds)
    return DownloadState(
        path=target,
        exists=True,
        complete=True,
        stable=stable,
        size_bytes=stat.st_size,
        age_seconds=age,
        partial_paths=(),
        reason="ready" if stable else "not_stable_yet",
    )


def wait_for_download_ready(
    path: str | Path,
    *,
    timeout_seconds: float = 60.0,
    poll_seconds: float = 1.0,
    min_stable_age_seconds: float = 1.0,
    now: NowFn | None = None,
    sleep: SleepFn | None = None,
) -> DownloadWaitResult:
    if timeout_seconds < 0:
        raise ValueError("timeout_seconds must not be negative")
    if poll_seconds <= 0:
        raise ValueError("poll_seconds must be positive")

    clock = time.time if now is None else now
    sleeper = time.sleep if sleep is None else sleep
    started_at = float(clock())
    attempts = 0

    while True:
        attempts += 1
        state = inspect_download_state(path, min_stable_age_seconds=min_stable_age_seconds, now=clock)
        elapsed = max(0.0, float(clock()) - started_at)

        if state.ready:
            return DownloadWaitResult(state=state, attempts=attempts, elapsed_seconds=elapsed, timed_out=False)

        if elapsed >= timeout_seconds:
            return DownloadWaitResult(state=state, attempts=attempts, elapsed_seconds=elapsed, timed_out=True)

        sleeper(min(float(poll_seconds), max(0.0, timeout_seconds - elapsed)))


def prepare_downloaded_artifact(
    source_path: str | Path,
    prepared_dir: str | Path,
    *,
    copy: bool = True,
) -> PreparedDownloadArtifact:
    source = Path(source_path)
    safe_filename = validate_download_filename(source.name)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"downloaded artifact does not exist: {source}")

    destination_root = Path(prepared_dir)
    destination_root.mkdir(parents=True, exist_ok=True)
    destination = destination_root / safe_filename

    if copy:
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
            copied = True
        else:
            copied = False
    else:
        destination = source
        copied = False

    size = destination.stat().st_size
    return PreparedDownloadArtifact(
        source_path=source,
        prepared_path=destination,
        filename=safe_filename,
        copied=copied,
        size_bytes=size,
    )


def wait_for_candidate_download(
    candidate: ArtifactCandidate,
    *,
    download_dir: str | Path,
    timeout_seconds: float = 60.0,
    poll_seconds: float = 1.0,
    min_stable_age_seconds: float = 1.0,
    now: NowFn | None = None,
    sleep: SleepFn | None = None,
) -> DownloadWaitResult:
    path = expected_download_path_for_candidate(download_dir, candidate)
    return wait_for_download_ready(
        path,
        timeout_seconds=timeout_seconds,
        poll_seconds=poll_seconds,
        min_stable_age_seconds=min_stable_age_seconds,
        now=now,
        sleep=sleep,
    )
