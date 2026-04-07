from pathlib import Path


def test_zip_bundle_standard_doc_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "docs" / "zip_bundle_standard.md"

    assert doc_path.exists(), "docs/zip_bundle_standard.md should exist."


def test_zip_bundle_standard_doc_locks_required_distinctions() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "docs" / "zip_bundle_standard.md"
    text = doc_path.read_text(encoding="utf-8").lower()

    required_phrases = [
        "manifest",
        "profile",
        "report",
        "project packet",
        "bundle transport",
        "manual unzip",
        "one canonical desktop txt report",
        "launchers/",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"zip bundle standard doc is missing required phrases: {missing}"
