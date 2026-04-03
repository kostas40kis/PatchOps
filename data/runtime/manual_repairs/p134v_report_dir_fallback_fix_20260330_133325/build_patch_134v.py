from __future__ import annotations

import json
import sys
from pathlib import Path

patch_root = Path(sys.argv[1]).resolve()
content_root = patch_root / "content"
(content_root / "patchops" / "workflows").mkdir(parents=True, exist_ok=True)
(content_root / "tests").mkdir(parents=True, exist_ok=True)

common_py = """from __future__ import annotations

from datetime import datetime
from hashlib import sha1
from pathlib import Path

from patchops.files.paths import ensure_directory


MAX_REPORT_PATH_LENGTH = 220
FALLBACK_REPORT_DIR_NAME = "patchops_reports"


def infer_workspace_root(target_project_root: Path) -> Path | None:
    return target_project_root.parent if target_project_root.parent != target_project_root else None


def default_report_directory() -> Path:
    return Path.home() / "Desktop"


def fallback_report_directory() -> Path:
    fallback_dir = default_report_directory() / FALLBACK_REPORT_DIR_NAME
    ensure_directory(fallback_dir)
    return fallback_dir


def build_report_path(prefix: str, patch_name: str, report_dir: Path) -> Path:
    safe_prefix = prefix.lower().replace(" ", "_")
    safe_patch = patch_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_directory(report_dir)

    name_token = safe_prefix if safe_prefix == safe_patch else f"{safe_prefix}_{safe_patch}"
    preferred = report_dir / f"{name_token}_{timestamp}.txt"
    if len(str(preferred)) <= MAX_REPORT_PATH_LENGTH:
        return preferred

    digest_source = f"{safe_prefix}|{safe_patch}|{report_dir}"
    digest = sha1(digest_source.encode("utf-8")).hexdigest()[:12]

    compact = report_dir / f"r_{digest}_{timestamp}.txt"
    if len(str(compact)) <= MAX_REPORT_PATH_LENGTH:
        return compact

    fallback_dir = fallback_report_directory()
    return fallback_dir / f"r_{digest}_{timestamp}.txt"
"""

test_py = """from __future__ import annotations

import json
import sys
from pathlib import Path

import patchops.workflows.common as common_module
from patchops.workflows.apply_patch import apply_manifest
from patchops.workflows.common import build_report_path


def _seed_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_self_hosted_state(wrapper_root: Path) -> None:
    _seed_text(wrapper_root / "docs" / "project_status.md", "old project status\\n")
    _seed_text(wrapper_root / "docs" / "patch_ledger.md", "old patch ledger\\n")
    _seed_text(wrapper_root / "docs" / "summary_integrity_repair_stream.md", "old stream\\n")
    _seed_text(wrapper_root / "handoff" / "current_handoff.md", "old handoff markdown\\n")
    _seed_text(wrapper_root / "handoff" / "current_handoff.json", "{}\\n")
    _seed_text(wrapper_root / "handoff" / "latest_report_copy.txt", "old latest report\\n")
    _seed_text(wrapper_root / "handoff" / "latest_report_index.json", "{}\\n")
    _seed_text(wrapper_root / "handoff" / "next_prompt.txt", "old next prompt\\n")


def _self_hosted_manifest(wrapper_root: Path, patch_name: str, report_dir: Path) -> dict:
    return {
        "manifest_version": "1",
        "patch_name": patch_name,
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
            "report_name_prefix": patch_name,
            "write_to_desktop": False,
        },
        "tags": ["test", "summary_integrity", "current", "long_report_path"],
        "notes": "Temporary manifest used by report-path current tests.",
    }


def test_build_report_path_keeps_short_custom_directory(tmp_path: Path) -> None:
    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    report_dir = tmp_path / "data" / "runtime" / "manual_repairs" / "short_case" / "inner_reports"

    report_path = build_report_path(token, token, report_dir)

    assert report_path.parent == report_dir
    assert report_dir.exists()
    assert len(str(report_path)) <= 220
    report_path.write_text("ok\\n", encoding="utf-8")
    assert report_path.exists()


def test_build_report_path_falls_back_to_short_directory_when_custom_dir_is_too_long(tmp_path: Path, monkeypatch) -> None:
    fake_desktop = tmp_path / "desktop"
    monkeypatch.setattr(common_module, "default_report_directory", lambda: fake_desktop)

    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    report_dir = (
        tmp_path
        / "data"
        / "runtime"
        / "manual_repairs"
        / ("very_long_segment_" * 8)
        / ("even_longer_nested_segment_" * 8)
        / "inner_reports"
    )

    minimal_candidate = report_dir / "r_123456789012_20260330_123944.txt"
    assert len(str(minimal_candidate)) > 220

    report_path = common_module.build_report_path(token, token, report_dir)

    assert report_path.parent == fake_desktop / "patchops_reports"
    assert report_path.name.startswith("r_")
    assert len(str(report_path)) <= 220
    report_path.write_text("ok\\n", encoding="utf-8")
    assert report_path.exists()


def test_apply_manifest_falls_back_to_short_directory_for_windows_hostile_shape(tmp_path: Path, monkeypatch) -> None:
    fake_desktop = tmp_path / "desktop"
    monkeypatch.setattr(common_module, "default_report_directory", lambda: fake_desktop)

    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir(parents=True, exist_ok=True)
    _seed_self_hosted_state(wrapper_root)

    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    report_dir = (
        wrapper_root
        / "data"
        / "runtime"
        / "manual_repairs"
        / ("very_long_segment_" * 8)
        / ("even_longer_nested_segment_" * 8)
        / "inner_reports"
    )

    minimal_candidate = report_dir / "r_123456789012_20260330_123944.txt"
    assert len(str(minimal_candidate)) > 220

    manifest_data = _self_hosted_manifest(wrapper_root, token, report_dir)
    patch_root = wrapper_root / "data" / "runtime" / "manual_repairs" / "fallback_proof_patch"
    patch_root.mkdir(parents=True, exist_ok=True)

    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    expected_dir = fake_desktop / "patchops_reports"

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert result.report_path.exists()
    assert result.report_path.parent == expected_dir
    assert result.report_path.name.startswith("r_")
    assert len(str(result.report_path)) <= 220


def test_apply_manifest_keeps_short_custom_directory_when_safe(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir(parents=True, exist_ok=True)
    _seed_self_hosted_state(wrapper_root)

    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    report_dir = wrapper_root / "data" / "runtime" / "manual_repairs" / "short_case" / "inner_reports"
    patch_root = wrapper_root / "data" / "runtime" / "manual_repairs" / "short_case_patch"
    patch_root.mkdir(parents=True, exist_ok=True)

    manifest_data = _self_hosted_manifest(wrapper_root, token, report_dir)
    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert result.report_path.exists()
    assert result.report_path.parent == report_dir
    assert len(str(result.report_path)) <= 220
"""

manifest = {
    "manifest_version": "1",
    "patch_name": "p134v_report_dir_fallback_fix",
    "active_profile": "generic_python",
    "target_project_root": "C:/dev/patchops",
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
            "name": "report_path_fallback_pytest",
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
        "report_dir": str((patch_root / "inner_reports")).replace("\\\\", "/"),
        "report_name_prefix": "p134v",
        "write_to_desktop": False,
    },
    "tags": [
        "self_hosted",
        "summary_integrity",
        "report_path",
        "fallback_fix",
    ],
    "notes": "Patch 134V adds a Windows-safe fallback report directory when a long self-hosted custom report_dir still yields an over-budget full path.",
}

(content_root / "patchops" / "workflows" / "common.py").write_text(common_py, encoding="utf-8")
(content_root / "tests" / "test_report_path_current.py").write_text(test_py, encoding="utf-8")
manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")

print(str(manifest_path))