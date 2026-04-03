from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_onboarding_bootstrap_artifacts_current.py"
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


test_text = TEST_PATH.read_text(encoding="utf-8")
old = 'assert manifest_payload["target_project_root"] == "C:/dev/demo_bootstrap"'
new = 'assert manifest_payload["target_project_root"] == r"C:\\dev\\demo_bootstrap"'

if old not in test_text:
    raise SystemExit("Could not locate the expected target_project_root assertion.")

TEST_PATH.write_text(test_text.replace(old, new, 1), encoding="utf-8")

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH94B_LEDGER:START -->
    ## Patch 94B

    Patch 94B repairs the new onboarding bootstrap artifact test to match the current path-format contract.

    The starter manifest currently preserves the Windows target root form for `target_project_root`, so the repair updates the test expectation rather than widening bootstrap behavior.

    This is a narrow test-contract repair, not an onboarding redesign.
    <!-- PATCHOPS_PATCH94B_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH94B_STATUS:START -->
    ## Patch 94B - onboarding bootstrap path contract repair

    ### Current state

    - Patch 94B repairs the single failing assertion introduced by Patch 94.
    - The bootstrap artifact test now matches the current starter-manifest path-format contract.
    - The repair stays on the validation surface and does not widen the bootstrap implementation.

    ### Why this matters

    - the onboarding bootstrap validation wave stays green without redesigning an already-shipped surface,
    - the path expectation now matches the actual generated artifact,
    - maintenance continues through small honest repairs.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer test-contract repairs when a new test drifted from the current implementation contract.
    <!-- PATCHOPS_PATCH94B_STATUS:END -->
    """
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH94B_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH94B_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH94B_STATUS:START -->",
    "<!-- PATCHOPS_PATCH94B_STATUS:END -->",
    status_block,
)

print(f"UPDATED: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")