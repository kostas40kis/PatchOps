from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.bundles.authoring import create_proof_bundle, build_bundle_zip

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "patchops.cli", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _load_json(stdout: str, stderr: str) -> dict:
    text = stdout.strip()
    assert text, stderr
    return json.loads(text)


def _assert_manifest_review_surfaces(manifest_path: Path) -> None:
    check_proc = _run_cli(["check", str(manifest_path)])
    assert check_proc.returncode == 0, check_proc.stdout + "\n" + check_proc.stderr
    check_payload = _load_json(check_proc.stdout, check_proc.stderr)
    assert check_payload["ok"] is True

    inspect_proc = _run_cli(["inspect", str(manifest_path)])
    assert inspect_proc.returncode == 0, inspect_proc.stdout + "\n" + inspect_proc.stderr
    inspect_payload = _load_json(inspect_proc.stdout, inspect_proc.stderr)
    assert inspect_payload["patch_name"].endswith("_proof_bundle")
    assert inspect_payload["manifest_version"] == "1"

    plan_proc = _run_cli(["plan", str(manifest_path)])
    assert plan_proc.returncode == 0, plan_proc.stdout + "\n" + plan_proc.stderr
    plan_payload = _load_json(plan_proc.stdout, plan_proc.stderr)
    assert plan_payload["patch_name"].endswith("_proof_bundle")


def _assert_bundle_root_review_surfaces(bundle_root: Path) -> None:
    doctor_proc = _run_cli(["bundle-doctor", str(bundle_root)])
    assert doctor_proc.returncode == 0, doctor_proc.stdout + "\n" + doctor_proc.stderr
    doctor_payload = _load_json(doctor_proc.stdout, doctor_proc.stderr)
    assert doctor_payload["ok"] is True

    check_proc = _run_cli(["check-bundle", str(bundle_root)])
    assert check_proc.returncode == 0, check_proc.stdout + "\n" + check_proc.stderr
    check_payload = _load_json(check_proc.stdout, check_proc.stderr)
    assert check_payload["ok"] is True


def _assert_built_zip_review_surfaces(built_zip: Path) -> None:
    for command in ("inspect-bundle", "plan-bundle"):
        proc = _run_cli([command, str(built_zip)])
        assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
        payload = _load_json(proc.stdout, proc.stderr)
        assert isinstance(payload, dict)
        if "ok" in payload:
            assert payload["ok"] is True


def test_release_gate_covers_apply_proof_bundle_across_manifest_and_bundle_surfaces(tmp_path: Path) -> None:
    proof = create_proof_bundle(
        tmp_path / "apply_proof_bundle",
        kind="apply",
        patch_name="apply_proof_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )

    assert proof.ok is True
    _assert_manifest_review_surfaces(proof.bundle_root / "manifest.json")
    _assert_bundle_root_review_surfaces(proof.bundle_root)

    built = build_bundle_zip(proof.bundle_root, tmp_path / "apply_proof_bundle.zip")
    assert built.ok is True
    _assert_built_zip_review_surfaces(built.output_zip)


def test_release_gate_covers_verify_proof_bundle_across_manifest_and_bundle_surfaces(tmp_path: Path) -> None:
    proof = create_proof_bundle(
        tmp_path / "verify_proof_bundle",
        kind="verify",
        patch_name="verify_proof_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )

    assert proof.ok is True
    _assert_manifest_review_surfaces(proof.bundle_root / "manifest.json")
    _assert_bundle_root_review_surfaces(proof.bundle_root)

    built = build_bundle_zip(proof.bundle_root, tmp_path / "verify_proof_bundle.zip")
    assert built.ok is True
    _assert_built_zip_review_surfaces(built.output_zip)


def test_bundle_regression_gate_doc_describes_both_worlds() -> None:
    text = (PROJECT_ROOT / "docs" / "bundle_regression_gate.md").read_text(encoding="utf-8")
    required = [
        "release gate",
        "regression matrix",
        "classic manifest review surfaces",
        "bundle review/build surfaces",
        "check",
        "inspect",
        "plan",
        "bundle-doctor",
        "check-bundle",
        "inspect-bundle",
        "plan-bundle",
        "build-bundle",
        "continue patch by patch from evidence",
    ]
    for phrase in required:
        assert phrase in text
