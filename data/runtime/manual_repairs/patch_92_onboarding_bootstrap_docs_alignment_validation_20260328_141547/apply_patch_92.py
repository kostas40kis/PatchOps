from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")

WORKFLOW_PATH = PROJECT_ROOT / "docs" / "project_packet_workflow.md"
EXAMPLES_PATH = PROJECT_ROOT / "docs" / "examples.md"
QUICKSTART_PATH = PROJECT_ROOT / "docs" / "operator_quickstart.md"
STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"
LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
TEST_PATH = PROJECT_ROOT / "tests" / "test_onboarding_bootstrap_docs_alignment.py"


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


workflow_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH92_WORKFLOW:START -->
    ## Onboarding bootstrap artifact surface

    The onboarding workflow now includes bootstrap artifacts that can accelerate first use for a brand-new target project.

    The maintained bootstrap artifact set is:

    - `onboarding/current_target_bootstrap.md`
    - `onboarding/current_target_bootstrap.json`
    - `onboarding/next_prompt.txt`
    - `onboarding/starter_manifest.json`

    These artifacts are for brand-new target onboarding.

    They should summarize:
    - project identity,
    - target root,
    - selected profile,
    - project packet path,
    - suggested reading order,
    - recommended command order,
    - initial goals when provided.

    They do not replace manifests, reports, project packets, or handoff.
    <!-- PATCHOPS_PATCH92_WORKFLOW:END -->
    """
)

examples_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH92_EXAMPLES:START -->
    ## Onboarding bootstrap examples

    Use onboarding bootstrap artifacts when the job is to start a brand-new target project faster.

    Expected bootstrap outputs include:

    - `onboarding/current_target_bootstrap.md`
    - `onboarding/current_target_bootstrap.json`
    - `onboarding/next_prompt.txt`
    - `onboarding/starter_manifest.json`

    Simple rule:

    - onboarding bootstrap = helper bundle for first use of a brand-new target,
    - project packet = maintained target-facing contract,
    - handoff = continuation of already-running PatchOps work,
    - report = evidence of what happened.
    <!-- PATCHOPS_PATCH92_EXAMPLES:END -->
    """
)

quickstart_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH92_QUICKSTART:START -->
    ## Onboarding bootstrap reminder

    For a brand-new target project, onboarding bootstrap artifacts can shorten the first-use path.

    Look for:

    - `onboarding/current_target_bootstrap.md`
    - `onboarding/current_target_bootstrap.json`
    - `onboarding/next_prompt.txt`
    - `onboarding/starter_manifest.json`

    For already-running PatchOps work, use handoff first instead.
    <!-- PATCHOPS_PATCH92_QUICKSTART:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH92_STATUS:START -->
    ## Patch 92 - onboarding bootstrap docs alignment validation

    ### Current state

    - Patch 92 adds a narrow doc-contract test for the onboarding bootstrap artifact surface.
    - The maintained docs now keep the bootstrap outputs explicit:
      - `onboarding/current_target_bootstrap.md`,
      - `onboarding/current_target_bootstrap.json`,
      - `onboarding/next_prompt.txt`,
      - `onboarding/starter_manifest.json`.

    ### Why this matters

    - the faster first-use onboarding surface is now documented as a maintained operator story,
    - bootstrap guidance stays distinct from handoff-first continuation,
    - the repo continues through maintenance validation instead of bigger redesign work.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small validation patches when the feature already exists and the main risk is wording drift.
    <!-- PATCHOPS_PATCH92_STATUS:END -->
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH92_LEDGER:START -->
    ## Patch 92

    Patch 92 adds a maintenance validation surface for onboarding bootstrap docs alignment.

    It keeps the bootstrap artifact story explicit across workflow, examples, quickstart, and status docs, and it preserves the rule that onboarding bootstrap is for brand-new target onboarding rather than already-running continuation.

    This is a narrow validation patch, not an onboarding redesign.
    <!-- PATCHOPS_PATCH92_LEDGER:END -->
    """
)

test_content = textwrap.dedent(
    """\
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
    """
)

upsert_block(
    WORKFLOW_PATH,
    "<!-- PATCHOPS_PATCH92_WORKFLOW:START -->",
    "<!-- PATCHOPS_PATCH92_WORKFLOW:END -->",
    workflow_block,
)

upsert_block(
    EXAMPLES_PATH,
    "<!-- PATCHOPS_PATCH92_EXAMPLES:START -->",
    "<!-- PATCHOPS_PATCH92_EXAMPLES:END -->",
    examples_block,
)

upsert_block(
    QUICKSTART_PATH,
    "<!-- PATCHOPS_PATCH92_QUICKSTART:START -->",
    "<!-- PATCHOPS_PATCH92_QUICKSTART:END -->",
    quickstart_block,
)

upsert_block(
    STATUS_PATH,
    "<!-- PATCHOPS_PATCH92_STATUS:START -->",
    "<!-- PATCHOPS_PATCH92_STATUS:END -->",
    status_block,
)

upsert_block(
    LEDGER_PATH,
    "<!-- PATCHOPS_PATCH92_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH92_LEDGER:END -->",
    ledger_block,
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

print(f"UPDATED: {WORKFLOW_PATH}")
print(f"UPDATED: {EXAMPLES_PATH}")
print(f"UPDATED: {QUICKSTART_PATH}")
print(f"UPDATED: {STATUS_PATH}")
print(f"UPDATED: {LEDGER_PATH}")
print(f"WROTE: {TEST_PATH}")