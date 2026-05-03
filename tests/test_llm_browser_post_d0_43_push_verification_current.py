from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_post_d0_43_push_verification_script_exists_and_has_report_contract() -> None:
    text = _read("scripts/llm_browser_post_d0_43_push_verification.ps1")

    required = [
        "PATCHOPS POST-D0.43 PUSH VERIFICATION",
        "patchops_reports",
        "patchops_post_d0_43_push_verification_",
        "patchops_latest_post_d0_43_push_verification.txt",
        "ReportPath",
        "PointerPath",
        "PlanOnly",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_post_d0_43_push_verification_script_checks_git_state_without_mutating() -> None:
    text = _read("scripts/llm_browser_post_d0_43_push_verification.ps1")

    required = [
        "git status before fetch",
        "git fetch remote branch",
        "git log latest commit",
        "git rev-parse HEAD",
        "git rev-parse {0}",
        "git status after fetch",
        "HEAD does not match",
        "Working tree still has modified, staged, conflicted, or untracked files.",
        "Latest commit message does not appear to be the expected D0.43 evidence commit.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []

    forbidden = [
        "Invoke-NativeCapture -Label 'git add",
        "Invoke-NativeCapture -Label 'git commit",
        "Invoke-NativeCapture -Label 'git push",
    ]
    present = [item for item in forbidden if item in text]
    assert present == []


def test_post_d0_43_push_verification_script_has_expected_commit_message_and_safety_text() -> None:
    text = _read("scripts/llm_browser_post_d0_43_push_verification.ps1")

    required = [
        "D0.43 record final validation and GitHub upload evidence",
        "this helper does not run git add, git commit, or git push",
        "this helper never commits or pushes automatically",
        "Result     : PASS",
        "ExitCode   : 0",
        "Result     : FAIL",
        "ExitCode   : 1",
        "--- STDOUT ---",
        "--- STDERR ---",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_post_d0_43_push_verification_docs_include_commands_outputs_and_pass_conditions() -> None:
    text = _read("docs/llm_browser_post_d0_43_push_verification.md")

    required = [
        "LLM Browser Post-D0.43 Push Verification",
        "git commit -m \"D0.43 record final validation and GitHub upload evidence\"",
        ".\\scripts\\llm_browser_post_d0_43_push_verification.ps1 -RepoRoot C:\\dev\\patchops",
        "%USERPROFILE%\\Desktop\\patchops_reports\\patchops_post_d0_43_push_verification_YYYYMMDD_HHMMSS.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_post_d0_43_push_verification.txt",
        "`HEAD` matches `origin/main`",
        "`git status --short --branch` shows `## main...origin/main`",
        "the latest commit message contains `D0.43 record final validation and GitHub upload evidence`",
        "Set-Clipboard",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_post_d0_43_push_verification_docs_have_safety_and_interpretation() -> None:
    text = _read("docs/llm_browser_post_d0_43_push_verification.md")

    required = [
        "Safety contract",
        "run git add",
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
        "D0 dry-mode browser-runner stream is ready for the final acceptance marker",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_44_post_push_verification_helper() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.44 post-D0.43 push verification helper",
        "scripts/llm_browser_post_d0_43_push_verification.ps1",
        "docs/llm_browser_post_d0_43_push_verification.md",
        "tests/test_llm_browser_post_d0_43_push_verification_current.py",
        "Desktop\\patchops_latest_post_d0_43_push_verification.txt",
        "`HEAD` matches `origin/main`",
        "latest commit message contains `D0.43 record final validation and GitHub upload evidence`",
        "the helper does not run git commit",
        "the helper does not run git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
