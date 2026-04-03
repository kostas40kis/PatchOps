from __future__ import annotations

from pathlib import Path


def test_project_packet_workflow_preserves_onboarding_vs_continuation_boundary() -> None:
    workflow_text = Path("docs/project_packet_workflow.md").read_text(encoding="utf-8")
    llm_usage_text = Path("docs/llm_usage.md").read_text(encoding="utf-8")
    operator_quickstart_text = Path("docs/operator_quickstart.md").read_text(encoding="utf-8")
    contract_text = Path("docs/project_packet_contract.md").read_text(encoding="utf-8")

    workflow_lower = workflow_text.lower()
    llm_usage_lower = llm_usage_text.lower()
    operator_quickstart_lower = operator_quickstart_text.lower()
    contract_lower = contract_text.lower()

    required_workflow_fragments = [
        "brand-new target project",
        "already-running patchops effort",
        "handoff/current_handoff.md",
        "handoff/current_handoff.json",
        "handoff/latest_report_copy.txt",
        "docs/projects/<project_name>.md",
        "generic onboarding packet",
        "project packet",
        "manifest",
        "report",
    ]
    for fragment in required_workflow_fragments:
        assert fragment in workflow_lower

    assert "the distinction between onboarding and continuation is explicit" in workflow_lower
    assert "the distinction between project packets and handoff is explicit" in workflow_lower

    assert "starting a brand-new target project with patchops" in llm_usage_lower
    assert "continuing an already-running patchops effort" in llm_usage_lower
    assert "handoff/current_handoff.md" in llm_usage_lower
    assert "docs/projects/<project_name>.md" in llm_usage_lower

    assert "brand-new target onboarding" in operator_quickstart_lower
    assert "already-running patchops work" in operator_quickstart_lower

    assert "how the packet differs from handoff files" in contract_lower
    assert "for an already-running patchops effort" in contract_lower
    assert "for a brand-new target project" in contract_lower
