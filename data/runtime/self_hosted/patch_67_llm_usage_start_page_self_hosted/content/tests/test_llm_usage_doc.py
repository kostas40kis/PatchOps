from pathlib import Path


def test_llm_usage_doc_points_to_handoff_first() -> None:
    text = Path("docs/llm_usage.md").read_text(encoding="utf-8")

    assert "This file is the orientation page for future coding LLMs." in text
    assert "It is not the main state-reconstruction surface anymore." in text
    assert "1. `handoff/current_handoff.md`" in text
    assert "2. `handoff/current_handoff.json`" in text
    assert "3. `handoff/latest_report_copy.txt`" in text


def test_llm_usage_doc_describes_default_takeover_flow() -> None:
    text = Path("docs/llm_usage.md").read_text(encoding="utf-8")

    assert "briefly restate:" in text
    assert "produce only the next repair patch or next planned patch" in text
    assert "do not move target-repo business logic into PatchOps" in text
    assert "prefer narrow repair over broad rewrite" in text


def test_llm_usage_doc_describes_operator_flow() -> None:
    text = Path("docs/llm_usage.md").read_text(encoding="utf-8")

    assert "run handoff export" in text
    assert "upload the generated bundle" in text
    assert "paste `handoff/next_prompt.txt`" in text


def test_handoff_surface_doc_mentions_patch_67_start_page() -> None:
    text = Path("docs/handoff_surface.md").read_text(encoding="utf-8")

    assert "Patch 67" in text
    assert "`docs/llm_usage.md`" in text
    assert "`handoff/current_handoff.md`" in text