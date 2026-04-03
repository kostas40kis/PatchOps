from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POWERSHELL_DIR = PROJECT_ROOT / "powershell"

SECONDARY_LAUNCHERS = (
    "Invoke-PatchHandoff.ps1",
    "Invoke-PatchInspect.ps1",
    "Invoke-PatchSchema.ps1",
)


def test_secondary_powershell_launchers_exist() -> None:
    missing = [
        str((POWERSHELL_DIR / name).relative_to(PROJECT_ROOT))
        for name in SECONDARY_LAUNCHERS
        if not (POWERSHELL_DIR / name).exists()
    ]
    assert not missing, f"Missing maintained secondary PowerShell launchers: {missing}"


def test_secondary_powershell_launcher_inventory_stays_explicit() -> None:
    discovered = {path.name for path in POWERSHELL_DIR.glob("Invoke-Patch*.ps1")}
    expected = set(SECONDARY_LAUNCHERS)
    assert expected.issubset(discovered)
