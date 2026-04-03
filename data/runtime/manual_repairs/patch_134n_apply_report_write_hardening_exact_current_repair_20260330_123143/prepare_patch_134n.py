from __future__ import annotations

import json
import re
import sys
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
patch_root = Path(sys.argv[2]).resolve()

content_root = patch_root / "content"
(content_root / "patchops" / "workflows").mkdir(parents=True, exist_ok=True)
(content_root / "tests").mkdir(parents=True, exist_ok=True)
(patch_root / "inner_reports").mkdir(parents=True, exist_ok=True)

apply_patch_path = project_root / "patchops" / "workflows" / "apply_patch.py"
apply_patch_text = apply_patch_path.read_text(encoding="utf-8")

helper_anchor = "from patchops.workflows.common import build_report_path, default_report_directory, infer_workspace_root\n"
helper_block = """

def _write_workflow_report(report_path: Path, report_text: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        report_path.write_text(report_text, encoding="utf-8")
    except FileNotFoundError:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")
"""

if "def _write_workflow_report(report_path: Path, report_text: str) -> None:" not in apply_patch_text:
    if helper_anchor not in apply_patch_text:
        raise SystemExit("Could not find apply_patch helper insertion anchor.")
    apply_patch_text = apply_patch_text.replace(helper_anchor, helper_anchor + helper_block, 1)

broken_tail_pattern = re.compile(
    r"(?ms)^ {8}report_path\.parent\.mkdir\(parents=True, exist_ok=True\)\s*"
    r"^ {4}report_path\.write_text\(render_workflow_report\(workflow_result\),\s*encoding=\"utf-8\"\)\s*"
    r"^ {4}return workflow_result"
)

fixed_tail = (
    "        report_text = render_workflow_report(workflow_result)\n"
    "        _write_workflow_report(report_path, report_text)\n"
    "    return workflow_result"
)

if "_write_workflow_report(report_path, report_text)" not in apply_patch_text:
    apply_patch_text, replacements = broken_tail_pattern.subn(fixed_tail, apply_patch_text, count=1)
    if replacements != 1:
        raise SystemExit("Could not find exact-current apply_patch report-write tail to replace.")

(content_root / "patchops" / "workflows" / "apply_patch.py").write_text(apply_patch_text, encoding="utf-8")

test_text = '''from __future__ import annotations

import json
import sys
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def _seed_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_apply_manifest_writes_custom_report_for_self_hosted_docs_shape(tmp_path: Path) -> None:
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

    patch_root = wrapper_root / "data" / "runtime" / "manual_repairs" / "proof_like_patch"
    report_dir = patch_root / "inner_reports"
    patch_root.mkdir(parents=True, exist_ok=True)

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "self_hosted_docs_report_write_current",
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
            "report_name_prefix": "self_hosted_docs_report_write_current",
            "write_to_desktop": False,
        },
        "tags": ["test", "summary_integrity", "current", "self_hosted_docs_shape"],
        "notes": "Temporary manifest used by test_apply_manifest_writes_custom_report_for_self_hosted_docs_shape.",
    }

    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert report_dir.exists()
    assert result.report_path.exists()
    assert result.report_path.parent == report_dir

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "SUMMARY" in report_text
    assert "ExitCode : 0" in report_text
    assert "Result   : PASS" in report_text

    assert (wrapper_root / "docs" / "project_status.md").read_text(encoding="utf-8") == "new project status\\n"
    assert (wrapper_root / "docs" / "patch_ledger.md").read_text(encoding="utf-8") == "new patch ledger\\n"
    assert (wrapper_root / "docs" / "summary_integrity_repair_stream.md").read_text(encoding="utf-8") == "new stream\\n"
'''
(content_root / "tests" / "test_apply_report_write_current.py").write_text(test_text, encoding="utf-8")

manifest = {
    "manifest_version": "1",
    "patch_name": "patch_134n_apply_report_write_hardening_exact_current_repair",
    "active_profile": "generic_python",
    "target_project_root": str(project_root).replace("\\", "/"),
    "backup_files": [],
    "files_to_write": [
        {
            "path": "patchops/workflows/apply_patch.py",
            "content": None,
            "content_path": "content/patchops/workflows/apply_patch.py",
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_apply_report_write_current.py",
            "content": None,
            "content_path": "content/tests/test_apply_report_write_current.py",
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "apply_report_write_hardening_pytest",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_report_preference_apply_flow.py",
                "tests/test_report_preference_apply_flow_current.py",
                "tests/test_report_preference_examples.py",
                "tests/test_apply_report_write_current.py",
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
        "report_name_prefix": "patch_134n_apply_report_write_hardening_exact_current_repair",
        "write_to_desktop": False,
    },
    "tags": ["self_hosted", "summary_integrity", "apply_flow", "report_write_hardening"],
    "notes": "Patch 134N repairs the exact current apply_patch report-write tail and adds a self-hosted docs-shape regression test.",
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")
print(str(manifest_path))