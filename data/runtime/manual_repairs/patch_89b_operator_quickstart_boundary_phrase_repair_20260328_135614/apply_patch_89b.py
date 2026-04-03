from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
QUICKSTART_PATH = PROJECT_ROOT / "docs" / "operator_quickstart.md"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"


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


quickstart_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH89B_QUICKSTART:START -->
    ### Boundary reminder

    Use handoff first for **already-running PatchOps work**.

    Use the generic onboarding packet first for **brand-new target onboarding**.

    If the task is target-specific after continuation or onboarding, also use the relevant project packet under `docs/projects/`.
    <!-- PATCHOPS_PATCH89B_QUICKSTART:END -->
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH89B_LEDGER:START -->
    ## Patch 89B

    Patch 89B repairs the single wording gap exposed by Patch 89.

    It restores the exact operator-quickstart phrase `already-running PatchOps work` so the onboarding-versus-continuation boundary test matches the maintained docs.

    This is a narrow documentation contract repair.
    <!-- PATCHOPS_PATCH89B_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH89B_STATUS:START -->
    ## Patch 89B - operator quickstart boundary phrase repair

    ### Current state

    - Patch 89B repairs the single missing phrase exposed by Patch 89.
    - `docs/operator_quickstart.md` now explicitly says `already-running PatchOps work`.
    - The onboarding-versus-continuation boundary remains documentation-driven and test-protected.

    ### Why this matters

    - the boundary test now matches the intended operator wording,
    - the repair stays narrow and honest,
    - continuation and onboarding remain clearly separated.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer tiny doc-contract repairs when the behavior is already correct.
    <!-- PATCHOPS_PATCH89B_STATUS:END -->
    """
)

upsert_block(
    QUICKSTART_PATH,
    "<!-- PATCHOPS_PATCH89B_QUICKSTART:START -->",
    "<!-- PATCHOPS_PATCH89B_QUICKSTART:END -->",
    quickstart_block,
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH89B_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH89B_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH89B_STATUS:START -->",
    "<!-- PATCHOPS_PATCH89B_STATUS:END -->",
    status_block,
)

print(f"UPDATED: {QUICKSTART_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")