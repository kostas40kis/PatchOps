from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import zipfile

from patchops.bundles.authoring import create_starter_bundle


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_bundle_doctor(bundle_path: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "bundle-doctor", str(bundle_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    return result.returncode, payload


def _stage_valid_content(bundle_root: Path) -> None:
    staged_file = bundle_root / "content" / "docs" / "note.md"
    staged_file.parent.mkdir(parents=True, exist_ok=True)
    staged_file.write_text("# doctor note\n", encoding="utf-8")

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


def test_bundle_doctor_cli_passes_for_valid_bundle_root(tmp_path: Path) -> None:
    bundle_root = tmp_path / "doctor_ok_bundle"
    create_starter_bundle(
        bundle_root,
        patch_name="doctor_ok_bundle",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
    )
    _stage_valid_content(bundle_root)

    exit_code, payload = _run_bundle_doctor(bundle_root)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["source_kind"] == "directory"
    assert payload["issue_count"] == 0
    assert payload["build_issue_count"] == 0
    assert "Build verification   : PASS" in payload["summary_text"]


def test_bundle_doctor_cli_reports_content_path_mismatch_for_bundle_root(tmp_path: Path) -> None:
    bundle_root = tmp_path / "doctor_bad_root"
    create_starter_bundle(
        bundle_root,
        patch_name="doctor_bad_root",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
    )
    real_file = bundle_root / "content" / "docs" / "real.md"
    real_file.parent.mkdir(parents=True, exist_ok=True)
    real_file.write_text("# real file\n", encoding="utf-8")

    manifest_path = bundle_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files_to_write"] = [
        {
            "path": "docs/missing.md",
            "content_path": "content/docs/missing.md",
            "encoding": "utf-8",
        }
    ]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    exit_code, payload = _run_bundle_doctor(bundle_root)

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["source_kind"] == "directory"
    assert any(issue["code"] == "content_path_missing" for issue in payload["issues"])
    assert payload["shape_issue_count"] >= 1
    assert "Overall result       : FAIL" in payload["summary_text"]


def test_bundle_doctor_cli_reports_export_shape_problems_for_zip_input(tmp_path: Path) -> None:
    bundle_root = tmp_path / "doctor_zip_root"
    create_starter_bundle(
        bundle_root,
        patch_name="doctor_zip_root",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
    )
    _stage_valid_content(bundle_root)

    bad_zip = tmp_path / "doctor_bad.zip"
    files = sorted(path for path in bundle_root.rglob("*") if path.is_file())
    with zipfile.ZipFile(bad_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(bundle_root).as_posix()
            archive.write(path, arcname=f"{bundle_root.name}/{bundle_root.name}/{relative}")

    exit_code, payload = _run_bundle_doctor(bad_zip)

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["source_kind"] == "zip"
    assert any(issue["code"] == "duplicate_nested_root" for issue in payload["issues"])
    assert payload["build_issue_count"] == 0
    assert "already-built zip" in payload["summary_text"]


def test_bundle_doctor_docs_describe_the_preferred_troubleshooting_entrypoint() -> None:
    standard_text = (PROJECT_ROOT / "docs" / "zip_bundle_standard.md").read_text(encoding="utf-8")
    template_text = (PROJECT_ROOT / "docs" / "bundle_authoring_template.md").read_text(encoding="utf-8")

    required_phrases = [
        "bundle-doctor",
        "preferred troubleshooting entrypoint",
        "shape validation",
        "build verification",
    ]

    for phrase in required_phrases:
        assert phrase in standard_text
        assert phrase in template_text
