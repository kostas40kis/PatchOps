from __future__ import annotations

import json
import subprocess
from pathlib import Path
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )


def _build_proof_bundle(tmp_path: Path) -> tuple[Path, Path]:
    bundle_root = tmp_path / "documentation_proof_bundle"
    content_root = bundle_root / "content"
    docs_root = content_root / "docs"
    launchers_root = bundle_root / "launchers"
    docs_root.mkdir(parents=True)
    launchers_root.mkdir(parents=True)

    (bundle_root / "run_with_patchops.ps1").write_text(
        'param([string]$WrapperRepoRoot = "C:\\dev\\patchops")\n'
        '$bundleRoot = Split-Path -Parent $PSCommandPath\n'
        '$manifestPath = Join-Path $bundleRoot "manifest.json"\n'
        'Set-Location $WrapperRepoRoot\n'
        'py -m patchops.cli check-bundle $bundleRoot\n'
        'if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }\n'
        'py -m patchops.cli apply $manifestPath --wrapper-root $WrapperRepoRoot\n'
        'exit $LASTEXITCODE\n',
        encoding="utf-8",
    )
    (launchers_root / "README.txt").write_text("launcher directory presence for bundle preflight\n", encoding="utf-8")
    (docs_root / "proof_note.md").write_text("# proof note\n", encoding="utf-8")

    metadata = {
        "bundle_schema_version": 1,
        "patch_name": "documentation_proof_bundle",
        "target_project": "patchops",
        "target_project_root": "C:\\dev\\patchops",
        "wrapper_project_root": "C:\\dev\\patchops",
        "recommended_profile": "generic_python",
        "content_root": "content",
        "manifest_path": "manifest.json",
        "launcher_path": "run_with_patchops.ps1",
    }
    (bundle_root / "bundle_meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    manifest = {
        "manifest_version": "1",
        "patch_name": "documentation_proof_bundle",
        "active_profile": "generic_python",
        "target_project_root": "C:/dev/patchops",
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": None,
            "report_name_prefix": "documentation_proof_bundle",
            "write_to_desktop": True,
        },
    }
    (bundle_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    (bundle_root / "README.txt").write_text("documentation proof bundle\n", encoding="utf-8")

    zip_path = tmp_path / "documentation_proof_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in bundle_root.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(tmp_path))

    return bundle_root, zip_path


def test_refreshed_docs_keep_current_actionable_surfaces_visible() -> None:
    readme = _read("README.md").lower()
    quickstart = _read("docs/operator_quickstart.md").lower()
    llm_usage = _read("docs/llm_usage.md").lower()
    examples = _read("docs/examples.md").lower()

    assert "run-package" in readme
    assert "check-bundle" in readme
    assert r"c:\dev\patchops" in quickstart
    assert "run-package" in quickstart
    assert "check-bundle" in quickstart
    assert "bundle-doctor" in quickstart
    assert "continue patch by patch from evidence" in quickstart
    assert "thin powershell" in llm_usage
    assert "run-package" in examples


def test_documented_bundle_review_surface_works_for_bundle_zip(tmp_path: Path) -> None:
    _, zip_path = _build_proof_bundle(tmp_path)
    result = _run_cli("py", "-m", "patchops.cli", "check-bundle", str(zip_path))
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    lowered = result.stdout.lower()
    assert '"ok": true' in lowered or '"ok":true' in lowered


def test_documented_normal_bundle_run_command_stays_visible() -> None:
    quickstart = _read("docs/operator_quickstart.md")
    expected = 'py -m patchops.cli run-package "D:\\some_patch_bundle.zip" --wrapper-root "C:\\dev\\patchops"'
    assert expected in quickstart


def test_quickstart_keeps_bundle_review_and_failure_reading_sequence_visible() -> None:
    quickstart = _read("docs/operator_quickstart.md").lower()
    assert "bundle-doctor" in quickstart
    assert "canonical desktop txt report" in quickstart
    assert "read the canonical desktop txt report" in quickstart
