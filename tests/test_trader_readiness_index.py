from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = PROJECT_ROOT / "docs" / "trader_readiness_index.md"


def _read_index() -> str:
    return INDEX_PATH.read_text(encoding="utf-8")


def test_trader_readiness_index_exists() -> None:
    assert INDEX_PATH.exists(), f"Missing readiness index: {INDEX_PATH}"


def test_trader_readiness_index_references_major_docs_and_manifests() -> None:
    text = _read_index()
    required_references = [
        "docs/trader_first_usage.md",
        "docs/trader_manifest_authoring_checklist.md",
        "docs/trader_safe_first_patch_types.md",
        "docs/trader_execution_sequence.md",
        "docs/trader_rehearsal_runbook.md",
        "docs/first_real_trader_run_checklist.md",
        "docs/stage2_entry_criteria.md",
        "examples/trader_first_verify_patch.json",
    ]

    for reference in required_references:
        assert reference in text, f"Expected reference missing from readiness index: {reference}"


def test_trader_readiness_index_positions_itself_as_single_starting_doc() -> None:
    source = _read_index()
    text = source.lower()
    assert "single operator map" in text
    assert "single jumping-off document" in text or "single jumping-off doc" in text
    assert "start with `docs/trader_readiness_index.md`" in text
    assert "stage 2" in text
