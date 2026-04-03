import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "patchops.cli", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_schema_command_returns_manifest_reference() -> None:
    result = run_cli("schema")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["manifest_version"] == "1"
    assert "required_top_level_fields" in payload
    assert "starter_notes" in payload
    assert "backup_files" in payload["optional_top_level_fields"]


def test_schema_command_mentions_command_groups() -> None:
    result = run_cli("schema")
    payload = json.loads(result.stdout)
    assert "validation_commands" in payload["command_groups"]
    assert "report_preferences" in payload


def test_schema_powershell_launcher_exists() -> None:
    launcher = ROOT / "powershell" / "Invoke-PatchSchema.ps1"
    text = launcher.read_text(encoding="utf-8")
    assert "patchops.cli schema" in text
