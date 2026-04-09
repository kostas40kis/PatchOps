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
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )


def _load_json(stdout_text: str, stderr_text: str) -> dict[str, object]:
    text = (stdout_text or "").strip()
    assert text, f"expected JSON output but stdout was empty; stderr={stderr_text!r}"
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"stdout was not valid JSON: {stdout_text!r}; stderr={stderr_text!r}"
        ) from exc


def test_self_hosted_bundle_authoring_workflow_for_patchops_target(tmp_path: Path) -> None:
    proof = create_proof_bundle(
        tmp_path / "self_hosted_proof_bundle",
        kind="apply",
        patch_name="self_hosted_proof_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )

    assert proof.ok is True
    assert proof.bundle_root.exists()

    doctor = _run_cli(["bundle-doctor", str(proof.bundle_root)])
    assert doctor.returncode == 0, doctor.stdout + "\n" + doctor.stderr
    doctor_payload = _load_json(doctor.stdout, doctor.stderr)
    assert doctor_payload["ok"] is True

    built = build_bundle_zip(proof.bundle_root, tmp_path / "self_hosted_proof_bundle.zip")
    assert built.ok is True
    assert built.output_zip.exists()

    inspect_proc = _run_cli(["inspect-bundle", str(built.output_zip)])
    assert inspect_proc.returncode == 0, inspect_proc.stdout + "\n" + inspect_proc.stderr
    inspect_payload = _load_json(inspect_proc.stdout, inspect_proc.stderr)
    assert inspect_payload["ok"] is True
    assert inspect_payload["launcher_status"] == "safe"
    assert inspect_payload["launcher_issue_count"] == 0
