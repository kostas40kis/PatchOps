from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_python_only_helper_surface_boundary.py"
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

    import argparse
    from pathlib import Path

    from patchops import cli


    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    POWERSHELL_DIR = PROJECT_ROOT / "powershell"

    PYTHON_ONLY_HELPER_COMMANDS = {
        "bootstrap-target",
        "recommend-profile",
        "starter",
        "init-project-doc",
        "refresh-project-doc",
    }

    FORBIDDEN_LAUNCHERS = {
        "Invoke-PatchBootstrapTarget.ps1",
        "Invoke-PatchRecommendProfile.ps1",
        "Invoke-PatchStarter.ps1",
        "Invoke-PatchInitProjectDoc.ps1",
        "Invoke-PatchRefreshProjectDoc.ps1",
    }


    def _subcommand_names() -> set[str]:
        parser = cli.build_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                return set(action.choices.keys())
        raise AssertionError("PatchOps parser did not expose a subcommand action.")


    def test_python_only_helper_commands_remain_shipped() -> None:
        subcommands = _subcommand_names()
        assert PYTHON_ONLY_HELPER_COMMANDS.issubset(subcommands)


    def test_python_only_helper_commands_remain_launcherless() -> None:
        discovered_launchers = {path.name for path in POWERSHELL_DIR.glob("Invoke-Patch*.ps1")}
        unexpected = sorted(FORBIDDEN_LAUNCHERS.intersection(discovered_launchers))
        assert not unexpected, f"Python-only helper commands unexpectedly gained PowerShell launchers: {unexpected}"
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH119_LEDGER:START -->
    ## Patch 119

    Patch 119 adds a narrow boundary validation surface for the maintained Python-only helper command layer.

    It proves the shipped helper-first commands still exist:
    - `bootstrap-target`
    - `recommend-profile`
    - `starter`
    - `init-project-doc`
    - `refresh-project-doc`

    It also keeps explicit that these helper surfaces remain Python-owned rather than growing new PowerShell launchers.

    This is a narrow maintenance validation patch, not an onboarding redesign.
    <!-- PATCHOPS_PATCH119_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH119_STATUS:START -->
    ## Patch 119 - Python-only helper surface boundary validation

    ### Current state

    - Patch 119 adds a narrow boundary test for the helper-first Python-only command layer.
    - The new test keeps two things explicit:
      - the shipped helper commands still exist,
      - the helper-first layer remains Python-owned rather than gaining new thin PowerShell wrappers.

    ### Why this matters

    - the onboarding helper boundary now stays explicit and test-backed,
    - future drift toward unnecessary PowerShell expansion is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small boundary or contract tests when the main risk is drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH119_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH119_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH119_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH119_STATUS:START -->",
    "<!-- PATCHOPS_PATCH119_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")