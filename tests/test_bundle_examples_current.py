from __future__ import annotations

from pathlib import Path

from patchops.bundles.authoring import (
    build_bundle_zip,
    resolve_bundle_execution_metadata,
    resolve_bundle_workflow_mode,
    run_bundle_authoring_self_check,
    run_bundle_doctor,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _example_bundle(name: str) -> Path:
    return PROJECT_ROOT / "examples" / "bundles" / name


def test_generic_apply_example_bundle_passes_self_check_and_build(tmp_path: Path) -> None:
    bundle_root = _example_bundle("generic_apply_bundle")

    self_check = run_bundle_authoring_self_check(bundle_root)
    assert self_check.issue_count == 0
    assert self_check.is_valid is True

    build_result = build_bundle_zip(bundle_root, tmp_path / "generic_apply_bundle.zip")
    assert build_result.ok is True
    assert build_result.issue_count == 0

    doctor_result = run_bundle_doctor(build_result.output_zip)
    assert doctor_result.ok is True
    assert doctor_result.issue_count == 0

    metadata = resolve_bundle_execution_metadata(bundle_root)
    assert metadata.bundle_mode == "apply"
    assert resolve_bundle_workflow_mode(metadata) == "apply"


def test_generic_verify_example_bundle_passes_self_check_and_build(tmp_path: Path) -> None:
    bundle_root = _example_bundle("generic_verify_bundle")

    self_check = run_bundle_authoring_self_check(bundle_root)
    assert self_check.issue_count == 0
    assert self_check.is_valid is True

    build_result = build_bundle_zip(bundle_root, tmp_path / "generic_verify_bundle.zip")
    assert build_result.ok is True
    assert build_result.issue_count == 0

    doctor_result = run_bundle_doctor(build_result.output_zip)
    assert doctor_result.ok is True
    assert doctor_result.issue_count == 0

    metadata = resolve_bundle_execution_metadata(bundle_root)
    assert metadata.bundle_mode == "verify"
    assert resolve_bundle_workflow_mode(metadata) == "verify"
