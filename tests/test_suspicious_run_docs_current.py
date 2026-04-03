from pathlib import Path


def test_failure_repair_guide_documents_suspicious_run_support():
    text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8").lower()
    assert "## suspicious-run support" in text
    assert "wrapper health aid" in text
    assert "not a target-content feature" in text
    assert "starts opt-in" in text
    assert "read it as a small machine-readable aid" in text


def test_failure_repair_guide_lists_conservative_suspicious_cases():
    text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8").lower()
    assert "required command evidence contradicting the rendered summary" in text
    assert "critical provenance fields missing after wrapper execution" in text
    assert "copied latest-report surface missing after a handoff export path" in text
    assert "report structure missing required core fields" in text
