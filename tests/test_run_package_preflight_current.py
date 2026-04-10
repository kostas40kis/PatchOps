from __future__ import annotations

import json
from pathlib import Path

from patchops.package_runner import ProcessCapture, run_delivery_package


def _write_bundle(root: Path) -> Path:
    bundle_root = root / "demo_bundle"
    (bundle_root / "content" / "docs").mkdir(parents=True)
    (bundle_root / "content" / "docs" / "example.md").write_text("# example\n", encoding="utf-8")
    (bundle_root / "manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": "patch_32_package_authoring_preflight_hardening",
                "active_profile": "generic_python",
                "target_project_root": "C:/dev/patchops",
                "files_to_write": [
                    {
                        "path": "docs/example.md",
                        "content": None,
                        "content_path": "content/docs/example.md",
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
                    "report_dir": None,
                    "report_name_prefix": "patch_32_package_authoring_preflight_hardening",
                    "write_to_desktop": True,
                },
            }
        ),
        encoding="utf-8",
    )
    (bundle_root / "bundle_meta.json").write_text(
        json.dumps(
            {
                "bundle_schema_version": 1,
                "patch_name": "patch_32_package_authoring_preflight_hardening",
                "target_project": "patchops",
                "recommended_profile": "generic_python",
                "target_project_root": r"C:\dev\patchops",
                "wrapper_project_root": r"C:\dev\patchops",
                "content_root": "content",
                "manifest_path": "manifest.json",
                "launcher_path": "run_with_patchops.ps1",
            }
        ),
        encoding="utf-8",
    )
    (bundle_root / "run_with_patchops.ps1").write_text(
        "param([string]$WrapperRepoRoot)\nWrite-Host 'launcher should not start during failed preflight'\n",
        encoding="utf-8",
    )
    return bundle_root


def test_run_package_fails_before_launcher_when_staged_test_file_is_missing(tmp_path: Path) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    outer_report = desktop_dir / "missing_staged_test.txt"

    manifest = json.loads((bundle_root / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"][0]["content_path"] = "content/tests/test_patch_29_wave.py"
    (bundle_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    runner_called = False

    def fake_runner(command: list[str], cwd: Path):
        nonlocal runner_called
        runner_called = True
        raise AssertionError("launcher should not be invoked when bundle preflight fails")

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert runner_called is False
    assert result.ok is False
    assert result.failure_category == "package_authoring_failure"
    assert result.inner_report_path is None
    assert "Bundle preflight failed before launcher execution" in result.stderr
    assert "content_path_missing" in result.stderr
    assert outer_report.exists()

    report_text = outer_report.read_text(encoding="utf-8")
    assert "Launcher invocation did not start." in report_text
    assert "content_path_missing" in report_text


def test_run_package_fails_before_launcher_when_content_subdirectory_is_missing(tmp_path: Path) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    outer_report = desktop_dir / "missing_content_directory.txt"

    manifest = json.loads((bundle_root / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"][0]["content_path"] = "content/generated/tests/test_patch_29.py"
    (bundle_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    runner_called = False

    def fake_runner(command: list[str], cwd: Path):
        nonlocal runner_called
        runner_called = True
        raise AssertionError("launcher should not be invoked when bundle preflight fails")

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert runner_called is False
    assert result.ok is False
    assert result.failure_category == "package_authoring_failure"
    assert "content_subdirectory_missing" in result.stderr
    assert "content_path_missing" in result.stderr
    assert outer_report.exists()


def test_run_package_fails_before_launcher_when_python_helper_is_invalid(tmp_path: Path) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    outer_report = desktop_dir / "invalid_helper.txt"
    (bundle_root / "prepare_patch.py").write_text("def broken(:\n    pass\n", encoding="utf-8")

    runner_called = False

    def fake_runner(command: list[str], cwd: Path):
        nonlocal runner_called
        runner_called = True
        raise AssertionError("launcher should not be invoked when bundle preflight fails")

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert runner_called is False
    assert result.ok is False
    assert result.failure_category == "package_authoring_failure"
    assert "helper_python_syntax_invalid" in result.stderr
    assert "prepare_patch.py" in result.stderr
    assert outer_report.exists()


def test_run_package_skips_strict_preflight_for_bare_legacy_transport_bundle(tmp_path: Path) -> None:
    bundle_root = tmp_path / "legacy_bundle"
    (bundle_root / "launchers").mkdir(parents=True)
    (bundle_root / "content").mkdir(parents=True)
    (bundle_root / "manifest.json").write_text("{}\n", encoding="utf-8")
    (bundle_root / "bundle_meta.json").write_text("{}\n", encoding="utf-8")
    (bundle_root / "launchers" / "apply_with_patchops.ps1").write_text("param([string]$WrapperRepoRoot)\nWrite-Output 'legacy'\n", encoding="utf-8")

    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    outer_report = desktop_dir / "legacy_transport.txt"

    runner_called = False

    def fake_runner(command: list[str], cwd: Path):
        nonlocal runner_called
        runner_called = True
        return ProcessCapture(command=command, working_directory=str(cwd), exit_code=0, stdout="legacy ok\n", stderr="")

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert runner_called is True
    assert result.launcher_path.endswith("apply_with_patchops.ps1")
    assert "Bundle preflight skipped because the bundle does not advertise the canonical staged-authoring contract." in result.notes


def test_run_package_fails_before_launcher_when_generated_test_source_is_invalid(tmp_path: Path) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    outer_report = desktop_dir / "invalid_generated_test_source.txt"

    generated_test = bundle_root / "content" / "tests" / "test_generated_patch_29_surface.py"
    generated_test.parent.mkdir(parents=True, exist_ok=True)
    generated_test.write_text("def test_generated():\nassert True\n", encoding="utf-8")

    manifest = json.loads((bundle_root / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"].append(
        {
            "path": "tests/test_generated_patch_29_surface.py",
            "content": None,
            "content_path": "content/tests/test_generated_patch_29_surface.py",
            "encoding": "utf-8",
        }
    )
    (bundle_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    runner_called = False

    def fake_runner(command: list[str], cwd: Path):
        nonlocal runner_called
        runner_called = True
        raise AssertionError("launcher should not be invoked when bundle preflight fails")

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert runner_called is False
    assert result.ok is False
    assert result.failure_category == "package_authoring_failure"
    assert "generated_python_syntax_invalid" in result.stderr
    assert "test_generated_patch_29_surface.py" in result.stderr
    assert outer_report.exists()
