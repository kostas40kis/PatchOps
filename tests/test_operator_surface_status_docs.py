from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_STATUS = PROJECT_ROOT / "docs" / "project_status.md"
PATCH_LEDGER = PROJECT_ROOT / "docs" / "patch_ledger.md"


def test_project_status_keeps_recent_operator_surface_wave_explicit() -> None:
    text = PROJECT_STATUS.read_text(encoding="utf-8")

    required_headings = [
        "## Patch 118 - CLI and PowerShell surface alignment validation",
        "## Patch 119 - Python-only helper surface boundary validation",
        "## Patch 120 - operator surface partition validation",
        "## Patch 121 - exact PowerShell launcher set validation",
    ]
    for heading in required_headings:
        assert heading in text

    required_phrases = [
        "launcher-backed commands",
        "Python-only helper commands",
        "thin PowerShell launcher layer",
        "maintenance validation rather than redesign",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_patch_ledger_keeps_recent_operator_surface_wave_explicit() -> None:
    text = PATCH_LEDGER.read_text(encoding="utf-8")

    required_sections = [
        "## Patch 118",
        "## Patch 119",
        "## Patch 120",
        "## Patch 121",
    ]
    for section in required_sections:
        assert section in text

    required_phrases = [
        "launcher-backed CLI commands",
        "Python-only helper command layer",
        "operator command map",
        "exact thin PowerShell launcher set",
    ]
    for phrase in required_phrases:
        assert phrase in text
