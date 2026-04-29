"""Post-275 maintained test-matrix refresh helpers.

Patch 278 updates the maintained validation story after the accepted
cautious-live widening pilot runway.  The module is intentionally a small
read-model/validator: it renders the post-275 test-matrix section and checks
that maintained text no longer stops at the old Patch 134 cleanup frontier.

It does not run tests, submit trades, touch wallets, change thresholds, or widen
live behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

START_MARKER = "<!-- PATCH_278_POST_275_TEST_MATRIX_REFRESH_START -->"
END_MARKER = "<!-- PATCH_278_POST_275_TEST_MATRIX_REFRESH_END -->"

CURRENT_ACCEPTED_FRONTIER = "Patch 275"
CURRENT_FRONTIER_MODULE = "cautious_live_widening_pilot_final_handoff_packet.py"
LATEST_RELEASE_COMMIT = "4d24c9ec65a8f2643a6b1ba482e82a27915fb77b"
LATEST_CI_RUN_ID = "25049340880"
LATEST_RELEASE_RESULT = "PASS"
FULL_RELEASE_TEST_COUNT = 1774

PRODUCTION_MILESTONE = "Patch 125"
CLEANUP_MILESTONE = "Patch 134"


@dataclass(frozen=True)
class ValidationSurfaceGroup:
    """A maintained group of validation surfaces introduced before Patch 275."""

    name: str
    patch_range: str
    required_surfaces: tuple[str, ...]
    purpose: str
    safety_note: str

    def render(self) -> str:
        surfaces = "\n".join(f"- `{surface}`" for surface in self.required_surfaces)
        return (
            f"### {self.name}\n"
            f"Patch range: **{self.patch_range}**\n\n"
            f"Purpose: {self.purpose}\n\n"
            f"Safety note: {self.safety_note}\n\n"
            f"Validation surfaces:\n{surfaces}\n"
        )


POST_275_VALIDATION_GROUPS: tuple[ValidationSurfaceGroup, ...] = (
    ValidationSurfaceGroup(
        name="Release gate and checkpoint evidence",
        patch_range="Patch 252-253",
        required_surfaces=(
            "tests.test_release_gate_script",
            "tests.test_green_checkpoint_tag",
            "scripts/test_and_upload_trader_to_github.ps1",
            "scripts/create_trader_green_checkpoint_tag.ps1",
        ),
        purpose=(
            "Proves the release gate script, GitHub/CI evidence capture, and "
            "green checkpoint tag/restore flow remain reviewable."
        ),
        safety_note="Release evidence is proof-of-state only; it is not trading authorization.",
    ),
    ValidationSurfaceGroup(
        name="Pilot runbook and proposal controls",
        patch_range="Patch 254-260",
        required_surfaces=(
            "tests.test_cautious_live_widening_pilot_runbook",
            "tests.test_cautious_live_widening_pilot_evidence_log",
            "tests.test_cautious_live_widening_pilot_preflight_check",
            "tests.test_cautious_live_widening_pilot_stop_conditions",
            "tests.test_cautious_live_widening_pilot_monitoring_plan",
            "tests.test_cautious_live_widening_pilot_review_packet",
            "tests.test_cautious_live_widening_pilot_go_no_go_summary",
        ),
        purpose=(
            "Covers the review-only pilot preparation chain from runbook through "
            "evidence, preflight, stop conditions, monitoring, review packet, and go/no-go summary."
        ),
        safety_note="Go/no-go output is operator-review evidence and does not submit orders.",
    ),
    ValidationSurfaceGroup(
        name="Operator handoff, acceptance, safety, execution window, incident, recovery, and audit controls",
        patch_range="Patch 261-270",
        required_surfaces=(
            "tests.test_cautious_live_widening_pilot_operator_handoff",
            "tests.test_cautious_live_widening_pilot_operator_acceptance_record",
            "tests.test_cautious_live_widening_pilot_safety_barrier",
            "tests.test_cautious_live_widening_pilot_readiness_attestation",
            "tests.test_cautious_live_widening_pilot_execution_window",
            "tests.test_cautious_live_widening_pilot_incident_response_plan",
            "tests.test_cautious_live_widening_pilot_recovery_drill",
            "tests.test_cautious_live_widening_pilot_audit_digest",
            "tests.test_cautious_live_widening_pilot_closeout_report",
            "tests.test_cautious_live_widening_pilot_batch_release_checklist",
        ),
        purpose=(
            "Covers the operator-facing surfaces that make a possible pilot review "
            "bounded, auditable, recoverable, and closeable."
        ),
        safety_note="These surfaces describe and constrain review; they do not grant live autonomy.",
    ),
    ValidationSurfaceGroup(
        name="Pilot suite, documentation stop, release readiness, milestone gate, and final handoff",
        patch_range="Patch 271-275",
        required_surfaces=(
            "tests.test_cautious_live_widening_pilot_suite_runner",
            "tests.test_cautious_live_widening_pilot_documentation_stop",
            "tests.test_cautious_live_widening_pilot_release_readiness_report",
            "tests.test_cautious_live_widening_pilot_milestone_gate",
            "tests.test_cautious_live_widening_pilot_final_handoff_packet",
        ),
        purpose=(
            "Covers the named validation surface and final handoff packet that closed "
            "the review-only pilot-preparation runway."
        ),
        safety_note="The final handoff packet does not authorize live trading.",
    ),
)

REQUIRED_POST_275_MATRIX_MARKERS: tuple[str, ...] = (
    "Patch 252-275 validation surfaces",
    "release gate script contract tests",
    "green checkpoint tag tests",
    "pilot runbook tests",
    "pilot evidence/preflight/stop/monitor/review/go-no-go tests",
    "operator handoff/acceptance/safety/readiness/execution-window/incident/recovery/audit/closeout/checklist tests",
    "suite runner/documentation stop/release-readiness/milestone/final handoff tests",
    "full unittest discovery",
    "1774 tests OK",
    "Patch 275",
    "cautious_live_widening_pilot_final_handoff_packet.py",
    "does not authorize live trading",
)

FORBIDDEN_CURRENT_STATE_CLAIMS: tuple[str, ...] = (
    "latest overall frontier is Patch 134",
    "current accepted frontier is Patch 134",
    "Patch 134 is the latest overall frontier",
    "pilot final handoff authorizes live trading",
    "final handoff authorizes live trading",
)


def validation_group_names() -> tuple[str, ...]:
    """Return the maintained post-275 validation group names."""

    return tuple(group.name for group in POST_275_VALIDATION_GROUPS)


def all_required_surfaces() -> tuple[str, ...]:
    """Return all post-275 validation surfaces in stable roadmap order."""

    surfaces: list[str] = []
    for group in POST_275_VALIDATION_GROUPS:
        surfaces.extend(group.required_surfaces)
    return tuple(surfaces)


def render_post_275_test_matrix_section() -> str:
    """Render the maintained Patch 278 section for ``trader_test_matrix.md``."""

    group_text = "\n---\n\n".join(group.render() for group in POST_275_VALIDATION_GROUPS)
    return f"""{START_MARKER}

## Patch 278 — Post-275 test matrix refresh

### Current validation frontier

The maintained test matrix now tracks the review-only cautious-live widening pilot
runway through **{CURRENT_ACCEPTED_FRONTIER} — `{CURRENT_FRONTIER_MODULE}`**.

Evidence anchor:

- latest accepted release commit: `{LATEST_RELEASE_COMMIT}`
- latest accepted GitHub CI run: `{LATEST_CI_RUN_ID}`
- release result: `{LATEST_RELEASE_RESULT}`
- full release gate discovery: **{FULL_RELEASE_TEST_COUNT} tests OK**

This does not erase older milestones:

- **{PRODUCTION_MILESTONE}** remains the key cautious-live production-control milestone.
- **{CLEANUP_MILESTONE}** remains the cleanup/documentation stabilization milestone.
- Neither milestone is the latest overall accepted frontier after the Patch 252-275 runway.

### Patch 252-275 validation surfaces

The post-275 matrix explicitly includes the following validation families:

- release gate script contract tests,
- green checkpoint tag tests,
- pilot runbook tests,
- pilot evidence/preflight/stop/monitor/review/go-no-go tests,
- operator handoff/acceptance/safety/readiness/execution-window/incident/recovery/audit/closeout/checklist tests,
- suite runner/documentation stop/release-readiness/milestone/final handoff tests,
- full unittest discovery as the release gate authority.

{group_text}

### Release gate authority

Focused patch tests prove each local module, but **full unittest discovery** is the
release gate authority for batch acceptance.  At Patch 275, the accepted release
evidence recorded **{FULL_RELEASE_TEST_COUNT} tests OK**.

The matrix should therefore not stop at Patch 134 and should not describe Patch 70,
Patch 125, or Patch 134 as the latest overall frontier.  Those are historical or
milestone references only.

### Safety interpretation

Patch 275's final handoff packet is deliberately review-only.  It does not authorize
live trading, does not submit orders, does not touch wallets, does not change live
thresholds, and does not bypass manual review gates.

Patch 278 only refreshes the maintained test-matrix story and adds a validator helper.
It makes no trading-behavior changes.

{END_MARKER}
"""


def replace_or_append_section(existing_text: str, section_text: str) -> str:
    """Replace the Patch 278 section if present; otherwise append it."""

    section = section_text.rstrip() + "\n"
    if START_MARKER in existing_text and END_MARKER in existing_text:
        before = existing_text.split(START_MARKER, 1)[0].rstrip()
        after = existing_text.split(END_MARKER, 1)[1].lstrip()
        return f"{before}\n\n{section}\n{after}".rstrip() + "\n"
    if not existing_text.strip():
        return f"# Trader Test Matrix\n\n{section}"
    return existing_text.rstrip() + "\n\n---\n\n" + section


def validate_post_275_test_matrix_text(text: str) -> tuple[bool, tuple[str, ...]]:
    """Validate maintained test-matrix text for the post-275 frontier story."""

    missing = [marker for marker in REQUIRED_POST_275_MATRIX_MARKERS if marker not in text]
    forbidden = [claim for claim in FORBIDDEN_CURRENT_STATE_CLAIMS if claim in text]
    issues: list[str] = []
    issues.extend(f"missing marker: {marker}" for marker in missing)
    issues.extend(f"forbidden claim: {claim}" for claim in forbidden)
    return (not issues, tuple(issues))


def summarize_post_275_test_matrix() -> str:
    """Return a compact operator-facing summary of the refreshed matrix."""

    groups = ", ".join(group.patch_range for group in POST_275_VALIDATION_GROUPS)
    return (
        f"Patch 278 test matrix refresh covers {groups}; current accepted frontier is "
        f"{CURRENT_ACCEPTED_FRONTIER} ({CURRENT_FRONTIER_MODULE}); release gate authority is "
        f"full unittest discovery with {FULL_RELEASE_TEST_COUNT} tests OK; final handoff remains review-only."
    )


def iter_group_patch_ranges(groups: Iterable[ValidationSurfaceGroup] = POST_275_VALIDATION_GROUPS) -> tuple[str, ...]:
    """Return group patch ranges for tests and simple reports."""

    return tuple(group.patch_range for group in groups)
