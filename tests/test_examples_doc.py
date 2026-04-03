from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = PROJECT_ROOT / "docs" / "examples.md"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_examples_doc_exists() -> None:
    assert DOC_PATH.exists(), f"Missing doc: {DOC_PATH}"


def test_examples_doc_covers_required_walkthroughs() -> None:
    text = _read_doc()
    lowered = text.lower()
    required_fragments = [
        "trader code patch example",
        "trader verification-only example",
        "generic python example",
        "documentation-only example",
        "examples/trader_code_patch.json",
        "examples/trader_first_verify_patch.json",
        "examples/generic_python_patch.json",
        "examples/trader_first_doc_patch.json",
        "powershell/invoke-patchverify.ps1",
    ]
    for fragment in required_fragments:
        assert fragment.lower() in lowered, f"Missing required fragment in examples doc: {fragment}"


def test_examples_doc_positions_examples_as_starting_surfaces() -> None:
    text = _read_doc()
    assert "Start from examples and adapt them." in text
    assert "If you are uncertain, start narrower." in text
    assert "That is the intended starting surface for practical PatchOps usage." in text
