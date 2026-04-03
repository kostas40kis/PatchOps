import json
import sys
from pathlib import Path

from patchops.cli import main


def _write_manifest(
    manifest_path: Path,
    project_root: Path,
    patch_name: str,
    report_dir: Path | None = None,
) -> None:
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": patch_name,
                "active_profile": "generic_python",
                "target_project_root": str(project_root),
                "files_to_write": [
                    {"path": "notes.txt", "content": f"{patch_name}\n"}
                ],
                "validation_commands": [
                    {
                        "name": "python_version",
                        "program": sys.executable,
                        "args": ["--version"],
                        "working_directory": ".",
                    }
                ],
                "report_preferences": {
                    "report_dir": str(report_dir or project_root.parent)
                },
            }
        ),
        encoding="utf-8",
    )


def test_plan_command_prints_apply_preview(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "plan_manifest.json"
    _write_manifest(manifest_path, project_root, "plan_demo")

    exit_code = main(["plan", str(manifest_path), "--wrapper-root", str(tmp_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["mode"] == "apply"
    assert payload["active_profile"] == "generic_python"
    assert payload["manifest_path"] == str(manifest_path.resolve())
    assert payload["target_project_root"] == str(project_root.resolve())
    assert payload["target_files"] == [str((project_root / "notes.txt").resolve())]
    assert payload["backup_files"] == ["notes.txt"]
    assert payload["report_path_pattern"].endswith("generic_python_patch_plan_demo_<timestamp>.txt")
    assert payload["backup_root_pattern"] is not None
    assert payload["validation_commands"][0]["name"] == "python_version"


def test_plan_command_prints_verify_preview(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "plan_verify_manifest.json"
    _write_manifest(manifest_path, project_root, "verify_demo")

    exit_code = main(["plan", str(manifest_path), "--mode", "verify", "--wrapper-root", str(tmp_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["mode"] == "verify"
    assert payload["active_profile"] == "generic_python"
    assert payload["manifest_path"] == str(manifest_path.resolve())
    assert payload["target_project_root"] == str(project_root.resolve())
    assert payload["target_files"] == [str((project_root / "notes.txt").resolve())]
    assert payload["backup_files"] == ["notes.txt"]
    assert payload["backup_root_pattern"] is None
    assert payload["report_path_pattern"].endswith("generic_python_patch_verify_verify_demo_<timestamp>.txt")
    assert payload["validation_commands"][0]["name"] == "python_version"


def test_plan_command_prints_wrapper_retry_preview(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "plan_wrapper_retry_manifest.json"
    _write_manifest(manifest_path, project_root, "wrapper_retry_demo")

    exit_code = main(
        [
            "plan",
            str(manifest_path),
            "--mode",
            "wrapper_retry",
            "--retry-reason",
            " report writer failed after validation ",
            "--wrapper-root",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    expected_target = str((project_root / "notes.txt").resolve())
    preview = payload["rerun_preview"]

    assert exit_code == 0
    assert payload["mode"] == "wrapper_retry"
    assert payload["active_profile"] == "generic_python"
    assert payload["manifest_path"] == str(manifest_path.resolve())
    assert payload["target_project_root"] == str(project_root.resolve())
    assert payload["target_files"] == [expected_target]
    assert payload["backup_files"] == ["notes.txt"]
    assert payload["backup_root_pattern"] is None
    assert payload["report_path_pattern"].endswith(
        "generic_python_patch_wrapper_retry_wrapper_retry_demo_<timestamp>.txt"
    )
    assert payload["writes_skipped"] is True
    assert payload["needs_escalation"] is True
    assert payload["retry_reason"] == "report writer failed after validation"

    assert preview["mode"] == "verify"
    assert preview["retry_kind"] == "wrapper_only_retry"
    assert preview["reason"] == "report writer failed after validation"
    assert preview["writes_skipped"] is True
    assert preview["explicit_retry_required"] is True
    assert preview["expected_target_files"] == [expected_target]
    assert preview["existing_target_files"] == []
    assert preview["missing_target_files"] == [expected_target]
    assert preview["validation_command_count"] == 1
    assert preview["smoke_command_count"] == 0
    assert preview["audit_command_count"] == 0
    assert preview["needs_escalation"] is True
    assert preview["allows_writes"] is False
    assert "Scope    : wrapper-only retry" in preview["scope_lines"]
    assert "Writes   : skipped" in preview["scope_lines"]
    assert "Escalate : full apply review required" in preview["scope_lines"]


def test_plan_command_wrapper_retry_uses_default_reason_when_omitted(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "plan_wrapper_retry_default_reason.json"
    _write_manifest(manifest_path, project_root, "wrapper_retry_default")

    exit_code = main(
        [
            "plan",
            str(manifest_path),
            "--mode",
            "wrapper_retry",
            "--wrapper-root",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["mode"] == "wrapper_retry"
    assert payload["writes_skipped"] is True
    assert payload["retry_reason"] == "wrapper/reporting failure after likely content success"
    assert payload["rerun_preview"]["reason"] == "wrapper/reporting failure after likely content success"


def test_plan_command_wrapper_retry_stays_narrow_when_expected_file_exists(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "notes.txt").write_text("already present", encoding="utf-8")

    manifest_path = tmp_path / "plan_wrapper_retry_existing_file.json"
    _write_manifest(manifest_path, project_root, "wrapper_retry_existing")

    exit_code = main(
        [
            "plan",
            str(manifest_path),
            "--mode",
            "wrapper_retry",
            "--retry-reason",
            "report writer failed after likely success",
            "--wrapper-root",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    preview = payload["rerun_preview"]
    expected_target = str((project_root / "notes.txt").resolve())

    assert exit_code == 0
    assert payload["mode"] == "wrapper_retry"
    assert payload["backup_root_pattern"] is None
    assert payload["writes_skipped"] is True
    assert payload["needs_escalation"] is False
    assert payload["retry_reason"] == "report writer failed after likely success"

    assert preview["expected_target_files"] == [expected_target]
    assert preview["existing_target_files"] == [expected_target]
    assert preview["missing_target_files"] == []
    assert preview["needs_escalation"] is False
    assert preview["allows_writes"] is False
    assert "Escalate : stay narrow" in preview["scope_lines"]


def test_plan_command_wrapper_retry_remains_distinct_from_verify_preview(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "plan_wrapper_retry_distinct.json"
    _write_manifest(manifest_path, project_root, "wrapper_retry_distinct")

    verify_exit_code = main(
        [
            "plan",
            str(manifest_path),
            "--mode",
            "verify",
            "--wrapper-root",
            str(tmp_path),
        ]
    )
    verify_payload = json.loads(capsys.readouterr().out)

    wrapper_retry_exit_code = main(
        [
            "plan",
            str(manifest_path),
            "--mode",
            "wrapper_retry",
            "--retry-reason",
            "report writer failed after validation",
            "--wrapper-root",
            str(tmp_path),
        ]
    )
    wrapper_retry_payload = json.loads(capsys.readouterr().out)

    assert verify_exit_code == 0
    assert wrapper_retry_exit_code == 0

    assert verify_payload["mode"] == "verify"
    assert verify_payload["backup_root_pattern"] is None
    assert "rerun_preview" not in verify_payload

    assert wrapper_retry_payload["mode"] == "wrapper_retry"
    assert wrapper_retry_payload["backup_root_pattern"] is None
    assert wrapper_retry_payload["writes_skipped"] is True
    assert wrapper_retry_payload["rerun_preview"]["retry_kind"] == "wrapper_only_retry"
    assert wrapper_retry_payload["report_path_pattern"] != verify_payload["report_path_pattern"]