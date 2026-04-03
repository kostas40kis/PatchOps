from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_core_execution_help_contract_inventory.py"
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
    from pathlib import Path

    from patchops import cli


    ROOT = Path(__file__).resolve().parents[1]


    def _subcommand_names() -> set[str]:
        parser = cli.build_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                return set(action.choices.keys())
        raise AssertionError("PatchOps parser did not expose a subcommand action.")


    def test_core_execution_subcommands_remain_shipped() -> None:
        subcommands = _subcommand_names()
        assert {"apply", "verify", "wrapper-retry"}.issubset(subcommands)


    def test_core_execution_help_contract_tests_exist() -> None:
        expected_tests = (
            ROOT / "tests" / "test_apply_cli_contract.py",
            ROOT / "tests" / "test_verify_cli_contract.py",
            ROOT / "tests" / "test_wrapper_retry_help_contract.py",
        )
        missing = [str(path) for path in expected_tests if not path.exists()]
        assert not missing, f"Missing core execution help-contract tests: {missing}"
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH113_LEDGER:START -->
    ## Patch 113

    Patch 113 adds a narrow inventory validation surface for the core execution help-contract wave.

    It proves the shipped CLI still exposes the three live execution-entry commands:
    `apply`, `verify`, and `wrapper-retry`,
    and it locks the expectation that the matching help-contract tests remain present.

    This is a narrow maintenance validation patch, not a command-surface redesign.
    <!-- PATCHOPS_PATCH113_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH113_STATUS:START -->
    ## Patch 113 - core execution help-contract inventory validation

    ### Current state

    - Patch 113 adds a narrow inventory test for the core execution-entry help-contract wave.
    - The new test keeps two things explicit:
      - the shipped parser still exposes `apply`, `verify`, and `wrapper-retry`,
      - the matching help-contract tests remain present.

    ### Why this matters

    - the core execution-entry trilogy is now protected as a maintained group instead of only as isolated tests,
    - future command-surface changes are more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small validation patches when the main risk is drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH113_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH113_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH113_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH113_STATUS:START -->",
    "<!-- PATCHOPS_PATCH113_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")