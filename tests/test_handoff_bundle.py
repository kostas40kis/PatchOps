import json
from pathlib import Path

import patchops.cli as cli
from patchops.handoff import export_handoff_bundle


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_apply_report(
    root: Path,
    *,
    patch_name: str = "patch_68_handoff_bundle_tests",
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


def test_export_handoff_bundle_green_writes_consistent_top_level_and_bundle_files(tmp_path: Path) -> None:
    report_path = _write_apply_report(tmp_path, result_label="PASS")
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    bundle_root = handoff_root / "bundle" / "current"

    expected_names = (
        "current_handoff.md",
        "current_handoff.json",
        "latest_report_copy.txt",
        "latest_report_index.json",
        "next_prompt.txt",
    )

    for name in expected_names:
        top_level = handoff_root / name
        bundled = bundle_root / name
        assert top_level.exists(), name
        assert bundled.exists(), name
        assert top_level.read_text(encoding="utf-8") == bundled.read_text(encoding="utf-8"), name

    assert payload["current_status"] == "pass"
    assert payload["next_recommended_mode"] == "new_patch"
    assert payload["next_action"] == "Continue with Patch 69."
    assert Path(payload["next_prompt_path"]) == handoff_root / "next_prompt.txt"


def test_export_handoff_bundle_green_json_and_index_agree_on_state(tmp_path: Path) -> None:
    report_path = _write_apply_report(tmp_path, result_label="PASS")
    export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    current_handoff = _read_json(handoff_root / "current_handoff.json")
    latest_index = _read_json(handoff_root / "latest_report_index.json")

    assert current_handoff["repo_state"]["current_status"] == "pass"
    assert latest_index["current_status"] == "pass"
    assert current_handoff["repo_state"]["failure_class"] == "none"
    assert latest_index["failure_class"] == "none"
    assert current_handoff["latest_patch"]["latest_attempted_patch"] == "Patch 68"
    assert latest_index["latest_attempted_patch"] == "Patch 68"
    assert current_handoff["latest_patch"]["latest_passed_patch"] == "Patch 68"
    assert latest_index["latest_passed_patch"] == "Patch 68"
    assert current_handoff["resume"]["next_recommended_mode"] == "new_patch"
    assert latest_index["next_recommended_mode"] == "new_patch"
    assert current_handoff["resume"]["next_action"] == "Continue with Patch 69."
    assert latest_index["next_action"] == "Continue with Patch 69."


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
    assert current_handoff["latest_patch"]["latest_passed_patch"] == "unknown from this run"
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


def test_export_handoff_bundle_next_prompt_read_order_stays_stable(tmp_path: Path) -> None:
    report_path = _write_apply_report(tmp_path, result_label="PASS")
    export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    text = (tmp_path / "handoff" / "next_prompt.txt").read_text(encoding="utf-8")
    assert "Read these files in this order:" in text
    assert "1. handoff/current_handoff.md" in text
    assert "2. handoff/current_handoff.json" in text
    assert "3. handoff/latest_report_copy.txt" in text
    assert "Then produce only the next repair patch or next planned patch." in text


def test_cli_export_handoff_bundle_contract_matches_function_surface(tmp_path: Path) -> None:
    report_path = _write_apply_report(tmp_path, result_label="PASS")

    exit_code = cli.main(
        [
            "export-handoff",
            "--report-path",
            str(report_path),
            "--wrapper-root",
            str(tmp_path),
            "--bundle-name",
            "current",
        ]
    )

    assert exit_code == 0

    handoff_root = tmp_path / "handoff"
    current_handoff = _read_json(handoff_root / "current_handoff.json")
    latest_index = _read_json(handoff_root / "latest_report_index.json")

    assert (handoff_root / "bundle" / "current" / "current_handoff.md").exists()
    assert (handoff_root / "bundle" / "current" / "current_handoff.json").exists()
    assert (handoff_root / "bundle" / "current" / "latest_report_copy.txt").exists()
    assert (handoff_root / "bundle" / "current" / "latest_report_index.json").exists()
    assert (handoff_root / "bundle" / "current" / "next_prompt.txt").exists()

    assert current_handoff["latest_patch"]["latest_attempted_patch"] == "Patch 68"
    assert latest_index["latest_attempted_patch"] == "Patch 68"
    assert current_handoff["resume"]["next_recommended_mode"] == "new_patch"
    assert latest_index["next_recommended_mode"] == "new_patch"


def test_cli_export_handoff_detects_verify_mode_from_report_header(tmp_path: Path) -> None:
    report_path = _write_apply_report(
        tmp_path,
        result_label="FAIL",
        failure_category="target_project_failure",
        first_line="PATCHOPS VERIFY",
    )

    exit_code = cli.main(
        [
            "export-handoff",
            "--report-path",
            str(report_path),
            "--wrapper-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    current_handoff = _read_json(tmp_path / "handoff" / "current_handoff.json")
    latest_index = _read_json(tmp_path / "handoff" / "latest_report_index.json")

    assert current_handoff["repo_state"]["latest_run_mode"] == "verify_only"
    assert latest_index["latest_run_mode"] == "verify_only"
    assert current_handoff["resume"]["next_recommended_mode"] == "repair_patch"