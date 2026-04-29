from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_broad_validation_one_command_doc_exists_and_has_primary_command() -> None:
    text = _read("docs/llm_browser_broad_validation_one_command.md")

    required = [
        "LLM Browser Broad Validation One-command Runner",
        "cd C:\\dev\\patchops",
        ".\\scripts\\llm_browser_broad_validation.ps1 -RepoRoot C:\\dev\\patchops",
        "%USERPROFILE%\\Desktop\\patchops_reports\\patchops_llm_browser_broad_validation_YYYYMMDD_HHMMSS.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_broad_validation_one_command_doc_includes_open_copy_and_parse_commands() -> None:
    text = _read("docs/llm_browser_broad_validation_one_command.md")

    required = [
        'notepad "$env:USERPROFILE\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt"',
        'explorer "$env:USERPROFILE\\Desktop\\patchops_reports"',
        "Set-Clipboard",
        "$reportPath = [regex]::Match($pointer, 'ReportPath\\s*:\\s*(.+)').Groups[1].Value.Trim()",
        "py -m patchops.cli llm-browser broad-report --path $reportPath --json --strict",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_broad_validation_one_command_doc_documents_plan_and_skip_modes() -> None:
    text = _read("docs/llm_browser_broad_validation_one_command.md")

    required = [
        "-PlanOnly",
        "-SkipFullPytest",
        "Normal acceptance should not use `-SkipFullPytest`.",
        "full pytest passed unless `-SkipFullPytest` was intentionally supplied",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_broad_validation_one_command_doc_documents_failure_interpretation() -> None:
    text = _read("docs/llm_browser_broad_validation_one_command.md")

    required = [
        "If the report says FAIL:",
        "Look at the `SUMMARY` section.",
        "ExitCode",
        "TimedOut",
        "Do not commit or push until the failing command is repaired.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_broad_validation_one_command_doc_documents_safety_contract() -> None:
    text = _read("docs/llm_browser_broad_validation_one_command.md")

    required = [
        "It does not:",
        "start a browser",
        "start Selenium",
        "click or download artifacts",
        "run PatchOps packages",
        "paste into the ChatGPT composer",
        "submit or send a message",
        "run git commit",
        "run git push",
        "create a localhost service",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_32_one_command_docs() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.32 broad validation one-command runner docs",
        "docs/llm_browser_broad_validation_one_command.md",
        ".\\scripts\\llm_browser_broad_validation.ps1 -RepoRoot C:\\dev\\patchops",
        "patchops_latest_llm_browser_broad_validation_report.txt",
        "copying the actual latest report content to clipboard",
        "llm-browser broad-report --path",
        "no git commit or git push is performed by the one-command runner",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
