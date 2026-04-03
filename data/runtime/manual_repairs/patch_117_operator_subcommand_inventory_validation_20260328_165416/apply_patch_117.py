from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_operator_subcommand_inventory.py"
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
        if text and not text.endswith("\n"):
            text += "\n"
        if text:
            text += "\n"
        new_text = text + block
    path.write_text(new_text.rstrip() + "\n", encoding="utf-8")


test_content = textwrap.dedent(
    """\
    from __future__ import annotations

    import argparse

    from patchops import cli


    OPERATOR_SUBCOMMANDS = {
        "apply",
        "verify",
        "wrapper-retry",
        "profiles",
        "doctor",
        "examples",
        "schema",
        "check",
        "inspect",
        "plan",
        "template",
        "export-handoff",
        "bootstrap-target",
        "recommend-profile",
        "starter",
        "init-project-doc",
        "refresh-project-doc",
        "release-readiness",
    }


    def _subcommand_names() -> set[str]:
        parser = cli.build_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                return set(action.choices.keys())
        raise AssertionError("PatchOps parser did not expose a subcommand action.")


    def test_operator_subcommands_remain_shipped() -> None:
        subcommands = _subcommand_names()
        assert OPERATOR_SUBCOMMANDS.issubset(subcommands)


    def test_operator_subcommand_inventory_stays_explicit() -> None:
        subcommands = _subcommand_names()
        discovered = {name for name in subcommands if name in OPERATOR_SUBCOMMANDS}
        assert discovered == OPERATOR_SUBCOMMANDS
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH117_LEDGER:START -->
    ## Patch 117

    Patch 117 adds a narrow parser-inventory validation surface for the maintained operator subcommand map.

    It proves the shipped CLI still exposes the current operator-facing subcommands across:
    execution, planning, discovery, onboarding helpers, handoff export, and release readiness.

    This is a narrow maintenance validation patch, not a CLI redesign.
    <!-- PATCHOPS_PATCH117_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH117_STATUS:START -->
    ## Patch 117 - operator subcommand inventory validation

    ### Current state

    - Patch 117 adds a narrow parser-inventory test for the maintained operator subcommand surface.
    - The new test protects the shipped subcommand map independently of help-text wording.

    ### Why this matters

    - the maintained operator surface now has a parser-level inventory check,
    - future command-map drift is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small inventory or contract tests when the main risk is operator-surface drift across already-shipped tooling.
    <!-- PATCHOPS_PATCH117_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH117_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH117_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH117_STATUS:START -->",
    "<!-- PATCHOPS_PATCH117_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")