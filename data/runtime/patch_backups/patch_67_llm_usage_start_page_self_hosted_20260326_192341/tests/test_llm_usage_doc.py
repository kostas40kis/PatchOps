from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = PROJECT_ROOT / "docs" / "llm_usage.md"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_llm_usage_doc_exists() -> None:
    assert DOC_PATH.exists(), f"Missing doc: {DOC_PATH}"


def test_llm_usage_doc_covers_required_topics() -> None:
    text = _read_doc()
    required_fragments = [
        "how to read the project",
        "how to pick a profile",
        "how to build a manifest",
        "how to decide between apply and verify-only",
        "how to classify failure",
        "how to avoid moving target-repo logic into PatchOps",
        "docs/failure_repair_guide.md",
        "examples/trader_first_verify_patch.json",
        "powershell/Invoke-PatchVerify.ps1",
    ]

    lowered = text.lower()
    for fragment in required_fragments:
        assert fragment.lower() in lowered, f"Missing required fragment in llm usage doc: {fragment}"


def test_llm_usage_doc_positions_patchops_as_wrapper_not_target_logic_owner() -> None:
    text = _read_doc()
    assert "PatchOps is a **standalone wrapper / harness project**." in text
    assert "Target repos own:" in text
    assert "Never move target-repo business logic into PatchOps" in text
    assert "Trader is the first serious profile, not the identity of the wrapper." in text
