from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops import cli


def test_check_launcher_help_exposes_current_live_args(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["check-launcher", "--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "usage: patchops check-launcher" in text
    assert "launcher_path" in text


def test_check_launcher_returns_clean_payload_for_safe_launcher(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    launcher_path = tmp_path / "safe_launcher.ps1"
    launcher_path.write_text(
        "& {\n"
        "param([string]$ManifestPath)\n"
        "& py -m patchops.cli apply $ManifestPath\n"
        "}\n",
        encoding="utf-8",
    )
    exit_code = cli.main(["check-launcher", str(launcher_path)])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["exists"] is True
    assert payload["path"] == str(launcher_path.resolve())
    assert payload["issue_count"] == 0
    assert payload["issues"] == []


def test_check_launcher_returns_nonzero_for_risky_launcher_patterns(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    launcher_path = tmp_path / "risky_launcher.ps1"
    launcher_path.write_text(
        "Get-Content state.json | ConvertFrom-Json\n"
        "Copy-Item .\\manifest.json .\\backup_manifest.json\n"
        "py -c \"print('hi')\"\n",
        encoding="utf-8",
    )
    exit_code = cli.main(["check-launcher", str(launcher_path)])
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["exists"] is True
    assert payload["issue_count"] >= 1
    joined = "\n".join(payload["issues"]).lower()
    assert (
        "json" in joined
        or "copy" in joined
        or "py -c" in joined
        or "inline python" in joined
    )


def test_check_launcher_returns_nonzero_for_missing_path(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = tmp_path / "missing_launcher.ps1"
    exit_code = cli.main(["check-launcher", str(missing)])
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["exists"] is False
    assert payload["issue_count"] == 1
    assert "does not exist" in payload["issues"][0].lower()
