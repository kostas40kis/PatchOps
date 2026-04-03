from __future__ import annotations

import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
patch_root = Path(sys.argv[2]).resolve()

content_root = patch_root / "content"
(content_root / "patchops" / "workflows").mkdir(parents=True, exist_ok=True)
(content_root / "tests").mkdir(parents=True, exist_ok=True)
(patch_root / "inner_reports").mkdir(parents=True, exist_ok=True)

common_path = project_root / "patchops" / "workflows" / "common.py"
common_text = common_path.read_text(encoding="utf-8")

old_block = """def build_report_path(prefix: str, patch_name: str, report_dir: Path) -> Path:
    safe_patch = patch_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_directory(report_dir)
    return report_dir / f"{prefix}_{safe_patch}_{timestamp}.txt"
"""

new_block = """def build_report_path(prefix: str, patch_name: str, report_dir: Path) -> Path:
    safe_prefix = prefix.lower().replace(" ", "_")
    safe_patch = patch_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_directory(report_dir)
    name_token = safe_prefix if safe_prefix == safe_patch else f"{safe_prefix}_{safe_patch}"
    return report_dir / f"{name_token}_{timestamp}.txt"
"""

if new_block not in common_text:
    if old_block not in common_text:
        raise SystemExit("Could not find current build_report_path block to replace.")
    common_text = common_text.replace(old_block, new_block, 1)

(content_root / "patchops" / "workflows" / "common.py").write_text(common_text, encoding="utf-8")

test_text = '''from __future__ import annotations

import json
import sys
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest
from patchops.workflows.common import build_report_path


def _seed_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_path_collapses_duplicate_patch_token_current(tmp_path: Path) -> None:
    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    report_dir = tmp_path / "data" / "runtime" / "manual_repairs" / (token + "_20260330_123944") / "inner_reports"

    report_path = build_report_path(token, token, report_dir)

    assert report_path.parent == report_dir
    assert report_dir.exists()
    assert report_path.name.startswith(token + "_")
    assert report_path.name.count(token) == 1
    report_path.write_text("ok\\n", encoding="utf-8")
    assert report_path.exists()


def test_apply_manifest_uses_collapsed_report_name_for_long_self_hosted_shape(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir(parents=True, exist_ok=True)

    _seed_text(wrapper_root / "docs" / "project_status.md", "old project status\\n")
    _seed_text(wrapper_root / "docs" / "patch_ledger.md", "old patch ledger\\n")
    _seed_text(wrapper_root / "docs" / "summary_integrity_repair_stream.md", "old stream\\n")
    _seed_text(wrapper_root / "handoff" / "current_handoff.md", "old handoff markdown\\n")
    _seed_text(wrapper_root / "handoff" / "current_handoff.json", "{}\\n")
    _seed_text(wrapper_root / "handoff" / "latest_report_copy.txt", "old latest report\\n")
    _seed_text(wrapper_root / "handoff" / "latest_report_index.json", "{}\\n")
    _seed_text(wrapper_root / "handoff" / "next_prompt.txt", "old next prompt\\n")

    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    patch_root = wrapper_root / "data" / "runtime" / "manual_repairs" / (token + "_20260330_123944")
    report_dir = patch_root / "inner_reports"
    patch_root.mkdir(parents=True, exist_ok=True)

    manifest_data = {
        "manifest_version": "1",
        "patch_name": token,
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace("\\\\", "/"),
        "backup_files": [
            "docs/project_status.md",
            "docs/patch_ledger.md",
            "docs/summary_integrity_repair_stream.md",
            "handoff/current_handoff.md",
            "handoff/current_handoff.json",
            "handoff/latest_report_copy.txt",
            "handoff/latest_report_index.json",
            "handoff/next_prompt.txt",
        ],
        "files_to_write": [
            {
                "path": "docs/project_status.md",
                "content": "new project status\\n",
                "content_path": None,
                "encoding": "utf-8",
            },
            {
                "path": "docs/patch_ledger.md",
                "content": "new patch ledger\\n",
                "content_path": None,
                "encoding": "utf-8",
            },
            {
                "path": "docs/summary_integrity_repair_stream.md",
                "content": "new stream\\n",
                "content_path": None,
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "python_version",
                "program": sys.executable,
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
            "report_dir": str(report_dir).replace("\\\\", "/"),
            "report_name_prefix": token,
            "write_to_desktop": False,
        },
        "tags": ["test", "summary_integrity", "current", "long_report_path"],
        "notes": "Temporary manifest used by test_apply_manifest_uses_collapsed_report_name_for_long_self_hosted_shape.",
    }

    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert result.report_path.exists()
    assert result.report_path.parent == report_dir
    assert result.report_path.name.count(token) == 1

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "SUMMARY" in report_text
    assert "ExitCode : 0" in report_text
    assert "Result   : PASS" in report_text
'''
(content_root / "tests" / "test_report_path_current.py").write_text(test_text, encoding="utf-8")

manifest = {
    "manifest_version": "1",
    "patch_name": "p134r_report_path_fix",
    "active_profile": "generic_python",
    "target_project_root": str(project_root).replace("\\", "/"),
    "backup_files": [],
    "files_to_write": [
        {
            "path": "patchops/workflows/common.py",
            "content": None,
            "content_path": "content/patchops/workflows/common.py",
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_report_path_current.py",
            "content": None,
            "content_path": "content/tests/test_report_path_current.py",
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "report_path_collapse_pytest",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_report_preference_apply_flow.py",
                "tests/test_report_preference_apply_flow_current.py",
                "tests/test_report_preference_examples.py",
                "tests/test_apply_report_write_current.py",
                "tests/test_report_path_current.py",
            ],
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
        "report_dir": str((patch_root / "inner_reports")).replace("\\", "/"),
        "report_name_prefix": "p134r",
        "write_to_desktop": False,
    },
    "tags": ["self_hosted", "summary_integrity", "report_path", "bootstrap_fix"],
    "notes": "Patch 134R is the short-name bootstrap patch that lands duplicate-token collapse in generated report filenames.",
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(str(manifest_path))