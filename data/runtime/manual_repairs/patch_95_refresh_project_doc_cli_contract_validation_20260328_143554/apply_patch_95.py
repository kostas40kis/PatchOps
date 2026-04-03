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


    def test_refresh_project_doc_help_exposes_artifact_inputs_and_mutable_overrides(capsys) -> None:
        with pytest.raises(SystemExit) as exc:
            cli.main(["refresh-project-doc", "--help"])

        assert exc.value.code == 0
        captured = capsys.readouterr()
        text = captured.out + captured.err

        assert "Refresh the mutable section of an existing project packet under docs/projects/" in text
        assert "Refresh the mutable packet state from explicit inputs and optional handoff/report artifacts." in text

        required_flags = [
            "--packet-path",
            "--handoff-json-path",
            "--report-path",
            "--current-phase",
            "--current-objective",
            "--latest-passed-patch",
            "--latest-attempted-patch",
            "--current-recommendation",
            "--next-action",
            "--blocker",
            "--wrapper-root",
            "--project-name",
        ]
        for flag in required_flags:
            assert flag in text
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH95_LEDGER:START -->
    ## Patch 95

    Patch 95 adds a maintenance validation surface for the `refresh-project-doc` CLI contract.

    It proves the operator-facing help still exposes the intended artifact-grounded refresh inputs:
    `--handoff-json-path`, `--report-path`, and the mutable-state override flags that keep packet refresh explicit rather than hidden.

    This is a narrow validation patch, not a refresh redesign.
    <!-- PATCHOPS_PATCH95_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH95_STATUS:START -->
    ## Patch 95 - refresh-project-doc CLI contract validation

    ### Current state

    - Patch 95 adds a direct CLI-contract test for `refresh-project-doc`.
    - The new test protects the operator-facing refresh shape:
      - packet path,
      - handoff JSON path,
      - report path,
      - mutable-state override flags,
      - blocker input.

    ### Why this matters

    - packet refresh remains explicitly grounded in handoff and report artifacts,
    - operator usage stays visible and test-protected,
    - the repo continues through narrow maintenance validation instead of broader redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small contract tests when the main risk is CLI/help drift across already-shipped surfaces.
    <!-- PATCHOPS_PATCH95_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH95_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH95_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH95_STATUS:START -->",
    "<!-- PATCHOPS_PATCH95_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")