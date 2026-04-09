\
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.bundles.authoring import build_bundle_zip, create_proof_bundle


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
    payload = stdout.strip()
    assert payload, stderr
    return json.loads(payload)


def test_post_build_smoke_gate_for_apply_proof_bundle(tmp_path: Path) -> None:
    proof = create_proof_bundle(
        tmp_path / "apply_proof_bundle",
        kind="apply",
        patch_name="apply_proof_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )
    assert proof.ok is True

    doctor = _run_cli(["bundle-doctor", str(proof.bundle_root)])
    assert doctor.returncode == 0, doctor.stdout + "\n" + doctor.stderr
    doctor_payload = _load_json(doctor.stdout, doctor.stderr)
    assert doctor_payload["ok"] is True

    built = build_bundle_zip(proof.bundle_root, tmp_path / "apply_proof_bundle.zip")
    assert built.ok is True

    inspect_proc = _run_cli(["inspect-bundle", str(built.output_zip)])
    assert inspect_proc.returncode == 0, inspect_proc.stdout + "\n" + inspect_proc.stderr
    inspect_payload = _load_json(inspect_proc.stdout, inspect_proc.stderr)
    assert inspect_payload["ok"] is True
    assert inspect_payload["launcher_status"] == "safe"

    plan_proc = _run_cli(["plan-bundle", str(built.output_zip)])
    assert plan_proc.returncode == 0, plan_proc.stdout + "\n" + plan_proc.stderr
    plan_payload = _load_json(plan_proc.stdout, plan_proc.stderr)
    assert plan_payload["launcher_status"] == "safe"


def test_post_build_smoke_gate_doc_uses_maintained_surface_split() -> None:
    text = (PROJECT_ROOT / "docs" / "bundle_smoke_gate.md").read_text(encoding="utf-8")
    required = [
        "post-build bundle smoke gate",
        "shippable",
        "bundle-doctor",
        "check-bundle",
        "inspect-bundle",
        "plan-bundle",
        "build-bundle",
        "continue patch by patch from evidence",
        "Do not treat raw `check-bundle` against a built zip as the maintained smoke gate",
    ]
    for phrase in required:
        assert phrase in text
