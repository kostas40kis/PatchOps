from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_status_mentions_closed_content_path_stream() -> None:
    content = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
    assert "## content_path wrapper-root repair stream" in content
    assert "bug is repaired and the stream is complete" in content
    assert "Handoff and onboarding surfaces now both carry the maintained content-path rule" in content
    assert "self-hosted Windows PowerShell / ISE authoring notes" in content
    assert "treat the content-path bug stream as closed unless new contrary repo evidence appears" in content


def test_patch_ledger_mentions_cp5_through_cp9_and_closed_outcome() -> None:
    content = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
    assert "### CP5 - docs stop and status lock" in content
    assert "### CP6 - handoff refresh and lock" in content
    assert "### CP7 - onboarding refresh and lock" in content
    assert "### CP8 - finalization closure lock" in content
    assert "### CP9 - self-hosted authoring hardening notes" in content
    assert "green through CP9 and closed" in content
    assert "ordinary maintenance, not runtime redesign" in content
