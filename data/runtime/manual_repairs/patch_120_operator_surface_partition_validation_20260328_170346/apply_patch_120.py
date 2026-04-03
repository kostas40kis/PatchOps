from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_operator_surface_partition.py"
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


    LAUNCHER_BACKED_COMMANDS = {
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
        "release-readiness",
    }

    PYTHON_ONLY_HELPER_COMMANDS = {
        "bootstrap-target",
        "recommend-profile",
        "starter",
        "init-project-doc",
        "refresh-project-doc",
    }

    EXPECTED_OPERATOR_SURFACE = LAUNCHER_BACKED_COMMANDS | PYTHON_ONLY_HELPER_COMMANDS


    def _subcommand_names() -> set[str]:
        parser = cli.build_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                return set(action.choices.keys())
        raise AssertionError("PatchOps parser did not expose a subcommand action.")


    def test_operator_surface_partitions_remain_disjoint() -> None:
        overlap = LAUNCHER_BACKED_COMMANDS.intersection(PYTHON_ONLY_HELPER_COMMANDS)
        assert not overlap, f"Operator surface partitions must stay disjoint: {sorted(overlap)}"


    def test_operator_surface_partitions_cover_current_operator_map() -> None:
        subcommands = _subcommand_names()
        discovered = {name for name in subcommands if name in EXPECTED_OPERATOR_SURFACE}
        assert discovered == EXPECTED_OPERATOR_SURFACE


    def test_operator_surface_partition_size_stays_explicit() -> None:
        assert len(LAUNCHER_BACKED_COMMANDS) == 13
        assert len(PYTHON_ONLY_HELPER_COMMANDS) == 5
        assert len(EXPECTED_OPERATOR_SURFACE) == 18
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH120_LEDGER:START -->
    ## Patch 120

    Patch 120 adds a narrow partition validation surface for the maintained operator command map.

    It proves the shipped operator-facing commands still split cleanly into two explicit groups:
    - launcher-backed commands,
    - Python-only helper commands.

    It also keeps the combined maintained operator map explicit without widening behavior.

    This is a narrow maintenance validation patch, not an operator-surface redesign.
    <!-- PATCHOPS_PATCH120_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH120_STATUS:START -->
    ## Patch 120 - operator surface partition validation

    ### Current state

    - Patch 120 adds a narrow partition test for the maintained operator command map.
    - The new test keeps three things explicit:
      - launcher-backed commands remain one maintained group,
      - Python-only helper commands remain a separate maintained group,
      - together they still cover the current operator-facing surface.

    ### Why this matters

    - the operator map is now protected as an explicit partition instead of only as separate inventories,
    - future drift across launcher-backed versus Python-only boundaries is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small partition, inventory, or contract tests when the main risk is drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH120_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH120_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH120_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH120_STATUS:START -->",
    "<!-- PATCHOPS_PATCH120_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")