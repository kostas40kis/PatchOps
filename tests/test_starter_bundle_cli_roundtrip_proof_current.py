from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.bundles.authoring import build_bundle_zip, create_starter_bundle

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "patchops.cli", *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_starter_bundle_zip_stays_green_across_check_inspect_plan(tmp_path: Path) -> None:
    bundle_root = tmp_path / "starter_bundle"
    result = create_starter_bundle(
        bundle_root,
        patch_name="patch_demo_bundle",
        target_project="trader",
        target_project_root=r"C:\dev\trader",
        wrapper_project_root=r"C:\dev\patchops",
        recommended_profile="trader",
        mode="apply",
    )

    zip_path = tmp_path / "starter_bundle.zip"
    build_result = build_bundle_zip(bundle_root, zip_path)
    assert build_result.ok is True
    assert zip_path.exists()

    check_result = _run_cli("check-bundle", str(zip_path))
    inspect_result = _run_cli("inspect-bundle", str(zip_path))
    plan_result = _run_cli("plan-bundle", str(zip_path))

    assert check_result.returncode == 0, check_result.stderr
    assert inspect_result.returncode == 0, inspect_result.stderr
    assert plan_result.returncode == 0, plan_result.stderr

    check_payload = json.loads(check_result.stdout)
    inspect_payload = json.loads(inspect_result.stdout)
    plan_payload = json.loads(plan_result.stdout)

    assert check_payload["ok"] is True
    assert inspect_payload["ok"] is True
    assert plan_payload["ok"] is True

    assert check_payload["launcher_status"] == "safe"
    assert inspect_payload["launcher_status"] == "safe"
    assert plan_payload["launcher_status"] == "safe"

    assert check_payload["launcher_issue_codes"] == []
    assert inspect_payload["launcher_issue_codes"] == []
    assert plan_payload["launcher_issue_codes"] == []

    assert "run_with_patchops.ps1" in check_payload["launcher_paths"][0]
    assert "run_with_patchops.ps1" in inspect_payload["launchers"][0]
    assert "run_with_patchops.ps1" in plan_payload["selected_launcher"]


def test_starter_bundle_zip_bundle_doctor_stays_green(tmp_path: Path) -> None:
    bundle_root = tmp_path / "starter_bundle"
    create_starter_bundle(
        bundle_root,
        patch_name="patch_demo_bundle",
        target_project="trader",
        target_project_root=r"C:\dev\trader",
        wrapper_project_root=r"C:\dev\patchops",
        recommended_profile="trader",
        mode="apply",
    )

    zip_path = tmp_path / "starter_bundle.zip"
    build_result = build_bundle_zip(bundle_root, zip_path)
    assert build_result.ok is True

    doctor_result = _run_cli("bundle-doctor", str(zip_path))
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["ok"] is True
    assert payload["launcher_issue_count"] == 0
    assert payload["issue_count"] == 0