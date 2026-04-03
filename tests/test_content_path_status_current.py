from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_status_mentions_content_path_repair_stream() -> None:
    content = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
    lowered = content.lower()
    assert "## content_path wrapper-root repair stream" in lowered
    assert "wrapper project root first" in lowered
    assert "compatibility fallback" in lowered
    assert "example manifest now has an end-to-end apply-flow proof" in lowered


def test_patch_ledger_mentions_content_path_repair_stream() -> None:
    content = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
    lowered = content.lower()
    assert "## content_path wrapper-root repair stream" in lowered
    assert "### cp1 - current-state repro contract" in lowered
    assert "### cp2 - wrapper-root resolution repair" in lowered
    assert "### cp3 - docs and example alignment" in lowered
    assert "### cp4 - example apply-flow proof" in lowered
    assert "ordinary maintenance, not runtime redesign" in lowered
