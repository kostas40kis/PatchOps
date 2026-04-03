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
validation_args_path = Path(sys.argv[6]).resolve()
validation_args = json.loads(validation_args_path.read_text(encoding="utf-8"))

test_path = project_root / "tests/test_content_path_example_apply_current.py"

test_content = textwrap.dedent(
    """
    from __future__ import annotations

    import json
    from pathlib import Path

    from patchops.workflows.apply_patch import apply_manifest


    PROJECT_ROOT = Path(__file__).resolve().parents[1]


    def test_generic_content_path_example_applies_successfully_end_to_end(tmp_path: Path) -> None:
        source_manifest_path = PROJECT_ROOT / "examples" / "generic_content_path_patch.json"
        source_payload_path = PROJECT_ROOT / "examples" / "content" / "generic_content_path_note.txt"

        wrapper_root = tmp_path / "wrapper_project"
        target_root = tmp_path / "target_repo"
        report_dir = tmp_path / "reports"
        patch_root = (
            wrapper_root
            / "data"
            / "runtime"
            / "manual_repairs"
            / "patch_cp4_content_path_example_apply_flow_proof"
        )

        target_root.mkdir(parents=True, exist_ok=True)
        report_dir.mkdir(parents=True, exist_ok=True)
        patch_root.mkdir(parents=True, exist_ok=True)

        payload = source_payload_path.read_text(encoding="utf-8")

        copied_payload_path = wrapper_root / "examples" / "content" / "generic_content_path_note.txt"
        copied_payload_path.parent.mkdir(parents=True, exist_ok=True)
        copied_payload_path.write_text(payload, encoding="utf-8")

        manifest_data = json.loads(source_manifest_path.read_text(encoding="utf-8"))
        manifest_data["target_project_root"] = target_root.as_posix()
        manifest_data["report_preferences"] = {
            "report_dir": report_dir.as_posix(),
            "report_name_prefix": "generic_content_path_example_apply_current",
            "write_to_desktop": False,
        }

        manifest_path = patch_root / "patch_manifest.json"
        # Write compact JSON (no extra whitespace/newline) for reliability
        manifest_path.write_text(json.dumps(manifest_data, separators=(',', ':')), encoding="utf-8")

        result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

        written_file = target_root / "CONTENT_PATH_EXAMPLE.txt"
        assert result.result_label == "PASS"
        assert result.exit_code == 0
        assert result.report_path.exists()
        assert written_file.exists()
        assert written_file.read_text(encoding="utf-8") == payload

        report_text = result.report_path.read_text(encoding="utf-8")
        assert "CONTENT_PATH_EXAMPLE.txt" in report_text
        assert "generic_content_path_example" in report_text
        assert "Result   : PASS" in report_text
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
            "path": "tests/test_content_path_example_apply_current.py",
            "content": test_content,
            "content_path": None,
            "encoding": "utf-8",
        }
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_example_apply_proof",
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
    "tags": ["content_path", "example_manifest", "apply_flow", "proof"],
    "notes": (
        "Fourth repair-stream patch. "
        "This patch adds an end-to-end apply-flow proof for the maintained generic_content_path example manifest."
    ),
}

manifest_path = patch_root / "patch_manifest.json"
# Write compact JSON (no extra whitespace, no trailing newline)
manifest_json = json.dumps(manifest, indent=None, separators=(',', ':'))
manifest_path.write_text(manifest_json, encoding="utf-8")

# Validate the manifest immediately
try:
    with manifest_path.open(encoding="utf-8") as f:
        json.load(f)
except Exception as e:
    raise RuntimeError(f"Manifest validation failed: {e}\nContent:\n{manifest_path.read_text(encoding='utf-8')}")

print(json.dumps({
    "manifest_path": str(manifest_path),
    "test_path": str(test_path),
}))