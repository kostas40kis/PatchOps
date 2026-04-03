from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_powershell_launcher_inventory.py"
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

    MAIN_LAUNCHERS = (
        "Invoke-PatchManifest.ps1",
        "Invoke-PatchVerify.ps1",
        "Invoke-PatchWrapperRetry.ps1",
        "Invoke-PatchReadiness.ps1",
        "Invoke-PatchProfiles.ps1",
        "Invoke-PatchDoctor.ps1",
        "Invoke-PatchExamples.ps1",
        "Invoke-PatchTemplate.ps1",
        "Invoke-PatchCheck.ps1",
        "Invoke-PatchPlan.ps1",
    )


    def test_main_powershell_launchers_exist() -> None:
        missing = [
            str((POWERSHELL_DIR / name).relative_to(PROJECT_ROOT))
            for name in MAIN_LAUNCHERS
            if not (POWERSHELL_DIR / name).exists()
        ]
        assert not missing, f"Missing maintained PowerShell launchers: {missing}"


    def test_main_powershell_launcher_inventory_stays_explicit() -> None:
        discovered = {path.name for path in POWERSHELL_DIR.glob("Invoke-Patch*.ps1")}
        expected = set(MAIN_LAUNCHERS)
        assert expected.issubset(discovered)
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH115_LEDGER:START -->
    ## Patch 115

    Patch 115 adds a narrow inventory validation surface for the maintained PowerShell launcher layer.

    It proves the main thin launcher set still exists for the shipped authoring, discovery, execution,
    retry, and readiness flows.

    This is a narrow maintenance validation patch, not a launcher redesign.
    <!-- PATCHOPS_PATCH115_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH115_STATUS:START -->
    ## Patch 115 - PowerShell launcher inventory validation

    ### Current state

    - Patch 115 adds a narrow inventory test for the maintained PowerShell launcher surface.
    - The new test protects the main thin launcher set used across:
      - apply / verify,
      - wrapper-only retry,
      - release readiness,
      - discovery and authoring flows.

    ### Why this matters

    - the documented launcher layer stays explicit and test-backed,
    - future launcher drift is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small inventory or contract tests when the main risk is operator-surface drift across already-shipped tooling.
    <!-- PATCHOPS_PATCH115_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH115_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH115_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH115_STATUS:START -->",
    "<!-- PATCHOPS_PATCH115_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")