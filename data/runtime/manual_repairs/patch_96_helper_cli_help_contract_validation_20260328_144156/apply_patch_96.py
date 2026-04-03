from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_helper_cli_help_contract.py"
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


    def _help_text(args: list[str], capsys: pytest.CaptureFixture[str]) -> str:
        with pytest.raises(SystemExit) as exc:
            cli.main(args)
        assert exc.value.code == 0
        captured = capsys.readouterr()
        return captured.out + captured.err


    def test_recommend_profile_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
        text = _help_text(["recommend-profile", "--help"], capsys)

        assert "usage: patchops recommend-profile" in text

        required_flags = [
            "--target-root",
            "--wrapper-root",
        ]
        for flag in required_flags:
            assert flag in text


    def test_starter_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
        text = _help_text(["starter", "--help"], capsys)

        assert "usage: patchops starter" in text

        required_flags = [
            "--profile",
            "--intent",
            "--target-root",
            "--patch-name",
            "--wrapper-root",
        ]
        for flag in required_flags:
            assert flag in text
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH96_LEDGER:START -->
    ## Patch 96

    Patch 96 adds a maintenance validation surface for the live help contracts of the helper-first onboarding commands.

    It proves the current CLI help for `recommend-profile` and `starter` still exposes the small live flag surface that the onboarding helper layer depends on.

    This is a narrow validation patch, not a helper redesign.
    <!-- PATCHOPS_PATCH96_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH96_STATUS:START -->
    ## Patch 96 - helper CLI help contract validation

    ### Current state

    - Patch 96 adds a direct CLI-help contract test for the remaining small helper-first commands.
    - The new test protects:
      - `recommend-profile`,
      - `starter`.

    ### Why this matters

    - the helper-first onboarding surface is now protected at both behavior and live help levels,
    - operator-facing usage stays visible and test-backed,
    - the repo continues through narrow maintenance validation instead of broader redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small contract tests when the main risk is CLI/help drift across already-shipped helper surfaces.
    <!-- PATCHOPS_PATCH96_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH96_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH96_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH96_STATUS:START -->",
    "<!-- PATCHOPS_PATCH96_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")