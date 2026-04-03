from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_inspect_cli_contract.py"
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

    import pytest

    from patchops import cli


    def test_inspect_help_exposes_current_live_surface(capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc:
            cli.main(["inspect", "--help"])

        assert exc.value.code == 0
        captured = capsys.readouterr()
        text = captured.out + captured.err

        assert "usage: patchops inspect" in text
        assert "inspect" in text.lower()
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH108_LEDGER:START -->
    ## Patch 108

    Patch 108 adds a maintenance validation surface for the live help contract of `inspect`.

    It proves the current CLI help still exposes the stable operator-help surface for the `inspect` command without guessing extra flags not grounded in the current uploaded sources.

    This is a narrow validation patch.
    <!-- PATCHOPS_PATCH108_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH108_STATUS:START -->
    ## Patch 108 - inspect help contract validation

    ### Current state

    - Patch 108 adds a direct CLI-help contract test for `inspect`.
    - The new test protects the existence and stable help surface of the inspect step in the current operator flow.

    ### Why this matters

    - the `check -> inspect -> plan` sequence is now more fully protected,
    - the inspect command stays visible and test-backed,
    - the repo continues through narrow maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small contract tests when the main risk is operator-surface drift.
    <!-- PATCHOPS_PATCH108_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH108_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH108_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH108_STATUS:START -->",
    "<!-- PATCHOPS_PATCH108_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")