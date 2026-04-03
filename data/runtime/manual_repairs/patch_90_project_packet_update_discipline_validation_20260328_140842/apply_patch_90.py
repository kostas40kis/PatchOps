from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")

WORKFLOW_PATH = PROJECT_ROOT / "docs" / "project_packet_workflow.md"
CONTRACT_PATH = PROJECT_ROOT / "docs" / "project_packet_contract.md"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"
TEST_PATH = PROJECT_ROOT / "tests" / "test_project_packet_update_discipline.py"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def upsert_block(path: Path, start_marker: str, end_marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start_marker in text and end_marker in text:
        start_index = text.index(start_marker)
        end_index = text.index(end_marker, start_index) + len(end_marker)
        new_text = text[:start_index] + block + text[end_index:]
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        if text:
            text += "\n"
        new_text = text + block
    path.write_text(new_text.rstrip() + "\n", encoding="utf-8")


workflow_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH90_WORKFLOW:START -->
    ## Maintained update discipline

    The project-packet workflow must stay explicit about update discipline.

    Stable packet sections should change rarely.
    Mutable packet sections should be refreshed as validated progress changes.

    Packet updates should be:

    - conservative,
    - grounded in reports and handoff when available,
    - explicit about uncertainty,
    - careful not to rewrite stable sections without real reason.

    For an already-running PatchOps effort:

    1. handoff bundle first,
    2. perform the exact next recommended action,
    3. read the relevant project packet if target context is needed,
    4. refresh the packet after validated progress.

    This keeps project-packet updates tied to real execution evidence instead of drifting into speculative rewrites.
    <!-- PATCHOPS_PATCH90_WORKFLOW:END -->
    """
)

contract_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH90_CONTRACT:START -->
    ## Update discipline contract

    Every maintained project packet should keep the distinction between stable and mutable sections explicit.

    Stable sections usually include:

    - purpose,
    - target root,
    - expected runtime,
    - selected profile,
    - boundary rules,
    - development phases,
    - validation philosophy,
    - report expectations.

    Mutable sections usually include:

    - current state,
    - latest passed patch,
    - latest attempted patch,
    - blockers,
    - next recommended action,
    - latest report reference when relevant.

    For a brand-new target project, create the packet before the first manifest.

    For an already-running PatchOps effort, use handoff first and refresh the relevant project packet only after validated progress.

    A project packet must not replace manifests, reports, or handoff files.
    <!-- PATCHOPS_PATCH90_CONTRACT:END -->
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH90_LEDGER:START -->
    ## Patch 90

    Patch 90 adds a narrow validation surface for project-packet update discipline.

    It keeps the stable-vs-mutable packet distinction explicit and test-protected, and it preserves the rule that packet refreshes should stay grounded in reports and handoff rather than broad speculative rewrites.

    This is a maintenance validation patch, not a workflow redesign.
    <!-- PATCHOPS_PATCH90_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH90_STATUS:START -->
    ## Patch 90 - project-packet update discipline validation

    ### Current state

    - Patch 90 adds a doc-contract test for project-packet update discipline.
    - The docs now keep three things explicit and testable:
      - stable sections change rarely,
      - mutable sections refresh with validated progress,
      - packet updates should stay grounded in reports and handoff.

    ### Why this matters

    - the onboarding layer remains usable without encouraging packet rewrites detached from evidence,
    - the packet-update story is now protected as a maintained rule,
    - the repo keeps moving through narrow maintenance patches after the substantially complete onboarding rollout.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small validation patches when the main risk is wording drift rather than missing architecture.
    <!-- PATCHOPS_PATCH90_STATUS:END -->
    """
)

test_content = textwrap.dedent(
    """\
    from __future__ import annotations

    from pathlib import Path


    def test_project_packet_update_discipline_stays_explicit() -> None:
        workflow_text = Path("docs/project_packet_workflow.md").read_text(encoding="utf-8").lower()
        contract_text = Path("docs/project_packet_contract.md").read_text(encoding="utf-8").lower()

        required_workflow_fragments = [
            "maintained update discipline",
            "stable packet sections should change rarely",
            "mutable packet sections should be refreshed as validated progress changes",
            "grounded in reports and handoff when available",
            "careful not to rewrite stable sections without real reason",
            "handoff bundle first",
            "refresh the packet after validated progress",
        ]
        for fragment in required_workflow_fragments:
            assert fragment in workflow_text

        required_contract_fragments = [
            "update discipline contract",
            "stable sections usually include",
            "mutable sections usually include",
            "current state",
            "latest passed patch",
            "latest attempted patch",
            "latest report reference when relevant",
            "for a brand-new target project, create the packet before the first manifest",
            "for an already-running patchops effort, use handoff first",
            "a project packet must not replace manifests, reports, or handoff files",
        ]
        for fragment in required_contract_fragments:
            assert fragment in contract_text
    """
)

upsert_block(
    WORKFLOW_PATH,
    "<!-- PATCHOPS_PATCH90_WORKFLOW:START -->",
    "<!-- PATCHOPS_PATCH90_WORKFLOW:END -->",
    workflow_block,
)

upsert_block(
    CONTRACT_PATH,
    "<!-- PATCHOPS_PATCH90_CONTRACT:START -->",
    "<!-- PATCHOPS_PATCH90_CONTRACT:END -->",
    contract_block,
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH90_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH90_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH90_STATUS:START -->",
    "<!-- PATCHOPS_PATCH90_STATUS:END -->",
    status_block,
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

print(f"UPDATED: {WORKFLOW_PATH}")
print(f"UPDATED: {CONTRACT_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")
print(f"WROTE: {TEST_PATH}")