from pathlib import Path
import json
import sys

PATCH_NAME = "patch_134j_report_dir_proof_pytest_repair"
BLOCK = """
<!-- PATCHOPS_PATCH134J_REPORT_DIR_PROOF:START -->
## Patch 134J â€” report-dir proof pytest repair

Patch 134H most likely fixed the underlying apply-flow bug by creating the report directory before writing the canonical report.
The remaining failures were inside the proof layer itself.

This patch keeps the apply-flow repair, updates the maintained report-preference proof test to use an explicit Python runtime, and proves the repair with focused pytest coverage only.
<!-- PATCHOPS_PATCH134J_REPORT_DIR_PROOF:END -->
""".strip() + "\n"

TEST_TEXT = '''import sys
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def test_apply_manifest_creates_missing_custom_report_dir(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports" / "nested"
    target_root.mkdir()

    manifest_path = tmp_path / "missing_report_dir_apply.json"
    manifest_path.write_text(
        """{
  "manifest_version": "1",
  "patch_name": "missing_report_dir_apply",
  "active_profile": "generic_python",
  "target_project_root": "%s",
  "backup_files": [],
  "files_to_write": [
    {
      "path": "REPORT_DIR_CURRENT.txt",
      "content": "report dir current proof\\n",
      "content_path": null,
      "encoding": "utf-8"
    }
  ],
  "validation_commands": [
    {
      "name": "python_version",
      "program": "%s",
      "args": ["--version"],
      "working_directory": ".",
      "use_profile_runtime": false,
      "allowed_exit_codes": [0]
    }
  ],
  "smoke_commands": [],
  "audit_commands": [],
  "cleanup_commands": [],
  "archive_commands": [],
  "failure_policy": {},
  "report_preferences": {
    "report_dir": "%s",
    "report_name_prefix": "report_dir_current",
    "write_to_desktop": false
  },
  "tags": ["test", "report_preferences", "current"],
  "notes": "Temporary manifest used by test_apply_manifest_creates_missing_custom_report_dir."
}
""" % (
            str(target_root).replace("\\", "/"),
            sys.executable.replace("\\", "/"),
            str(report_dir).replace("\\", "/"),
        ),
        encoding="utf-8",
    )

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert report_dir.exists()
    assert result.report_path.exists()
    assert result.report_path.parent == report_dir
    assert (target_root / "REPORT_DIR_CURRENT.txt").read_text(encoding="utf-8") == "report dir current proof\\n"
'''


def append_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "PATCHOPS_PATCH134J_REPORT_DIR_PROOF" in text:
        return text
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n" + BLOCK


def update_existing_report_pref_test(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "import sys" not in text:
        text = "import sys\n" + text
    return text.replace('"program": "python"', '"program": "%s"' % sys.executable.replace("\\", "/"))


def main() -> None:
    patch_root = Path(__file__).resolve().parent
    project_root = patch_root.parent.parent.parent.parent
    content_root = patch_root / "content"

    apply_src = project_root / "patchops" / "workflows" / "apply_patch.py"
    apply_text = apply_src.read_text(encoding="utf-8")
    needle = '    report_path.write_text(render_workflow_report(workflow_result), encoding="utf-8")'
    if "report_path.parent.mkdir(parents=True, exist_ok=True)" not in apply_text:
        if needle not in apply_text:
            raise RuntimeError("Expected report write line not found in apply_patch.py")
        apply_text = apply_text.replace(
            needle,
            '    report_path.parent.mkdir(parents=True, exist_ok=True)\n' + needle,
            1,
        )

    writes = {
        content_root / "patchops" / "workflows" / "apply_patch.py": apply_text,
        content_root / "tests" / "test_report_preference_apply_flow.py": update_existing_report_pref_test(project_root / "tests" / "test_report_preference_apply_flow.py"),
        content_root / "tests" / "test_report_preference_apply_flow_current.py": TEST_TEXT,
        content_root / "docs" / "summary_integrity_repair_stream.md": append_block(project_root / "docs" / "summary_integrity_repair_stream.md"),
        content_root / "docs" / "project_status.md": append_block(project_root / "docs" / "project_status.md"),
        content_root / "docs" / "patch_ledger.md": append_block(project_root / "docs" / "patch_ledger.md"),
    }

    for path, text in writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "backup_files": [],
        "files_to_write": [
            {"path": "patchops/workflows/apply_patch.py", "content": None, "content_path": "content/patchops/workflows/apply_patch.py", "encoding": "utf-8"},
            {"path": "tests/test_report_preference_apply_flow.py", "content": None, "content_path": "content/tests/test_report_preference_apply_flow.py", "encoding": "utf-8"},
            {"path": "tests/test_report_preference_apply_flow_current.py", "content": None, "content_path": "content/tests/test_report_preference_apply_flow_current.py", "encoding": "utf-8"},
            {"path": "docs/summary_integrity_repair_stream.md", "content": None, "content_path": "content/docs/summary_integrity_repair_stream.md", "encoding": "utf-8"},
            {"path": "docs/project_status.md", "content": None, "content_path": "content/docs/project_status.md", "encoding": "utf-8"},
            {"path": "docs/patch_ledger.md", "content": None, "content_path": "content/docs/patch_ledger.md", "encoding": "utf-8"},
        ],
        "validation_commands": [
            {
                "name": "report_dir_proof_pytest",
                "program": "py",
                "args": ["-m", "pytest", "-q", "tests/test_report_preference_apply_flow.py", "tests/test_report_preference_apply_flow_current.py"],
                "working_directory": str(project_root),
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
            "report_dir": str(patch_root / "inner_reports"),
            "report_name_prefix": PATCH_NAME,
            "write_to_desktop": True,
        },
        "tags": ["summary_integrity", "self_hosted", "report_dir_proof_pytest_repair"],
        "notes": "Patch 134J keeps the report-dir creation repair and proves it with focused pytest coverage using an explicit Python runtime.",
    }

    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(str(manifest_path))


if __name__ == "__main__":
    main()