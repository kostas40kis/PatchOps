from __future__ import annotations

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
    _seed_text(wrapper_root / "docs" / "project_status.md", "old project status\n")
    _seed_text(wrapper_root / "docs" / "patch_ledger.md", "old patch ledger\n")
    _seed_text(wrapper_root / "docs" / "summary_integrity_repair_stream.md", "old stream\n")
    _seed_text(wrapper_root / "handoff" / "current_handoff.md", "old handoff markdown\n")
    _seed_text(wrapper_root / "handoff" / "current_handoff.json", "{}\n")
    _seed_text(wrapper_root / "handoff" / "latest_report_copy.txt", "old latest report\n")
    _seed_text(wrapper_root / "handoff" / "latest_report_index.json", "{}\n")
    _seed_text(wrapper_root / "handoff" / "next_prompt.txt", "old next prompt\n")


def _self_hosted_manifest(wrapper_root: Path, patch_name: str, report_dir: Path) -> dict:
    return {
        "manifest_version": "1",
        "patch_name": patch_name,
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace("\", "/"),
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
                "content": "new project status\n",
                "content_path": None,
                "encoding": "utf-8",
            },
            {
                "path": "docs/patch_ledger.md",
                "content": "new patch ledger\n",
                "content_path": None,
                "encoding": "utf-8",
            },
            {
                "path": "docs/summary_integrity_repair_stream.md",
                "content": "new stream\n",
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
            "report_dir": str(report_dir).replace("\", "/"),
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
    report_path.write_text("ok\n", encoding="utf-8")
    assert report_path.exists()


def test_build_report_path_keeps_compact_path_in_custom_directory_when_that_is_enough(tmp_path: Path) -> None:
    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    report_dir = tmp_path / "data" / "runtime" / "manual_repairs" / ("segment_" * 6) / "inner_reports"

    report_path = build_report_path(token, token, report_dir)

    assert report_path.parent == report_dir
    assert len(str(report_path)) <= 220
    assert report_path.name.startswith("patch_134p_summary_integrity_final_proof_") or report_path.name.startswith("r_")


def test_build_report_path_falls_back_to_short_directory_when_custom_dir_is_still_too_long(tmp_path: Path, monkeypatch) -> None:
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
    report_path.write_text("ok\n", encoding="utf-8")
    assert report_path.exists()


def test_apply_manifest_uses_compact_report_name_for_long_self_hosted_shape(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir(parents=True, exist_ok=True)
    _seed_self_hosted_state(wrapper_root)

    token = "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry"
    patch_root = wrapper_root / "data" / "runtime" / "manual_repairs" / (token + "_20260330_123944")
    report_dir = patch_root / "inner_reports"
    patch_root.mkdir(parents=True, exist_ok=True)

    manifest_data = _self_hosted_manifest(wrapper_root, token, report_dir)
    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert result.report_path.exists()
    assert result.report_path.parent == report_dir
    assert len(str(result.report_path)) <= 220


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
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    expected_dir = fake_desktop / "patchops_reports"

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert result.report_path.exists()
    assert result.report_path.parent == expected_dir
    assert result.report_path.name.startswith("r_")
    assert len(str(result.report_path)) <= 220
