from __future__ import annotations

import json
from pathlib import Path

from patchops.handoff import export_handoff_bundle


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_apply_report(
    root: Path,
    *,
    patch_name: str = "patch_70_handoff_failure_class_propagation",
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


def test_export_handoff_bundle_failure_is_honest_for_target_failure(tmp_path: Path) -> None:
    report_path = _write_apply_report(
        tmp_path,
        result_label="FAIL",
        failure_category="target_project_failure",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    current_handoff = _read_json(handoff_root / "current_handoff.json")
    latest_index = _read_json(handoff_root / "latest_report_index.json")
    next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8")

    assert payload["current_status"] == "fail"
    assert payload["failure_class"] == "target_project_failure"
    assert payload["next_recommended_mode"] == "repair_patch"
    assert "repair patch" in payload["next_action"].lower()

    assert current_handoff["repo_state"]["current_status"] == "fail"
    assert current_handoff["repo_state"]["failure_class"] == "target_project_failure"
    assert current_handoff["resume"]["next_recommended_mode"] == "repair_patch"

    assert latest_index["current_status"] == "fail"
    assert latest_index["failure_class"] == "target_project_failure"
    assert latest_index["next_recommended_mode"] == "repair_patch"

    assert "failure class: target_project_failure" in next_prompt
    assert "Keep the repair narrow. Write a repair patch for the failed target surface." in next_prompt


def test_export_handoff_bundle_failure_is_honest_for_wrapper_failure(tmp_path: Path) -> None:
    report_path = _write_apply_report(
        tmp_path,
        result_label="FAIL",
        failure_category="wrapper_failure",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    current_handoff = _read_json(handoff_root / "current_handoff.json")
    latest_index = _read_json(handoff_root / "latest_report_index.json")
    next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8")

    assert payload["current_status"] == "fail"
    assert payload["failure_class"] == "wrapper_failure"
    assert payload["next_recommended_mode"] == "wrapper_only_retry"
    assert "wrapper-only retry" in payload["next_action"].lower()

    assert current_handoff["repo_state"]["failure_class"] == "wrapper_failure"
    assert current_handoff["resume"]["next_recommended_mode"] == "wrapper_only_retry"
    assert latest_index["failure_class"] == "wrapper_failure"
    assert latest_index["next_recommended_mode"] == "wrapper_only_retry"
    assert "failure class: wrapper_failure" in next_prompt
