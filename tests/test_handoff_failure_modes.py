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
        failure_block = f"Category : {failure_category}\nMessage  : simulated failure\n"

    report_text = (
        f"{first_line}\n"
        f"Patch Name           : {patch_name}\n"
        "Manifest Path        : C:\\dev\\patchops\\data\\runtime\\self_hosted\\example.json\n"
        "Workspace Root       : C:\\dev\n"
        f"Wrapper Project Root : {root}\n"
        f"Target Project Root  : {root}\n"
        "Active Profile       : generic_python\n"
        "Runtime Path         : (none)\n"
        f"Backup Root          : {root}\\data\\runtime\\patch_backups\\example\n"
        f"Report Path          : {report_path}\n"
        "Manifest Version     : 1\n"
        "\n"
        "TARGET FILES\n"
        "------------\n"
        f"{root}\\patchops\\handoff.py\n"
        "\n"
        "BACKUP\n"
        "------\n"
        "(none)\n"
        "\n"
        "WRITING FILES\n"
        "-------------\n"
        f"WROTE : {root}\\patchops\\handoff.py\n"
        "\n"
        "VALIDATION COMMANDS\n"
        "-------------------\n"
        "NAME    : pytest\n"
        "COMMAND : python -m pytest -q\n"
        f"CWD     : {root}\n"
        f"EXIT    : {0 if result_label == 'PASS' else 1}\n"
        "\n"
        "FULL OUTPUT\n"
        "-----------\n"
        "[pytest][stdout]\n"
        "...\n"
        "\n"
        "[pytest][stderr]\n"
        "\n"
        "\n"
        "FAILURE DETAILS\n"
        "---------------\n"
        f"{failure_block}\n"
        "SUMMARY\n"
        "-------\n"
        f"ExitCode : {0 if result_label == 'PASS' else 1}\n"
        f"Result   : {result_label}\n"
    )
    report_path.write_text(report_text, encoding="utf-8")
    return report_path


def test_export_handoff_bundle_fails_closed_for_missing_report_path(tmp_path: Path) -> None:
    missing_report = tmp_path / "missing_report.txt"
    with pytest.raises(FileNotFoundError):
        export_handoff_bundle(report_path=missing_report, wrapper_project_root=tmp_path)


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
