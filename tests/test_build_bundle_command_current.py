from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import zipfile

from patchops.bundles.authoring import build_bundle_zip, create_starter_bundle
from patchops.bundles.shape_validation import validate_bundle_zip


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _stage_minimal_content(bundle_root: Path) -> None:
    staged_file = bundle_root / "content" / "docs" / "note.md"
    staged_file.parent.mkdir(parents=True, exist_ok=True)
    staged_file.write_text("# starter note\n", encoding="utf-8")

    manifest_path = bundle_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files_to_write"] = [
        {
            "path": "docs/note.md",
            "content_path": "content/docs/note.md",
            "encoding": "utf-8",
        }
    ]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _run_make_bundle(bundle_root: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "make-bundle",
            str(bundle_root),
            "--mode",
            "apply",
            "--patch-name",
            "build_bundle_starter",
            "--target-project",
            "patchops",
            "--target-root",
            r"C:\dev\patchops",
            "--wrapper-root",
            r"C:\dev\patchops",
            "--profile",
            "generic_python",
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_build_bundle_zip_helper_creates_deterministic_one_root_archive(tmp_path: Path) -> None:
    bundle_root = tmp_path / "deterministic_bundle"
    create_starter_bundle(
        bundle_root,
        patch_name="deterministic_bundle",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
    )
    _stage_minimal_content(bundle_root)

    output_a = tmp_path / "deterministic_a.zip"
    output_b = tmp_path / "deterministic_b.zip"

    result_a = build_bundle_zip(bundle_root, output_a)
    result_b = build_bundle_zip(bundle_root, output_b)

    assert result_a.ok is True
    assert result_b.ok is True
    assert result_a.member_count == result_b.member_count
    assert output_a.read_bytes() == output_b.read_bytes()

    with zipfile.ZipFile(output_a, "r") as archive:
        member_names = archive.namelist()

    assert member_names == sorted(member_names)
    assert all(name.startswith(f"{bundle_root.name}/") for name in member_names)
    assert not any(name.startswith(f"{bundle_root.name}/{bundle_root.name}/") for name in member_names)

    shape = validate_bundle_zip(output_a)
    assert shape.ok is True
    assert shape.root_folder_name == bundle_root.name


def test_build_bundle_cli_builds_zip_from_checked_bundle_root(tmp_path: Path) -> None:
    bundle_root = tmp_path / "cli_bundle"
    _run_make_bundle(bundle_root)
    _stage_minimal_content(bundle_root)
    output_zip = tmp_path / "cli_bundle.zip"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "build-bundle",
            str(bundle_root),
            "--output",
            str(output_zip),
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["issue_count"] == 0
    assert payload["root_folder_name"] == bundle_root.name
    assert payload["output_zip"] == str(output_zip.resolve())
    assert output_zip.is_file()

    shape = validate_bundle_zip(output_zip)
    assert shape.ok is True
    assert shape.root_folder_name == bundle_root.name


def test_build_bundle_cli_rejects_duplicate_nested_root_before_zip_creation(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bad_bundle"
    _run_make_bundle(bundle_root)
    _stage_minimal_content(bundle_root)
    (bundle_root / bundle_root.name).mkdir(parents=True, exist_ok=True)
    output_zip = tmp_path / "bad_bundle.zip"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "build-bundle",
            str(bundle_root),
            "--output",
            str(output_zip),
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any(issue["code"] == "duplicate_nested_root" for issue in payload["issues"])
    assert not output_zip.exists()
