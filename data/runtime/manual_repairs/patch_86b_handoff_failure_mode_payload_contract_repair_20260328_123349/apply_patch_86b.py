from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_handoff_failure_modes.py"
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

old = textwrap.dedent(
    """\
        top_level_prompt = Path(second_payload["next_prompt_path"])
        assert bundle_prompt.exists()
        assert top_level_prompt.exists()
        assert bundle_prompt.read_text(encoding="utf-8") == top_level_prompt.read_text(encoding="utf-8")
        assert Path(first_payload["latest_report_copy_path"]).exists()
"""
)

new = textwrap.dedent(
    """\
        top_level_prompt = Path(second_payload["next_prompt_path"])
        assert bundle_prompt.exists()
        assert top_level_prompt.exists()
        assert bundle_prompt.read_text(encoding="utf-8") == top_level_prompt.read_text(encoding="utf-8")

        latest_report_copy = handoff_root / "latest_report_copy.txt"
        assert latest_report_copy.exists()

        latest_index = _read_json(handoff_root / "latest_report_index.json")
        assert Path(latest_index["latest_report_copy_path"]) == latest_report_copy
"""
)

if old not in test_text:
    raise SystemExit("Could not locate the expected assertion block in tests/test_handoff_failure_modes.py")

TEST_PATH.write_text(test_text.replace(old, new, 1), encoding="utf-8")

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH86B_LEDGER:START -->
    ## Patch 86B

    Patch 86B repairs the new handoff failure-mode test to match the existing export-handoff contract.

    The repair keeps `latest_report_copy_path` as an indexed handoff surface asserted through `latest_report_index.json`, rather than incorrectly expecting it in the direct `export_handoff_bundle()` return payload.

    This is a narrow contract-repair patch, not a handoff-engine redesign.
    <!-- PATCHOPS_PATCH86B_LEDGER:END -->
    """
)

project_status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH86B_STATUS:START -->
    ## Patch 86B - handoff payload contract repair

    ### Current state

    - Patch 86B repairs the failing assertion introduced by Patch 86.
    - The test now matches the already-shipped contract:
      - direct export payload -> status, next-action, prompt path,
      - latest report copy path -> asserted through `handoff/latest_report_index.json`.

    ### Why this matters

    - the new failure-mode coverage stays useful without rewriting stable handoff behavior,
    - the repair is narrow and honest,
    - continuation remains maintenance-first.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer test-contract repairs when a new test drifted from an already-proven surface.
    <!-- PATCHOPS_PATCH86B_STATUS:END -->
    """
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH86B_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH86B_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH86B_STATUS:START -->",
    "<!-- PATCHOPS_PATCH86B_STATUS:END -->",
    project_status_block,
)

print(f"UPDATED: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")