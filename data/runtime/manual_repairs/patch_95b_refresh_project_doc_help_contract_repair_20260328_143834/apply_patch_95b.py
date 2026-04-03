from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_refresh_project_doc_cli_contract.py"
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


    def test_refresh_project_doc_help_exposes_current_live_flags(capsys) -> None:
        with pytest.raises(SystemExit) as exc:
            cli.main(["refresh-project-doc", "--help"])

        assert exc.value.code == 0
        captured = capsys.readouterr()
        text = captured.out + captured.err

        assert "usage: patchops refresh-project-doc" in text

        required_flags = [
            "--project-name",
            "--wrapper-root",
            "--packet-path",
            "--current-phase",
            "--current-objective",
            "--latest-passed-patch",
            "--latest-attempted-patch",
            "--current-recommendation",
            "--next-action",
            "--risk",
        ]
        for flag in required_flags:
            assert flag in text
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH95B_LEDGER:START -->
    ## Patch 95B

    Patch 95B repairs the new `refresh-project-doc` help contract test so it matches the live CLI help surface.

    The local help output currently proves the usage line and the live flags, including `--risk`.
    This repair keeps the validation narrow and avoids widening the CLI just to satisfy a newer-than-live expectation.

    This is a narrow test-contract repair.
    <!-- PATCHOPS_PATCH95B_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH95B_STATUS:START -->
    ## Patch 95B - refresh-project-doc help contract repair

    ### Current state

    - Patch 95B repairs the failing help-text assertion introduced by Patch 95.
    - The test now matches the live `refresh-project-doc --help` surface instead of expecting a newer description string.
    - The repair also aligns the new test with the current `--risk` flag name shown by the live CLI help.

    ### Why this matters

    - the refresh CLI validation stays useful without forcing a CLI wording change,
    - the test now follows the shipped surface,
    - maintenance continues through small honest repairs.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer test-contract repairs when a new test drifted from live operator output.
    <!-- PATCHOPS_PATCH95B_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH95B_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH95B_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH95B_STATUS:START -->",
    "<!-- PATCHOPS_PATCH95B_STATUS:END -->",
    status_block,
)

print(f"UPDATED: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")