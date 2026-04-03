import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = PROJECT_ROOT / "powershell" / "Invoke-PatchManifest.ps1"
WRITE_ORIGIN_MARKERS = ['mp28_file_write_origin_metadata_contract', 'wrapper_owned_write_engine', 'mp28_file_write_origin_report_contract', 'File Write Origin : wrapper_owned_write_engine', 'File Write Origin : {metadata.run_origin.file_write_origin or', 'File Write Origin', 'Write Origin', 'Wrapper-Owned Write Engine', 'Wrapper Write Engine', 'Writes Applied By Wrapper', 'Writes Applied By']


def _powershell_exe() -> str:
    candidates = [
        shutil.which("powershell"),
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    pytest.skip("Could not resolve powershell.exe for launcher testing.")


def _write_manifest(tmp_path: Path) -> tuple[Path, Path, Path]:
    target_root = tmp_path / "target"
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir = tmp_path / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp29_launcher_to_core_provenance_proof",
        "active_profile": "generic_python",
        "target_project_root": str(target_root.resolve()),
        "files_to_write": [
            {
                "path": "generated/launcher_probe.txt",
                "content": "launcher provenance proof\n",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [],
        "report_preferences": {
            "report_dir": str(report_dir.resolve()),
            "report_name_prefix": "mp29_launcher",
            "write_to_desktop": False,
        },
    }

    manifest_path = tmp_path / "mp29_launcher_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path, target_root, report_dir


def _assert_report_line_contains(report_text: str, label: str, expected_fragment: str) -> None:
    lines = report_text.splitlines()
    assert any(label in line and expected_fragment in line for line in lines), (
        f"Expected one report line containing label {label!r} and fragment {expected_fragment!r}.\n"
        f"Report text:\n{report_text}"
    )


def test_invoke_patch_manifest_launcher_preserves_provenance_into_report(tmp_path: Path) -> None:
    assert LAUNCHER_PATH.exists(), f"Missing launcher: {LAUNCHER_PATH}"

    manifest_path, target_root, report_dir = _write_manifest(tmp_path)
    powershell_exe = _powershell_exe()

    result = subprocess.run(
        [
            powershell_exe,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LAUNCHER_PATH),
            "-ManifestPath",
            str(manifest_path),
            "-PythonExe",
            sys.executable,
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, (
        f"Launcher apply failed.\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )

    written_path = target_root / "generated" / "launcher_probe.txt"
    assert written_path.exists(), f"Expected written file from launcher apply: {written_path}"

    reports = sorted(report_dir.glob("*.txt"))
    assert reports, f"Expected a generated report under {report_dir}"
    report_text = reports[-1].read_text(encoding="utf-8")

    assert "PATCHOPS APPLY" in report_text
    _assert_report_line_contains(report_text, "Manifest Path", str(manifest_path.resolve()))
    _assert_report_line_contains(report_text, "Wrapper Project Root", str(PROJECT_ROOT.resolve()))
    _assert_report_line_contains(report_text, "Target Project Root", str(target_root.resolve()))
    _assert_report_line_contains(report_text, "Active Profile", "generic_python")
    assert "Runtime Path" in report_text
    assert str(written_path.resolve()) in report_text
    assert any(marker in report_text for marker in WRITE_ORIGIN_MARKERS), (
        "Expected current write-origin proof marker in launcher-generated report.\n"
        f"Markers: {WRITE_ORIGIN_MARKERS}\n\nReport text:\n{report_text}"
    )
