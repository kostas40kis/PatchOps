from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_final_closeout_validation_doc_exists_and_has_primary_command() -> None:
    text = _read("docs/llm_browser_final_closeout_validation_script.md")

    required = [
        "LLM Browser Final Closeout Validation Script",
        "cd C:\\dev\\patchops",
        ".\\scripts\\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\\dev\\patchops",
        "final operator guide",
        "does not commit or push automatically",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_validation_doc_documents_report_outputs_and_pointers() -> None:
    text = _read("docs/llm_browser_final_closeout_validation_script.md")

    required = [
        "%USERPROFILE%\\Desktop\\patchops_reports\\patchops_llm_browser_closeout_checkpoint_YYYYMMDD_HHMMSS.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        'notepad "$env:USERPROFILE\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt"',
        'notepad "$env:USERPROFILE\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt"',
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_validation_doc_includes_clipboard_and_parser_commands() -> None:
    text = _read("docs/llm_browser_final_closeout_validation_script.md")

    required = [
        "Set-Clipboard",
        "$reportPath = [regex]::Match($pointer, 'ReportPath\\s*:\\s*(.+)').Groups[1].Value.Trim()",
        "py -m patchops.cli llm-browser broad-report --path $reportPath --json --strict",
        "Copy the latest closeout report to clipboard",
        "Copy the latest broad-validation report to clipboard",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_validation_doc_documents_pass_fail_and_manual_git_commands() -> None:
    text = _read("docs/llm_browser_final_closeout_validation_script.md")

    required = [
        "PASS requirements",
        "`Result : PASS`",
        "`ExitCode : 0`",
        "FAIL handling",
        "Do not commit or push.",
        "git status --short --branch",
        "git add -A",
        "git commit -m \"Close out llm-browser dry-mode validation stream\"",
        "git push origin main",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_validation_doc_documents_modes_and_safety_contract() -> None:
    text = _read("docs/llm_browser_final_closeout_validation_script.md")

    required = [
        "-PlanOnly",
        "Plan-only is not final acceptance.",
        "-SkipFullPytest",
        "A final closeout should not use `-SkipFullPytest`.",
        "The final closeout validation script does not:",
        "run git commit",
        "run git push",
        "start a browser",
        "start Selenium",
        "click or download artifacts",
        "run PatchOps packages",
        "paste into the ChatGPT composer",
        "submit or send a message",
        "create a localhost service",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_validation_doc_documents_closeout_interpretation() -> None:
    text = _read("docs/llm_browser_final_closeout_validation_script.md")

    required = [
        "the dry-mode stream is validated",
        "the future live-adapter work remains a separate planned stream",
        "the repository can be committed and pushed by the operator",
        "no live browser automation has been shipped by this dry-mode closeout",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_36_final_closeout_docs() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.36 final closeout validation script docs",
        "docs/llm_browser_final_closeout_validation_script.md",
        ".\\scripts\\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\\dev\\patchops",
        "Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "copying the latest closeout report to clipboard",
        "manual commit and push commands",
        "the final closeout validation script does not run git commit",
        "the final closeout validation script does not run git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
