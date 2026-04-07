from __future__ import annotations

import json
from pathlib import Path
import sys
import zipfile

from patchops.bundles import BundleVerifyResult, verify_bundle_archive, verify_bundle_zip


def _build_bundle_zip(tmp_path: Path, *, patch_name: str = "patch_12_demo") -> tuple[Path, Path]:
    target_root = tmp_path / "target_project"
    report_dir = tmp_path / "reports"
    target_root.mkdir()
    report_dir.mkdir()

    bundle_root = tmp_path / patch_name
    content_root = bundle_root / "content"
    docs_root = content_root / "docs"
    docs_root.mkdir(parents=True)

    (bundle_root / "run_with_patchops.ps1").write_text(
        "& { py -m patchops.cli verify .\\manifest.json }\n",
        encoding="utf-8",
    )
    (docs_root / "note.md").write_text("bundle verify content\n", encoding="utf-8")

    metadata = {
        "bundle_schema_version": 1,
        "patch_name": patch_name,
        "target_project": "patchops",
        "recommended_profile": "generic_python",
        "target_project_root": str(target_root),
        "wrapper_project_root": "C:\\dev\\patchops",
        "content_root": "content",
        "manifest_path": "manifest.json",
        "launcher_path": "run_with_patchops.ps1",
    }
    (bundle_root / "bundle_meta.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "manifest_version": 1,
        "patch_name": patch_name,
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "files_to_write": [
            {
                "path": "notes.txt",
                "content_path": "content/docs/note.md",
            }
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
        "report_preferences": {
            "report_dir": str(report_dir),
            "report_name_prefix": patch_name,
            "write_to_desktop": False,
        },
    }
    (bundle_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    zip_path = tmp_path / f"{patch_name}.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in bundle_root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_root))
    return zip_path, target_root


def test_bundle_verify_helper_exports_are_available() -> None:
    assert BundleVerifyResult is not None
    assert verify_bundle_zip is not None
    assert verify_bundle_archive is verify_bundle_zip


def test_verify_bundle_zip_runs_verify_only_without_rewriting_target_files(tmp_path: Path) -> None:
    zip_path, target_root = _build_bundle_zip(tmp_path)
    target_file = target_root / "notes.txt"
    target_file.write_text("already present\n", encoding="utf-8")

    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = verify_bundle_zip(zip_path, wrapper_root, timestamp_token="20260404_230400")

    assert result.is_valid_bundle is True
    assert result.run_executed is True
    assert result.workflow_result is not None
    assert result.workflow_result.exit_code == 0
    assert result.workflow_result.result_label == "PASS"

    assert target_file.read_text(encoding="utf-8") == "already present\n"

    assert result.report_path is not None
    report_text = result.report_path.read_text(encoding="utf-8")
    assert "PATCHOPS VERIFY_ONLY" in report_text
    assert "ExitCode : 0" in report_text
    assert "Result   : PASS" in report_text


def test_verify_bundle_zip_prepares_manifest_with_absolute_extracted_content_paths(tmp_path: Path) -> None:
    zip_path, target_root = _build_bundle_zip(tmp_path, patch_name="patch_12_absolute")
    (target_root / "notes.txt").write_text("already present\n", encoding="utf-8")

    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = verify_bundle_zip(zip_path, wrapper_root, timestamp_token="20260404_230401")

    assert result.prepared_manifest_path is not None
    manifest_data = json.loads(result.prepared_manifest_path.read_text(encoding="utf-8"))
    content_path = manifest_data["files_to_write"][0]["content_path"]

    normalized_content_path = content_path.replace("\\", "/")
    assert Path(content_path).is_absolute()
    assert "extracted_bundle" in normalized_content_path
    assert normalized_content_path.endswith("content/docs/note.md")


def test_verify_bundle_zip_returns_without_running_when_bundle_is_invalid(tmp_path: Path) -> None:
    broken_zip = tmp_path / "broken_bundle.zip"
    with zipfile.ZipFile(broken_zip, "w") as archive:
        archive.writestr("bundle_meta.json", "{}\n")

    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = verify_bundle_zip(broken_zip, wrapper_root, timestamp_token="20260404_230402")

    assert result.is_valid_bundle is False
    assert result.run_executed is False
    assert result.prepared_manifest_path is None
    assert result.workflow_result is None
