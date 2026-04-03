from __future__ import annotations

from pathlib import Path


def test_handoff_operator_docs_stay_current() -> None:
    root = Path(__file__).resolve().parents[1]

    readme = (root / "README.md").read_text(encoding="utf-8")
    llm_usage = (root / "docs" / "llm_usage.md").read_text(encoding="utf-8")
    operator_quickstart = (root / "docs" / "operator_quickstart.md").read_text(encoding="utf-8")
    project_status = (root / "docs" / "project_status.md").read_text(encoding="utf-8")
    handoff_surface = (root / "docs" / "handoff_surface.md").read_text(encoding="utf-8")

    assert "handoff/current_handoff.md" in readme
    assert "handoff/current_handoff.json" in readme
    assert "handoff/latest_report_copy.txt" in readme
    assert "handoff/next_prompt.txt" in readme

    assert "Do not start current-state reconstruction by scanning scattered docs when the handoff bundle exists." in llm_usage
    assert "handoff/current_handoff.md" in llm_usage
    assert "handoff/current_handoff.json" in llm_usage
    assert "handoff/latest_report_copy.txt" in llm_usage

    assert "Handoff-first continuation quickstart" in operator_quickstart
    assert "export-handoff" in operator_quickstart
    assert "handoff/next_prompt.txt" in operator_quickstart

    assert "Patch 87 - handoff operator docs stop" in project_status
    assert "handoff = current run-state and next action" in project_status
    assert "project packets = target-facing contract for new target onboarding" in project_status

    assert "The handoff surface is now a maintained continuation contract." in handoff_surface
    assert "export-handoff" in handoff_surface
    assert "handoff/next_prompt.txt" in handoff_surface
