from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_stage1_consolidation_docs_exist() -> None:
    assert (PROJECT_ROOT / "docs" / "patch_ledger.md").exists()
    assert (PROJECT_ROOT / "docs" / "stage1_freeze_checklist.md").exists()
    assert (PROJECT_ROOT / "docs" / "release_checklist.md").exists()


def test_project_status_mentions_late_stage1() -> None:
    content = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
    assert "late Stage 1 / pre-Stage 2" in content


def test_patch_ledger_mentions_patch_24_and_patch_25_26() -> None:
    content = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
    assert "## Patch 24" in content
    assert "## Patch 25_26" in content


def test_readme_mentions_consolidation_status() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Consolidation status" in content
    assert "docs/patch_ledger.md" in content
