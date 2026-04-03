from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_handoff_failure_modes.py"
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

    import pytest

    from patchops.handoff import export_handoff_bundle


    def _read_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


    def _write_apply_report(
        root: Path,
        *,
        patch_name: str = "patch_86_handoff_failure_mode_validation",
        result_label: str = "PASS",
        failure_category: str | None = None,
        first_line: str = "PATCHOPS APPLY",
    ) -> Path:
        report_path = root / "latest_report.txt"
        failure_block = "(none)"
        if failure_category is not None:
            failure_block = f"Category : {failure_category}\\nMessage  : simulated failure\\n"

        report_text = (
            f"{first_line}\\n"
            f"Patch Name           : {patch_name}\\n"
            "Manifest Path        : C:\\\\dev\\\\patchops\\\\data\\\\runtime\\\\self_hosted\\\\example.json\\n"
            "Workspace Root       : C:\\\\dev\\n"
            f"Wrapper Project Root : {root}\\n"
            f"Target Project Root  : {root}\\n"
            "Active Profile       : generic_python\\n"
            "Runtime Path         : (none)\\n"
            f"Backup Root          : {root}\\\\data\\\\runtime\\\\patch_backups\\\\example\\n"
            f"Report Path          : {report_path}\\n"
            "Manifest Version     : 1\\n"
            "\\n"
            "TARGET FILES\\n"
            "------------\\n"
            f"{root}\\\\patchops\\\\handoff.py\\n"
            "\\n"
            "BACKUP\\n"
            "------\\n"
            "(none)\\n"
            "\\n"
            "WRITING FILES\\n"
            "-------------\\n"
            f"WROTE : {root}\\\\patchops\\\\handoff.py\\n"
            "\\n"
            "VALIDATION COMMANDS\\n"
            "-------------------\\n"
            "NAME    : pytest\\n"
            "COMMAND : python -m pytest -q\\n"
            f"CWD     : {root}\\n"
            f"EXIT    : {0 if result_label == 'PASS' else 1}\\n"
            "\\n"
            "FULL OUTPUT\\n"
            "-----------\\n"
            "[pytest][stdout]\\n"
            "...\\n"
            "\\n"
            "[pytest][stderr]\\n"
            "\\n"
            "\\n"
            "FAILURE DETAILS\\n"
            "---------------\\n"
            f"{failure_block}\\n"
            "SUMMARY\\n"
            "-------\\n"
            f"ExitCode : {0 if result_label == 'PASS' else 1}\\n"
            f"Result   : {result_label}\\n"
        )
        report_path.write_text(report_text, encoding="utf-8")
        return report_path


    def test_export_handoff_bundle_fails_closed_for_missing_report_path(tmp_path: Path) -> None:
        missing_report = tmp_path / "missing_report.txt"
        with pytest.raises(FileNotFoundError):
            export_handoff_bundle(report_path=missing_report, wrapper_project_root=tmp_path)


    def test_export_handoff_bundle_recreates_missing_bundle_file_on_reexport(tmp_path: Path) -> None:
        report_path = _write_apply_report(tmp_path, result_label="PASS")
        first_payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

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
        assert Path(first_payload["latest_report_copy_path"]).exists()


    def test_export_handoff_bundle_recreates_missing_top_level_index_on_reexport(tmp_path: Path) -> None:
        report_path = _write_apply_report(tmp_path, result_label="PASS")
        export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

        handoff_root = tmp_path / "handoff"
        top_level_index = handoff_root / "latest_report_index.json"
        assert top_level_index.exists()

        top_level_index.unlink()
        assert not top_level_index.exists()

        export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

        assert top_level_index.exists()
        payload = _read_json(top_level_index)
        assert payload["current_status"] == "pass"
        assert payload["next_recommended_mode"] == "new_patch"


    def test_export_handoff_bundle_refreshes_stale_prompt_when_failure_class_changes(tmp_path: Path) -> None:
        pass_report = _write_apply_report(tmp_path, result_label="PASS")
        pass_payload = export_handoff_bundle(report_path=pass_report, wrapper_project_root=tmp_path)

        prompt_path = Path(pass_payload["next_prompt_path"])
        pass_prompt = prompt_path.read_text(encoding="utf-8")
        assert "Continue with Patch" in pass_prompt

        fail_report = _write_apply_report(
            tmp_path,
            result_label="FAIL",
            failure_category="target_project_failure",
        )
        fail_payload = export_handoff_bundle(report_path=fail_report, wrapper_project_root=tmp_path)

        fail_prompt = Path(fail_payload["next_prompt_path"]).read_text(encoding="utf-8")
        assert fail_prompt != pass_prompt
        assert "failure class: target_project_failure" in fail_prompt
        assert "Keep the repair narrow. Write a repair patch for the failed target surface." in fail_prompt
        assert "Continue with Patch" not in fail_prompt
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH86_LEDGER:START -->
    ## Patch 86

    Patch 86 adds handoff failure-mode validation for self-hosted continuation.

    It proves that handoff export fails closed for a missing report path, recreates missing bundle artifacts on re-export, recreates a missing top-level index on re-export, and refreshes a stale generated prompt when the report result changes.

    The patch stays validation-first and does not widen the handoff engine.
    <!-- PATCHOPS_PATCH86_LEDGER:END -->
    """
)

project_status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH86_STATUS:START -->
    ## Patch 86 - handoff failure-mode validation

    ### Current state

    - Patch 86 adds targeted handoff failure-mode tests.
    - The new validation covers:
      - missing report path -> fail closed,
      - missing bundled prompt -> recreated on re-export,
      - missing top-level index -> recreated on re-export,
      - stale prompt after state change -> refreshed on re-export.
    - The patch stays within maintenance/refinement posture after the Patch 84 onboarding stop and the Patch 85 onboarding helper roundtrip validation.

    ### Why this matters

    - continuation becomes more trustworthy in realistic self-hosted rerun conditions,
    - export-handoff behavior is protected against stale or partially missing artifacts,
    - the repo keeps improving through narrow validation patches instead of broad redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer the smallest test or repair patch that closes a real workflow gap.
    <!-- PATCHOPS_PATCH86_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH86_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH86_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH86_STATUS:START -->",
    "<!-- PATCHOPS_PATCH86_STATUS:END -->",
    project_status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")