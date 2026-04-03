from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_status_mentions_closed_content_path_stream() -> None:
    content = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
    lowered = content.lower()
    assert "## content_path wrapper-root repair stream" in lowered
    assert "bug is repaired and the stream is complete" in lowered
    assert "handoff and onboarding surfaces now both carry the maintained content-path rule" in lowered
    assert "self-hosted windows powershell / ise authoring notes" in lowered
    assert "treat the content-path bug stream as closed unless new contrary repo evidence appears" in lowered


def test_patch_ledger_mentions_cp5_through_cp9_and_closed_outcome() -> None:
    content = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
    lowered = content.lower()
    assert "### cp5 - docs stop and status lock" in lowered
    assert "### cp6 - handoff refresh and lock" in lowered
    assert "### cp7 - onboarding refresh and lock" in lowered
    assert "### cp8 - finalization closure lock" in lowered
    assert "### cp9 - self-hosted authoring hardening notes" in lowered
    assert "green through cp9 and closed" in lowered
    assert "ordinary maintenance, not runtime redesign" in lowered
