from __future__ import annotations

from pathlib import Path


def test_project_packet_update_discipline_stays_explicit() -> None:
    workflow_text = Path("docs/project_packet_workflow.md").read_text(encoding="utf-8").lower()
    contract_text = Path("docs/project_packet_contract.md").read_text(encoding="utf-8").lower()

    required_workflow_fragments = [
        "maintained update discipline",
        "stable packet sections should change rarely",
        "mutable packet sections should be refreshed as validated progress changes",
        "grounded in reports and handoff when available",
        "careful not to rewrite stable sections without real reason",
        "handoff bundle first",
        "refresh the packet after validated progress",
    ]
    for fragment in required_workflow_fragments:
        assert fragment in workflow_text

    required_contract_fragments = [
        "update discipline contract",
        "stable sections usually include",
        "mutable sections usually include",
        "current state",
        "latest passed patch",
        "latest attempted patch",
        "latest report reference when relevant",
        "for a brand-new target project, create the packet before the first manifest",
        "for an already-running patchops effort, use handoff first",
        "a project packet must not replace manifests, reports, or handoff files",
    ]
    for fragment in required_contract_fragments:
        assert fragment in contract_text
