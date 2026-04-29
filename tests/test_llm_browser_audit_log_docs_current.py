from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_llm_browser_audit_log_operator_examples_exist_and_cover_cli_surfaces() -> None:
    text = _read("docs/llm_browser_audit_log_operator_examples.md")

    required = [
        "LLM Browser Audit Log Operator Examples",
        "py -m patchops.cli llm-browser dry-run",
        "--audit-log",
        "dry_run_result",
        "py -m patchops.cli llm-browser run-once",
        "--dry-run",
        "integration_result",
        "py -m patchops.cli llm-browser audit-log",
        "--path",
        "--limit",
        "--json",
        "--event-type",
        "--status",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_audit_log_operator_examples_describe_safety_contract() -> None:
    text = _read("docs/llm_browser_audit_log_operator_examples.md")

    required = [
        "The audit-log surfaces are passive.",
        "start a browser",
        "start Selenium",
        "click a download link",
        "run PatchOps",
        "paste into a composer",
        "submit or send a message",
        "start a localhost service",
        "The write path is opt-in and append-only through `--audit-log`.",
        "The readback path is read-only through `llm-browser audit-log`.",
        "There is still no `--auto-send` or `--allow-send` option.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_audit_log_operator_examples_describe_default_path_resolution() -> None:
    text = _read("docs/llm_browser_audit_log_operator_examples.md")

    required = [
        "PATCHOPS_LLM_BROWSER_AUDIT_LOG",
        "PATCHOPS_LLM_BROWSER_STORE_DIR\\audit.jsonl",
        "%LOCALAPPDATA%\\PatchOps\\llm_browser\\audit.jsonl",
        "~\\.patchops\\llm_browser\\audit.jsonl",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_audit_log_operator_examples_describe_state_interpretation() -> None:
    text = _read("docs/llm_browser_audit_log_operator_examples.md")

    required = [
        "BLOCKED_ARTIFACT_MISSING",
        "DOWNLOADING",
        "RUNNING_PATCHOPS",
        "BLOCKED_REPORT_MISSING",
        "SUMMARY_READY",
        "Treat this as fail-closed.",
        "current surfaces do not auto-send anything",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_27_audit_examples() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.27 audit-log docs and operator examples",
        "docs/llm_browser_audit_log_operator_examples.md",
        "audit-log safety contract",
        "llm-browser dry-run --audit-log",
        "llm-browser run-once --dry-run --audit-log",
        "llm-browser audit-log --path --limit --json",
        "no `--auto-send`, `--delete`, or `--clear` option is documented",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_audit_log_docs_do_not_document_mutation_or_send_flags() -> None:
    text = _read("docs/llm_browser_audit_log_operator_examples.md")

    forbidden = [
        "--auto-send",
        "--allow-send",
        "--delete",
        "--clear",
    ]

    # The first two appear only in explicit "there is no ..." safety text.
    assert "There is still no `--auto-send` or `--allow-send` option." in text
    for item in ("--delete", "--clear"):
        assert item not in text
