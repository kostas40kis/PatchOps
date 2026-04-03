from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_trader_first_usage_doc_exists() -> None:
    assert (PROJECT_ROOT / "docs" / "trader_first_usage.md").exists()


def test_stage2_entry_criteria_doc_exists() -> None:
    assert (PROJECT_ROOT / "docs" / "stage2_entry_criteria.md").exists()


def test_trader_first_usage_mentions_doctor_template_check_plan_apply() -> None:
    content = (PROJECT_ROOT / "docs" / "trader_first_usage.md").read_text(encoding="utf-8")
    assert "doctor --profile trader" in content
    assert "template --profile trader" in content
    assert "check <manifest>" in content
    assert "plan <manifest>" in content
    assert "apply <manifest>" in content


def test_stage2_entry_criteria_mentions_real_trader_facing_usage() -> None:
    content = (PROJECT_ROOT / "docs" / "stage2_entry_criteria.md").read_text(encoding="utf-8")
    assert "real trader-facing PatchOps usage" in content
