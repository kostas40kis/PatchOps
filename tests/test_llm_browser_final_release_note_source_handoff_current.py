from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_final_release_note_exists_and_sets_release_status() -> None:
    text = _read("docs/llm_browser_final_release_note_source_handoff.md")

    required = [
        "LLM Browser Final Release Note and Source Handoff",
        "D0 dry-mode browser-runner stream ready for final validation, manual commit, manual push, and post-push verification",
        "does not claim that a live browser automation loop shipped",
        "passive dry-mode validation and evidence layer",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_release_note_lists_source_handoff_summary() -> None:
    text = _read("docs/llm_browser_final_release_note_source_handoff.md")

    required = [
        "patchops.llm_browser",
        "optional browser dependency metadata",
        "Edge and Opera browser config/profile/path scaffolding",
        "saved HTML snapshot readiness and artifact detection",
        "dry-run orchestration state",
        "fail-closed PatchOps runner interpretation",
        "audit-log write/readback CLI",
        "broad-validation report parser",
        "closeout checkpoint scripts and Desktop pointers",
        "final GitHub upload and post-push verification docs",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_release_note_lists_operator_scripts_docs_and_tests() -> None:
    text = _read("docs/llm_browser_final_release_note_source_handoff.md")

    required = [
        "scripts/llm_browser_broad_validation.ps1",
        "scripts/llm_browser_closeout_validation_push_checkpoint.ps1",
        "scripts/llm_browser_final_operator_validation_commit_checkpoint.ps1",
        "scripts/llm_browser_final_closeout_broad_validation_push.ps1",
        "docs/llm_browser_final_github_upload_helper.md",
        "docs/llm_browser_final_post_push_verification.md",
        "docs/llm_browser_future_live_adapter_plan.md",
        "tests/test_llm_browser_final_post_push_verification_docs_current.py",
        "tests/test_llm_browser_future_live_adapter_plan_current.py",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_release_note_has_final_validation_commit_and_post_push_paths() -> None:
    text = _read("docs/llm_browser_final_release_note_source_handoff.md")

    required = [
        ".\\scripts\\llm_browser_final_closeout_broad_validation_push.ps1 -RepoRoot C:\\dev\\patchops",
        "`Result : PASS`",
        "`ExitCode : 0`",
        "git add -A",
        "git commit -m \"Close out llm-browser dry-mode validation stream\"",
        "git push origin main",
        "git log -1 --oneline",
        "git fetch origin main",
        "git rev-parse HEAD",
        "git rev-parse origin/main",
        "These commands remain manual.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_release_note_preserves_desktop_evidence_pointers() -> None:
    text = _read("docs/llm_browser_final_release_note_source_handoff.md")

    required = [
        "%USERPROFILE%\\Desktop\\patchops_reports\\",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_release_note_lists_not_shipped_and_safety_boundary() -> None:
    text = _read("docs/llm_browser_final_release_note_source_handoff.md")

    required = [
        "What did not ship",
        "live browser-runner loop",
        "automatic send",
        "automatic composer submission",
        "browser extension",
        "localhost service",
        "unattended background work",
        "automatic git commit",
        "automatic git push",
        "Safety boundary",
        "start a browser by itself",
        "start Selenium by itself",
        "click or download artifacts by itself",
        "run PatchOps packages by itself",
        "paste into the ChatGPT composer",
        "submit or send a message",
        "commit or push automatically",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_release_note_defines_future_live_adapter_handoff_and_next_llm_rule() -> None:
    text = _read("docs/llm_browser_final_release_note_source_handoff.md")

    required = [
        "Future live-adapter work remains a separate stream.",
        "must not silently expand this dry-mode closeout into live browser automation",
        "live browser startup",
        "download click",
        "PatchOps package execution",
        "composer paste",
        "final send/submit safety design",
        "The final send/submit action remains unsupported",
        "Handoff rule for the next LLM",
        "continue from evidence, not guesses",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_42_release_note_handoff() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.42 final release note and source handoff",
        "docs/llm_browser_final_release_note_source_handoff.md",
        "release status",
        "source handoff summary",
        "Desktop evidence pointers",
        "what did not ship",
        "future live-adapter handoff",
        "The shipped work is a passive dry-mode validation and evidence layer.",
        "no git commit is performed automatically",
        "no git push is performed automatically",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
