from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_root_cli_help_contract.py"
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


    def test_root_help_exposes_current_live_operator_surface(capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc:
            cli.main(["--help"])

        assert exc.value.code == 0
        captured = capsys.readouterr()
        text = captured.out + captured.err

        assert "usage: patchops" in text

        required_commands = [
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
        ]
        for command in required_commands:
            assert command in text
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH114_LEDGER:START -->
    ## Patch 114

    Patch 114 adds a narrow help-contract test for the root `patchops --help` surface.

    It proves the top-level CLI entry still exposes the maintained operator-facing command map,
    including the core execution commands, the onboarding helpers, and the planning / validation surfaces.

    This is a narrow validation patch, not a CLI redesign.
    <!-- PATCHOPS_PATCH114_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH114_STATUS:START -->
    ## Patch 114 - root help contract validation

    ### Current state

    - Patch 114 adds a direct CLI-help contract test for the root `patchops --help` entry.
    - The new test protects the maintained operator-visible command map as a whole.

    ### Why this matters

    - the root command index is now covered at the help-contract level,
    - future drift in the top-level operator surface is more likely to trigger a narrow honest repair,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH114_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH114_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH114_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH114_STATUS:START -->",
    "<!-- PATCHOPS_PATCH114_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")