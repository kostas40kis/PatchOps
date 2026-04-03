from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_backup_write_mechanics_doc_guides_contributors_to_helper_path() -> None:
    doc_path = PROJECT_ROOT / "docs" / "backup_write_mechanics.md"
    content = doc_path.read_text(encoding="utf-8")

    assert "Python-owned reusable surfaces" in content
    assert "rather than patch-body boilerplate" in content
    assert "single-file writes go through one deterministic helper" in content
    assert "batch writes go through one shared orchestration path" in content
    assert "prefer the existing Python backup/write helpers" in content
    assert "keep PowerShell thin and operator-facing" in content
