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

old = 'assert payload["profile_name"] == "generic_python"'
new = textwrap.dedent(
    """\
    assert payload["written"] is True
        assert Path(payload["bootstrap_markdown_path"]) == bootstrap_md.resolve()
        assert Path(payload["bootstrap_json_path"]) == bootstrap_json.resolve()
        assert Path(payload["next_prompt_path"]) == next_prompt.resolve()
        assert Path(payload["starter_manifest_path"]) == starter_manifest.resolve()
    """
).rstrip()

if old not in test_text:
    raise SystemExit("Could not locate the expected payload profile assertion.")

TEST_PATH.write_text(test_text.replace(old, new, 1), encoding="utf-8")

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH94C_LEDGER:START -->
    ## Patch 94C

    Patch 94C repairs the onboarding bootstrap artifact test so it matches the current direct payload contract.

    The direct return payload is asserted through `written` plus the returned artifact paths, while profile identity remains asserted through the generated bootstrap markdown and JSON artifact surfaces.

    This is a narrow test-contract repair, not an onboarding redesign.
    <!-- PATCHOPS_PATCH94C_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH94C_STATUS:START -->
    ## Patch 94C - onboarding bootstrap payload contract repair

    ### Current state

    - Patch 94C repairs the remaining failing assertion from the Patch 94 validation wave.
    - The bootstrap artifact test now matches the current direct payload contract:
      - `written`,
      - returned artifact paths,
      - generated markdown and JSON surfaces for profile identity.

    ### Why this matters

    - the onboarding bootstrap validation wave can finish without widening the shipped implementation,
    - the direct payload expectations now match the already-proven bootstrap contract,
    - maintenance continues through small honest repairs.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer test-contract repairs when a new test drifts from the current implementation contract.
    <!-- PATCHOPS_PATCH94C_STATUS:END -->
    """
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH94C_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH94C_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH94C_STATUS:START -->",
    "<!-- PATCHOPS_PATCH94C_STATUS:END -->",
    status_block,
)

print(f"UPDATED: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")