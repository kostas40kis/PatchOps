from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = PROJECT_ROOT / "docs" / "trader_profile.md"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_trader_profile_doc_exists() -> None:
    assert DOC_PATH.exists(), f"Missing doc: {DOC_PATH}"


def test_trader_profile_doc_covers_required_topics() -> None:
    text = _read_doc()
    lowered = text.lower()
    required_fragments = [
        "expected roots",
        "expected runtime",
        "backup conventions",
        "report expectations",
        "trader remains a profile, not the core identity of patchops",
        "what trader logic must remain outside patchops",
        r"c:\dev\trader",
        r"c:\dev\patchops",
        r".venv\scripts\python.exe",
        "examples/trader_first_verify_patch.json",
    ]
    for fragment in required_fragments:
        assert fragment.lower() in lowered, f"Missing required fragment in trader profile doc: {fragment}"


def test_trader_profile_doc_preserves_wrapper_target_boundary() -> None:
    text = _read_doc()
    expected_fragment = "trader business logic remains inside `C:" + chr(92) + "dev" + chr(92) + "trader`"
    assert "PatchOps stays project-agnostic" in text
    assert expected_fragment in text
    assert "PatchOps may execute manifests that touch trader files, but it must not become the home for trader business logic." in text
