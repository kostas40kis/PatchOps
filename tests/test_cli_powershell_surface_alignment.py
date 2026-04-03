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
