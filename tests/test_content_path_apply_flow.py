import json
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def test_apply_manifest_writes_content_from_content_path(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports"
    manifest_root = tmp_path / "manifest_root"

    target_root.mkdir()
    report_dir.mkdir()
    (manifest_root / "examples" / "content").mkdir(parents=True)

    payload = "External payload loaded through content_path.\n"
    payload_path = manifest_root / "examples" / "content" / "external_note.txt"
    payload_path.write_text(payload, encoding="utf-8")

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "content_path_apply_proof",
        "active_profile": "generic_python",
        "target_project_root": str(target_root).replace("\\", "/"),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "CONTENT_PATH_APPLY_RESULT.txt",
                "content": None,
                "content_path": "examples/content/external_note.txt",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "python_version",
                "program": "python",
                "args": ["--version"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir).replace("\\", "/"),
            "report_name_prefix": "content_path_apply_proof",
            "write_to_desktop": False,
        },
        "tags": ["test", "content_path", "apply_flow"],
        "notes": "Temporary manifest used by test_content_path_apply_flow.",
    }

    manifest_path = manifest_root / "content_path_apply_proof.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    written_file = target_root / "CONTENT_PATH_APPLY_RESULT.txt"
    assert result.result_label == "PASS"
    assert result.exit_code == 0
    assert written_file.exists()
    assert written_file.read_text(encoding="utf-8") == payload
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "CONTENT_PATH_APPLY_RESULT.txt" in report_text
    assert "content_path_apply_proof" in report_text
