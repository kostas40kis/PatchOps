from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
patch_root = Path(sys.argv[2]).resolve()
desktop = Path(sys.argv[3]).resolve()
patch_name = sys.argv[4]
validation_program = sys.argv[5]
validation_args = json.loads(sys.argv[6])

test_relative = Path("tests/test_content_path_wrapper_root_current.py")
test_path = project_root / test_relative

test_content = textwrap.dedent(
    """
    import json
    from pathlib import Path

    from patchops.workflows.apply_patch import apply_manifest


    def test_apply_manifest_accepts_wrapper_relative_content_path_from_nested_patch_dir(tmp_path: Path) -> None:
        wrapper_root = tmp_path / "wrapper_project"
        target_root = tmp_path / "target_repo"
        report_dir = tmp_path / "reports"
        patch_root = (
            wrapper_root
            / "data"
            / "runtime"
            / "manual_repairs"
            / "patch_cp1_content_path_wrapper_root_repro_contract"
        )

        wrapper_root.mkdir(parents=True, exist_ok=True)
        target_root.mkdir(parents=True, exist_ok=True)
        report_dir.mkdir(parents=True, exist_ok=True)
        patch_root.mkdir(parents=True, exist_ok=True)

        payload_relative = Path(
            "data/runtime/manual_repairs/"
            "patch_cp1_content_path_wrapper_root_repro_contract/"
            "content/src/external_note.txt"
        )
        payload_path = wrapper_root / payload_relative
        payload_path.parent.mkdir(parents=True, exist_ok=True)

        payload = "Wrapper-relative content_path payload.\\n"
        payload_path.write_text(payload, encoding="utf-8")

        manifest_data = {
            "manifest_version": "1",
            "patch_name": "content_path_wrapper_root_repro",
            "active_profile": "generic_python",
            "target_project_root": target_root.as_posix(),
            "backup_files": [],
            "files_to_write": [
                {
                    "path": "CONTENT_PATH_WRAPPER_ROOT_RESULT.txt",
                    "content": None,
                    "content_path": payload_relative.as_posix(),
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
                "report_dir": report_dir.as_posix(),
                "report_name_prefix": "content_path_wrapper_root_repro",
                "write_to_desktop": False,
            },
            "tags": ["test", "content_path", "wrapper_relative", "current_state"],
            "notes": "Current-state repro for wrapper-relative content_path resolution.",
        }

        manifest_path = patch_root / "patch_manifest.json"
        manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

        result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

        expected_source = wrapper_root / payload_relative
        if result.result_label != "PASS":
            failure_category = str(result.failure.category) if result.failure else "(none)"
            failure_message = result.failure.message if result.failure else "(none)"
            failure_details = result.failure.details if result.failure else "(none)"
            report_text = result.report_path.read_text(encoding="utf-8") if result.report_path.exists() else "(report missing)"
            raise AssertionError(
                "Wrapper-relative content_path should resolve from the wrapper root and succeed. "
                f"Expected source path: {expected_source}. "
                f"Failure category: {failure_category}. "
                f"Failure message: {failure_message}. "
                f"Failure details: {failure_details}. "
                f"Report text: {report_text}"
            )

        written_file = target_root / "CONTENT_PATH_WRAPPER_ROOT_RESULT.txt"
        assert written_file.exists()
        assert written_file.read_text(encoding="utf-8") == payload
    """
).lstrip()

patch_root.mkdir(parents=True, exist_ok=True)

manifest = {
    "manifest_version": "1",
    "patch_name": patch_name,
    "active_profile": "generic_python",
    "target_project_root": project_root.as_posix(),
    "backup_files": [],
    "files_to_write": [
        {
            "path": test_relative.as_posix(),
            "content": test_content,
            "content_path": None,
            "encoding": "utf-8",
        }
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_wrapper_root_current",
            "program": validation_program,
            "args": validation_args,
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
        "report_dir": desktop.as_posix(),
        "report_name_prefix": patch_name,
        "write_to_desktop": False,
    },
    "tags": ["content_path", "wrapper_relative", "audit", "repro", "current_state"],
    "notes": (
        "First repair-stream patch. "
        "This patch adds a failing current-state repro test for the documented wrapper-relative content_path contract."
    ),
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")

print(json.dumps({
    "manifest_path": str(manifest_path),
    "test_path": str(test_path),
}))