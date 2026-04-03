from pathlib import Path


def test_invoke_patch_handoff_launcher_exists() -> None:
    path = Path("powershell/Invoke-PatchHandoff.ps1")
    assert path.exists()


def test_invoke_patch_handoff_launcher_calls_export_handoff_cli() -> None:
    text = Path("powershell/Invoke-PatchHandoff.ps1").read_text(encoding="utf-8")

    assert "patchops.cli" in text
    assert "export-handoff" in text
    assert "--wrapper-root" in text
    assert "--current-stage" in text
    assert "--bundle-name" in text


def test_invoke_patch_handoff_launcher_uses_thin_process_capture_pattern() -> None:
    text = Path("powershell/Invoke-PatchHandoff.ps1").read_text(encoding="utf-8")

    assert "System.Diagnostics.ProcessStartInfo" in text
    assert "RedirectStandardOutput = $true" in text
    assert "RedirectStandardError = $true" in text
    assert "CreateNoWindow = $true" in text
    assert "UseShellExecute = $false" in text


def test_invoke_patch_handoff_launcher_writes_one_desktop_report_and_opens_it() -> None:
    text = Path("powershell/Invoke-PatchHandoff.ps1").read_text(encoding="utf-8")

    assert "[Environment]::GetFolderPath('Desktop')" in text
    assert "patch_handoff_export_" in text
    assert "SUMMARY" in text
    assert "Invoke-Item -LiteralPath $launcherReportPath" in text


def test_handoff_surface_doc_mentions_patch_65_launcher() -> None:
    text = Path("docs/handoff_surface.md").read_text(encoding="utf-8")

    assert "Patch 65" in text
    assert "Invoke-PatchHandoff.ps1" in text
    assert "export-handoff" in text