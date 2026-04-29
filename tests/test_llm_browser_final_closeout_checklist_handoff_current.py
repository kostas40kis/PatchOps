from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_final_closeout_checklist_handoff_doc_exists_and_sets_status() -> None:
    text = _read("docs/llm_browser_final_closeout_checklist_handoff.md")

    required = [
        "LLM Browser Final Closeout Checklist and Handoff",
        "Current status: **dry-mode stream ready for final operator closeout validation**.",
        "This is not a live browser automation release.",
        "passive dry-mode validation layer",
        "future live-adapter planning",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_checklist_handoff_doc_has_validation_command_and_pass_requirements() -> None:
    text = _read("docs/llm_browser_final_closeout_checklist_handoff.md")

    required = [
        ".\\scripts\\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\\dev\\patchops",
        "`Result : PASS`",
        "`ExitCode : 0`",
        "broad-validation parser result is PASS under `--strict`",
        "dry-mode release gate is PASS",
        "passive checkpoint command is PASS",
        "manual commit and push commands are printed",
        "no automatic commit or push was performed",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_checklist_handoff_doc_has_report_locations_clipboard_and_parser_commands() -> None:
    text = _read("docs/llm_browser_final_closeout_checklist_handoff.md")

    required = [
        "%USERPROFILE%\\Desktop\\patchops_reports\\",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        "Set-Clipboard",
        "$reportPath = [regex]::Match($pointer, 'ReportPath\\s*:\\s*(.+)').Groups[1].Value.Trim()",
        "py -m patchops.cli llm-browser broad-report --path $reportPath --json --strict",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_checklist_handoff_doc_has_manual_commit_push_and_no_auto_commit_push() -> None:
    text = _read("docs/llm_browser_final_closeout_checklist_handoff.md")

    required = [
        "git status --short --branch",
        "git add -A",
        "git commit -m \"Close out llm-browser dry-mode validation stream\"",
        "git push origin main",
        "They do not run commit or push automatically.",
        "does not commit or push automatically",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_checklist_handoff_doc_summarizes_shipped_and_not_shipped_surfaces() -> None:
    text = _read("docs/llm_browser_final_closeout_checklist_handoff.md")

    required = [
        "What is shipped:",
        "optional browser dependency group",
        "dry-run orchestration state machine",
        "audit-log write/readback CLI",
        "broad-validation report parser",
        "closeout validation and push checkpoint script",
        "future live-adapter development plan",
        "What is not shipped:",
        "live browser-runner loop",
        "automatic send",
        "automatic composer submission",
        "browser extension",
        "localhost service",
        "unattended background work",
        "automatic git commit",
        "automatic git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_checklist_handoff_doc_defines_future_live_adapter_gates_and_safety() -> None:
    text = _read("docs/llm_browser_final_closeout_checklist_handoff.md")

    required = [
        "Future live-adapter work must start as a separate stream.",
        "Do not silently expand this dry-mode closeout into live browser automation.",
        "live browser startup",
        "download click",
        "PatchOps package execution",
        "composer paste",
        "final send/submit safety design",
        "The final send/submit action remains unsupported",
        "does not submit or send a message",
        "does not create a localhost service",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_closeout_checklist_handoff_doc_has_final_operator_rule() -> None:
    text = _read("docs/llm_browser_final_closeout_checklist_handoff.md")

    required = [
        "If the final closeout report is PASS, commit and push manually.",
        "If the final closeout report is FAIL, do not commit or push.",
        "Repair the first failing command section and rerun the final closeout checkpoint.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_37_checklist_handoff() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.37 final closeout checklist and handoff docs",
        "docs/llm_browser_final_closeout_checklist_handoff.md",
        "final closeout validation command",
        "Desktop closeout pointer",
        "Desktop broad-validation pointer",
        "manual commit and push commands",
        "future live-adapter handoff gates",
        "If the final closeout report is PASS, commit and push manually.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
