import json
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = PROJECT_ROOT / "powershell" / "Invoke-PatchVerify.ps1"
TRADER_MANIFEST = PROJECT_ROOT / "examples" / "trader_first_verify_patch.json"


def _powershell_exe() -> str:
    candidates = [
        shutil.which("powershell"),
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise AssertionError("Could not resolve powershell.exe for launcher testing.")


def test_invoke_patch_verify_launcher_exists() -> None:
    assert LAUNCHER_PATH.exists(), f"Missing launcher: {LAUNCHER_PATH}"


def test_invoke_patch_verify_launcher_stays_thin_and_verify_focused() -> None:
    text = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert "verify" in text
    assert "plan" in text
    assert "$PSScriptRoot" in text
    assert "Split-Path -Path $PSScriptRoot -Parent" in text
    assert "$arguments = @('-m', 'patchops.cli')" in text
    assert "--mode" in text
    assert "verify" in text
    assert "Invoke-PatchManifest" not in text


def test_invoke_patch_verify_preview_executes_successfully() -> None:
    result = subprocess.run(
        [
            _powershell_exe(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LAUNCHER_PATH),
            "-ManifestPath",
            str(TRADER_MANIFEST),
            "-Preview",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, (
        f"Launcher preview failed.\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )
    payload = json.loads(result.stdout)
    assert payload["mode"] == "verify"
    assert payload["manifest_path"].lower().endswith("trader_first_verify_patch.json")
    assert payload["active_profile"] == "trader"
    assert payload["wrapper_project_root"].lower().endswith("patchops")
