from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_future_live_adapter_plan_exists_and_separates_stream_from_dry_mode() -> None:
    text = _read("docs/llm_browser_future_live_adapter_plan.md")

    required = [
        "LLM Browser Future Live-adapter Development Plan",
        "The dry-mode browser-runner stream is closed for operator validation.",
        "A future live adapter must be developed as a separate stream.",
        "must not silently expand dry-mode code into unattended browser automation",
        "The goal is not to create an unattended bot.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_future_live_adapter_plan_lists_non_goals() -> None:
    text = _read("docs/llm_browser_future_live_adapter_plan.md")

    required = [
        "automatic send",
        "automatic composer submission",
        "unattended background work",
        "localhost service",
        "browser extension",
        "hidden browser automation",
        "automatic git commit",
        "automatic git push",
        "live PatchOps package execution without an explicit gate",
        "download click without an explicit gate",
        "composer paste without an explicit gate",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_future_live_adapter_plan_lists_required_gates() -> None:
    text = _read("docs/llm_browser_future_live_adapter_plan.md")

    required = [
        "live browser startup gate",
        "page readiness gate",
        "latest assistant reply detection gate",
        "artifact candidate detection gate",
        "download click gate",
        "download stabilization gate",
        "PatchOps package execution gate",
        "canonical report detection gate",
        "pasteback summary construction gate",
        "composer paste gate",
        "final send/submit gate",
        "The final send/submit gate remains unsupported",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_future_live_adapter_plan_documents_patch_sequence() -> None:
    text = _read("docs/llm_browser_future_live_adapter_plan.md")

    required = [
        "L1 live adapter skeleton",
        "L2 browser startup gate",
        "L3 page readiness live read gate",
        "L4 latest assistant reply live detection",
        "L5 download click gate",
        "L6 PatchOps execution gate",
        "L7 canonical report gate",
        "L8 pasteback construction gate",
        "L9 composer paste gate",
        "L10 send/submit safety design only",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_future_live_adapter_plan_keeps_validation_and_report_rules() -> None:
    text = _read("docs/llm_browser_future_live_adapter_plan.md")

    required = [
        ".\\scripts\\llm_browser_broad_validation.ps1 -RepoRoot C:\\dev\\patchops",
        ".\\scripts\\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\\dev\\patchops",
        "%USERPROFILE%\\Desktop\\patchops_reports\\",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "create a Desktop pointer file to the actual report path",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_future_live_adapter_plan_keeps_audit_commit_and_closeout_rules() -> None:
    text = _read("docs/llm_browser_future_live_adapter_plan.md")

    required = [
        "Every future live-adapter gate must append a compact audit event",
        "side effects performed",
        "artifact filename when applicable",
        "report path when applicable",
        "Future patch scripts must not run git commit or git push automatically.",
        "Operator scripts may print manual commands",
        "actual commit/push remains operator-controlled",
        "broad validation passes",
        "closeout checkpoint passes",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_35_future_plan() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.35 future live-adapter development plan",
        "docs/llm_browser_future_live_adapter_plan.md",
        "future live adapter to be developed as a separate stream",
        "must not silently expand dry-mode code into unattended browser automation",
        "final send/submit gate remains unsupported",
        "Future live-adapter reports must use `Desktop\\patchops_reports`",
        "patch scripts must not run git commit or git push automatically",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
