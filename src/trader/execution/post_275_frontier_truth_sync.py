"""Post-275 frontier truth synchronization helpers.

Patch 276 keeps the maintained frontier vocabulary aligned with the accepted
Patch 275 release evidence. It is deliberately read-only metadata logic: it
classifies frontier markers and renders report/export wording. It does not
submit trades, call wallets, or widen live behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class FrontierRecord:
    """Accepted frontier evidence rendered by handoff/export surfaces."""

    patch_number: int
    module_name: str
    commit_sha: str
    ci_run_id: str
    ci_result: str
    release_result: str
    full_test_result: str
    frontier_kind: str
    description: str

    def as_dict(self) -> dict[str, object]:
        return {
            "patch_number": self.patch_number,
            "module_name": self.module_name,
            "commit_sha": self.commit_sha,
            "ci_run_id": self.ci_run_id,
            "ci_result": self.ci_result,
            "release_result": self.release_result,
            "full_test_result": self.full_test_result,
            "frontier_kind": self.frontier_kind,
            "description": self.description,
        }

    def stable_identity(self) -> str:
        return f"patch-{self.patch_number}:{self.module_name}:{self.commit_sha}"


POST_275_FRONTIER = FrontierRecord(
    patch_number=275,
    module_name="cautious_live_widening_pilot_final_handoff_packet.py",
    commit_sha="4d24c9ec65a8f2643a6b1ba482e82a27915fb77b",
    ci_run_id="25049340880",
    ci_result="success",
    release_result="PASS",
    full_test_result="1774 tests OK",
    frontier_kind="latest_accepted_frontier",
    description="Post-275 review-only cautious-live widening pilot handoff frontier.",
)

PRODUCTION_MILESTONE_FRONTIER = FrontierRecord(
    patch_number=125,
    module_name="cautious_live_manual_review_request.py",
    commit_sha="",
    ci_run_id="",
    ci_result="",
    release_result="PASS",
    full_test_result="285 tests OK",
    frontier_kind="production_milestone_frontier",
    description="Original cautious-live operator-controlled manual review chain milestone.",
)

CLEANUP_DOCUMENTATION_FRONTIER = FrontierRecord(
    patch_number=134,
    module_name="repo_backup_archive_cleanup.py",
    commit_sha="",
    ci_run_id="",
    ci_result="",
    release_result="PASS",
    full_test_result="cleanup/documentation stabilization tests OK",
    frontier_kind="cleanup_documentation_frontier",
    description="Cleanup/documentation stabilization milestone, not the latest overall frontier.",
)

HISTORICAL_MARKERS: dict[int, str] = {
    70: "historical_entry_execution_marker",
    125: "production_milestone_frontier",
    134: "cleanup_documentation_frontier",
}

PATCH_70_MARKER_TOKENS = (
    "patch 70",
    "entry_execution_coordinator",
    "run_patch_70_entry_execution_coordinator",
)

CURRENT_FRONTIER_PREFIX = "Current accepted frontier detected from accepted release evidence"


def current_frontier() -> FrontierRecord:
    """Return the accepted overall frontier after Patch 275."""

    return POST_275_FRONTIER


def milestone_records() -> tuple[FrontierRecord, FrontierRecord]:
    """Return important historical milestones that should remain visible."""

    return (PRODUCTION_MILESTONE_FRONTIER, CLEANUP_DOCUMENTATION_FRONTIER)


def classify_patch_number(patch_number: int) -> str:
    """Classify a patch number relative to the post-275 frontier."""

    if patch_number == POST_275_FRONTIER.patch_number:
        return "current_accepted_frontier"
    if patch_number in HISTORICAL_MARKERS:
        return HISTORICAL_MARKERS[patch_number]
    if patch_number < POST_275_FRONTIER.patch_number:
        return "historical_lower_patch"
    return "future_or_unaccepted_patch"


def classify_frontier_signal(signal: object) -> dict[str, object]:
    """Classify a frontier-like signal without treating file presence as authority.

    The export that motivated Patch 276 printed old Patch-70 presence markers as
    "Current frontier signals detected". This helper keeps those markers visible
    as historical context but makes the accepted Patch 275 release evidence the
    only current frontier.
    """

    if isinstance(signal, int):
        patch_number = signal
        return {
            "signal": signal,
            "classification": classify_patch_number(patch_number),
            "is_current_frontier": patch_number == POST_275_FRONTIER.patch_number,
        }

    text = str(signal).strip()
    normalized = text.lower().replace("\\", "/")

    if str(POST_275_FRONTIER.patch_number) in normalized or POST_275_FRONTIER.module_name.lower() in normalized:
        return {
            "signal": text,
            "classification": "current_accepted_frontier",
            "is_current_frontier": True,
        }

    if any(token in normalized for token in PATCH_70_MARKER_TOKENS):
        return {
            "signal": text,
            "classification": "historical_entry_execution_marker",
            "is_current_frontier": False,
        }

    if "patch 125" in normalized or PRODUCTION_MILESTONE_FRONTIER.module_name.lower() in normalized:
        return {
            "signal": text,
            "classification": "production_milestone_frontier",
            "is_current_frontier": False,
        }

    if "patch 134" in normalized or CLEANUP_DOCUMENTATION_FRONTIER.module_name.lower() in normalized:
        return {
            "signal": text,
            "classification": "cleanup_documentation_frontier",
            "is_current_frontier": False,
        }

    return {
        "signal": text,
        "classification": "unknown_or_context_only_signal",
        "is_current_frontier": False,
    }


def classify_frontier_signals(signals: Iterable[object]) -> list[dict[str, object]]:
    """Classify multiple frontier-like markers."""

    return [classify_frontier_signal(signal) for signal in signals]


def render_post_275_frontier_summary(historical_signals: Iterable[object] = ()) -> str:
    """Render exporter-safe frontier wording for the post-275 baseline."""

    frontier = current_frontier()
    lines = [
        CURRENT_FRONTIER_PREFIX,
        f"Patch number: {frontier.patch_number}",
        f"Patch module: {frontier.module_name}",
        f"Release commit: {frontier.commit_sha}",
        f"GitHub CI run: {frontier.ci_run_id} ({frontier.ci_result})",
        f"Release result: {frontier.release_result}",
        f"Full tests: {frontier.full_test_result}",
        "Historical frontier markers remain visible but are not authoritative current-frontier evidence.",
    ]
    classified = classify_frontier_signals(historical_signals)
    for item in classified:
        lines.append(f"Historical/context signal: {item['signal']} -> {item['classification']}")
    return "\n".join(lines)


def render_post_275_frontier_payload(historical_signals: Iterable[object] = ()) -> dict[str, object]:
    """Return a structured payload for future exporters or docs refresh helpers."""

    return {
        "current_frontier": current_frontier().as_dict(),
        "milestones": [record.as_dict() for record in milestone_records()],
        "historical_signals": classify_frontier_signals(historical_signals),
        "safety": {
            "review_only": True,
            "no_live_behavior_widening": True,
            "submits_orders": False,
            "touches_wallets": False,
        },
    }


def export_wording_is_stale(text: str) -> bool:
    """Detect old export wording that can mislead future handoffs."""

    normalized = text.lower()
    stale_prefix = "current frontier signals detected" in normalized
    patch_70_presence = all(token in normalized for token in ("entry_execution_coordinator", "run_patch_70"))
    accepted_patch_275_missing = "patch number: 275" not in normalized and "patch      : 275" not in normalized
    return bool(stale_prefix and patch_70_presence and accepted_patch_275_missing)


def validate_post_275_payload(payload: Mapping[str, object]) -> list[str]:
    """Return validation issues for a post-275 frontier payload."""

    issues: list[str] = []
    current = payload.get("current_frontier")
    if not isinstance(current, Mapping):
        return ["current_frontier_missing"]
    if current.get("patch_number") != POST_275_FRONTIER.patch_number:
        issues.append("patch_275_not_current_frontier")
    if current.get("module_name") != POST_275_FRONTIER.module_name:
        issues.append("post_275_module_mismatch")
    if current.get("release_result") != "PASS":
        issues.append("release_result_not_pass")
    if current.get("ci_result") != "success":
        issues.append("ci_result_not_success")
    return issues
