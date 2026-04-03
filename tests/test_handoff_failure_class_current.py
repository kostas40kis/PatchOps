import json
from pathlib import Path

from patchops.handoff import export_handoff_bundle


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_apply_report(
    tmp_path: Path,
    result_label: str = "PASS",
    failure_category: str = "none",
    first_line: str = "PATCHOPS APPLY",
) -> Path:
    report_path = tmp_path / "sample_apply_report.txt"
    manifest_path = tmp_path / "patch_manifest.json"
    wrapper_root = tmp_path
    target_root = tmp_path / "target"
    backup_root = tmp_path / "backups"
    target_root.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("{}\n", encoding="utf-8")

    if result_label == "PASS":
        failure_block = "(none)"
        exit_code = 0
    else:
        reason = "Command 'example validation' failed during validation with exit code 1."
        failure_block = (
            f"Failure Class : {failure_category}\n"
            f"Failure Reason: {reason}\n"
            f"Category : {failure_category}\n"
            f"Message  : {reason}"
        )
        exit_code = 1

    report_text = (
        f"{first_line}\n"
        f"Patch Name           : Patch 68\n"
        f"Manifest Path        : {manifest_path}\n"
        f"Workspace Root       : {tmp_path}\n"
        f"Wrapper Project Root : {wrapper_root}\n"
        f"Target Project Root  : {target_root}\n"
        "Active Profile       : generic_python\n"
        "Runtime Path         : (none)\n"
        f"Backup Root          : {backup_root}\n"
        f"Report Path          : {report_path}\n"
        "Manifest Version     : 1\n"
        "Wrapper Mode Used    : apply\n"
        f"Manifest Path Used   : {manifest_path}\n"
        "Profile Resolved     : generic_python\n"
        "Runtime Resolved     : (none)\n"
        "File Write Origin    : wrapper_owned_write_engine\n"
        "\n"
        "TARGET FILES\n"
        "------------\n"
        f"{target_root / 'example.txt'}\n"
        "\n"
        "BACKUP\n"
        "------\n"
        f"MISSING: {target_root / 'example.txt'}\n"
        "\n"
        "WRITING FILES\n"
        "-------------\n"
        f"WROTE : {target_root / 'example.txt'}\n"
        "\n"
        "VALIDATION COMMANDS\n"
        "-------------------\n"
        "NAME    : example validation\n"
        "COMMAND : py -3 -m pytest -q\n"
        f"CWD     : {tmp_path}\n"
        f"EXIT    : {exit_code}\n"
        "\n"
        "FULL OUTPUT\n"
        "-----------\n"
        "[pytest][stdout]\n"
        "\n"
        "[pytest][stderr]\n"
        "\n"
        "\n"
        "FAILURE DETAILS\n"
        "---------------\n"
        f"{failure_block}\n"
        "SUMMARY\n"
        "-------\n"
        f"ExitCode : {exit_code}\n"
        f"Result   : {result_label}\n"
    )
    report_path.write_text(report_text, encoding="utf-8")
    return report_path


def test_export_handoff_bundle_target_failure_propagates_failure_class() -> None:
    tmp_path = Path('tmp_handoff_target_failure_case')
    if tmp_path.exists():
        import shutil
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    try:
        report_path = _write_apply_report(
            tmp_path,
            result_label="FAIL",
            failure_category="target_project_failure",
        )
        payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

        handoff_root = tmp_path / "handoff"
        current_handoff = _read_json(handoff_root / "current_handoff.json")
        latest_index = _read_json(handoff_root / "latest_report_index.json")
        next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8").lower()

        assert payload["current_status"] == "fail"
        assert payload["failure_class"] == "target_project_failure"
        assert payload["next_recommended_mode"] == "repair_patch"
        assert current_handoff["repo_state"]["failure_class"] == "target_project_failure"
        assert latest_index["failure_class"] == "target_project_failure"
        assert "failure class: target_project_failure" in next_prompt
    finally:
        import shutil
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_export_handoff_bundle_wrapper_failure_propagates_failure_class() -> None:
    tmp_path = Path('tmp_handoff_wrapper_failure_case')
    if tmp_path.exists():
        import shutil
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    try:
        report_path = _write_apply_report(
            tmp_path,
            result_label="FAIL",
            failure_category="wrapper_failure",
        )
        payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

        handoff_root = tmp_path / "handoff"
        current_handoff = _read_json(handoff_root / "current_handoff.json")
        latest_index = _read_json(handoff_root / "latest_report_index.json")
        next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8").lower()

        assert payload["current_status"] == "fail"
        assert payload["failure_class"] == "wrapper_failure"
        assert payload["next_recommended_mode"] == "wrapper_only_retry"
        assert current_handoff["repo_state"]["failure_class"] == "wrapper_failure"
        assert latest_index["failure_class"] == "wrapper_failure"
        assert "failure class: wrapper_failure" in next_prompt
    finally:
        import shutil
        shutil.rmtree(tmp_path, ignore_errors=True)