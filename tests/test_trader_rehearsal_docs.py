from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_trader_rehearsal_docs_exist() -> None:
    assert (PROJECT_ROOT / "docs" / "trader_rehearsal_runbook.md").exists()
    assert (PROJECT_ROOT / "docs" / "first_real_trader_run_checklist.md").exists()


def test_trader_rehearsal_runbook_mentions_verify_and_apply() -> None:
    content = (PROJECT_ROOT / "docs" / "trader_rehearsal_runbook.md").read_text(encoding="utf-8")
    assert "patchops.cli verify" in content
    assert "patchops.cli apply" in content


def test_first_real_run_checklist_mentions_check_inspect_plan() -> None:
    content = (PROJECT_ROOT / "docs" / "first_real_trader_run_checklist.md").read_text(encoding="utf-8")
    assert "check" in content
    assert "inspect" in content
    assert "plan" in content
