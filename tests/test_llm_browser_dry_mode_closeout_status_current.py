from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_dry_mode_closeout_doc_exists_and_records_closed_status() -> None:
    text = _read("docs/llm_browser_dry_mode_closeout.md")

    required = [
        "LLM Browser Dry-mode Closeout Status",
        "Current status: **dry-mode stream closed for operator validation**.",
        "not a live browser automation release",
        "operator-controlled validation layer",
        "one-command operator docs",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_dry_mode_closeout_doc_lists_closed_surfaces() -> None:
    text = _read("docs/llm_browser_dry_mode_closeout.md")

    required = [
        "optional dependency group",
        "Edge and Opera path/profile/session scaffolding",
        "passive page-readiness and artifact detection",
        "dry-run orchestration state machine",
        "fail-closed PatchOps runner result interpretation",
        "audit-log write and readback CLI",
        "passive dry-mode release gate",
        "passive checkpoint guidance",
        "operator broad-validation script",
        "Desktop report folder and Desktop pointer file",
        "broad-validation report parser",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_dry_mode_closeout_doc_keeps_operator_commands_visible() -> None:
    text = _read("docs/llm_browser_dry_mode_closeout.md")

    required = [
        ".\\scripts\\llm_browser_broad_validation.ps1 -RepoRoot C:\\dev\\patchops",
        "%USERPROFILE%\\Desktop\\patchops_reports\\",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        "py -m patchops.cli llm-browser broad-report --path $reportPath --json --strict",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_dry_mode_closeout_doc_names_intentionally_not_shipped_items() -> None:
    text = _read("docs/llm_browser_dry_mode_closeout.md")

    required = [
        "automatic send",
        "automatic composer submission",
        "live browser-runner loop",
        "localhost service",
        "browser extension",
        "unattended background work",
        "automatic git commit or push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_dry_mode_closeout_doc_sets_future_live_adapter_rule() -> None:
    text = _read("docs/llm_browser_dry_mode_closeout.md")

    required = [
        "Any future live adapter must start as a new development stream.",
        "must not silently expand this dry-mode closeout into live browser automation",
        "live browser startup",
        "download click",
        "PatchOps package execution",
        "composer paste",
        "send/submit action",
        "The send/submit action must remain unsupported",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_33_closeout_status() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.33 browser-runner dry-mode closeout status refresh",
        "docs/llm_browser_dry_mode_closeout.md",
        "dry-mode stream closed for operator validation",
        "not a live browser automation release",
        "Desktop\\patchops_reports",
        "Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        "automatic send",
        "live browser-runner loop",
        "Any future live adapter must start as a separate development stream",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
