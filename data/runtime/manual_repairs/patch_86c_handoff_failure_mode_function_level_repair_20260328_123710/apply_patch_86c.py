from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_handoff_failure_modes.py"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"


def replace_function(text: str, function_name: str, replacement: str) -> str:
    start_marker = f"def {function_name}("
    start_index = text.find(start_marker)
    if start_index == -1:
        raise SystemExit(f"Could not locate function: {function_name}")

    next_index = text.find("\ndef ", start_index + 1)
    if next_index == -1:
        next_index = len(text)

    before = text[:start_index]
    after = text[next_index:]
    if before and not before.endswith("\n\n"):
        if before.endswith("\n"):
            before += "\n"
        else:
            before += "\n\n"
    return before + replacement.rstrip() + "\n" + after


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


test_text = TEST_PATH.read_text(encoding="utf-8")

replacement_function = textwrap.dedent(
    """\
    def test_export_handoff_bundle_recreates_missing_bundle_file_on_reexport(tmp_path: Path) -> None:
        report_path = _write_apply_report(tmp_path, result_label="PASS")
        export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

        handoff_root = tmp_path / "handoff"
        bundle_prompt = handoff_root / "bundle" / "current" / "next_prompt.txt"
        assert bundle_prompt.exists()

        bundle_prompt.unlink()
        assert not bundle_prompt.exists()

        second_payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

        top_level_prompt = Path(second_payload["next_prompt_path"])
        assert bundle_prompt.exists()
        assert top_level_prompt.exists()
        assert bundle_prompt.read_text(encoding="utf-8") == top_level_prompt.read_text(encoding="utf-8")

        latest_report_copy = handoff_root / "latest_report_copy.txt"
        assert latest_report_copy.exists()

        latest_index = _read_json(handoff_root / "latest_report_index.json")
        assert Path(latest_index["latest_report_copy_path"]) == latest_report_copy
    """
)

new_test_text = replace_function(
    test_text,
    "test_export_handoff_bundle_recreates_missing_bundle_file_on_reexport",
    replacement_function,
)

if new_test_text == test_text:
    raise SystemExit("Function-level replacement produced no change.")

TEST_PATH.write_text(new_test_text, encoding="utf-8")

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH86C_LEDGER:START -->
    ## Patch 86C

    Patch 86C repairs the Patch 86B repair attempt by switching from fragile literal-block matching to function-level replacement for the failing handoff failure-mode test.

    The content repair remains the same:
    the test now asserts `latest_report_copy_path` through `handoff/latest_report_index.json` instead of incorrectly expecting it in the direct `export_handoff_bundle()` return payload.

    This stays a narrow test-contract repair and does not widen the handoff engine.
    <!-- PATCHOPS_PATCH86C_LEDGER:END -->
    """
)

project_status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH86C_STATUS:START -->
    ## Patch 86C - function-level handoff test repair

    ### Current state

    - Patch 86C repairs the failed Patch 86B repair attempt.
    - The new patcher replaces the failing handoff test by function name instead of relying on one exact text block.
    - The repaired assertion path now matches the shipped handoff contract:
      - direct export payload -> prompt path and continuation fields,
      - latest report copy path -> indexed handoff surface.

    ### Why this matters

    - the repair becomes resilient to local formatting drift,
    - the handoff failure-mode coverage remains useful,
    - the repo continues through narrow contract repair instead of wider code changes.

    ### Remaining posture

    - continue with narrow maintenance and refinement patches,
    - prefer robust patchers when fixing test-only drift in already-shipped surfaces.
    <!-- PATCHOPS_PATCH86C_STATUS:END -->
    """
)

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH86C_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH86C_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH86C_STATUS:START -->",
    "<!-- PATCHOPS_PATCH86C_STATUS:END -->",
    project_status_block,
)

print(f"UPDATED: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")