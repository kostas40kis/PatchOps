from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_closeout_checkpoint_script_exists_and_uses_desktop_report_contract() -> None:
    text = _read("scripts/llm_browser_closeout_validation_push_checkpoint.ps1")

    required = [
        "PATCHOPS LLM-BROWSER CLOSEOUT VALIDATION AND PUSH CHECKPOINT",
        "patchops_reports",
        "patchops_llm_browser_closeout_checkpoint_",
        "patchops_latest_llm_browser_closeout_checkpoint.txt",
        "patchops_latest_llm_browser_broad_validation_report.txt",
        "BroadReportPath",
        "ReportPath",
        "PointerPath",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_closeout_checkpoint_script_runs_validation_but_not_git_mutation() -> None:
    text = _read("scripts/llm_browser_closeout_validation_push_checkpoint.ps1")

    required = [
        "operator broad validation",
        "llm-browser_broad_validation.ps1",
        "broad-report",
        "--strict",
        "llm-browser release-gate",
        "llm-browser checkpoint",
        "git status",
        "git add -A",
        'git commit -m "Close out llm-browser dry-mode validation stream"',
        "git push origin main",
        "this checkpoint never commits or pushes automatically",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []

    forbidden_invocations = [
        "Invoke-NativeCapture -Label 'git add",
        "Invoke-NativeCapture -Label 'git commit",
        "Invoke-NativeCapture -Label 'git push",
    ]
    present = [item for item in forbidden_invocations if item in text]
    assert present == []


def test_closeout_checkpoint_script_has_plan_skip_and_timeout_controls() -> None:
    text = _read("scripts/llm_browser_closeout_validation_push_checkpoint.ps1")

    required = [
        "PlanOnly",
        "SkipBroadValidation",
        "SkipFullPytest",
        "TimeoutBroadValidationSeconds",
        "TimeoutShortSeconds",
        "WaitForExit([Math]::Max(1, $TimeoutSeconds) * 1000)",
        "--- STDOUT ---",
        "--- STDERR ---",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_closeout_checkpoint_docs_include_command_outputs_and_safety() -> None:
    text = _read("docs/llm_browser_closeout_validation_push_checkpoint.md")

    required = [
        "LLM Browser Closeout Validation and Push Checkpoint",
        ".\\scripts\\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\\dev\\patchops",
        "%USERPROFILE%\\Desktop\\patchops_reports\\patchops_llm_browser_closeout_checkpoint_YYYYMMDD_HHMMSS.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "llm-browser broad-report --json --strict",
        "git add -A",
        "git commit -m \"Close out llm-browser dry-mode validation stream\"",
        "git push origin main",
        "does not run git commit",
        "does not run git push",
        "submit or send a message",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_34_closeout_checkpoint() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.34 closeout validation and push checkpoint",
        "scripts/llm_browser_closeout_validation_push_checkpoint.ps1",
        "Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "parses the latest broad-validation report",
        "prints manual commit and push commands",
        "no git commit is performed automatically",
        "no git push is performed automatically",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
