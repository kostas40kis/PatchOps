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

if "WINDOWS_SAFE_REPORT_PATH_LIMIT = 220" not in common_text:
    marker = "from patchops.files.paths import ensure_directory\n\n\n"
    insert = "from patchops.files.paths import ensure_directory\n\n\nWINDOWS_SAFE_REPORT_PATH_LIMIT = 220\n\n\n"
    if marker not in common_text:
        raise SystemExit("Could not find common.py constant insertion marker.")
    common_text = common_text.replace(marker, insert, 1)

old_block = """def build_report_path(prefix: str, patch_name: str, report_dir: Path) -> Path:
    safe_prefix = prefix.lower().replace(" ", "_")
    safe_patch = patch_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_directory(report_dir)

    name_token = safe_prefix if safe_prefix == safe_patch else f"{safe_prefix}_{safe_patch}"
    preferred = report_dir / f"{name_token}_{timestamp}.txt"

    if len(str(preferred)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return preferred

    digest_source = f"{safe_prefix}|{safe_patch}|{report_dir}"
    digest = sha1(digest_source.encode("utf-8")).hexdigest()[:12]
    compact_base = safe_patch[:40] if safe_patch else "report"
    compact = report_dir / f"{compact_base}_{digest}_{timestamp}.txt"

    if len(str(compact)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return compact

    very_compact = report_dir / f"r_{digest}_{timestamp}.txt"
    if len(str(very_compact)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return very_compact

    fallback_dir = default_report_directory() / "patchops_reports"
    ensure_directory(fallback_dir)

    desktop_name = f"r_{digest}_{timestamp}.txt"
    desktop_path = fallback_dir / desktop_name
    if len(str(desktop_path)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return desktop_path

    return default_report_directory() / f"r_{digest}_{timestamp}.txt"
"""

new_block = """def build_report_path(prefix: str, patch_name: str, report_dir: Path) -> Path:
    safe_prefix = prefix.lower().replace(" ", "_")
    safe_patch = patch_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_directory(report_dir)

    name_token = safe_prefix if safe_prefix == safe_patch else f"{safe_prefix}_{safe_patch}"
    preferred = report_dir / f"{name_token}_{timestamp}.txt"

    if len(str(preferred)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return preferred

    digest_source = f"{safe_prefix}|{safe_patch}|{report_dir}"
    digest = sha1(digest_source.encode("utf-8")).hexdigest()[:12]
    compact_base = safe_patch[:40] if safe_patch else "report"
    compact = report_dir / f"{compact_base}_{digest}_{timestamp}.txt"

    if len(str(compact)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return compact

    very_compact = report_dir / f"r_{digest}_{timestamp}.txt"
    if len(str(very_compact)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return very_compact

    fallback_dir = default_report_directory() / "patchops_reports"
    ensure_directory(fallback_dir)

    desktop_name = f"r_{digest}_{timestamp}.txt"
    desktop_path = fallback_dir / desktop_name
    if len(str(desktop_path)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return desktop_path

    return default_report_directory() / f"r_{digest}_{timestamp}.txt"
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
from patchops.workflows.common import build_report_path, default_report_directory


def _seed_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_path_falls_back_from_long_current_shape(tmp_path: Path) -> None:
    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    report_dir = tmp_path / "data" / "runtime" / "manual_repairs" / (token + "_20260330_123944") / "inner_reports"

    report_path = build_report_path(token, token, report_dir)

    assert report_path.exists() is False
    assert len(str(report_path)) <= 220
    assert report_path.parent.exists()

    if report_path.parent != report_dir:
        assert report_path.parent == default_report_directory() / "patchops_reports"

    report_path.write_text("ok\\n", encoding="utf-8")
    assert report_path.exists()


def test_apply_manifest_falls_back_from_long_self_hosted_report_dir(tmp_path: Path) -> None:
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
        "notes": "Temporary manifest used by test_apply_manifest_falls_back_from_long_self_hosted_report_dir.",
    }

    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert result.report_path.exists()
    assert len(str(result.report_path)) <= 220

    if result.report_path.parent != report_dir:
        assert result.report_path.parent == default_report_directory() / "patchops_reports"

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "SUMMARY" in report_text
    assert "ExitCode : 0" in report_text
    assert "Result   : PASS" in report_text
'''
(content_root / "tests" / "test_report_path_current.py").write_text(test_text, encoding="utf-8")

manifest = {
    "manifest_version": "1",
    "patch_name": "p134u_report_dir_fallback_manifest_fix",
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
            "name": "report_dir_fallback_pytest",
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
        "report_name_prefix": "p134u",
        "write_to_desktop": False,
    },
    "tags": ["self_hosted", "summary_integrity", "report_dir", "manifest_fix"],
    "notes": "Patch 134U keeps the report-directory fallback payload and repairs the manifest authoring shape only.",
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(str(manifest_path))