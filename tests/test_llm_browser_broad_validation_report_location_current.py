from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_broad_validation_script_defaults_to_desktop_reports_folder_and_pointer() -> None:
    text = _read("scripts/llm_browser_broad_validation.ps1")

    required = [
        "ReportFolder",
        "PointerPath",
        "patchops_reports",
        "patchops_latest_llm_browser_broad_validation_report.txt",
        "ReportFolder :",
        "PointerPath  :",
        "Latest PatchOps LLM-browser broad validation report",
        "Open report with:",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_broad_validation_script_keeps_full_pytest_phrase_and_plan_only() -> None:
    text = _read("scripts/llm_browser_broad_validation.ps1")

    required = [
        "full pytest",
        "full pytest is enabled by default",
        "PlanOnly",
        "SkipFullPytest",
        "TimeoutFullPytestSeconds",
        "python -m pytest -q",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_31_parser_and_report_location_contract() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.31 broad validation report parser",
        "patchops_reports",
        "patchops_latest_llm_browser_broad_validation_report.txt",
        "llm-browser broad-report --path",
        "Desktop report folder",
        "pointer file",
        "parse result, exit code, commands, failures, and timeouts",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
