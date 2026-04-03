from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")

README_PATH = PROJECT_ROOT / "README.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"
LLM_USAGE_PATH = PROJECT_ROOT / "docs" / "llm_usage.md"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"


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
    <!-- PATCHOPS_PATCH88B_README:START -->
    ## Legacy-tested handoff wording that remains current

    Read these files in this order:

    1. `handoff/current_handoff.md`
    2. `handoff/current_handoff.json`
    3. `handoff/latest_report_copy.txt`

    For already-running PatchOps continuation, run handoff export first and then paste `handoff/next_prompt.txt`.

    Generic Python + PowerShell profile examples remain part of the maintained orientation story, including the `generic_python_powershell` profile.
    <!-- PATCHOPS_PATCH88B_README:END -->
    """
)

project_status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH88B_PROJECT_STATUS:START -->
    ## Current state snapshot

    This section preserves older snapshot language that is still intentionally tested, while remaining accurate for the current repo state.

    ### Stable now

    The following exists in the repo today:

    - verification-only reruns,
    - wrapper-only retry classification support,
    - `powershell/Invoke-PatchVerify.ps1`,
    - `patchops.cli examples`,
    - the handoff-first continuation surface completed through Patch 69,
    - the later maintenance patches that keep the handoff surface current.

    ### What remains future work rather than current behavior

    This section preserves the distinction between shipped behavior and future work, not yet shipped behavior.

    The project should still describe what remains future work rather than current behavior, especially when discussing additive follow-on improvements beyond the current maintained continuation flow.

    ### Historical anchors that still matter

    - Patch 41 remains the profile-surface reference point for `generic_python_powershell`.
    - Patch 48 remains the final initial-milestone gate reference point.
    - Later handoff work should preserve these anchors rather than flatten the earlier project history.

    ### Current continuation shorthand

    For the already-running handoff-first UX, the operator can now run one export command and paste one generated prompt.
    <!-- PATCHOPS_PATCH88B_PROJECT_STATUS:END -->
    """
)

llm_usage_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH88B_LLM_USAGE:START -->
    ## Legacy-tested orientation wording that remains current

    This guide still teaches:

    - how to read the project,
    - how to pick a profile,
    - how to build a manifest,
    - how to decide between apply and verify-only,
    - how to classify failure,
    - how to avoid moving target-repo logic into patchops.

    Maintained reference surfaces still include:

    - `docs/failure_repair_guide.md`
    - `examples/trader_first_verify_patch.json`
    - `powershell/Invoke-PatchVerify.ps1`

    These older references remain valid even though the handoff bundle is now the first continuation surface for already-running PatchOps work.
    <!-- PATCHOPS_PATCH88B_LLM_USAGE:END -->
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH88B_LEDGER:START -->
    ## Patch 88B

    Patch 88B repairs the Patch 88 docs refresh by restoring older tested wording in `README.md`, `docs/project_status.md`, and `docs/llm_usage.md`.

    The repair is intentionally additive:
    it keeps the newer handoff-first continuation wording while reintroducing the legacy phrases that the maintained doc-contract tests still enforce.

    This is a narrow documentation contract repair, not a surface redesign.
    <!-- PATCHOPS_PATCH88B_LEDGER:END -->
    """
)

upsert_block(
    README_PATH,
    "<!-- PATCHOPS_PATCH88B_README:START -->",
    "<!-- PATCHOPS_PATCH88B_README:END -->",
    readme_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH88B_PROJECT_STATUS:START -->",
    "<!-- PATCHOPS_PATCH88B_PROJECT_STATUS:END -->",
    project_status_block,
)

upsert_block(
    LLM_USAGE_PATH,
    "<!-- PATCHOPS_PATCH88B_LLM_USAGE:START -->",
    "<!-- PATCHOPS_PATCH88B_LLM_USAGE:END -->",
    llm_usage_block,
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH88B_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH88B_LEDGER:END -->",
    ledger_block,
)

print(f"UPDATED: {README_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")
print(f"UPDATED: {LLM_USAGE_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")