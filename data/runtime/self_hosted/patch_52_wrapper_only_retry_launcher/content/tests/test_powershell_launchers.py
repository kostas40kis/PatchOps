from pathlib import Path


def test_manifest_launcher_invokes_apply_cli():
    text = Path("powershell/Invoke-PatchManifest.ps1").read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert '"apply"' in text


def test_verify_launcher_invokes_verify_cli():
    text = Path("powershell/Invoke-PatchVerify.ps1").read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert '"verify"' in text


def test_wrapper_retry_launcher_invokes_wrapper_retry_cli():
    text = Path("powershell/Invoke-PatchWrapperRetry.ps1").read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert "wrapper-retry" in text
    assert "--retry-reason" in text
    assert "--wrapper-root" in text


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


def test_template_launcher_invokes_template_cli_and_supports_output_path():
    text = Path("powershell/Invoke-PatchTemplate.ps1").read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert '"template"' in text
    assert "--wrapper-root" in text
    assert "--output-path" in text


def test_check_launcher_invokes_check_cli():
    text = Path("powershell/Invoke-PatchCheck.ps1").read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert '"check"' in text