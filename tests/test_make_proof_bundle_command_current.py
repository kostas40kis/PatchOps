from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.bundles.authoring import build_bundle_zip, resolve_bundle_workflow_mode
from patchops.bundles.shape_validation import validate_bundle_directory, validate_bundle_zip


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_make_proof_bundle(bundle_root: Path, *, kind: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "make-proof-bundle",
            str(bundle_root),
            "--kind",
            kind,
            "--patch-name",
            f"proof_{kind.replace('-', '_')}_bundle",
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
    return json.loads(result.stdout)


def test_make_proof_bundle_cli_generates_apply_proof_bundle(tmp_path: Path) -> None:
    bundle_root = tmp_path / "proof_apply_bundle"
    payload = _run_make_proof_bundle(bundle_root, kind="apply")

    assert payload["ok"] is True
    assert payload["kind"] == "apply"
    assert payload["bundle_mode"] == "apply"
    assert payload["intended_surface"] == "run-package"
    assert payload["expected_exit_code"] == 0

    shape = validate_bundle_directory(bundle_root)
    assert shape.ok is True
    assert resolve_bundle_workflow_mode(bundle_root) == "apply"

    output_zip = tmp_path / "proof_apply_bundle.zip"
    build_result = build_bundle_zip(bundle_root, output_zip)
    assert build_result.ok is True

    zip_shape = validate_bundle_zip(output_zip)
    assert zip_shape.ok is True
    assert zip_shape.root_folder_name == bundle_root.name


def test_make_proof_bundle_cli_generates_verify_proof_bundle(tmp_path: Path) -> None:
    bundle_root = tmp_path / "proof_verify_bundle"
    payload = _run_make_proof_bundle(bundle_root, kind="verify")

    assert payload["ok"] is True
    assert payload["kind"] == "verify"
    assert payload["bundle_mode"] == "verify"
    assert payload["intended_surface"] == "run-package"
    assert payload["expected_exit_code"] == 0

    shape = validate_bundle_directory(bundle_root)
    assert shape.ok is True
    assert resolve_bundle_workflow_mode(bundle_root) == "verify"

    output_zip = tmp_path / "proof_verify_bundle.zip"
    build_result = build_bundle_zip(bundle_root, output_zip)
    assert build_result.ok is True

    zip_shape = validate_bundle_zip(output_zip)
    assert zip_shape.ok is True
    assert zip_shape.root_folder_name == bundle_root.name


def test_make_proof_bundle_cli_generates_launcher_risk_proof_bundle(tmp_path: Path) -> None:
    bundle_root = tmp_path / "proof_launcher_risk_bundle"
    payload = _run_make_proof_bundle(bundle_root, kind="launcher-risk")

    assert payload["ok"] is True
    assert payload["kind"] == "launcher-risk"
    assert payload["bundle_mode"] == "apply"
    assert payload["intended_surface"] == "bundle-doctor"
    assert payload["expected_exit_code"] == 1

    result = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "bundle-doctor", str(bundle_root)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr or result.stdout
    doctor_payload = json.loads(result.stdout)
    assert doctor_payload["ok"] is False
    assert doctor_payload["launcher_issue_count"] >= 1
    combined = "\n".join(issue["message"] for issue in doctor_payload["issues"]).lower()
    assert "json" in combined or "convertfrom-json" in combined
    assert "python" in combined or "inline" in combined
