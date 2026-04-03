from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_llm_usage_mentions_helpers_and_handoff_split() -> None:
    text = _read("docs/llm_usage.md")
    assert "PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:START" in text
    assert "recommend-profile" in text
    assert "starter --profile" in text
    assert "handoff/current_handoff.md" in text


def test_workflow_doc_describes_mechanical_sequence() -> None:
    text = _read("docs/project_packet_workflow.md")
    assert "PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:START" in text
    assert "bootstrap-target" in text
    assert "refresh-project-doc" in text
    assert "structured, conservative, and evidence-first" in text


def test_profile_system_and_examples_explain_helper_relationship() -> None:
    profile_text = _read("docs/profile_system.md")
    examples_text = _read("docs/examples.md")
    assert "PATCHOPS_PATCH84_PROFILE_SYSTEM_HELPERS:START" in profile_text
    assert "recommend-profile --target-root" in profile_text
    assert "PATCHOPS_PATCH84_EXAMPLES_STARTER_GUIDANCE:START" in examples_text
    assert "examples as the baseline" in examples_text


def test_project_status_marks_onboarding_layer_substantially_complete() -> None:
    text = _read("docs/project_status.md")
    assert "PATCHOPS_PATCH84_STATUS_FINALIZATION:START" in text
    assert "profile recommendation helper" in text
    assert "starter helper by intent" in text
    assert "handoff remains the resume surface" in text
