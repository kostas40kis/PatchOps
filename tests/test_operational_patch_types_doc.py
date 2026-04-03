from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = PROJECT_ROOT / "docs" / "operational_patch_types.md"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_operational_patch_types_doc_exists() -> None:
    assert DOC_PATH.exists(), f"Missing doc: {DOC_PATH}"


def test_operational_patch_types_doc_covers_all_main_classes() -> None:
    text = _read_doc().lower()
    required_fragments = [
        "code patch",
        "documentation patch",
        "validation patch",
        "cleanup patch",
        "archive patch",
        "verify-only patch",
        "examples/trader_code_patch.json",
        "examples/trader_first_doc_patch.json",
        "examples/generic_verify_patch.json",
        "powershell/invoke-patchverify.ps1",
    ]
    for fragment in required_fragments:
        assert fragment in text, f"Missing required fragment in operational patch types doc: {fragment}"


def test_operational_patch_types_doc_emphasizes_narrow_choice() -> None:
    text = _read_doc()
    assert "If uncertain, start narrower." in text
    assert "choose the smallest correct patch class" in text
    assert "PatchOps should not make every task look like a generic apply flow." in text
