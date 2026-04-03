from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_init_project_doc_cli_contract.py"
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


    def test_init_project_doc_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc:
            cli.main(["init-project-doc", "--help"])

        assert exc.value.code == 0
        captured = capsys.readouterr()
        text = captured.out + captured.err

        assert "usage: patchops init-project-doc" in text

        required_flags = [
            "--project-name",
            "--target-root",
            "--profile",
            "--runtime-path",
            "--initial-goal",
            "--output-path",
            "--wrapper-root",
        ]
        for flag in required_flags:
            assert flag in text
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH97_LEDGER:START -->
    ## Patch 97

    Patch 97 adds a maintenance validation surface for the live help contract of `init-project-doc`.

    It proves the current CLI help still exposes the first-use packet scaffold inputs:
    `--project-name`, `--target-root`, `--profile`, `--runtime-path`, `--initial-goal`, `--output-path`, and `--wrapper-root`.

    This is a narrow validation patch, not a scaffold redesign.
    <!-- PATCHOPS_PATCH97_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH97_STATUS:START -->
    ## Patch 97 - init-project-doc help contract validation

    ### Current state

    - Patch 97 adds a direct CLI-help contract test for `init-project-doc`.
    - The new test protects the live scaffold-help shape used by the helper-first onboarding flow.

    ### Why this matters

    - the remaining first-use packet scaffold command is now covered at the operator-help level,
    - helper-first onboarding stays visible and test-backed,
    - the repo continues through narrow maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small contract tests when the main risk is CLI/help drift across already-shipped helper surfaces.
    <!-- PATCHOPS_PATCH97_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH97_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH97_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH97_STATUS:START -->",
    "<!-- PATCHOPS_PATCH97_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")