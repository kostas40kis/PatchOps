from pathlib import Path


def test_github_publish_helper_doc_preserves_manual_guardrails_and_defaults() -> None:
    doc = Path("docs/github_publish_helper.md").read_text(encoding="utf-8")

    assert "manual" in doc
    assert "operator-reviewed" in doc
    assert "not a second apply engine" in doc
    assert "C:\\dev\\patchops" in doc
    assert "https://github.com/kostas40kis/PatchOps.git" in doc
    assert "`main`" in doc
    assert "ArgumentList" in doc
    assert "ProcessStartInfo.Arguments" in doc


def test_github_publish_helper_doc_mentions_green_report_before_push() -> None:
    doc = Path("docs/github_publish_helper.md").read_text(encoding="utf-8")

    assert "canonical report says PASS" in doc
    assert "validation is green" in doc
    assert "reviewed the repo changes" in doc
