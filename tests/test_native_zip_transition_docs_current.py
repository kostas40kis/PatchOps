from pathlib import Path


def test_native_zip_transition_doc_states_before_and_after_milestone() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "docs" / "native_zip_transition.md"
    text = doc_path.read_text(encoding="utf-8").lower()

    required_phrases = [
        "before this patch series finished",
        "you manually unzipped bundles",
        "after this patch series finished",
        "you no longer manually unzip bundles",
        "patchops accepts the `.zip`",
        "patchops extracts it",
        "patchops finds and calls the bundled `.ps1`",
        "one canonical desktop txt report",
        "zip support is additive",
        "not a replacement for the existing manifest-driven flow",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"native zip transition doc is missing required phrases: {missing}"


def test_native_zip_transition_example_states_manual_unzip_ended() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    example_path = repo_root / "examples" / "bundles" / "native_zip_transition_example.md"
    text = example_path.read_text(encoding="utf-8").lower()

    required_phrases = [
        "before the native zip milestone",
        "manually unzip it",
        "after the native zip milestone",
        "do not manually unzip it",
        "let patchops extract it",
        "let patchops call the bundled `.ps1`",
        "one canonical desktop txt report",
        "additive, not a replacement",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"native zip transition example is missing required phrases: {missing}"
