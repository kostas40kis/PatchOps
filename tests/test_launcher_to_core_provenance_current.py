from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = PROJECT_ROOT / "powershell" / "Invoke-PatchManifest.ps1"
WRITE_ORIGIN_MARKERS = [
    "mp29_launcher_to_core_provenance_proof",
    "wrapper_owned_write_engine",
    "mp28_file_write_origin_report_contract",
    "File Write Origin    : wrapper_owned_write_engine",
    "File Write Origin",
    "Write Origin",
    "Wrapper-Owned Write Engine",
    "Wrapper Write Engine",
    "Writes Applied By Wrapper",
    "Writes Applied By",
]


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
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir.resolve()),
            "report_name_prefix": "mp29_launcher",
            "write_to_desktop": False,
        },
    }

    manifest_path = tmp_path / "mp29_launcher_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    written_file = target_root / "generated" / "launcher_probe.txt"
    return manifest_path, report_dir, written_file


def _run_launcher(manifest_path: Path) -> subprocess.CompletedProcess[str]:
    powershell = _powershell_exe()
    candidates = [
        [
            powershell,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LAUNCHER_PATH),
            "-ManifestPath",
            str(manifest_path),
        ],
        [
            powershell,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LAUNCHER_PATH),
            "-ManifestPath",
            str(manifest_path),
            "-WrapperProjectRoot",
            str(PROJECT_ROOT),
        ],
        [
            powershell,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LAUNCHER_PATH),
            "-ManifestPath",
            str(manifest_path),
            "-WrapperRepoRoot",
            str(PROJECT_ROOT),
        ],
    ]

    last = None
    for command in candidates:
        result = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        last = result
        if result.returncode == 0:
            return result
        combined = (result.stdout + "\n" + result.stderr).lower()
        if "parameter cannot be found" in combined or "named parameter" in combined:
            continue
        return result
    assert last is not None
    return last


def test_powershell_launcher_preserves_wrapper_provenance_into_report(tmp_path: Path) -> None:
    manifest_path, report_dir, written_file = _write_manifest(tmp_path)

    result = _run_launcher(manifest_path)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert written_file.exists()
    assert written_file.read_text(encoding="utf-8") == "launcher provenance proof\n"

    reports = sorted(report_dir.glob("*.txt"))
    assert reports, "expected launcher run to emit a report"
    report_text = reports[-1].read_text(encoding="utf-8")

    assert "PATCHOPS APPLY" in report_text
    assert "Wrapper Mode Used    : apply" in report_text
    assert f"Manifest Path Used   : {manifest_path}" in report_text
    assert "Profile Resolved     : generic_python" in report_text
    assert "Runtime Resolved     : (none)" in report_text
    assert any(marker in report_text for marker in WRITE_ORIGIN_MARKERS)