from __future__ import annotations

from pathlib import Path


def test_onboarding_helper_docs_stay_aligned() -> None:
    workflow_text = Path("docs/project_packet_workflow.md").read_text(encoding="utf-8").lower()
    quickstart_text = Path("docs/operator_quickstart.md").read_text(encoding="utf-8").lower()
    status_text = Path("docs/project_status.md").read_text(encoding="utf-8").lower()

    required_workflow_fragments = [
        "helper-first onboarding command surface",
        "recommend-profile",
        "init-project-doc",
        "starter",
        "onboarding bootstrap artifacts",
        "refresh-project-doc",
        "reduce ambiguity during first use",
        "do not replace manifests, reports, or handoff",
    ]
    for fragment in required_workflow_fragments:
        assert fragment in workflow_text

    required_quickstart_fragments = [
        "onboarding helper reminder",
        "recommend-profile",
        "init-project-doc",
        "starter",
        "onboarding bootstrap artifacts",
        "refresh-project-doc",
        "for already-running patchops work, use handoff first",
    ]
    for fragment in required_quickstart_fragments:
        assert fragment in quickstart_text

    required_status_fragments = [
        "patch 91 - onboarding helper docs alignment validation",
        "recommend-profile",
        "init-project-doc",
        "starter",
        "onboarding bootstrap artifacts",
        "refresh-project-doc",
        "operator-visible onboarding path stays aligned with the shipped helper layer",
    ]
    for fragment in required_status_fragments:
        assert fragment in status_text
