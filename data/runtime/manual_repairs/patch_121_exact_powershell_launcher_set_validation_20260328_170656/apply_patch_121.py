from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_exact_powershell_launcher_set.py"
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
    POWERSHELL_DIR = PROJECT_ROOT / "powershell"

    EXPECTED_LAUNCHERS = {
        "Invoke-PatchManifest.ps1",
        "Invoke-PatchVerify.ps1",
        "Invoke-PatchWrapperRetry.ps1",
        "Invoke-PatchProfiles.ps1",
        "Invoke-PatchDoctor.ps1",
        "Invoke-PatchExamples.ps1",
        "Invoke-PatchSchema.ps1",
        "Invoke-PatchCheck.ps1",
        "Invoke-PatchInspect.ps1",
        "Invoke-PatchPlan.ps1",
        "Invoke-PatchTemplate.ps1",
        "Invoke-PatchHandoff.ps1",
        "Invoke-PatchReadiness.ps1",
    }


    def test_exact_powershell_launcher_set_remains_explicit() -> None:
        discovered = {path.name for path in POWERSHELL_DIR.glob("Invoke-Patch*.ps1")}
        assert discovered == EXPECTED_LAUNCHERS


    def test_exact_powershell_launcher_count_remains_stable() -> None:
        assert len(EXPECTED_LAUNCHERS) == 13
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH121_LEDGER:START -->
    ## Patch 121

    Patch 121 adds a narrow validation surface for the exact thin PowerShell launcher set.

    It proves the maintained launcher layer remains exactly:
    - manifest
    - verify
    - wrapper retry
    - profiles
    - doctor
    - examples
    - schema
    - check
    - inspect
    - plan
    - template
    - handoff
    - readiness

    This is a narrow maintenance validation patch, not a launcher redesign.
    <!-- PATCHOPS_PATCH121_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH121_STATUS:START -->
    ## Patch 121 - exact PowerShell launcher set validation

    ### Current state

    - Patch 121 adds a narrow exact-set test for the maintained thin PowerShell launcher layer.
    - The new test keeps explicit that the launcher surface is not only present but also bounded.

    ### Why this matters

    - the shipped launcher layer now fails on both missing and unexpected launcher drift,
    - future PowerShell expansion is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small exact-set, boundary, or contract tests when the main risk is drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH121_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH121_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH121_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH121_STATUS:START -->",
    "<!-- PATCHOPS_PATCH121_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")