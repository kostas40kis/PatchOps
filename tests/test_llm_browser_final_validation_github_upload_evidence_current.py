from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_final_validation_upload_evidence_doc_exists_and_names_sources() -> None:
    text = _read("docs/llm_browser_final_validation_github_upload_evidence.md")

    required = [
        "LLM Browser Final Validation Run and GitHub Upload Evidence",
        "patchops_extensive_validate_push_streamsafe_20260429_235823.txt",
        "Patch      : D0.42 final release note and source handoff",
        "Next patch : D0.43 Final validation run and GitHub upload",
        "Result     : PASS",
        "ExitCode   : 0",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_validation_upload_evidence_doc_records_streamsafe_policy_and_compile() -> None:
    text = _read("docs/llm_browser_final_validation_github_upload_evidence.md")

    required = [
        "Policy: run extensive validation first; commit/push only if validation is green.",
        "commands write stdout/stderr to temp files to avoid pipe-buffer deadlocks",
        "heartbeat output shows which long command is still running",
        "PYTHONPATH includes repo src/ so trader.* tests can collect",
        "COMMAND: compileall patchops tests scripts src",
        "ExitCode  : 0",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_validation_upload_evidence_doc_records_pytest_evidence() -> None:
    text = _read("docs/llm_browser_final_validation_github_upload_evidence.md")

    required = [
        "COMMAND: focused llm-browser pytest sweep",
        "collected 443 items",
        "443 passed in 9.09s",
        "COMMAND: full pytest suite",
        "collected 1513 items",
        "Action     : Extensive validation passed; changes committed and pushed to GitHub.",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_validation_upload_evidence_doc_records_github_push_and_status() -> None:
    text = _read("docs/llm_browser_final_validation_github_upload_evidence.md")

    required = [
        "To https://github.com/kostas40kis/PatchOps.git",
        "ea5dd01..4a4b6e3  main -> main",
        "COMMAND: git status after push",
        "## main...origin/main",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_validation_upload_evidence_doc_states_d0_43_boundary() -> None:
    text = _read("docs/llm_browser_final_validation_github_upload_evidence.md")

    required = [
        "D0.43 is an evidence-recording patch.",
        "prior stream-safe validation/push report proves the D0.42 closeout stream was validated, committed, and pushed before D0.43 existed",
        "D0.43 itself creates new doc/test changes",
        "D0.43 docs are not included in that prior push",
        "after D0.43 is accepted, the operator should run a final small validation and commit/push D0.43 itself",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_validation_upload_evidence_doc_has_recommended_next_operator_command() -> None:
    text = _read("docs/llm_browser_final_validation_github_upload_evidence.md")

    required = [
        "Recommended next operator command after D0.43",
        "py -m pytest -q tests\\test_llm_browser_final_validation_github_upload_evidence_current.py tests\\test_llm_browser_final_release_note_source_handoff_current.py tests\\test_exact_cli_subcommand_set.py",
        "git status --short --branch",
        "git add -A",
        "git commit -m \"D0.43 record final validation and GitHub upload evidence\"",
        "git push origin main",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_final_validation_upload_evidence_doc_has_safety_and_d_phase_interpretation() -> None:
    text = _read("docs/llm_browser_final_validation_github_upload_evidence.md")

    required = [
        "Safety contract",
        "run git commit",
        "run git push",
        "stage files automatically",
        "start a browser",
        "start Selenium",
        "click or download artifacts",
        "run PatchOps packages",
        "paste into the ChatGPT composer",
        "submit or send a message",
        "create a localhost service",
        "D-phase interpretation",
        "D0 dry-mode browser-runner stream can be treated as practically closed",
        "L1 live-adapter skeleton",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_d0_43_validation_upload_evidence() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.43 final validation run and GitHub upload evidence",
        "docs/llm_browser_final_validation_github_upload_evidence.md",
        "tests/test_llm_browser_final_validation_github_upload_evidence_current.py",
        "patchops_extensive_validate_push_streamsafe_20260429_235823.txt",
        "focused LLM-browser pytest sweep collected 443 items and passed",
        "full pytest suite collected 1513 items and passed",
        "GitHub push to `https://github.com/kostas40kis/PatchOps.git` succeeded",
        "D0.43 records prior validation/push evidence",
        "the docs do not run git commit",
        "the docs do not run git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
