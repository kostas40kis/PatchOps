from __future__ import annotations

from pathlib import Path

from patchops.bundles.launcher_self_check import check_launcher_path


def test_check_launcher_path_reports_missing_file(tmp_path: Path) -> None:
    payload = check_launcher_path(tmp_path / "missing_launcher.ps1")

    assert payload["exists"] is False
    assert payload["ok"] is False
    assert payload["issue_count"] == 1
    assert "does not exist" in payload["issues"][0].lower()


def test_check_launcher_path_reports_directory_input(tmp_path: Path) -> None:
    launcher_dir = tmp_path / "launcher_dir"
    launcher_dir.mkdir()

    payload = check_launcher_path(launcher_dir)

    assert payload["exists"] is True
    assert payload["ok"] is False
    assert payload["issue_count"] == 1
    assert "directory" in payload["issues"][0].lower()


def test_check_launcher_path_collects_heuristic_messages(tmp_path: Path) -> None:
    launcher_path = tmp_path / "bad_launcher.ps1"
    launcher_path.write_text(
        "& {\n"
        "    Get-Content prep.json | ConvertFrom-Json\n"
        "    py -c \"print('inline')\"\n"
        "}\n",
        encoding="utf-8",
    )

    payload = check_launcher_path(launcher_path)

    assert payload["exists"] is True
    assert payload["ok"] is False
    assert payload["issue_count"] >= 2
    combined = "\n".join(payload["issues"]).lower()
    assert "json" in combined or "convertfrom-json" in combined
    assert "python" in combined or "inline" in combined


def test_check_launcher_path_accepts_safe_standard_launcher(tmp_path: Path) -> None:
    launcher_path = tmp_path / "safe_launcher.ps1"
    launcher_path.write_text(
        "& {\n"
        "    py -m patchops.cli apply .\\manifest.json\n"
        "}\n",
        encoding="utf-8",
    )

    payload = check_launcher_path(launcher_path)

    assert payload["exists"] is True
    assert payload["ok"] is True
    assert payload["issue_count"] == 0
    assert payload["issues"] == []
