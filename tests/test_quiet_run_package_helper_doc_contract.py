from pathlib import Path


def test_quiet_run_package_helper_usage_is_copy_paste_safe() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "docs" / "quiet_run_package_helper.md"
    text = doc_path.read_text(encoding="utf-8")

    required_phrases = [
        "Invoke-QuietRunPackage.ps1",
        "Set-Location",
        "PackagePath",
        "WrapperRepoRoot",
        "VerboseConsole",
        "source of truth",
    ]
    for phrase in required_phrases:
        assert phrase in text
