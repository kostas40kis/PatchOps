from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")

README_PATH = PROJECT_ROOT / "README.md"
LLM_USAGE_PATH = PROJECT_ROOT / "docs" / "llm_usage.md"
OPERATOR_QUICKSTART_PATH = PROJECT_ROOT / "docs" / "operator_quickstart.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"
HANDOFF_SURFACE_PATH = PROJECT_ROOT / "docs" / "handoff_surface.md"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
TEST_PATH = PROJECT_ROOT / "tests" / "test_handoff_operator_docs_current.py"


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


readme_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH87_README:START -->
    ## Current handoff operator reality

    The handoff bundle is a shipped continuation surface, not just a future idea.

    When resuming already-running PatchOps work, start with:

    1. `handoff/current_handoff.md`
    2. `handoff/current_handoff.json`
    3. `handoff/latest_report_copy.txt`

    The default operator continuation flow is:

    1. run `export-handoff`
    2. upload the generated handoff bundle
    3. paste `handoff/next_prompt.txt`

    Project packets remain the target-facing contract for brand-new target-project onboarding.
    They do not replace handoff for current PatchOps continuation.
    <!-- PATCHOPS_PATCH87_README:END -->
    """
)

llm_usage_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH87_LLM_USAGE:START -->
    ## Current continuation entry point

    For already-running PatchOps work, the handoff bundle is the first maintained entry point.

    Read these files in this order:

    1. `handoff/current_handoff.md`
    2. `handoff/current_handoff.json`
    3. `handoff/latest_report_copy.txt`

    After reading the handoff bundle:

    - briefly restate current state,
    - restate latest attempted patch,
    - restate failure class,
    - perform the exact next recommended action.

    Do not start current-state reconstruction by scanning scattered docs when the handoff bundle exists.

    Use project packets for brand-new target onboarding, not as the primary resume surface for PatchOps itself.
    <!-- PATCHOPS_PATCH87_LLM_USAGE:END -->
    """
)

operator_quickstart_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH87_OPERATOR_QUICKSTART:START -->
    ## Handoff-first continuation quickstart

    Use this path when PatchOps work is already in progress.

    1. Run `py -m patchops.cli export-handoff --report-path <latest_report> --wrapper-root <wrapper_root>`
    2. Upload the generated files under `handoff/`
    3. Paste `handoff/next_prompt.txt` into the next LLM session
    4. Let the next LLM continue from the exact next recommended action

    This is the default continuation flow.

    Use the generic onboarding packet and project packets only when the task is to start a brand-new target project with PatchOps.
    <!-- PATCHOPS_PATCH87_OPERATOR_QUICKSTART:END -->
    """
)

project_status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH87_PROJECT_STATUS:START -->
    ## Patch 87 - handoff operator docs stop

    ### Current state

    - Patch 87 refreshes the operator-facing handoff docs after the repaired handoff failure-mode tests are green.
    - The docs now describe handoff export and `handoff/next_prompt.txt` as shipped continuation surfaces.
    - The docs also keep the distinction explicit:
      - handoff = current run-state and next action,
      - project packets = target-facing contract for new target onboarding.

    ### Why this matters

    - future LLMs and operators no longer need to infer whether handoff export is still future work,
    - current continuation flow is documented as current reality,
    - the repo stays in maintenance/refinement posture instead of drifting back into stale roadmap language.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - treat the old handoff redesign stream as implemented and now maintained.
    <!-- PATCHOPS_PATCH87_PROJECT_STATUS:END -->
    """
)

handoff_surface_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH87_HANDOFF_SURFACE:START -->
    ## Current operator contract

    The handoff surface is now a maintained continuation contract.

    Operator-facing reality:

    - `export-handoff` is the standard way to produce the current continuation bundle.
    - `handoff/current_handoff.md` is the first human-readable resume surface.
    - `handoff/current_handoff.json` is the machine-readable resume surface.
    - `handoff/latest_report_copy.txt` is the stable copy of the latest canonical report.
    - `handoff/next_prompt.txt` is the generated takeover prompt for the next LLM.

    Current expectation:

    - use handoff first for already-running PatchOps continuation,
    - use project packets first only for brand-new target-project onboarding,
    - preserve the one-report evidence contract and narrow-repair discipline.
    <!-- PATCHOPS_PATCH87_HANDOFF_SURFACE:END -->
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH87_LEDGER:START -->
    ## Patch 87

    Patch 87 is the handoff operator docs stop after the repaired handoff failure-mode validation wave.

    It refreshes the main operator-facing docs so they describe current handoff reality instead of sounding like handoff export is still pending future work.

    It also adds one doc-contract test that keeps the handoff-first continuation wording aligned across README, llm usage, quickstart, status, and handoff-surface docs.
    <!-- PATCHOPS_PATCH87_LEDGER:END -->
    """
)

test_content = textwrap.dedent(
    """\
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
    """
)

upsert_block(
    README_PATH,
    "<!-- PATCHOPS_PATCH87_README:START -->",
    "<!-- PATCHOPS_PATCH87_README:END -->",
    readme_block,
)

upsert_block(
    LLM_USAGE_PATH,
    "<!-- PATCHOPS_PATCH87_LLM_USAGE:START -->",
    "<!-- PATCHOPS_PATCH87_LLM_USAGE:END -->",
    llm_usage_block,
)

upsert_block(
    OPERATOR_QUICKSTART_PATH,
    "<!-- PATCHOPS_PATCH87_OPERATOR_QUICKSTART:START -->",
    "<!-- PATCHOPS_PATCH87_OPERATOR_QUICKSTART:END -->",
    operator_quickstart_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH87_PROJECT_STATUS:START -->",
    "<!-- PATCHOPS_PATCH87_PROJECT_STATUS:END -->",
    project_status_block,
)

upsert_block(
    HANDOFF_SURFACE_PATH,
    "<!-- PATCHOPS_PATCH87_HANDOFF_SURFACE:START -->",
    "<!-- PATCHOPS_PATCH87_HANDOFF_SURFACE:END -->",
    handoff_surface_block,
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH87_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH87_LEDGER:END -->",
    ledger_block,
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

print(f"UPDATED: {README_PATH}")
print(f"UPDATED: {LLM_USAGE_PATH}")
print(f"UPDATED: {OPERATOR_QUICKSTART_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")
print(f"UPDATED: {HANDOFF_SURFACE_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"WROTE: {TEST_PATH}")