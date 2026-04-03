from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
WORKFLOW_PATH = PROJECT_ROOT / "docs" / "project_packet_workflow.md"
QUICKSTART_PATH = PROJECT_ROOT / "docs" / "operator_quickstart.md"
STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"
LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
TEST_PATH = PROJECT_ROOT / "tests" / "test_onboarding_helper_docs_alignment.py"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def upsert_block(path: Path, start_marker: str, end_marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start_marker in text and end_marker in text:
        start_index = text.index(start_marker)
        end_index = text.index(end_marker, start_index) + len(end_marker)
        new_text = text[:start_index] + block + text[end_index:]
    else:
        if text and not text.endswith("\\n"):
            text += "\\n"
        if text:
            text += "\\n"
        new_text = text + block
    path.write_text(new_text.rstrip() + "\\n", encoding="utf-8")


workflow_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH91_WORKFLOW:START -->
    ## Helper-first onboarding command surface

    The onboarding workflow now includes a helper-first command layer that should remain explicit in the docs.

    For brand-new target onboarding, the maintained helper flow is:

    1. use `recommend-profile` to choose the smallest plausible profile,
    2. use `init-project-doc` to create the first maintained packet,
    3. use `starter` to choose the nearest manifest shape by intent,
    4. use onboarding bootstrap artifacts when a compact startup bundle is helpful,
    5. use `refresh-project-doc` after validated progress.

    These helpers reduce ambiguity during first use.
    They do not replace manifests, reports, or handoff.
    <!-- PATCHOPS_PATCH91_WORKFLOW:END -->
    """
)

quickstart_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH91_QUICKSTART:START -->
    ## Onboarding helper reminder

    For a brand-new target project, the operator can now use a helper-first onboarding path:

    - `recommend-profile`
    - `init-project-doc`
    - `starter`
    - onboarding bootstrap artifacts
    - `refresh-project-doc`

    This path is for onboarding only.
    For already-running PatchOps work, use handoff first.
    <!-- PATCHOPS_PATCH91_QUICKSTART:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH91_STATUS:START -->
    ## Patch 91 - onboarding helper docs alignment validation

    ### Current state

    - Patch 91 adds a narrow doc-contract test for the helper-first onboarding command surface.
    - The maintained docs now keep the helper story explicit:
      - `recommend-profile`,
      - `init-project-doc`,
      - `starter`,
      - onboarding bootstrap artifacts,
      - `refresh-project-doc`.

    ### Why this matters

    - the operator-visible onboarding path stays aligned with the shipped helper layer,
    - onboarding remains distinct from handoff-first continuation,
    - the repo continues through maintenance validation rather than wider redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer validation patches when the main risk is wording drift across maintained docs.
    <!-- PATCHOPS_PATCH91_STATUS:END -->
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH91_LEDGER:START -->
    ## Patch 91

    Patch 91 adds a maintenance validation surface for onboarding-helper docs alignment.

    It keeps the helper-first onboarding story explicit across workflow, quickstart, and status docs, and it preserves the rule that these helpers are for brand-new target onboarding rather than already-running continuation.

    This is a narrow validation patch, not a CLI redesign.
    <!-- PATCHOPS_PATCH91_LEDGER:END -->
    """
)

test_content = textwrap.dedent(
    """\
    from __future__ import annotations

    from pathlib import Path


    def test_onboarding_helper_docs_stay_aligned() -> None:
        workflow_text = Path("docs/project_packet_workflow.md").read_text(encoding="utf-8").lower()
        quickstart_text = Path("docs/operator_quickstart.md").read_text(encoding="utf-8").lower()
        status_text = Path("docs/project_status.md").read_text(encoding="utf-8").lower()

        required_workflow_fragments = [
            "helper-first onboarding command surface",
            "recommend-profile",
            "init-project-doc",
            "starter",
            "onboarding bootstrap artifacts",
            "refresh-project-doc",
            "reduce ambiguity during first use",
            "do not replace manifests, reports, or handoff",
        ]
        for fragment in required_workflow_fragments:
            assert fragment in workflow_text

        required_quickstart_fragments = [
            "onboarding helper reminder",
            "recommend-profile",
            "init-project-doc",
            "starter",
            "onboarding bootstrap artifacts",
            "refresh-project-doc",
            "for already-running patchops work, use handoff first",
        ]
        for fragment in required_quickstart_fragments:
            assert fragment in quickstart_text

        required_status_fragments = [
            "patch 91 - onboarding helper docs alignment validation",
            "recommend-profile",
            "init-project-doc",
            "starter",
            "onboarding bootstrap artifacts",
            "refresh-project-doc",
            "operator-visible onboarding path stays aligned with the shipped helper layer",
        ]
        for fragment in required_status_fragments:
            assert fragment in status_text
    """
)

upsert_block(
    WORKFLOW_PATH,
    "<!-- PATCHOPS_PATCH91_WORKFLOW:START -->",
    "<!-- PATCHOPS_PATCH91_WORKFLOW:END -->",
    workflow_block,
)

upsert_block(
    QUICKSTART_PATH,
    "<!-- PATCHOPS_PATCH91_QUICKSTART:START -->",
    "<!-- PATCHOPS_PATCH91_QUICKSTART:END -->",
    quickstart_block,
)

upsert_block(
    STATUS_PATH,
    "<!-- PATCHOPS_PATCH91_STATUS:START -->",
    "<!-- PATCHOPS_PATCH91_STATUS:END -->",
    status_block,
)

upsert_block(
    LEDGER_PATH,
    "<!-- PATCHOPS_PATCH91_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH91_LEDGER:END -->",
    ledger_block,
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

print(f"UPDATED: {WORKFLOW_PATH}")
print(f"UPDATED: {QUICKSTART_PATH}")
print(f"UPDATED: {STATUS_PATH}")
print(f"UPDATED: {LEDGER_PATH}")
print(f"WROTE: {TEST_PATH}")