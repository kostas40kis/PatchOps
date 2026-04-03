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
