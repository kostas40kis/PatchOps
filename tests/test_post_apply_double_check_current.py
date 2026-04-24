from __future__ import annotations

import json
from pathlib import Path

from patchops.models import WriteRecord
from patchops.workflows import apply_patch as apply_module


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_manifest(tmp_path: Path, target_root: Path, *, patch_name: str = "post_apply_double_check") -> Path:
    report_dir = tmp_path / "reports"
    manifest_path = tmp_path / f"{patch_name}.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": patch_name,
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "files_to_write": [
                    {
                        "path": "docs/created_by_patchops.md",
                        "content": "created by patchops\n",
                    }
                ],
                "validation_commands": [],
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": patch_name,
                    "write_to_desktop": False,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return manifest_path


def test_apply_post_apply_double_check_passes_when_expected_file_exists(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    target_root.mkdir()
    manifest_path = _write_manifest(tmp_path, target_root, patch_name="double_check_pass")

    result = apply_module.apply_manifest(manifest_path, wrapper_project_root=REPO_ROOT)

    expected = target_root / "docs" / "created_by_patchops.md"
    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert expected.exists()
    assert "created by patchops" in expected.read_text(encoding="utf-8")


def test_apply_post_apply_double_check_fails_when_writer_reports_success_but_file_is_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    target_root = tmp_path / "target"
    target_root.mkdir()
    manifest_path = _write_manifest(tmp_path, target_root, patch_name="double_check_fail")

    def fake_write_files(*args, **kwargs):
        # Simulate a stale/lying writer result: it returns a write record but does not create the file.
        return [WriteRecord(path=target_root / "docs" / "created_by_patchops.md", encoding="utf-8")]

    monkeypatch.setattr(apply_module, "write_files", fake_write_files)

    result = apply_module.apply_manifest(manifest_path, wrapper_project_root=REPO_ROOT)

    assert result.exit_code == 1
    assert result.result_label == "FAIL"
    assert result.failure is not None
    assert result.failure.category == "wrapper_failure"
    assert "Post-apply double-check failed" in result.failure.message
    assert "MissingFileCount: 1" in (result.failure.details or "")
    assert "created_by_patchops.md" in (result.failure.details or "")
    assert result.report_path.exists()
    report_text = result.report_path.read_text(encoding="utf-8")
    assert "Post-apply double-check failed" in report_text
    assert "MissingFileCount: 1" in report_text


def test_post_apply_missing_path_helper_uses_manifest_files_to_write(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    target_root.mkdir()
    manifest_path = _write_manifest(tmp_path, target_root, patch_name="helper_shape")
    manifest = apply_module.load_manifest(manifest_path)

    missing = apply_module._patchops_223_post_apply_missing_paths(manifest, target_root)

    assert missing == [target_root / "docs" / "created_by_patchops.md"]
