from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GUIDE_PATH = PROJECT_ROOT / "docs" / "failure_repair_guide.md"


def _read_guide() -> str:
    return GUIDE_PATH.read_text(encoding="utf-8")


def test_failure_repair_guide_exists() -> None:
    assert GUIDE_PATH.exists(), f"Missing guide: {GUIDE_PATH}"


def test_failure_repair_guide_covers_main_failure_classes() -> None:
    text = _read_guide()
    required_phrases = [
        "Content failure",
        "Wrapper failure",
        "Verification-only rerun",
        "Wrapper-only repair",
        "writes are skipped",
        "expected target files are re-checked",
    ]

    for phrase in required_phrases:
        assert phrase in text, f"Expected phrase missing from failure repair guide: {phrase}"


def test_failure_repair_guide_includes_decision_table_and_escalation_guidance() -> None:
    text = _read_guide()
    assert "Quick decision table" in text
    assert "Escalation rules" in text
    assert "ExitCode` / `Result`" in text
    assert "What failed, and what is the narrowest trustworthy recovery path?" in text
