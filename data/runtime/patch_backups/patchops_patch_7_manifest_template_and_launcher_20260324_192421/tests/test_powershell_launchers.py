from pathlib import Path


def test_plan_launcher_invokes_plan_cli():
    text = Path("powershell/Invoke-PatchPlan.ps1").read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert '"plan"' in text
    assert "--wrapper-root" in text


def test_inspect_launcher_invokes_inspect_cli():
    text = Path("powershell/Invoke-PatchInspect.ps1").read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert '"inspect"' in text


def test_profiles_launcher_invokes_profiles_cli():
    text = Path("powershell/Invoke-PatchProfiles.ps1").read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert '"profiles"' in text
    assert "--wrapper-root" in text