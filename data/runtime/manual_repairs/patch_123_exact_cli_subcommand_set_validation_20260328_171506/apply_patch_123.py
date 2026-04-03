from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_exact_cli_subcommand_set.py"
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


    EXPECTED_SUBCOMMANDS = {
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


    def test_exact_cli_subcommand_set_remains_explicit() -> None:
        assert _subcommand_names() == EXPECTED_SUBCOMMANDS


    def test_exact_cli_subcommand_count_remains_stable() -> None:
        assert len(EXPECTED_SUBCOMMANDS) == 18
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH123_LEDGER:START -->
    ## Patch 123

    Patch 123 adds a narrow validation surface for the exact shipped CLI subcommand set.

    It proves the maintained operator-facing command surface remains exactly:
    - the launcher-backed operator commands,
    - plus the Python-only helper commands,
    - with no unexpected CLI command drift.

    This is a narrow maintenance validation patch, not a CLI redesign.
    <!-- PATCHOPS_PATCH123_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH123_STATUS:START -->
    ## Patch 123 - exact CLI subcommand set validation

    ### Current state

    - Patch 123 adds a narrow exact-set test for the shipped CLI subcommand surface.
    - The new test keeps explicit that the maintained operator-facing command map is not only partitioned and inventoried, but also bounded.

    ### Why this matters

    - the shipped CLI now fails on both missing and unexpected subcommand drift,
    - future operator-surface expansion is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small exact-set, boundary, inventory, or contract tests when the main risk is drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH123_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH123_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH123_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH123_STATUS:START -->",
    "<!-- PATCHOPS_PATCH123_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")