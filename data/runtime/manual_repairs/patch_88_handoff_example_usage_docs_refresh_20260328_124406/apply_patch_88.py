from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")

EXAMPLES_PATH = PROJECT_ROOT / "docs" / "examples.md"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"
TEST_PATH = PROJECT_ROOT / "tests" / "test_handoff_examples_current.py"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def upsert_block(path: Path, start_marker: str, end_marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start_marker in text and end_marker in text:
        start_index = text.index(start_marker)
        end_index = text.index(end_marker, start_index) + len(end_marker)
        new_text = text[:start_index] + block + text[end_index:]
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        if text:
            text += "\n"
        new_text = text + block
    path.write_text(new_text.rstrip() + "\n", encoding="utf-8")


examples_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH88_EXAMPLES:START -->
    ## Handoff-first continuation examples

    Use these examples when PatchOps work is already in progress and the right first surface is the handoff bundle, not a brand-new target onboarding packet.

    ### Example 1 — export the current handoff bundle from a known report

    ```powershell
    py -m patchops.cli export-handoff --report-path C:\\Users\\kostas\\Desktop\\patch_87_handoff_operator_docs_stop_20260328_124012.txt --wrapper-root C:\\dev\\patchops
    ```

    Expected stable outputs under `handoff/` include:

    - `handoff/current_handoff.md`
    - `handoff/current_handoff.json`
    - `handoff/latest_report_copy.txt`
    - `handoff/latest_report_index.json`
    - `handoff/next_prompt.txt`
    - `handoff/bundle/current/`

    ### Example 2 — operator continuation flow

    When handing off to the next LLM during an already-running PatchOps effort:

    1. run handoff export,
    2. upload the generated handoff files or the compact bundle,
    3. paste `handoff/next_prompt.txt`,
    4. continue from the exact next recommended action.

    ### Example 3 — when not to use handoff first

    Do **not** use handoff as the first step when the job is to onboard a brand-new target project.

    For brand-new target onboarding, start with the generic PatchOps packet, then create or refresh the relevant project packet under `docs/projects/`.

    Simple rule:

    - handoff = continuation of current PatchOps run-state,
    - project packet = maintained target-facing contract,
    - manifest = exact instructions for this run,
    - report = evidence of what happened.
    <!-- PATCHOPS_PATCH88_EXAMPLES:END -->
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH88_LEDGER:START -->
    ## Patch 88

    Patch 88 refreshes the handoff-first example usage surfaces after the operator-docs stop.

    It updates `docs/examples.md` so continuation examples now show the current export-handoff flow, the expected handoff artifacts, and the distinction between handoff-first continuation and brand-new target onboarding.

    It also adds one doc-contract test so example usage wording stays aligned with the shipped handoff surfaces.
    <!-- PATCHOPS_PATCH88_LEDGER:END -->
    """
)

project_status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH88_STATUS:START -->
    ## Patch 88 - handoff example usage docs refresh

    ### Current state

    - Patch 88 refreshes `docs/examples.md` for the current handoff-first continuation flow.
    - The examples now show how to run `export-handoff`, which files are expected under `handoff/`, and when handoff should be used instead of project-packet onboarding.
    - This keeps the handoff redesign sequence moving through small documentation patches after the green validation wave.

    ### Why this matters

    - examples now match the current CLI and handoff surfaces,
    - continuation guidance is easier to follow mechanically,
    - onboarding and continuation remain clearly separated.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - treat the old handoff-redesign stream as implemented and now maintained.
    <!-- PATCHOPS_PATCH88_STATUS:END -->
    """
)

test_content = textwrap.dedent(
    """\
    from __future__ import annotations

    from pathlib import Path


    def test_examples_doc_describes_current_handoff_export_usage() -> None:
        text = Path("docs/examples.md").read_text(encoding="utf-8")

        assert "Handoff-first continuation examples" in text
        assert "py -m patchops.cli export-handoff" in text
        assert "handoff/current_handoff.md" in text
        assert "handoff/current_handoff.json" in text
        assert "handoff/latest_report_copy.txt" in text
        assert "handoff/latest_report_index.json" in text
        assert "handoff/next_prompt.txt" in text
        assert "handoff/bundle/current/" in text
        assert "Do **not** use handoff as the first step when the job is to onboard a brand-new target project." in text
        assert "project packet = maintained target-facing contract" in text
        assert "report = evidence of what happened." in text
    """
)

upsert_block(
    EXAMPLES_PATH,
    "<!-- PATCHOPS_PATCH88_EXAMPLES:START -->",
    "<!-- PATCHOPS_PATCH88_EXAMPLES:END -->",
    examples_block,
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH88_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH88_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH88_STATUS:START -->",
    "<!-- PATCHOPS_PATCH88_STATUS:END -->",
    project_status_block,
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

print(f"UPDATED: {EXAMPLES_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")
print(f"WROTE: {TEST_PATH}")