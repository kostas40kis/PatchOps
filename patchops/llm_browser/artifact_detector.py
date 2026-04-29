"""Downloadable PatchOps artifact detector for the LLM browser runner.

This module consumes the passive ChatPageSnapshot produced by
chat_page_contract.py and decides whether there is a runnable PatchOps zip
bundle in the latest assistant reply.

It is intentionally passive:
- it imports no Selenium modules,
- it starts no browser driver,
- it does not click/download anything,
- it does not run PatchOps,
- it emits compact metadata only.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence

from .chat_page_contract import ArtifactCandidate, ChatPageSnapshot


PATCHOPS_BUNDLE_RE = re.compile(
    r"^patch_[A-Za-z0-9][A-Za-z0-9_.-]*_patchops_bundle\.zip$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ArtifactDetectionResult:
    found: bool
    candidate: ArtifactCandidate | None
    reason: str
    candidates_seen: tuple[ArtifactCandidate, ...]
    ignored_filenames: tuple[str, ...]

    @property
    def filename(self) -> str | None:
        return None if self.candidate is None else self.candidate.filename

    @property
    def href(self) -> str | None:
        return None if self.candidate is None else self.candidate.href

    def to_payload(self) -> dict[str, object]:
        return {
            "found": self.found,
            "reason": self.reason,
            "filename": self.filename,
            "href": self.href,
            "candidates_seen": [candidate.to_payload() for candidate in self.candidates_seen],
            "ignored_filenames": list(self.ignored_filenames),
        }


def normalize_artifact_key(value: str) -> str:
    return value.strip().lower()


def is_patchops_bundle_filename(filename: str) -> bool:
    return bool(PATCHOPS_BUNDLE_RE.fullmatch(filename.strip()))


def _processed_key_set(processed_artifacts: Iterable[str] | None) -> set[str]:
    if processed_artifacts is None:
        return set()
    return {normalize_artifact_key(item) for item in processed_artifacts if item and item.strip()}


def _candidate_keys(candidate: ArtifactCandidate) -> set[str]:
    keys = {normalize_artifact_key(candidate.filename)}
    if candidate.href:
        keys.add(normalize_artifact_key(candidate.href))
    return keys


def candidate_is_processed(candidate: ArtifactCandidate, processed_artifacts: Iterable[str] | None) -> bool:
    processed = _processed_key_set(processed_artifacts)
    if not processed:
        return False
    return bool(_candidate_keys(candidate) & processed)


def filter_patchops_bundle_candidates(
    candidates: Sequence[ArtifactCandidate],
    *,
    processed_artifacts: Iterable[str] | None = None,
) -> tuple[tuple[ArtifactCandidate, ...], tuple[str, ...]]:
    processed = _processed_key_set(processed_artifacts)
    accepted: list[ArtifactCandidate] = []
    ignored: list[str] = []

    for candidate in candidates:
        if not is_patchops_bundle_filename(candidate.filename):
            ignored.append(candidate.filename)
            continue

        candidate_keys = _candidate_keys(candidate)
        if candidate_keys & processed:
            ignored.append(candidate.filename)
            continue

        accepted.append(candidate)

    return tuple(accepted), tuple(ignored)


def detect_downloadable_patchops_artifact(
    snapshot: ChatPageSnapshot,
    *,
    processed_artifacts: Iterable[str] | None = None,
) -> ArtifactDetectionResult:
    """Find the first unprocessed PatchOps bundle candidate in a ready snapshot."""

    if not snapshot.has_latest_assistant_reply:
        return ArtifactDetectionResult(
            found=False,
            candidate=None,
            reason="missing_latest_assistant_reply",
            candidates_seen=(),
            ignored_filenames=(),
        )

    if snapshot.streaming:
        return ArtifactDetectionResult(
            found=False,
            candidate=None,
            reason="reply_still_streaming",
            candidates_seen=snapshot.artifact_candidates,
            ignored_filenames=tuple(candidate.filename for candidate in snapshot.artifact_candidates),
        )

    if not snapshot.composer_enabled:
        return ArtifactDetectionResult(
            found=False,
            candidate=None,
            reason="composer_not_ready",
            candidates_seen=snapshot.artifact_candidates,
            ignored_filenames=tuple(candidate.filename for candidate in snapshot.artifact_candidates),
        )

    accepted, ignored = filter_patchops_bundle_candidates(
        snapshot.artifact_candidates,
        processed_artifacts=processed_artifacts,
    )

    if not accepted:
        reason = "no_patchops_bundle_candidates"
        if snapshot.artifact_candidates and len(ignored) == len(snapshot.artifact_candidates):
            processed = _processed_key_set(processed_artifacts)
            all_processed = bool(processed) and all(
                _candidate_keys(candidate) & processed
                for candidate in snapshot.artifact_candidates
                if is_patchops_bundle_filename(candidate.filename)
            )
            reason = "artifact_already_processed" if all_processed else "no_unprocessed_patchops_bundle_candidates"

        return ArtifactDetectionResult(
            found=False,
            candidate=None,
            reason=reason,
            candidates_seen=snapshot.artifact_candidates,
            ignored_filenames=ignored,
        )

    # href-backed candidates are emitted first by chat_page_contract, and that
    # preference is preserved here.
    return ArtifactDetectionResult(
        found=True,
        candidate=accepted[0],
        reason="found",
        candidates_seen=snapshot.artifact_candidates,
        ignored_filenames=ignored,
    )
