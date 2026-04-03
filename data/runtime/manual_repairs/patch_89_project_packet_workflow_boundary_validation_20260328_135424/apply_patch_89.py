from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_project_packet_workflow_boundary.py"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def upsert_block(path: Path, start_marker: str, end_marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start_marker in text and end_marker in text:
        start_index = text.index(start_marker)
        end_index = text.index(end_marker, start_index) + len(end_marker)
        new_text = text[:start_index] + block + text[end_index:]
    else:
        if text and not text.endswith("\\n"):
            text += "\\n"
        if text:
            text += "\\n"
        new_text = text + block
    path.write_text(new_text.rstrip() + "\\n", encoding="utf-8")


test_content = textwrap.dedent(
    """\
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
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH89_LEDGER:START -->
    ## Patch 89

    Patch 89 adds a narrow validation surface for the project-packet workflow boundary.

    It proves the maintained docs still keep the intended separation explicit:
    - handoff first for continuation of already-running PatchOps work,
    - generic onboarding packet plus project packet for a brand-new target project.

    This is a maintenance validation patch, not a workflow redesign.
    <!-- PATCHOPS_PATCH89_LEDGER:END -->
    """
)

project_status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH89_STATUS:START -->
    ## Patch 89 - project-packet workflow boundary validation

    ### Current state

    - Patch 89 adds a doc-contract validation test for the onboarding-versus-continuation boundary.
    - The new test reads `docs/project_packet_workflow.md`, `docs/llm_usage.md`, `docs/operator_quickstart.md`, and `docs/project_packet_contract.md`.
    - The goal is to keep the current architecture legible:
      - handoff first for already-running PatchOps continuation,
      - generic packet plus project packet for brand-new target onboarding.

    ### Why this matters

    - the most important workflow distinction now has an explicit test,
    - continuation and onboarding remain separate in the docs,
    - the repo continues through narrow maintenance patches rather than broader redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small validation patches when the architecture is already shipped and the main risk is wording drift.
    <!-- PATCHOPS_PATCH89_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH89_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH89_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH89_STATUS:START -->",
    "<!-- PATCHOPS_PATCH89_STATUS:END -->",
    project_status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")