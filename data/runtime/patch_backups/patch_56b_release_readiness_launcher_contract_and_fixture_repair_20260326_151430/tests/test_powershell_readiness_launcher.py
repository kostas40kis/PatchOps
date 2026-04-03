import json
import shutil
import subprocess
from pathlib import Path

from patchops.readiness import (
    REQUIRED_INITIAL_MILESTONE_DOCS,
    REQUIRED_INITIAL_MILESTONE_EXAMPLES,
    REQUIRED_INITIAL_MILESTONE_WORKFLOWS,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = PROJECT_ROOT / "powershell" / "Invoke-PatchReadiness.ps1"


def _powershell_exe() -> str:
    candidates = [
        shutil.which("powershell"),
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise AssertionError("Could not resolve powershell.exe for launcher testing.")


def test_invoke_patch_readiness_launcher_exists() -> None:
    assert LAUNCHER_PATH.exists(), f"Missing launcher: {LAUNCHER_PATH}"


def test_invoke_patch_readiness_launcher_stays_thin_and_readiness_focused() -> None:
    text = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert "release-readiness" in text
    assert "$PSScriptRoot" in text
    assert "Split-Path -Path $PSScriptRoot -Parent" in text
    assert "$arguments = @('-m', 'patchops.cli')" in text
    assert "--wrapper-root" in text
    assert "--profile" in text
    assert "--core-tests-green" in text
    assert "Invoke-PatchManifest" not in text


def test_invoke_patch_readiness_launcher_executes_successfully_against_seeded_green_wrapper_root(
    tmp_path: Path,
) -> None:
    for relative in (
        *REQUIRED_INITIAL_MILESTONE_DOCS,
        *REQUIRED_INITIAL_MILESTONE_EXAMPLES,
        *REQUIRED_INITIAL_MILESTONE_WORKFLOWS,
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok", encoding="utf-8")

    result = subprocess.run(
        [
            _powershell_exe(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LAUNCHER_PATH),
            "-WrapperRoot",
            str(tmp_path),
            "-Profile",
            "trader",
            "-CoreTestsGreen",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, (
        f"Launcher readiness execution failed.\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "green"
    assert payload["core_tests_green"] is True