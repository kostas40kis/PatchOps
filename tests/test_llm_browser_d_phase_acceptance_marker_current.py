from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_d_phase_acceptance_marker_exists_and_sets_status() -> None:
    text = _read("docs/llm_browser_d_phase_acceptance_marker.md")

    required = [
        "LLM Browser Final D-phase Acceptance Marker",
        "D0 dry-mode browser-runner stream accepted pending final manual commit, manual push, and post-push verification",
        "does not claim that live browser automation shipped",
        "passive dry-mode validation and evidence layer",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_d_phase_acceptance_marker_lists_accepted_closeout_patches() -> None:
    text = _read("docs/llm_browser_d_phase_acceptance_marker.md")

    required = [
        "D0.42 final release note and source handoff",
        "D0.43 final validation run and GitHub upload evidence",
        "D0.44 post-D0.43 push verification helper",
        "D0.45 final D-phase acceptance marker",
        "Patch      : D0.42 final release note and source handoff",
        "Patch      : D0.43 final validation run and GitHub upload evidence",
        "Patch      : D0.44 post-D0.43 push verification helper",
        "Next patch : D0.45 Final D-phase acceptance marker",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_d_phase_acceptance_marker_has_manual_commit_push_and_post_push_verification() -> None:
    text = _read("docs/llm_browser_d_phase_acceptance_marker.md")

    required = [
        "git status --short --branch",
        "git add -A",
        "git commit -m \"Close D0 llm-browser dry-mode acceptance marker\"",
        "git push origin main",
        "These commands are manual.",
        ".\\scripts\\llm_browser_post_d0_43_push_verification.ps1 -RepoRoot C:\\dev\\patchops",
        "`HEAD` matches `origin/main`",
        "`git status --short --branch` shows `## main...origin/main`",
        "working tree is clean",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_d_phase_acceptance_marker_defines_acceptance_requirements() -> None:
    text = _read("docs/llm_browser_d_phase_acceptance_marker.md")

    required = [
        "D-phase acceptance definition",
        "D0.45 patch passes",
        "D0.43, D0.44, and D0.45 changes are manually committed",
        "the commit is manually pushed to `origin/main`",
        "post-push verification proves `HEAD` matches `origin/main`",
        "the working tree is clean",
        "Desktop evidence reports remain available",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_d_phase_acceptance_marker_preserves_evidence_pointers() -> None:
    text = _read("docs/llm_browser_d_phase_acceptance_marker.md")

    required = [
        "%USERPROFILE%\\Desktop\\patchops_reports\\",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_closeout_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt",
        "%USERPROFILE%\\Desktop\\patchops_latest_post_d0_43_push_verification.txt",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_d_phase_acceptance_marker_lists_shipped_and_not_shipped_boundaries() -> None:
    text = _read("docs/llm_browser_d_phase_acceptance_marker.md")

    required = [
        "What shipped",
        "optional browser dependency group",
        "passive browser config/profile/path scaffolding for Edge and Opera",
        "dry-run orchestration state",
        "fail-closed PatchOps runner interpretation",
        "broad-validation report parser",
        "post-D0.43 push verification helper",
        "What did not ship",
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


def test_d_phase_acceptance_marker_safety_and_next_stream() -> None:
    text = _read("docs/llm_browser_d_phase_acceptance_marker.md")

    required = [
        "Safety boundary",
        "start a browser by itself",
        "start Selenium by itself",
        "click or download artifacts by itself",
        "run PatchOps packages by itself",
        "paste into the ChatGPT composer",
        "submit or send a message",
        "create a localhost service",
        "commit or push automatically",
        "Next stream",
        "L1 live-adapter skeleton",
        "L1 must start as a separate stream.",
        "must not silently expand this D0 dry-mode closeout into live browser automation",
        "no-side-effect live-adapter interface",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_45_acceptance_marker() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.45 final D-phase acceptance marker",
        "docs/llm_browser_d_phase_acceptance_marker.md",
        "tests/test_llm_browser_d_phase_acceptance_marker_current.py",
        "D phase is accepted when all of the following are true",
        "git commit -m \"Close D0 llm-browser dry-mode acceptance marker\"",
        "L1 live-adapter skeleton",
        "the marker does not run git commit",
        "the marker does not run git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
