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
