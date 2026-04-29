from __future__ import annotations

from pathlib import Path

from patchops.llm_browser import dependency_check
from patchops.llm_browser.dependency_check import (
    build_dependency_report,
    edge_candidate_paths,
    opera_candidate_paths,
    render_dependency_report,
)


def test_dependency_doctor_reports_pass_when_required_surfaces_exist(tmp_path: Path) -> None:
    edge = tmp_path / "msedge.exe"
    downloads = tmp_path / "Downloads"
    edge.write_text("", encoding="utf-8")
    downloads.mkdir()

    def exists(path: Path) -> bool:
        return path in {edge, downloads, tmp_path}

    report = build_dependency_report(
        wrapper_root=tmp_path,
        download_dir=downloads,
        browser="edge",
        import_probe=lambda _module: True,
        exists=exists,
        environ={"PATCHOPS_EDGE_PATH": str(edge), "LOCALAPPDATA": str(tmp_path)},
    )

    assert report.ok is True
    assert report.exit_code == 0
    assert report.to_payload()["result"] == "PASS"


def test_dependency_doctor_fails_when_required_optional_import_is_missing(tmp_path: Path) -> None:
    edge = tmp_path / "msedge.exe"
    downloads = tmp_path / "Downloads"
    edge.write_text("", encoding="utf-8")
    downloads.mkdir()

    def exists(path: Path) -> bool:
        return path in {edge, downloads, tmp_path}

    report = build_dependency_report(
        wrapper_root=tmp_path,
        download_dir=downloads,
        browser="edge",
        import_probe=lambda module: module != "selenium",
        exists=exists,
        environ={"PATCHOPS_EDGE_PATH": str(edge), "LOCALAPPDATA": str(tmp_path)},
    )

    assert report.ok is False
    assert report.exit_code == 1
    assert "selenium" in render_dependency_report(report)


def test_default_import_probe_is_resolved_at_call_time(monkeypatch, tmp_path: Path) -> None:
    edge = tmp_path / "msedge.exe"
    downloads = tmp_path / "Downloads"
    edge.write_text("", encoding="utf-8")
    downloads.mkdir()
    monkeypatch.setattr(dependency_check, "_module_available", lambda _module: True)

    def exists(path: Path) -> bool:
        return path in {edge, downloads, tmp_path}

    report = build_dependency_report(
        wrapper_root=tmp_path,
        download_dir=downloads,
        browser="edge",
        exists=exists,
        environ={"PATCHOPS_EDGE_PATH": str(edge), "LOCALAPPDATA": str(tmp_path)},
    )
    assert report.ok is True


def test_opera_is_warning_when_edge_is_the_required_browser(tmp_path: Path) -> None:
    edge = tmp_path / "msedge.exe"
    downloads = tmp_path / "Downloads"
    edge.write_text("", encoding="utf-8")
    downloads.mkdir()

    def exists(path: Path) -> bool:
        return path in {edge, downloads, tmp_path}

    report = build_dependency_report(
        wrapper_root=tmp_path,
        download_dir=downloads,
        browser="edge",
        import_probe=lambda _module: True,
        exists=exists,
        environ={"PATCHOPS_EDGE_PATH": str(edge), "LOCALAPPDATA": str(tmp_path)},
    )

    opera_check = next(check for check in report.checks if check.name == "Opera installed")
    assert opera_check.required is False
    assert opera_check.status == "WARN"


def test_browser_candidate_paths_support_environment_overrides(tmp_path: Path) -> None:
    env = {
        "PATCHOPS_EDGE_PATH": str(tmp_path / "custom_edge.exe"),
        "PATCHOPS_OPERA_PATH": str(tmp_path / "custom_opera.exe"),
        "LOCALAPPDATA": str(tmp_path),
    }
    assert edge_candidate_paths(env)[0] == tmp_path / "custom_edge.exe"
    assert opera_candidate_paths(env)[0] == tmp_path / "custom_opera.exe"
