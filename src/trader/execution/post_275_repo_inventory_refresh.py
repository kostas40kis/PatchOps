from __future__ import annotations

from dataclasses import dataclass

PATCH_NUMBER = 279
PATCH_NAME = "post_275_repo_inventory_refresh"
CURRENT_ACCEPTED_FRONTIER_PATCH = 275
CURRENT_ACCEPTED_FRONTIER_MODULE = "cautious_live_widening_pilot_final_handoff_packet.py"
CURRENT_ACCEPTED_COMMIT_SHA = "4d24c9ec65a8f2643a6b1ba482e82a27915fb77b"
CURRENT_ACCEPTED_CI_RUN_ID = "25049340880"
CURRENT_ACCEPTED_TEST_COUNT = 1774
CURRENT_ACCEPTED_RESULT = "PASS"

PRODUCTION_MILESTONE_PATCH = 125
PRODUCTION_MILESTONE_MODULE = "cautious_live_manual_review_request.py"
CLEANUP_DOCUMENTATION_MILESTONE_PATCH = 134
CLEANUP_DOCUMENTATION_MILESTONE_MODULE = "repo_backup_archive_cleanup.py"
IMPLEMENTATION_CENTER_OF_GRAVITY = "src\\trader\\execution"

OPERATOR_SUPPORT_SCRIPTS: tuple[str, ...] = (
    "scripts\\test_and_upload_trader_to_github.ps1",
    "scripts\\create_trader_green_checkpoint_tag.ps1",
)

PILOT_CONTROL_PATCHES: tuple[tuple[int, str], ...] = (
    (254, "cautious_live_widening_pilot_runbook"),
    (255, "cautious_live_widening_pilot_evidence_log"),
    (256, "cautious_live_widening_pilot_preflight_check"),
    (257, "cautious_live_widening_pilot_stop_conditions"),
    (258, "cautious_live_widening_pilot_monitoring_plan"),
    (259, "cautious_live_widening_pilot_review_packet"),
    (260, "cautious_live_widening_pilot_go_no_go_summary"),
    (261, "cautious_live_widening_pilot_operator_handoff"),
    (262, "cautious_live_widening_pilot_operator_acceptance_record"),
    (263, "cautious_live_widening_pilot_safety_barrier"),
    (264, "cautious_live_widening_pilot_readiness_attestation"),
    (265, "cautious_live_widening_pilot_execution_window"),
    (266, "cautious_live_widening_pilot_incident_response_plan"),
    (267, "cautious_live_widening_pilot_recovery_drill"),
    (268, "cautious_live_widening_pilot_audit_digest"),
    (269, "cautious_live_widening_pilot_closeout_report"),
    (270, "cautious_live_widening_pilot_batch_release_checklist"),
    (271, "cautious_live_widening_pilot_suite_runner"),
    (272, "cautious_live_widening_pilot_documentation_stop"),
    (273, "cautious_live_widening_pilot_release_readiness_report"),
    (274, "cautious_live_widening_pilot_milestone_gate"),
    (275, "cautious_live_widening_pilot_final_handoff_packet"),
)

FORBIDDEN_LIVE_WIDENING_ACTIONS: tuple[str, ...] = (
    "submit orders",
    "call wallet signing code",
    "alter wallet code",
    "bypass manual review",
    "authorize unattended live trading",
    "weaken production gates",
)


@dataclass(frozen=True)
class InventoryReference:
    path: str
    role: str
    canonicality: str


@dataclass(frozen=True)
class InventoryRefreshSummary:
    current_frontier_patch: int
    current_frontier_module: str
    production_milestone_patch: int
    cleanup_documentation_milestone_patch: int
    implementation_center: str
    operator_support_scripts: tuple[str, ...]
    pilot_control_modules: tuple[str, ...]
    release_evidence_policy: str
    safety_posture: str


@dataclass(frozen=True)
class InventoryValidationResult:
    ok: bool
    missing_markers: tuple[str, ...]
    stale_markers: tuple[str, ...]


def pilot_control_module_names() -> tuple[str, ...]:
    return tuple(name for _, name in PILOT_CONTROL_PATCHES)


def pilot_control_reference_paths(module_name: str) -> tuple[InventoryReference, ...]:
    """Return the canonical source/doc/test/runner paths for one pilot-control surface."""
    return (
        InventoryReference(
            path=f"src\\trader\\execution\\{module_name}.py",
            role="pilot-control implementation module",
            canonicality="canonical source",
        ),
        InventoryReference(
            path=f"docs\\architecture\\{module_name}.md",
            role="pilot-control architecture note",
            canonicality="canonical documentation",
        ),
        InventoryReference(
            path=f"tests\\test_{module_name}.py",
            role="pilot-control regression test",
            canonicality="executable truth",
        ),
        InventoryReference(
            path=f"scripts\\run_patch_*_{module_name}_tests.ps1",
            role="focused patch runner",
            canonicality="operator validation wrapper",
        ),
    )


def build_post_275_inventory_summary() -> InventoryRefreshSummary:
    return InventoryRefreshSummary(
        current_frontier_patch=CURRENT_ACCEPTED_FRONTIER_PATCH,
        current_frontier_module=CURRENT_ACCEPTED_FRONTIER_MODULE,
        production_milestone_patch=PRODUCTION_MILESTONE_PATCH,
        cleanup_documentation_milestone_patch=CLEANUP_DOCUMENTATION_MILESTONE_PATCH,
        implementation_center=IMPLEMENTATION_CENTER_OF_GRAVITY,
        operator_support_scripts=OPERATOR_SUPPORT_SCRIPTS,
        pilot_control_modules=pilot_control_module_names(),
        release_evidence_policy=(
            "Release evidence reports are external Desktop artifacts produced by PatchOps or the release gate; "
            "they are authoritative evidence to review, but they are not repo-tracked source files."
        ),
        safety_posture=(
            "Patch 275 is a review-only final handoff frontier. It does not authorize live trading, "
            "wallet mutation, order submission, or unattended autonomy."
        ),
    )


def render_pilot_control_family_table() -> str:
    rows = ["| Patch | Surface | Canonical module |", "|---:|---|---|"]
    for patch, module_name in PILOT_CONTROL_PATCHES:
        rows.append(f"| {patch} | `{module_name}` | `src\\trader\\execution\\{module_name}.py` |")
    return "\n".join(rows)


def render_post_275_repo_inventory_section() -> str:
    summary = build_post_275_inventory_summary()
    script_lines = "\n".join(f"- `{script}`" for script in summary.operator_support_scripts)
    forbidden_lines = "\n".join(f"- {action}" for action in FORBIDDEN_LIVE_WIDENING_ACTIONS)
    return f"""<!-- PATCH_279_POST_275_REPO_INVENTORY_REFRESH_START -->

## Patch 279 — Post-275 Repo Inventory Refresh

### Current accepted frontier

The current accepted overall frontier is **Patch {summary.current_frontier_patch} — `{summary.current_frontier_module}`**.

Patch {PRODUCTION_MILESTONE_PATCH} — `{PRODUCTION_MILESTONE_MODULE}` remains the production milestone frontier, and Patch {CLEANUP_DOCUMENTATION_MILESTONE_PATCH} — `{CLEANUP_DOCUMENTATION_MILESTONE_MODULE}` remains the cleanup/documentation milestone. They are important historical milestones, but they are not the latest overall accepted frontier.

Accepted release evidence for the current frontier:

- commit SHA: `{CURRENT_ACCEPTED_COMMIT_SHA}`
- GitHub CI run: `{CURRENT_ACCEPTED_CI_RUN_ID}`
- release result: `{CURRENT_ACCEPTED_RESULT}`
- full release gate discovery: `{CURRENT_ACCEPTED_TEST_COUNT} tests OK`

### Modern operator-support scripts

The post-275 repo inventory should explicitly recognize these operator-support scripts:

{script_lines}

These scripts are operator wrappers and release/checkpoint helpers. They are not the home of canonical trading logic.

### Pilot-control architecture family

The Patch 254–275 pilot-control family is now part of the active repo shape. It is review-only and no-submit oriented:

{render_pilot_control_family_table()}

For each pilot-control surface, the canonical pattern remains:

```text
src\\trader\\execution\\<surface>.py
docs\\architecture\\<surface>.md
tests\\test_<surface>.py
scripts\\run_patch_<patch>_<surface>_tests.ps1
```

### Canonical implementation center

`{summary.implementation_center}` remains the implementation center of gravity for canonical execution, review, safety, pilot-control, shadow, and future growth-control logic.

Thin PowerShell runners and manual scripts may call this layer, but they must not absorb deep canonical logic.

### Runtime and release evidence artifacts

{summary.release_evidence_policy}

Runtime/report artifacts, PatchOps reports, release gate reports, Desktop txt reports, temporary logs, generated caches, and archived residue should be treated as non-canonical or caution-required. They can be evidence, but they should not be confused with maintained source, tests, or architecture notes.

### Safety boundary

{summary.safety_posture}

Patch 279 does not:

{forbidden_lines}

### Inventory interpretation rule

When reading the repo after Patch 279, use this order:

1. current accepted frontier evidence through Patch 275,
2. maintained top-level docs,
3. `docs\\architecture`,
4. `src\\trader\\execution`,
5. `tests`,
6. `scripts`,
7. runtime/external report evidence only as supporting artifacts.

Do not infer the current frontier from old Patch 70 presence markers or from Patch 125/134 milestone wording alone.

<!-- PATCH_279_POST_275_REPO_INVENTORY_REFRESH_END -->
"""


def validate_repo_inventory_text(text: str) -> InventoryValidationResult:
    required_markers = (
        "Patch 275",
        "cautious_live_widening_pilot_final_handoff_packet.py",
        "scripts\\test_and_upload_trader_to_github.ps1",
        "scripts\\create_trader_green_checkpoint_tag.ps1",
        "Pilot-control architecture family",
        "cautious_live_widening_pilot_runbook",
        "cautious_live_widening_pilot_final_handoff_packet",
        "external Desktop artifacts",
        "not repo-tracked source files",
        "src\\trader\\execution",
        "does not authorize live trading",
        "Patch 125",
        "Patch 134",
    )
    missing = tuple(marker for marker in required_markers if marker not in text)
    stale_markers = tuple(
        marker for marker in (
            "Patch 70 is the current frontier",
            "Patch 134 is the latest overall frontier",
            "Patch 125 is the latest overall frontier",
            "current frontier signal: Patch 70",
        )
        if marker.lower() in text.lower()
    )
    return InventoryValidationResult(ok=not missing and not stale_markers, missing_markers=missing, stale_markers=stale_markers)


def summarize_validation(result: InventoryValidationResult) -> str:
    if result.ok:
        return "PASS: post-275 repo inventory markers are present and stale frontier markers were not found."
    parts: list[str] = ["FAIL: post-275 repo inventory validation failed."]
    if result.missing_markers:
        parts.append("Missing markers: " + ", ".join(result.missing_markers))
    if result.stale_markers:
        parts.append("Stale markers: " + ", ".join(result.stale_markers))
    return "\n".join(parts)
