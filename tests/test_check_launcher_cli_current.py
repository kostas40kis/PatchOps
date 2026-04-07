from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["py", "-m", "patchops.cli", *args],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )


def test_check_launcher_cli_returns_zero_for_safe_launcher(tmp_path: Path) -> None:
    launcher_path = tmp_path / "safe_launcher.ps1"
    launcher_path.write_text(
        "& {\n"
        "    py -m patchops.cli apply .\\manifest.json\n"
        "}\n",
        encoding="utf-8",
    )

    completed = _run_cli("check-launcher", str(launcher_path))

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["path"].endswith("safe_launcher.ps1")
    assert payload["exists"] is True
    assert payload["ok"] is True
    assert payload["issue_count"] == 0


def test_check_launcher_cli_returns_nonzero_when_issues_are_found(tmp_path: Path) -> None:
    launcher_path = tmp_path / "bad_launcher.ps1"
    launcher_path.write_text(
        "& {\n"
        "    Get-Content prep.json | ConvertFrom-Json\n"
        "}\n",
        encoding="utf-8",
    )

    completed = _run_cli("check-launcher", str(launcher_path))

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["exists"] is True
    assert payload["ok"] is False
    assert payload["issue_count"] >= 1
    assert any("json" in issue.lower() or "convertfrom-json" in issue.lower() for issue in payload["issues"])
