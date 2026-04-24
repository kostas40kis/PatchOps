from __future__ import annotations

import zipfile
from pathlib import Path

from patchops import package_runner
from patchops.package_runner import ProcessCapture, run_delivery_package


def _write_bundle_zip(tmp_path: Path) -> Path:
    bundle_root = tmp_path / "reject_bundle"
    (bundle_root / "content").mkdir(parents=True)
    (bundle_root / "manifest.json").write_text("{}\n", encoding="utf-8")
    (bundle_root / "bundle_meta.json").write_text("{}\n", encoding="utf-8")
    (bundle_root / "README.txt").write_text("demo\n", encoding="utf-8")
    (bundle_root / "run_with_patchops.ps1").write_text(
        "& {\nparam([string]$WrapperRepoRoot)\nWrite-Host 'demo launcher'\n}\n",
        encoding="utf-8",
    )
    (bundle_root / "content" / "marker.txt").write_text("ok\n", encoding="utf-8")

    zip_path = tmp_path / "reject_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in bundle_root.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(tmp_path))
    return zip_path


def test_run_package_blocks_launcher_execution_when_bundle_review_rejects(tmp_path: Path, monkeypatch) -> None:
    zip_path = _write_bundle_zip(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    outer_report = desktop_dir / "outer_reject.txt"

    monkeypatch.setattr(package_runner, "_should_run_bundle_preflight", lambda bundle_root: False)
    monkeypatch.setattr(package_runner, "_discover_launcher", lambda *args, **kwargs: args[0] / "run_with_patchops.ps1")
    monkeypatch.setattr(
        package_runner,
        "_patchops_p01_should_preflight_reject",
        lambda source_path: (
            True,
            {
                "ok": False,
                "launcher_status": "reject",
                "launcher_issue_codes": ["launcher_risk_detected"],
                "issues": ["Launcher review rejected this bundle because the launcher matches the risky proof contract."],
                "launcher_review": {
                    "status": "reject",
                    "launcher_path": "reject_bundle/run_with_patchops.ps1",
                    "issue_count": 1,
                    "issues": [
                        {
                            "code": "launcher_risk_detected",
                            "message": "Launcher review rejected this bundle because the launcher matches the risky proof contract.",
                            "path": "reject_bundle/run_with_patchops.ps1",
                        }
                    ],
                },
            },
        ),
    )

    def fail_runner(command: list[str], cwd: Path):
        raise AssertionError("runner should not be called when launcher review rejects execution")

    result = run_delivery_package(
        zip_path,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fail_runner,
    )

    assert result.ok is False
    assert result.exit_code == 1
    assert result.failure_category == "package_authoring_failure"
    assert result.inner_report_path is None
    assert "launcher_risk_detected" in result.stderr
    assert any("bundle review rejection" in note.lower() for note in result.notes)
    assert outer_report.exists()
    report_text = outer_report.read_text(encoding="utf-8").lower()
    assert "package_authoring_failure" in report_text
    assert "launcher execution skipped" in report_text
    assert "launcher_risk_detected" in report_text


def test_run_package_continues_when_bundle_review_payload_is_missing(tmp_path: Path, monkeypatch) -> None:
    zip_path = _write_bundle_zip(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    outer_report = desktop_dir / "outer_missing_review.txt"

    monkeypatch.setattr(package_runner, "_should_run_bundle_preflight", lambda bundle_root: False)
    monkeypatch.setattr(package_runner, "_discover_launcher", lambda *args, **kwargs: args[0] / "run_with_patchops.ps1")
    monkeypatch.setattr(package_runner, "_build_launcher_command", lambda **kwargs: ["pwsh", "-File", str(kwargs["launcher_path"])])
    monkeypatch.setattr(package_runner, "_detect_inner_report_path", lambda **kwargs: None)

    original_helper = package_runner._patchops_p01_should_preflight_reject
    monkeypatch.setattr(package_runner, "_patchops_p01_should_preflight_reject", lambda source_path: (False, None))

    def fake_runner(command: list[str], cwd: Path) -> ProcessCapture:
        return ProcessCapture(
            command=command,
            working_directory=str(cwd),
            exit_code=0,
            stdout="launcher ok\n",
            stderr="",
        )

    result = run_delivery_package(
        zip_path,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert result.ok is True
    assert result.exit_code == 0
    assert result.failure_category == ""
    assert outer_report.exists()
    monkeypatch.setattr(package_runner, "_patchops_p01_should_preflight_reject", original_helper)
