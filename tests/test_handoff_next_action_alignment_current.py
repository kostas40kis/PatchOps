import json
from pathlib import Path

from patchops.handoff import export_handoff_bundle


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_report(
    root: Path,
    *,
    patch_name: str = "mp41_handoff_alignment_demo",
    result_label: str = "FAIL",
    failure_category: str | None = "wrapper_failure",
    recommended_next_mode: str | None = None,
    first_line: str = "PATCHOPS APPLY",
) -> Path:
    report_path = root / "latest_report.txt"
    failure_block = "(none)"
    if failure_category is not None:
        failure_block = f"Category : {failure_category}\nMessage  : simulated failure\n"

    recommendation_block = ""
    if recommended_next_mode is not None:
        recommendation_block = (
            "RECOMMENDATION\n"
            "--------------\n"
            f"Recommended next mode : {recommended_next_mode}\n\n"
        )

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
        f"{failure_block}"
        f"{recommendation_block}"
        "SUMMARY\n"
        "-------\n"
        f"ExitCode : {0 if result_label == 'PASS' else 1}\n"
        f"Result   : {result_label}\n"
    )
    report_path.write_text(report_text, encoding="utf-8")
    return report_path


def test_report_note_verify_only_maps_handoff_to_verify_only(tmp_path: Path) -> None:
    report_path = _write_report(
        tmp_path,
        result_label="FAIL",
        failure_category="wrapper_failure",
        recommended_next_mode="verify_only",
        first_line="PATCHOPS VERIFY",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)
    current_handoff = _read_json(tmp_path / "handoff" / "current_handoff.json")

    assert payload["next_recommended_mode"] == "verify_only"
    assert current_handoff["resume"]["next_recommended_mode"] == "verify_only"
    assert "verify-only" in payload["next_action"].lower()


def test_report_note_wrapper_only_repair_maps_handoff_to_wrapper_only_retry_guidance(tmp_path: Path) -> None:
    report_path = _write_report(
        tmp_path,
        result_label="FAIL",
        failure_category="wrapper_failure",
        recommended_next_mode="wrapper_only_repair",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)
    current_handoff = _read_json(tmp_path / "handoff" / "current_handoff.json")

    assert payload["next_recommended_mode"] == "wrapper_only_retry"
    assert current_handoff["resume"]["next_recommended_mode"] == "wrapper_only_retry"
    assert "wrapper-only" in payload["next_action"].lower()


def test_report_note_content_repair_maps_handoff_to_repair_patch_guidance(tmp_path: Path) -> None:
    report_path = _write_report(
        tmp_path,
        result_label="FAIL",
        failure_category="wrapper_failure",
        recommended_next_mode="content_repair",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)
    current_handoff = _read_json(tmp_path / "handoff" / "current_handoff.json")

    assert payload["next_recommended_mode"] == "repair_patch"
    assert current_handoff["resume"]["next_recommended_mode"] == "repair_patch"
    assert "content repair" in payload["next_action"].lower() or "repair" in payload["next_action"].lower()


def test_missing_report_note_falls_back_to_failure_class_logic(tmp_path: Path) -> None:
    report_path = _write_report(
        tmp_path,
        result_label="FAIL",
        failure_category="wrapper_failure",
        recommended_next_mode=None,
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    assert payload["next_recommended_mode"] == "wrapper_only_retry"
    assert "wrapper-only" in payload["next_action"].lower()


def test_pass_status_still_recommends_new_patch_even_if_report_note_exists(tmp_path: Path) -> None:
    report_path = _write_report(
        tmp_path,
        patch_name="mp41_demo_pass",
        result_label="PASS",
        failure_category=None,
        recommended_next_mode="content_repair",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    assert payload["current_status"] == "pass"
    assert payload["next_recommended_mode"] == "new_patch"
    assert "continue with" in payload["next_action"].lower()
