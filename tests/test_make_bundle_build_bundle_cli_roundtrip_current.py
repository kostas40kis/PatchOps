from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "patchops.cli", *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_make_bundle_then_build_bundle_then_review_zip_stays_green(tmp_path: Path) -> None:
    bundle_root = tmp_path / "starter_bundle"
    zip_path = tmp_path / "starter_bundle.zip"

    make_result = _run_cli(
        "make-bundle",
        str(bundle_root),
        "--mode",
        "apply",
        "--patch-name",
        "patch_demo_bundle",
        "--target-project",
        "trader",
        "--target-root",
        r"C:\dev\trader",
        "--profile",
        "trader",
        "--wrapper-root",
        r"C:\dev\patchops",
    )
    assert make_result.returncode == 0, make_result.stderr
    assert (bundle_root / "manifest.json").exists()
    assert (bundle_root / "bundle_meta.json").exists()
    assert (bundle_root / "README.txt").exists()
    assert (bundle_root / "run_with_patchops.ps1").exists()
    assert (bundle_root / "content").exists()

    build_result = _run_cli(
        "build-bundle",
        str(bundle_root),
        "--output",
        str(zip_path),
    )
    assert build_result.returncode == 0, build_result.stderr
    assert zip_path.exists()

    check_result = _run_cli("check-bundle", str(zip_path))
    inspect_result = _run_cli("inspect-bundle", str(zip_path))
    plan_result = _run_cli("plan-bundle", str(zip_path))
    doctor_result = _run_cli("bundle-doctor", str(zip_path))

    assert check_result.returncode == 0, check_result.stderr
    assert inspect_result.returncode == 0, inspect_result.stderr
    assert plan_result.returncode == 0, plan_result.stderr
    assert doctor_result.returncode == 0, doctor_result.stderr

    check_payload = json.loads(check_result.stdout)
    inspect_payload = json.loads(inspect_result.stdout)
    plan_payload = json.loads(plan_result.stdout)
    doctor_payload = json.loads(doctor_result.stdout)

    assert check_payload["ok"] is True
    assert inspect_payload["ok"] is True
    assert plan_payload["ok"] is True
    assert doctor_payload["ok"] is True

    assert check_payload["launcher_status"] == "safe"
    assert inspect_payload["launcher_status"] == "safe"
    assert plan_payload["launcher_status"] == "safe"
    assert doctor_payload["launcher_issue_count"] == 0
    assert doctor_payload["issue_count"] == 0


def test_make_bundle_verify_mode_then_build_bundle_keeps_verify_metadata(tmp_path: Path) -> None:
    bundle_root = tmp_path / "verify_bundle"
    zip_path = tmp_path / "verify_bundle.zip"

    make_result = _run_cli(
        "make-bundle",
        str(bundle_root),
        "--mode",
        "verify",
        "--patch-name",
        "patch_verify_bundle",
        "--target-project",
        "trader",
        "--target-root",
        r"C:\dev\trader",
        "--profile",
        "trader",
        "--wrapper-root",
        r"C:\dev\patchops",
    )
    assert make_result.returncode == 0, make_result.stderr

    manifest = json.loads((bundle_root / "manifest.json").read_text(encoding="utf-8"))
    bundle_meta = json.loads((bundle_root / "bundle_meta.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "verify"
    assert bundle_meta["mode"] == "verify"

    build_result = _run_cli(
        "build-bundle",
        str(bundle_root),
        "--output",
        str(zip_path),
    )
    assert build_result.returncode == 0, build_result.stderr
    assert zip_path.exists()

    inspect_result = _run_cli("inspect-bundle", str(zip_path))
    assert inspect_result.returncode == 0, inspect_result.stderr
    payload = json.loads(inspect_result.stdout)
    assert payload["ok"] is True
    assert payload["launcher_status"] == "safe"