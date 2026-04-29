from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_final_github_upload_helper_doc_exists_and_requires_pre_upload_validation() -> None:
    text = _read("docs/llm_browser_final_github_upload_helper.md")

    required = [
        "LLM Browser Final GitHub Upload Helper",
        "Required pre-upload validation",
        ".\\scripts\\llm_browser_final_closeout_broad_validation_push.ps1 -RepoRoot C:\\dev\\patchops",
        "`Result : PASS`",
        "`ExitCode : 0`",
        "Do not upload to GitHub if the final closeout report is FAIL.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_github_upload_helper_doc_lists_report_pointers_and_clipboard_command() -> None:
    text = _read("docs/llm_browser_final_github_upload_helper.md")

    required = [
        'notepad "$env:USERPROFILE\\Desktop\\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt"',
        'notepad "$env:USERPROFILE\\Desktop\\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt"',
        'notepad "$env:USERPROFILE\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt"',
        'notepad "$env:USERPROFILE\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt"',
        "%USERPROFILE%\\Desktop\\patchops_reports\\",
        "Set-Clipboard",
        "$reportPath = [regex]::Match($pointer, 'ReportPath\\s*:\\s*(.+)').Groups[1].Value.Trim()",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_github_upload_helper_doc_has_parser_and_manual_upload_commands() -> None:
    text = _read("docs/llm_browser_final_github_upload_helper.md")

    required = [
        "py -m patchops.cli llm-browser broad-report --path $reportPath --json --strict",
        "Manual GitHub upload commands",
        "git status --short --branch",
        "git add -A",
        "git commit -m \"Close out llm-browser dry-mode validation stream\"",
        "git push origin main",
        "Run these manually only after reviewing a PASS final closeout report",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_github_upload_helper_doc_has_post_upload_and_remote_verification() -> None:
    text = _read("docs/llm_browser_final_github_upload_helper.md")

    required = [
        "Post-upload verification",
        "git log -1 --oneline",
        "Optional remote verification",
        "git fetch origin main",
        "git rev-parse HEAD",
        "git rev-parse origin/main",
        "The two hashes should match after a successful push.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_github_upload_helper_doc_safety_contract_and_failure_handling() -> None:
    text = _read("docs/llm_browser_final_github_upload_helper.md")

    required = [
        "Safety contract",
        "do not:",
        "run git commit",
        "run git push",
        "stage files automatically",
        "create a commit automatically",
        "start a browser",
        "start Selenium",
        "click or download artifacts",
        "run PatchOps packages",
        "paste into the ChatGPT composer",
        "submit or send a message",
        "create a localhost service",
        "Failure handling",
        "Do not run `git add -A`.",
        "Do not run `git commit`.",
        "Do not run `git push`.",
        "Upload only after the final closeout report is PASS.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_github_upload_helper_doc_handoff_note_separates_future_live_adapter() -> None:
    text = _read("docs/llm_browser_final_github_upload_helper.md")

    required = [
        "Handoff note",
        "dry-mode browser-runner stream can be treated as uploaded to GitHub",
        "Future live-adapter work remains a separate stream",
        "must not silently expand this dry-mode closeout into live browser automation",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_40_github_upload_helper() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.40 final GitHub upload helper docs",
        "docs/llm_browser_final_github_upload_helper.md",
        ".\\scripts\\llm_browser_final_closeout_broad_validation_push.ps1 -RepoRoot C:\\dev\\patchops",
        "git commit -m \"Close out llm-browser dry-mode validation stream\"",
        "git push origin main",
        "git log -1 --oneline",
        "the docs do not run git commit",
        "the docs do not run git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
