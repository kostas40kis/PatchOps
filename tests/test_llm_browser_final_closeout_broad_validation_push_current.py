from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_final_closeout_push_script_exists_and_uses_desktop_report_contract() -> None:
    text = _read("scripts/llm_browser_final_closeout_broad_validation_push.ps1")

    required = [
        "PATCHOPS LLM-BROWSER FINAL CLOSEOUT BROAD VALIDATION AND PUSH",
        "patchops_reports",
        "patchops_llm_browser_final_closeout_broad_validation_push_",
        "patchops_latest_llm_browser_final_closeout_broad_validation_push.txt",
        "patchops_latest_llm_browser_final_operator_commit_checkpoint.txt",
        "patchops_latest_llm_browser_closeout_checkpoint.txt",
        "patchops_latest_llm_browser_broad_validation_report.txt",
        "FinalOperatorReportPath",
        "CloseoutReportPath",
        "BroadReportPath",
        "PointerPath",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_push_script_runs_validation_but_not_git_mutation() -> None:
    text = _read("scripts/llm_browser_final_closeout_broad_validation_push.ps1")

    required = [
        "final operator validation and commit checkpoint",
        "llm_browser_final_operator_validation_commit_checkpoint.ps1",
        "broad-report",
        "--strict",
        "llm-browser release-gate",
        "llm-browser checkpoint",
        "git status",
        "git add -A",
        'git commit -m "Close out llm-browser dry-mode validation stream"',
        "git push origin main",
        "this final closeout helper never commits or pushes automatically",
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


def test_final_closeout_push_script_has_plan_skip_and_timeout_controls() -> None:
    text = _read("scripts/llm_browser_final_closeout_broad_validation_push.ps1")

    required = [
        "PlanOnly",
        "SkipFinalOperatorCheckpoint",
        "SkipFullPytest",
        "TimeoutFinalCheckpointSeconds",
        "TimeoutShortSeconds",
        "WaitForExit([Math]::Max(1, $TimeoutSeconds) * 1000)",
        "--- STDOUT ---",
        "--- STDERR ---",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_push_docs_include_command_outputs_and_safety() -> None:
    text = _read("docs/llm_browser_final_closeout_broad_validation_push.md")

    required = [
        "LLM Browser Final Closeout Broad Validation and Push",
        ".\\scripts\\llm_browser_final_closeout_broad_validation_push.ps1 -RepoRoot C:\\dev\\patchops",
        "%USERPROFILE%\\Desktop\\patchops_reports\\patchops_llm_browser_final_closeout_broad_validation_push_YYYYMMDD_HHMMSS.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        "llm-browser broad-report --path ... --json --strict",
        "git add -A",
        "git commit -m \"Close out llm-browser dry-mode validation stream\"",
        "git push origin main",
        "does not run git commit",
        "does not run git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_push_docs_include_clipboard_and_pass_requirements() -> None:
    text = _read("docs/llm_browser_final_closeout_broad_validation_push.md")

    required = [
        "Set-Clipboard",
        "$reportPath = [regex]::Match($pointer, 'ReportPath\\s*:\\s*(.+)').Groups[1].Value.Trim()",
        "`Result : PASS`",
        "`ExitCode : 0`",
        "final operator checkpoint evidence exists",
        "closeout checkpoint evidence exists",
        "broad-validation parser returns PASS under `--strict`",
        "manual commit and push commands are printed",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_39_final_closeout_push() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.39 final closeout broad validation and push",
        "scripts/llm_browser_final_closeout_broad_validation_push.ps1",
        "Desktop\\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt",
        "runs the final operator validation and commit checkpoint",
        "prints manual commit and push commands",
        "no git commit is performed automatically",
        "no git push is performed automatically",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
