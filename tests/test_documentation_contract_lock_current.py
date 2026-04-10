from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (PROJECT_ROOT / relative).read_text(encoding="utf-8").lower()


def test_readme_locks_current_command_inventory_and_truth_rule() -> None:
    text = _read("README.md")
    for phrase in ["check", "inspect", "plan", "apply", "verify", "check-bundle", "run-package"]:
        assert phrase in text
    assert "one canonical truth" in text
    assert "suspicious-success" in text or "suspicious success" in text


def test_project_status_locks_code_first_docs_last_process() -> None:
    text = _read("docs/project_status.md")
    assert "code-proof frontier is green" in text or "code-proof frontier" in text
    assert "docs only after the code-proof frontier is green" in text or "documentation contract tests last" in text
    assert "maintenance / additive-improvement posture" in text or "maintenance / additive improvement posture" in text


def test_llm_usage_locks_reporting_and_process_contract() -> None:
    text = _read("docs/llm_usage.md")
    assert "thin powershell" in text
    assert "reusable mechanics in python" in text
    assert "suspicious-success blocker" in text or "suspicious success blocker" in text
    assert "code-first / docs-last" in text or "code-first" in text


def test_operator_quickstart_locks_wrapper_root_and_bundle_flow() -> None:
    text = _read("docs/operator_quickstart.md")
    assert "c:\\dev\\patchops" in text
    assert "check-bundle" in text
    assert "run-package" in text
    assert "canonical report" in text


def test_examples_lock_current_surface_language() -> None:
    text = _read("docs/examples.md")
    assert "modular package layout" in text
    assert "one canonical truth rule" in text
    assert "code-first / docs-last" in text or "code-first" in text
