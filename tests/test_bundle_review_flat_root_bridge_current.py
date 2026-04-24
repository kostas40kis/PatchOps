from __future__ import annotations

import json
import zipfile
from pathlib import Path

import patchops.bundle_review as bundle_review


def _write_flat_bundle_zip(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            "manifest.json",
            json.dumps(
                {
                    "manifest_version": "1",
                    "patch_name": "flat_root_review",
                    "active_profile": "generic_python",
                    "target_project_root": ".",
                    "backup_files": [],
                    "files_to_write": [],
                    "validation_commands": [],
                }
            ),
        )
        zf.writestr(
            "bundle_meta.json",
            json.dumps(
                {
                    "bundle_schema_version": 1,
                    "patch_name": "flat_root_review",
                    "bundle_mode": "apply",
                    "recommended_profile": "generic_python",
                    "target_project": "patchops",
                    "target_project_root": ".",
                    "content_root": "content",
                    "manifest_path": "manifest.json",
                    "launcher_path": "run_with_patchops.ps1",
                }
            ),
        )
        zf.writestr("README.txt", "flat root bundle\n")
        zf.writestr("run_with_patchops.ps1", "param()\n")
        zf.writestr("content/docs/example.md", "example\n")


def _write_content_only_zip(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("content/docs/example.md", "example\n")


def test_bundle_review_accepts_flat_root_zip_for_run_package_preflight(tmp_path: Path) -> None:
    bundle_zip = tmp_path / "flat_bundle.zip"
    _write_flat_bundle_zip(bundle_zip)

    payload = bundle_review.inspect_bundle_payload(bundle_zip, profile="generic_python")

    assert payload["ok"] is True
    assert payload["zip_layout"] == "flat_root"
    assert payload["root_folder"] == "."
    assert payload["manifest_path"] == "manifest.json"
    assert payload["bundle_meta_path"] == "bundle_meta.json"
    assert payload["readme_path"] == "README.txt"
    assert payload["content_prefix"] == "content/"
    assert payload["launcher_path"] == "run_with_patchops.ps1"
    assert payload["launcher_status"] == "safe"
    assert payload["launcher_issue_codes"] == []
    assert payload["issues"] == []


def test_bundle_review_still_rejects_content_only_zip(tmp_path: Path) -> None:
    bundle_zip = tmp_path / "content_only.zip"
    _write_content_only_zip(bundle_zip)

    payload = bundle_review.inspect_bundle_payload(bundle_zip, profile="generic_python")

    assert payload["ok"] is False
    assert payload["launcher_status"] == "reject"
