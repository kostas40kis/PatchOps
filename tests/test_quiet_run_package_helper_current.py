from pathlib import Path


def test_quiet_run_package_helper_script_exists_and_mentions_summary_surface() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "powershell" / "Invoke-QuietRunPackage.ps1"
    text = script_path.read_text(encoding="utf-8")

    required_phrases = [
        "patchops.cli",
        "run-package",
        "Canonical Report Path",
        "Report Path",
        "PATCHOPS QUIET RUN SUMMARY",
        "Result       :",
        "ExitCode     :",
        "VerboseConsole",
        "ProcessStartInfo",
        "Arguments",
    ]
    for phrase in required_phrases:
        assert phrase in text

    assert "ArgumentList" not in text


def test_quiet_run_package_helper_doc_locks_report_truth_model() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "docs" / "quiet_run_package_helper.md"
    text = doc_path.read_text(encoding="utf-8")

    required_phrases = [
        "canonical Desktop txt report",
        "run-package",
        "report path",
        "less live console noise",
        "Keep PowerShell thin.",
        "Keep reusable mechanics in Python.",
        "Keep one canonical Desktop txt report.",
    ]
    for phrase in required_phrases:
        assert phrase in text
