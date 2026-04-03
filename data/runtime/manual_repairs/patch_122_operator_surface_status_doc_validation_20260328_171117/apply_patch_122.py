from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_operator_surface_status_docs.py"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"


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


test_content = textwrap.dedent(
    """\
    from __future__ import annotations

    from pathlib import Path


    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    PROJECT_STATUS = PROJECT_ROOT / "docs" / "project_status.md"
    PATCH_LEDGER = PROJECT_ROOT / "docs" / "patch_ledger.md"


    def test_project_status_keeps_recent_operator_surface_wave_explicit() -> None:
        text = PROJECT_STATUS.read_text(encoding="utf-8")

        required_headings = [
            "## Patch 118 - CLI and PowerShell surface alignment validation",
            "## Patch 119 - Python-only helper surface boundary validation",
            "## Patch 120 - operator surface partition validation",
            "## Patch 121 - exact PowerShell launcher set validation",
        ]
        for heading in required_headings:
            assert heading in text

        required_phrases = [
            "launcher-backed commands",
            "Python-only helper commands",
            "thin PowerShell launcher layer",
            "maintenance validation rather than redesign",
        ]
        for phrase in required_phrases:
            assert phrase in text


    def test_patch_ledger_keeps_recent_operator_surface_wave_explicit() -> None:
        text = PATCH_LEDGER.read_text(encoding="utf-8")

        required_sections = [
            "## Patch 118",
            "## Patch 119",
            "## Patch 120",
            "## Patch 121",
        ]
        for section in required_sections:
            assert section in text

        required_phrases = [
            "launcher-backed CLI commands",
            "Python-only helper command layer",
            "operator command map",
            "exact thin PowerShell launcher set",
        ]
        for phrase in required_phrases:
            assert phrase in text
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH122_LEDGER:START -->
    ## Patch 122

    Patch 122 adds a narrow documentation-validation surface for the recent operator-surface hardening wave.

    It proves the maintained status docs still keep the latest operator-surface maintenance sequence explicit:
    - CLI and PowerShell surface alignment,
    - Python-only helper boundary,
    - operator-surface partitioning,
    - exact thin PowerShell launcher set.

    This is a narrow maintenance validation patch, not a documentation redesign.
    <!-- PATCHOPS_PATCH122_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH122_STATUS:START -->
    ## Patch 122 - operator surface status doc validation

    ### Current state

    - Patch 122 adds a narrow documentation-validation test for the recent operator-surface hardening wave.
    - The new test protects the maintained status surfaces that describe:
      - launcher-backed alignment,
      - Python-only helper boundaries,
      - operator-surface partitioning,
      - exact thin PowerShell launcher bounds.

    ### Why this matters

    - the recent maintenance wave now stays explicit in both code-facing and doc-facing surfaces,
    - future doc drift is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small boundary, inventory, or doc-contract tests when the main risk is drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH122_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH122_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH122_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH122_STATUS:START -->",
    "<!-- PATCHOPS_PATCH122_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")