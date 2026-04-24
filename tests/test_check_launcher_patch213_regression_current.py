from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "patchops.cli", *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_check_launcher_rejects_patch213_style_json_handoff_launcher(tmp_path: Path) -> None:
    launcher_path = tmp_path / "run_with_patchops.ps1"
    launcher_path.write_text(
        r"""param(
    [string]$WrapperRepoRoot = "C:\dev\patchops"
)

$ErrorActionPreference = "Stop"

function Write-Utf8NoBomFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

$bundleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifestPath = Join-Path $bundleRoot "manifest.json"

if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Bundle manifest not found: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

$writeCollections = @()
if ($null -ne $manifest.writes) { $writeCollections += ,$manifest.writes }
if ($null -ne $manifest.file_writes) { $writeCollections += ,$manifest.file_writes }

foreach ($collection in $writeCollections) {
    foreach ($write in $collection) {
        foreach ($propName in @('content_path','source_path')) {
            if ($null -ne $write.$propName -and [string]::IsNullOrWhiteSpace([string]$write.$propName) -eq $false) {
                $write.$propName = Join-Path $bundleRoot ([string]$write.$propName)
            }
        }
    }
}

$tempManifestPath = Join-Path $env:TEMP ("patch_213_incident_timeline_builder_manifest_" + [guid]::NewGuid().ToString("N") + ".json")
Write-Utf8NoBomFile -Path $tempManifestPath -Content ($manifest | ConvertTo-Json -Depth 100)

Push-Location $WrapperRepoRoot
try {
    py -m patchops.cli apply $tempManifestPath --wrapper-root $WrapperRepoRoot
}
finally {
    Pop-Location
}
""",
        encoding="utf-8",
    )

    completed = _run_cli("check-launcher", str(launcher_path))

    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["exists"] is True
    assert payload["ok"] is False
    assert payload["issue_count"] >= 2

    lowered = "\n".join(payload["issues"]).lower()
    assert "convertfrom-json" in lowered or "json" in lowered
    assert "backslash" in lowered or "nested quoting" in lowered or "quoting" in lowered


def test_check_launcher_still_accepts_minimal_launcher_after_patch213_regression(tmp_path: Path) -> None:
    launcher_path = tmp_path / "safe_launcher.ps1"
    launcher_path.write_text(
        '& {\n'
        '    py -m patchops.cli apply .\\manifest.json\n'
        '}\n',
        encoding="utf-8",
    )

    completed = _run_cli("check-launcher", str(launcher_path))

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["exists"] is True
    assert payload["ok"] is True
    assert payload["issue_count"] == 0