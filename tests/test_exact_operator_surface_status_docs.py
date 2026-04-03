from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_STATUS = PROJECT_ROOT / "docs" / "project_status.md"
PATCH_LEDGER = PROJECT_ROOT / "docs" / "patch_ledger.md"


def test_project_status_keeps_exact_operator_surface_wave_explicit() -> None:
    text = PROJECT_STATUS.read_text(encoding="utf-8")

    required_headings = [
        "## Patch 121 - exact PowerShell launcher set validation",
        "## Patch 122 - operator surface status doc validation",
        "## Patch 123 - exact CLI subcommand set validation",
    ]
    for heading in required_headings:
        assert heading in text

    required_phrases = [
        "exact thin PowerShell launcher set",
        "exact-set test for the shipped CLI subcommand surface",
        "operator-facing command map is not only partitioned and inventoried, but also bounded",
        "maintenance validation rather than redesign",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_patch_ledger_keeps_exact_operator_surface_wave_explicit() -> None:
    text = PATCH_LEDGER.read_text(encoding="utf-8")

    required_sections = [
        "## Patch 121",
        "## Patch 122",
        "## Patch 123",
    ]
    for section in required_sections:
        assert section in text

    required_phrases = [
        "exact thin PowerShell launcher set",
        "documentation-validation surface for the recent operator-surface hardening wave",
        "exact shipped CLI subcommand set",
    ]
    for phrase in required_phrases:
        assert phrase in text
