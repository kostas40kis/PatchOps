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
    "setup-windows-env",
}

FORBIDDEN_LAUNCHERS = {
    "Invoke-PatchBootstrapTarget.ps1",
    "Invoke-PatchRecommendProfile.ps1",
    "Invoke-PatchStarter.ps1",
    "Invoke-PatchInitProjectDoc.ps1",
    "Invoke-PatchRefreshProjectDoc.ps1",
    "Invoke-PatchSetupWindowsEnv.ps1",
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
