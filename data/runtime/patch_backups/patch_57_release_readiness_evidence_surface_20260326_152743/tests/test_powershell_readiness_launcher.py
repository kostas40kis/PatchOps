import json
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = PROJECT_ROOT / "powershell" / "Invoke-PatchReadiness.ps1"

REQUIRED_RELEASE_DOCS = (
    "docs/release_checklist.md",
    "docs/stage1_freeze_checklist.md",
    "docs/project_status.md",
    "docs/patch_ledger.md",
)

REQUIRED_RELEASE_EXAMPLES = (
    "examples/trader_first_doc_patch.json",
    "examples/trader_first_verify_patch.json",
    "examples/generic_python_patch.json",
    "examples/generic_verify_patch.json",
)

REQUIRED_RELEASE_WORKFLOWS = (
    "patchops/cli.py",
    "patchops/readiness.py",
    "patchops/initial_milestone_gate.py",
    "patchops/workflows/verify_only.py",
    "patchops/workflows/wrapper_retry.py",
)

REQUIRED_RELEASE_LAUNCHERS = (
    "powershell/Invoke-PatchManifest.ps1",
    "powershell/Invoke-PatchVerify.ps1",
    "powershell/Invoke-PatchWrapperRetry.ps1",
)


def _powershell_exe() -> str:
    candidates = [
        shutil.which("powershell"),
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise AssertionError("Could not resolve powershell.exe for launcher testing.")


def _write_file(root: Path, relative: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("ok", encoding="utf-8")


def _seed_release_ready_wrapper_root(root: Path) -> None:
    for relative in (
        *REQUIRED_RELEASE_DOCS,
        *REQUIRED_RELEASE_EXAMPLES,
        *REQUIRED_RELEASE_WORKFLOWS,
        *REQUIRED_RELEASE_LAUNCHERS,
    ):
        _write_file(root, relative)


def test_invoke_patch_readiness_launcher_exists() -> None:
    assert LAUNCHER_PATH.exists(), f"Missing launcher: {LAUNCHER_PATH}"


def test_invoke_patch_readiness_launcher_stays_thin_and_readiness_focused() -> None:
    text = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert "patchops.cli" in text
    assert '"release-readiness"' in text
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
    _seed_release_ready_wrapper_root(tmp_path)

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
    assert payload["core_tests_state"] == "green"