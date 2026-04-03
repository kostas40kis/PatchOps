from __future__ import annotations

from pathlib import Path


def test_onboarding_bootstrap_docs_stay_aligned() -> None:
    workflow_text = Path("docs/project_packet_workflow.md").read_text(encoding="utf-8").lower()
    examples_text = Path("docs/examples.md").read_text(encoding="utf-8").lower()
    quickstart_text = Path("docs/operator_quickstart.md").read_text(encoding="utf-8").lower()
    status_text = Path("docs/project_status.md").read_text(encoding="utf-8").lower()

    required_workflow_fragments = [
        "onboarding bootstrap artifact surface",
        "onboarding/current_target_bootstrap.md",
        "onboarding/current_target_bootstrap.json",
        "onboarding/next_prompt.txt",
        "onboarding/starter_manifest.json",
        "they do not replace manifests, reports, project packets, or handoff",
    ]
    for fragment in required_workflow_fragments:
        assert fragment in workflow_text

    required_examples_fragments = [
        "onboarding bootstrap examples",
        "onboarding/current_target_bootstrap.md",
        "onboarding/current_target_bootstrap.json",
        "onboarding/next_prompt.txt",
        "onboarding/starter_manifest.json",
        "handoff = continuation of already-running patchops work",
    ]
    for fragment in required_examples_fragments:
        assert fragment in examples_text

    required_quickstart_fragments = [
        "onboarding bootstrap reminder",
        "onboarding/current_target_bootstrap.md",
        "onboarding/current_target_bootstrap.json",
        "onboarding/next_prompt.txt",
        "onboarding/starter_manifest.json",
        "for already-running patchops work, use handoff first instead",
    ]
    for fragment in required_quickstart_fragments:
        assert fragment in quickstart_text

    required_status_fragments = [
        "patch 92 - onboarding bootstrap docs alignment validation",
        "onboarding/current_target_bootstrap.md",
        "onboarding/current_target_bootstrap.json",
        "onboarding/next_prompt.txt",
        "onboarding/starter_manifest.json",
        "bootstrap guidance stays distinct from handoff-first continuation",
    ]
    for fragment in required_status_fragments:
        assert fragment in status_text
