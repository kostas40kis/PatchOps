"""Post-275 release evidence index.

Patch 280 adds a review-only release-evidence index for the accepted
post-275 frontier and the release batches that led to it.  The index is a
truth-synchronization/read-model surface only.  It never authorizes live
trading, wallet mutation, threshold widening, autonomous execution, or manual
review bypass.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Sequence, Tuple

_PASS = "PASS"
_INCOMPLETE = "INCOMPLETE"
_BLOCKED = "BLOCKED_INCOMPLETE_EVIDENCE"


@dataclass(frozen=True)
class ReleaseEvidenceEntry:
    """One release-evidence batch in the post-275 index."""

    patch_range: str
    title: str
    commit_sha: str = ""
    github_ci_run_id: str = ""
    release_result: str = _INCOMPLETE
    test_count: Optional[int] = None
    safety_summary: str = "Review-only; no live behavior widening."
    evidence_notes: Tuple[str, ...] = ()

    @property
    def patch_start(self) -> int:
        return _parse_patch_start(self.patch_range)

    @property
    def patch_end(self) -> int:
        return _parse_patch_end(self.patch_range)

    @property
    def has_remote_sha(self) -> bool:
        return bool(self.commit_sha.strip())

    @property
    def has_ci_evidence(self) -> bool:
        return bool(str(self.github_ci_run_id).strip())

    @property
    def is_complete(self) -> bool:
        return self.release_result.upper() == _PASS and self.has_remote_sha and self.has_ci_evidence

    @property
    def effective_result(self) -> str:
        if self.release_result.upper() == _PASS and not (self.has_remote_sha and self.has_ci_evidence):
            return _BLOCKED
        return self.release_result.upper()


@dataclass(frozen=True)
class ReleaseEvidenceIndex:
    """A chronological index of release evidence batches."""

    entries: Tuple[ReleaseEvidenceEntry, ...]

    @property
    def chronological_entries(self) -> Tuple[ReleaseEvidenceEntry, ...]:
        return tuple(sorted(self.entries, key=lambda item: (item.patch_start, item.patch_end)))

    @property
    def accepted_entries(self) -> Tuple[ReleaseEvidenceEntry, ...]:
        return tuple(entry for entry in self.chronological_entries if entry.is_complete)

    @property
    def incomplete_entries(self) -> Tuple[ReleaseEvidenceEntry, ...]:
        return tuple(entry for entry in self.chronological_entries if not entry.is_complete)

    @property
    def latest_accepted_entry(self) -> Optional[ReleaseEvidenceEntry]:
        accepted = self.accepted_entries
        return accepted[-1] if accepted else None

    @property
    def current_frontier_patch(self) -> Optional[int]:
        latest = self.latest_accepted_entry
        return latest.patch_end if latest else None


def _parse_patch_start(value: str) -> int:
    digits = []
    for char in value:
        if char.isdigit():
            digits.append(char)
        elif digits:
            break
    if not digits:
        raise ValueError(f"patch range has no numeric start: {value!r}")
    return int("".join(digits))


def _parse_patch_end(value: str) -> int:
    numbers = []
    current = []
    for char in value:
        if char.isdigit():
            current.append(char)
        elif current:
            numbers.append(int("".join(current)))
            current = []
    if current:
        numbers.append(int("".join(current)))
    if not numbers:
        raise ValueError(f"patch range has no numeric end: {value!r}")
    return numbers[-1]


def validate_release_entry(entry: ReleaseEvidenceEntry) -> Tuple[str, ...]:
    """Return fail-closed validation issues for one evidence entry."""
    issues = []
    if not entry.patch_range.strip():
        issues.append("missing patch range")
    if not entry.title.strip():
        issues.append("missing title")
    if entry.release_result.upper() == _PASS and not entry.has_remote_sha:
        issues.append("PASS entry missing remote commit SHA")
    if entry.release_result.upper() == _PASS and not entry.has_ci_evidence:
        issues.append("PASS entry missing GitHub CI run ID")
    if "submit" in entry.safety_summary.lower() and "does not submit" not in entry.safety_summary.lower():
        issues.append("safety summary contains ambiguous submit wording")
    return tuple(issues)


def build_release_evidence_index(entries: Iterable[ReleaseEvidenceEntry]) -> ReleaseEvidenceIndex:
    """Build a deterministic index ordered by patch range."""
    return ReleaseEvidenceIndex(tuple(sorted(tuple(entries), key=lambda item: (item.patch_start, item.patch_end))))


def default_post_275_release_evidence_entries() -> Tuple[ReleaseEvidenceEntry, ...]:
    """Return the maintained post-275 release evidence entries.

    Earlier post-252 batches are indexed even when the available roadmap text
    does not carry their exact commit/CI evidence.  Those entries are kept as
    incomplete rather than being falsely promoted to PASS.  The Patch 271-275
    batch contains the current accepted release evidence from the roadmap.
    """
    review_only = "Review-only / no-submit evidence; no wallet mutation, no live submission, no autonomous widening."
    return (
        ReleaseEvidenceEntry(
            patch_range="252",
            title="Accepted release gate script",
            release_result=_INCOMPLETE,
            safety_summary=review_only,
            evidence_notes=("Indexed from post-275 roadmap; remote SHA/CI details must be attached before PASS.",),
        ),
        ReleaseEvidenceEntry(
            patch_range="253",
            title="Green checkpoint tag and restore guide",
            release_result=_INCOMPLETE,
            safety_summary=review_only,
            evidence_notes=("Checkpoint tag evidence is required before this entry can be marked PASS.",),
        ),
        ReleaseEvidenceEntry(
            patch_range="254",
            title="Release-gate repair and pilot runbook",
            release_result=_INCOMPLETE,
            safety_summary=review_only,
            evidence_notes=("Release repair and runbook are indexed; batch commit evidence is not embedded here.",),
        ),
        ReleaseEvidenceEntry(
            patch_range="255R-260",
            title="Pilot evidence, preflight, stop, monitor, review, and go/no-go packet",
            release_result=_INCOMPLETE,
            safety_summary=review_only,
            evidence_notes=("Accepted batch name is known; full remote/CI evidence is not embedded in the roadmap excerpt.",),
        ),
        ReleaseEvidenceEntry(
            patch_range="261-270",
            title="Operator handoff, acceptance, safety, execution-window, incident, recovery, audit, closeout, and batch checklist",
            release_result=_INCOMPLETE,
            safety_summary=review_only,
            evidence_notes=("Accepted batch name is known; full remote/CI evidence is not embedded in the roadmap excerpt.",),
        ),
        ReleaseEvidenceEntry(
            patch_range="271-275",
            title="Suite runner, documentation stop, release readiness, milestone gate, and final handoff packet",
            commit_sha="4d24c9ec65a8f2643a6b1ba482e82a27915fb77b",
            github_ci_run_id="25049340880",
            release_result=_PASS,
            test_count=1774,
            safety_summary=review_only + " Final handoff is not an execution bridge or authorization mechanism.",
            evidence_notes=("Latest accepted post-275 release evidence; Trader CI success.",),
        ),
    )


def build_default_post_275_release_evidence_index() -> ReleaseEvidenceIndex:
    return build_release_evidence_index(default_post_275_release_evidence_entries())


def render_release_evidence_index(index: ReleaseEvidenceIndex | None = None) -> str:
    """Render the index as operator-readable plain text."""
    index = index or build_default_post_275_release_evidence_index()
    lines = [
        "POST-275 RELEASE EVIDENCE INDEX",
        "Current accepted frontier: Patch 275",
        "Safety: review-only / no-submit; this index does not authorize live trading.",
        "",
        "Entries:",
    ]
    for entry in index.chronological_entries:
        status = entry.effective_result
        test_count = "unknown" if entry.test_count is None else str(entry.test_count)
        lines.extend([
            f"- Patch {entry.patch_range}: {entry.title}",
            f"  Result: {status}",
            f"  Commit SHA: {entry.commit_sha or 'MISSING'}",
            f"  GitHub CI run: {entry.github_ci_run_id or 'MISSING'}",
            f"  Test count: {test_count}",
            f"  Safety: {entry.safety_summary}",
        ])
        issues = validate_release_entry(entry)
        if issues:
            lines.append("  Evidence issues: " + "; ".join(issues))
        if entry.evidence_notes:
            lines.append("  Notes: " + " | ".join(entry.evidence_notes))
    latest = index.latest_accepted_entry
    lines.extend(["", "Summary:"])
    if latest:
        lines.append(f"Latest accepted entry: Patch {latest.patch_range}")
        lines.append(f"Current frontier patch: {latest.patch_end}")
        lines.append(f"Latest accepted commit: {latest.commit_sha}")
        lines.append(f"Latest accepted GitHub CI run: {latest.github_ci_run_id}")
    else:
        lines.append("Latest accepted entry: NONE")
        lines.append("Current frontier patch: UNKNOWN")
    lines.append(f"Incomplete entries: {len(index.incomplete_entries)}")
    return "\n".join(lines)


def index_to_dict(index: ReleaseEvidenceIndex | None = None) -> Mapping[str, object]:
    index = index or build_default_post_275_release_evidence_index()
    latest = index.latest_accepted_entry
    return {
        "current_frontier_patch": index.current_frontier_patch,
        "latest_accepted_patch_range": latest.patch_range if latest else None,
        "latest_accepted_commit_sha": latest.commit_sha if latest else None,
        "latest_accepted_github_ci_run_id": latest.github_ci_run_id if latest else None,
        "entries": [
            {
                "patch_range": entry.patch_range,
                "title": entry.title,
                "commit_sha": entry.commit_sha,
                "github_ci_run_id": entry.github_ci_run_id,
                "release_result": entry.release_result,
                "effective_result": entry.effective_result,
                "test_count": entry.test_count,
                "is_complete": entry.is_complete,
                "safety_summary": entry.safety_summary,
                "validation_issues": validate_release_entry(entry),
            }
            for entry in index.chronological_entries
        ],
    }


__all__ = [
    "ReleaseEvidenceEntry",
    "ReleaseEvidenceIndex",
    "build_default_post_275_release_evidence_index",
    "build_release_evidence_index",
    "default_post_275_release_evidence_entries",
    "index_to_dict",
    "render_release_evidence_index",
    "validate_release_entry",
]
