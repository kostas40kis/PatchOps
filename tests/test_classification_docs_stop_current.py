from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = PROJECT_ROOT / "docs" / "repair_guidance.md"
REQUIRED_PHRASES = [
    "Use verify-only rerun when",
    "Use wrapper-only repair or retry when",
    "Repair target content when",
    "Stop because the run is suspicious when",
    "Repair patch authoring when",
    "wrapper_failure",
    "target_project_failure",
    "patch_authoring_failure",
    "ambiguous_or_suspicious_run",
    "continue patch by patch from evidence",
]


def test_classification_docs_stop_current() -> None:
    assert DOC_PATH.exists(), f"Missing repair guidance doc: {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing phrase in classification docs stop: {phrase!r}"
