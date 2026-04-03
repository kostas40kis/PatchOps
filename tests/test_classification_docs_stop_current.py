from pathlib import Path


def test_failure_repair_guide_mentions_classification_guided_repair_choice():
    text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8").lower()

    assert "classification-guided repair choice" in text
    assert "verify-only" in text
    assert "wrapper-only repair" in text
    assert "repair target content" in text
    assert "suspicious" in text


def test_failure_repair_guide_mentions_maintained_failure_classes():
    text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8").lower()

    assert "target_project_failure" in text
    assert "wrapper_failure" in text
    assert "patch_authoring_failure" in text
    assert "ambiguous_or_suspicious_run" in text
