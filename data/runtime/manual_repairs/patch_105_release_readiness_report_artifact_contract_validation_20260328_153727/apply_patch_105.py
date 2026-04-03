from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_release_readiness_report_artifact_current.py"
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

    import json
    from pathlib import Path

    from patchops.cli import main
    from tests.test_release_readiness_command import _seed_release_ready_repo


    def test_release_readiness_report_artifact_matches_current_contract(tmp_path: Path, capsys) -> None:
        _seed_release_ready_repo(tmp_path)
        report_path = tmp_path / "evidence" / "release_readiness.txt"

        exit_code = main(
            [
                "release-readiness",
                "--wrapper-root",
                str(tmp_path),
                "--profile",
                "trader",
                "--core-tests-green",
                "--report-path",
                str(report_path),
            ]
        )
        payload = json.loads(capsys.readouterr().out)
        report_text = report_path.read_text(encoding="utf-8")

        assert exit_code == 0
        assert payload["report_path"] == str(report_path.resolve())
        assert report_text.startswith("PATCHOPS RELEASE READINESS\\n")
        assert f"Wrapper Project   : {tmp_path.resolve()}" in report_text
        assert "Focused Profile   : trader" in report_text
        assert "Status            : green" in report_text
        assert "Core Tests        : green" in report_text
        assert "Tests             : ok" in report_text
        assert "NOTES" in report_text
        assert report_text.endswith(
            "Use --core-tests-green only when the green test state was already proven externally.\\n"
        )
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH105_LEDGER:START -->
    ## Patch 105

    Patch 105 adds a maintenance validation surface for the `release-readiness` report artifact contract.

    It proves the live command still writes a deterministic UTF-8 text artifact through `--report-path` and returns the resolved `report_path` in the JSON payload.

    This is a narrow validation patch, not a readiness redesign.
    <!-- PATCHOPS_PATCH105_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH105_STATUS:START -->
    ## Patch 105 - release-readiness report artifact contract validation

    ### Current state

    - Patch 105 adds a direct contract test for the `release-readiness` evidence artifact.
    - The new test protects the current `--report-path` surface:
      - resolved report path in JSON,
      - deterministic readiness heading,
      - focused profile line,
      - status line,
      - core-tests line,
      - notes footer.

    ### Why this matters

    - the readiness evidence file is now protected as a current operator-facing surface,
    - release/freeze reporting stays deterministic and test-backed,
    - the repo continues through narrow maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small contract tests when the main risk is drift across already-shipped operator surfaces.
    <!-- PATCHOPS_PATCH105_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH105_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH105_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH105_STATUS:START -->",
    "<!-- PATCHOPS_PATCH105_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")