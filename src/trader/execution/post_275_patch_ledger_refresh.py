from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

CURRENT_FRONTIER_PATCH = 275
CURRENT_FRONTIER_MODULE = "cautious_live_widening_pilot_final_handoff_packet.py"
CURRENT_FRONTIER_COMMIT = "4d24c9ec65a8f2643a6b1ba482e82a27915fb77b"
CURRENT_FRONTIER_CI_RUN = "25049340880"
CURRENT_FRONTIER_CI_WORKFLOW = "Trader CI"
CURRENT_FRONTIER_CI_RESULT = "success"
CURRENT_FRONTIER_RELEASE_RESULT = "PASS"
CURRENT_FRONTIER_FULL_TESTS = "1774 tests OK"
PRODUCTION_MILESTONE_PATCH = 125
CLEANUP_MILESTONE_PATCH = 134

LEDGER_SECTION_START = "<!-- PATCH_277_POST_275_PATCH_LEDGER_REFRESH_START -->"
LEDGER_SECTION_END = "<!-- PATCH_277_POST_275_PATCH_LEDGER_REFRESH_END -->"


@dataclass(frozen=True)
class PatchRunwaySegment:
    patch_range: str
    title: str
    status: str
    evidence: str
    summary: str
    safety_summary: str


@dataclass(frozen=True)
class Post275LedgerRefreshStatus:
    current_frontier_present: bool
    release_batches_present: bool
    preserves_patch_125: bool
    reclassifies_patch_134: bool
    no_patch_134_latest_overall_claim: bool
    no_live_authorization_claim: bool
    missing_requirements: tuple[str, ...]

    @property
    def is_ready(self) -> bool:
        return not self.missing_requirements


def _plain(text: str) -> str:
    return " ".join(text.lower().replace("*", "").replace("`", "").split())


def build_post_275_runway_segments() -> tuple[PatchRunwaySegment, ...]:
    """Return accepted post-250 release/pilot runway entries for the maintained ledger."""
    return (
        PatchRunwaySegment(
            patch_range="Patch 252",
            title="release gate script",
            status="accepted release support",
            evidence="Release-gate script contract tests and upload workflow evidence.",
            summary="Added the maintained local-to-GitHub validation and upload lane used for batch release stops.",
            safety_summary="Evidence-only release tooling; no trading behavior, no wallet behavior, and no live widening.",
        ),
        PatchRunwaySegment(
            patch_range="Patch 253",
            title="green checkpoint tag and restore guide",
            status="accepted checkpoint support",
            evidence="Green checkpoint tag and restore-guide validation.",
            summary="Created the green-checkpoint/restore reference so accepted release states can be recovered deliberately.",
            safety_summary="Recovery documentation and checkpoint evidence only; no live authorization.",
        ),
        PatchRunwaySegment(
            patch_range="Patch 254",
            title="pilot runbook and release-gate repair",
            status="accepted pilot preparation",
            evidence="Pilot runbook tests plus release-gate repair evidence.",
            summary="Established the review-only operator runbook for a future cautious-live widening pilot.",
            safety_summary="Runbook-only planning surface; not a pilot launcher and not an execution bridge.",
        ),
        PatchRunwaySegment(
            patch_range="Patch 255R-260",
            title="pilot evidence, preflight, stop, monitor, review, and go/no-go packet",
            status="accepted local batch",
            evidence="Focused tests for evidence log, preflight check, stop conditions, monitoring plan, review packet, and go/no-go summary.",
            summary="Built the first pilot-control packet layer for evidence readiness and explicit operator review.",
            safety_summary="Review-only readiness surfaces; go/no-go output remains advisory and does not authorize live trading.",
        ),
        PatchRunwaySegment(
            patch_range="Patch 261-270",
            title="operator handoff, acceptance, safety, execution-window, incident, recovery, audit, closeout, and batch checklist",
            status="accepted local/release batch",
            evidence="Focused tests and batch release evidence for the operator handoff/control family.",
            summary="Completed the operator-control and incident/recovery/audit layers required before any separate pilot decision.",
            safety_summary="Fail-closed control-plane and audit surfaces; no order submission, no wallet mutation, no threshold change.",
        ),
        PatchRunwaySegment(
            patch_range="Patch 271-275",
            title="suite runner, documentation stop, release-readiness report, milestone gate, and final handoff",
            status="accepted release batch",
            evidence=(
                f"Commit {CURRENT_FRONTIER_COMMIT}; GitHub CI run {CURRENT_FRONTIER_CI_RUN} "
                f"({CURRENT_FRONTIER_CI_WORKFLOW}: {CURRENT_FRONTIER_CI_RESULT}); {CURRENT_FRONTIER_FULL_TESTS}."
            ),
            summary="Closed the cautious-live widening pilot preparation runway with a final review-only handoff packet.",
            safety_summary="Final handoff packet is not a live-submission tool, not a wallet tool, and not an authorization mechanism.",
        ),
    )


def render_runway_table(segments: Iterable[PatchRunwaySegment]) -> str:
    lines = [
        "| Patch range | Accepted purpose | Evidence | Safety boundary |",
        "|---|---|---|---|",
    ]
    for segment in segments:
        lines.append(
            "| {patch_range} | {title}: {summary} | {evidence} | {safety} |".format(
                patch_range=segment.patch_range,
                title=segment.title,
                summary=segment.summary,
                evidence=segment.evidence,
                safety=segment.safety_summary,
            )
        )
    return "\n".join(lines)


def render_post_275_ledger_section() -> str:
    """Render the maintained ledger section introduced by Patch 277."""
    table = render_runway_table(build_post_275_runway_segments())
    return f"""{LEDGER_SECTION_START}

## Patch 277 — Post-275 patch ledger refresh

### Current accepted frontier

The latest overall accepted frontier is now:

**Patch {CURRENT_FRONTIER_PATCH} — `{CURRENT_FRONTIER_MODULE}`**

Accepted release evidence:

- latest accepted release commit: `{CURRENT_FRONTIER_COMMIT}`
- latest accepted GitHub CI run: `{CURRENT_FRONTIER_CI_RUN}` — `{CURRENT_FRONTIER_CI_WORKFLOW}` — `{CURRENT_FRONTIER_CI_RESULT}`
- release result: `{CURRENT_FRONTIER_RELEASE_RESULT}`
- full release validation: `{CURRENT_FRONTIER_FULL_TESTS}`

### Milestone interpretation

Patch {PRODUCTION_MILESTONE_PATCH} remains the production milestone frontier because it completed the original cautious-live manual-review chain.

Patch {CLEANUP_MILESTONE_PATCH} remains the cleanup/documentation milestone frontier because it completed the initial cleanup and archive cycle.

Patch {CLEANUP_MILESTONE_PATCH} is not the latest overall frontier anymore. It is a historical cleanup milestone that must be preserved without outranking Patch {CURRENT_FRONTIER_PATCH}.

Patch {CURRENT_FRONTIER_PATCH} is the current accepted frontier for the whole repo, and the Patch 252-275 runway is the accepted release evidence batch that led there.

### Accepted Patch 252-275 runway

The maintained ledger now includes these release evidence batches:

{table}

### Safety interpretation

The Patch 252-275 runway is review-only pilot preparation. It does not authorize live trading, does not submit orders, does not touch wallet signing, does not bypass manual review, and does not start autonomous live behavior.

The final Patch 275 handoff packet is a handoff and review artifact only. It is deliberately not an execution bridge, not a wallet tool, not a live-submission tool, and not an authorization mechanism.

### Patch 277 validation purpose

Patch 277 adds a small validator/helper so future ledger refreshes can check that:

- Patch 275 is named as the current accepted frontier,
- the accepted Patch 252-275 release runway is visible,
- Patch 125 remains the production milestone,
- Patch 134 remains a cleanup/documentation milestone only,
- stale Patch 70/125/134-only wording does not reappear as the latest overall frontier,
- no maintained ledger wording implies live authorization.

{LEDGER_SECTION_END}
"""


def replace_or_append_ledger_section(existing_text: str, section_text: str | None = None) -> str:
    section = (section_text if section_text is not None else render_post_275_ledger_section()).rstrip() + "\n"
    if LEDGER_SECTION_START in existing_text and LEDGER_SECTION_END in existing_text:
        before = existing_text.split(LEDGER_SECTION_START, 1)[0].rstrip()
        after = existing_text.split(LEDGER_SECTION_END, 1)[1].lstrip()
        return f"{before}\n\n{section}\n{after}".rstrip() + "\n"
    if not existing_text.strip():
        return "# Trader Patch Ledger\n\n" + section
    return existing_text.rstrip() + "\n\n---\n\n" + section


def validate_patch_ledger_text(text: str) -> Post275LedgerRefreshStatus:
    normalized = _plain(text)
    current_frontier_present = all(
        marker in normalized
        for marker in (
            "patch 275",
            CURRENT_FRONTIER_MODULE.lower(),
            "current accepted frontier",
            CURRENT_FRONTIER_COMMIT.lower(),
            CURRENT_FRONTIER_CI_RUN,
            "1774 tests ok",
        )
    )
    release_batches_present = all(
        marker in normalized
        for marker in (
            "patch 252",
            "patch 253",
            "patch 254",
            "patch 255r-260",
            "patch 261-270",
            "patch 271-275",
            "release evidence batches",
        )
    )
    preserves_patch_125 = "patch 125 remains the production milestone" in normalized
    reclassifies_patch_134 = (
        "patch 134 remains the cleanup/documentation milestone" in normalized
        and "patch 134 is not the latest overall frontier" in normalized
    )
    forbidden_patch_134_latest_overall_claims = (
        "patch 134 is the latest overall frontier",
        "latest overall frontier is patch 134",
        "latest overall accepted frontier is patch 134",
        "current accepted frontier: patch 134",
    )
    no_patch_134_latest_overall_claim = not any(claim in normalized for claim in forbidden_patch_134_latest_overall_claims)
    forbidden_live_claims = (
        "handoff packet authorizes live trading",
        "final handoff authorizes live trading",
        "handoff authorizes a real-money pilot",
        "final handoff submits orders",
        "bypass manual review is allowed",
        "start autonomous live behavior from patch 275",
    )
    no_live_authorization_claim = not any(claim in normalized for claim in forbidden_live_claims)

    missing: list[str] = []
    if not current_frontier_present:
        missing.append("current Patch 275 frontier evidence")
    if not release_batches_present:
        missing.append("Patch 252-275 release evidence batches")
    if not preserves_patch_125:
        missing.append("Patch 125 production milestone preservation")
    if not reclassifies_patch_134:
        missing.append("Patch 134 cleanup milestone reclassification")
    if not no_patch_134_latest_overall_claim:
        missing.append("removal of Patch 134 latest-overall-frontier claim")
    if not no_live_authorization_claim:
        missing.append("no-live-authorization safety wording")

    return Post275LedgerRefreshStatus(
        current_frontier_present=current_frontier_present,
        release_batches_present=release_batches_present,
        preserves_patch_125=preserves_patch_125,
        reclassifies_patch_134=reclassifies_patch_134,
        no_patch_134_latest_overall_claim=no_patch_134_latest_overall_claim,
        no_live_authorization_claim=no_live_authorization_claim,
        missing_requirements=tuple(missing),
    )


def render_validation_summary(status: Post275LedgerRefreshStatus) -> str:
    lines = [
        "Post-275 patch ledger refresh validation",
        f"Result: {'PASS' if status.is_ready else 'FAIL'}",
        f"current_frontier_present: {status.current_frontier_present}",
        f"release_batches_present: {status.release_batches_present}",
        f"preserves_patch_125: {status.preserves_patch_125}",
        f"reclassifies_patch_134: {status.reclassifies_patch_134}",
        f"no_patch_134_latest_overall_claim: {status.no_patch_134_latest_overall_claim}",
        f"no_live_authorization_claim: {status.no_live_authorization_claim}",
    ]
    if status.missing_requirements:
        lines.append("Missing requirements:")
        lines.extend(f"- {item}" for item in status.missing_requirements)
    return "\n".join(lines)
