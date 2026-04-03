from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_trader_execution_sequence_doc_exists() -> None:
    assert (PROJECT_ROOT / "docs" / "trader_execution_sequence.md").exists()


def test_trader_execution_sequence_mentions_check_inspect_plan_apply() -> None:
    content = (PROJECT_ROOT / "docs" / "trader_execution_sequence.md").read_text(encoding="utf-8")
    assert "check <manifest>" in content
    assert "inspect <manifest>" in content
    assert "plan <manifest>" in content
    assert "apply <manifest>" in content


def test_release_checklist_mentions_trader_starter_manifest_review() -> None:
    content = (PROJECT_ROOT / "docs" / "release_checklist.md").read_text(encoding="utf-8")
    assert "trader_first_doc_patch.json" in content or "trader starter manifest" in content
