from __future__ import annotations

import json
from pathlib import Path
import zipfile

from patchops.bundles import build_patchops_bundle_launcher
from patchops.bundles.preflight import preflight_bundle_zip


def _write_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _build_bundle_zip(
    tmp_path: Path,
    *,
    patch_name: str = "zp15_demo",
    root_launcher_text: str | None = None,
) -> Path:
    bundle_root = tmp_path / patch_name
    content_root = bundle_root / "content"
    docs_root = content_root / "docs"
    tests_root = content_root / "tests"
    docs_root.mkdir(parents=True)
    tests_root.mkdir(parents=True)

    (docs_root / "note.md").write_text("# note\n", encoding="utf-8")
    (tests_root / "test_note_current.py").write_text("def test_note():\n    assert True\n", encoding="utf-8")

    safe_root_launcher = root_launcher_text or build_patchops_bundle_launcher(
        wrapper_project_root=r"C:\dev\patchops",
        mode="apply",
        launcher_directory_relative_to_bundle_root=False,
    )
    (bundle_root / "run_with_patchops.ps1").write_text(safe_root_launcher, encoding="utf-8")
    (bundle_root / "README.txt").write_text("demo bundle\n", encoding="utf-8")

    metadata = {
        "bundle_schema_version": 1,
        "patch_name": patch_name,
        "target_project": "patchops",
        "recommended_profile": "generic_python",
        "target_project_root": "C:\\dev\\patchops",
        "wrapper_project_root": "C:\\dev\\patchops",
        "content_root": "content",
        "manifest_path": "manifest.json",
        "launcher_path": "run_with_patchops.ps1",
    }
    (bundle_root / "bundle_meta.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "manifest_version": 1,
        "patch_name": patch_name,
        "active_profile": "generic_python",
        "target_project_root": "C:\\dev\\patchops",
        "files_to_write": [
            {
                "target_path": "docs\\note.md",
                "content_path": "content/docs/note.md",
            },
            {
                "target_path": "tests\\test_note_current.py",
                "content_path": "content/tests/test_note_current.py",
            },
        ],
        "validation_commands": [
            {
                "name": "demo_contract",
                "command": ["py", "-m", "pytest", "-q", "tests/test_note_current.py"],
            }
        ],
    }
    (bundle_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    zip_path = tmp_path / f"{patch_name}.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in bundle_root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_root))
    return zip_path


def test_preflight_bundle_zip_returns_green_for_safe_bundle(tmp_path: Path) -> None:
    zip_path = _build_bundle_zip(tmp_path, patch_name="zp15_safe")
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = preflight_bundle_zip(
        zip_path,
        wrapper_root,
        timestamp_token="20260407_173500",
    )

    assert result.is_valid is True
    assert result.ok is True
    assert result.warning_count == 0
    assert result.inspect.target_paths == ("docs\\note.md", "tests\\test_note_current.py")
    assert result.inspect.validation_command_names == ("demo_contract",)
    assert result.launcher_audits
    assert all(audit.ok for audit in result.launcher_audits)
    audited_names = {audit.path.name for audit in result.launcher_audits}
    assert "run_with_patchops.ps1" in audited_names


def test_preflight_bundle_zip_reports_launcher_findings_for_risky_launcher(tmp_path: Path) -> None:
    risky_launcher = """param([string]$WrapperRepoRoot = 'C:\\dev\\patchops')
$state = Get-Content state.json | ConvertFrom-Json
py -c "print('demo')"
"""
    zip_path = _build_bundle_zip(
        tmp_path,
        patch_name="zp15_risky",
        root_launcher_text=risky_launcher,
    )
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = preflight_bundle_zip(
        zip_path,
        wrapper_root,
        timestamp_token="20260407_173501",
    )

    assert result.is_valid is True
    assert result.ok is False
    findings = {code for audit in result.launcher_audits for code in audit.codes}
    assert "fragile_json_handoff" in findings
    assert "large_inline_python_emission" in findings


def test_preflight_bundle_zip_returns_failed_check_state_for_invalid_bundle(tmp_path: Path) -> None:
    zip_path = _build_bundle_zip(tmp_path, patch_name="zp15_invalid")
    broken_dir = tmp_path / "broken_bundle"
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(broken_dir)
    (broken_dir / "manifest.json").unlink()

    broken_zip = tmp_path / "zp15_invalid_broken.zip"
    with zipfile.ZipFile(broken_zip, "w") as archive:
        for path in broken_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(broken_dir))

    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = preflight_bundle_zip(
        broken_zip,
        wrapper_root,
        timestamp_token="20260407_173502",
    )

    assert result.is_valid is False
    assert result.ok is False
    assert "bundle_validation_failed" in result.warnings
    assert result.inspect.resolved_layout is None
    assert result.launcher_audits == ()
