from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_final_post_push_verification_doc_exists_and_has_precondition() -> None:
    text = _read("docs/llm_browser_final_post_push_verification.md")

    required = [
        "LLM Browser Final Post-push Verification",
        "Precondition",
        "git status --short --branch",
        "git add -A",
        "git commit -m \"Close out llm-browser dry-mode validation stream\"",
        "git push origin main",
        "These commands are not run automatically by PatchOps helper scripts.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_post_push_verification_doc_has_primary_verification_sequence() -> None:
    text = _read("docs/llm_browser_final_post_push_verification.md")

    required = [
        "Primary post-push verification command sequence",
        "git log -1 --oneline",
        "git fetch origin main",
        "git rev-parse HEAD",
        "git rev-parse origin/main",
        "local branch is `main`",
        "local branch is not behind `origin/main`",
        "`git rev-parse HEAD` matches `git rev-parse origin/main`",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_post_push_verification_doc_has_optional_release_checks() -> None:
    text = _read("docs/llm_browser_final_post_push_verification.md")

    required = [
        "Optional final validation after push",
        "py -m patchops.cli llm-browser release-gate --repo-root C:\\dev\\patchops --json",
        "py -m patchops.cli llm-browser checkpoint --repo-root C:\\dev\\patchops --json",
        "release-gate returns `PASS`",
        "checkpoint returns `PASS`",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_post_push_verification_doc_preserves_report_pointers_and_clipboard_command() -> None:
    text = _read("docs/llm_browser_final_post_push_verification.md")

    required = [
        "%USERPROFILE%\\Desktop\\patchops_reports\\",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        "Set-Clipboard",
        "$reportPath = [regex]::Match($pointer, 'ReportPath\\s*:\\s*(.+)').Groups[1].Value.Trim()",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_post_push_verification_doc_has_final_state_and_failure_handling() -> None:
    text = _read("docs/llm_browser_final_post_push_verification.md")

    required = [
        "Final repository state interpretation",
        "D0 dry-mode browser-runner closeout is uploaded to GitHub",
        "latest local commit matches `origin/main`",
        "final closeout evidence is preserved under `Desktop\\patchops_reports`",
        "future live-adapter work remains a separate stream",
        "no live browser automation is implied by this dry-mode closeout",
        "Failure handling",
        "Do not create another commit until the failure is understood.",
        "Check whether the push failed, the remote changed, or the local branch is not on `main`.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_post_push_verification_doc_safety_contract() -> None:
    text = _read("docs/llm_browser_final_post_push_verification.md")

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
        "The operator performs post-push verification manually.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_41_post_push_verification() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.41 final post-push verification docs",
        "docs/llm_browser_final_post_push_verification.md",
        "git log -1 --oneline",
        "git fetch origin main",
        "git rev-parse HEAD",
        "git rev-parse origin/main",
        "the docs do not run git commit",
        "the docs do not run git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
