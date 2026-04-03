from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_status_mentions_content_path_repair_stream() -> None:
    content = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
    assert "## content_path wrapper-root repair stream" in content
    assert "wrapper project root first" in content
    assert "compatibility fallback" in content
    assert "example manifest now has an end-to-end apply-flow proof" in content


def test_patch_ledger_mentions_content_path_repair_stream() -> None:
    content = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
    assert "## content_path wrapper-root repair stream" in content
    assert "### CP1 - current-state repro contract" in content
    assert "### CP2 - wrapper-root resolution repair" in content
    assert "### CP3 - docs and example alignment" in content
    assert "### CP4 - example apply-flow proof" in content
    assert "remaining work is documentation stop and normal maintenance" in content
