from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_cli_powershell_surface_alignment.py"
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

    CLI_TO_LAUNCHER = {
        "apply": "Invoke-PatchManifest.ps1",
        "verify": "Invoke-PatchVerify.ps1",
        "wrapper-retry": "Invoke-PatchWrapperRetry.ps1",
        "profiles": "Invoke-PatchProfiles.ps1",
        "doctor": "Invoke-PatchDoctor.ps1",
        "examples": "Invoke-PatchExamples.ps1",
        "schema": "Invoke-PatchSchema.ps1",
        "check": "Invoke-PatchCheck.ps1",
        "inspect": "Invoke-PatchInspect.ps1",
        "plan": "Invoke-PatchPlan.ps1",
        "template": "Invoke-PatchTemplate.ps1",
        "export-handoff": "Invoke-PatchHandoff.ps1",
        "release-readiness": "Invoke-PatchReadiness.ps1",
    }


    def _subcommand_names() -> set[str]:
        parser = cli.build_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                return set(action.choices.keys())
        raise AssertionError("PatchOps parser did not expose a subcommand action.")


    def test_launcher_backed_cli_surface_remains_aligned() -> None:
        subcommands = _subcommand_names()

        missing_commands = [name for name in CLI_TO_LAUNCHER if name not in subcommands]
        assert not missing_commands, f"Missing launcher-backed CLI commands: {missing_commands}"

        missing_launchers = [
            launcher
            for launcher in CLI_TO_LAUNCHER.values()
            if not (POWERSHELL_DIR / launcher).exists()
        ]
        assert not missing_launchers, f"Missing launchers for maintained CLI surface: {missing_launchers}"


    def test_launcher_backed_surface_mapping_stays_explicit() -> None:
        discovered_launchers = {path.name for path in POWERSHELL_DIR.glob("Invoke-Patch*.ps1")}
        expected_launchers = set(CLI_TO_LAUNCHER.values())

        assert expected_launchers.issubset(discovered_launchers)
        assert len(CLI_TO_LAUNCHER) == len(expected_launchers)
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH118_LEDGER:START -->
    ## Patch 118

    Patch 118 adds a narrow alignment validation surface between the maintained launcher-backed CLI commands
    and the thin PowerShell launcher layer.

    It proves the current shipped mapping remains explicit across:
    apply, verify, wrapper-retry, discovery, inspection, schema, planning, template, handoff export, and release readiness.

    This is a narrow maintenance validation patch, not a CLI or launcher redesign.
    <!-- PATCHOPS_PATCH118_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH118_STATUS:START -->
    ## Patch 118 - CLI and PowerShell surface alignment validation

    ### Current state

    - Patch 118 adds a narrow alignment test for the launcher-backed operator surface.
    - The new test protects the maintained mapping between:
      - shipped CLI commands,
      - thin PowerShell launchers.

    ### Why this matters

    - launcher-backed operator entry points now stay aligned as one maintained surface,
    - future drift between CLI and launcher layers is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small alignment or contract tests when the main risk is drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH118_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH118_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH118_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH118_STATUS:START -->",
    "<!-- PATCHOPS_PATCH118_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")