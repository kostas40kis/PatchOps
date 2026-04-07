from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.bundles.cli_payloads import (
    bundle_apply_result_as_dict,
    bundle_plan_result_as_dict,
    bundle_verify_result_as_dict,
)


def test_bundle_plan_payload_contains_report_chain_fields(tmp_path: Path) -> None:
    metadata = SimpleNamespace(
        patch_name="patch_16_payload_plan",
        recommended_profile="generic_python",
    )
    extraction = SimpleNamespace(
        bundle_zip_path=tmp_path / "patch_16_payload_plan.zip",
        run_root=tmp_path / "workspace",
        bundle_root=tmp_path / "workspace" / "extracted_bundle",
    )
    check_result = SimpleNamespace(metadata=metadata, extraction=extraction)
    resolved_layout = SimpleNamespace(
        manifest_path=tmp_path / "workspace" / "extracted_bundle" / "manifest.json",
        content_root_path=tmp_path / "workspace" / "extracted_bundle" / "content",
    )
    inspect_result = SimpleNamespace(check=check_result, resolved_layout=resolved_layout)
    result = SimpleNamespace(
        inspect=inspect_result,
        resolved_profile="generic_python",
        target_project_root=r"C:\dev\patchops",
        report_path_preview=tmp_path / "workspace" / "plan.txt",
        write_targets=("docs/example.md",),
        validation_command_names=("pytest",),
    )

    payload = bundle_plan_result_as_dict(result)

    assert payload["patch_name"] == "patch_16_payload_plan"
    assert payload["report_chain"]["patch_name"] == "patch_16_payload_plan"
    assert payload["report_chain"]["manifest_path"].endswith("manifest.json")
    assert payload["report_chain"]["target_project_root"] == r"C:\dev\patchops"
    assert payload["report_chain"]["final_report_path"] is None


def test_bundle_apply_and_verify_payloads_surface_report_chain_with_launcher(tmp_path: Path) -> None:
    metadata = SimpleNamespace(
        patch_name="patch_16_payload_apply",
        recommended_profile="generic_python",
    )
    extraction = SimpleNamespace(
        bundle_zip_path=tmp_path / "patch_16_payload_apply.zip",
        run_root=tmp_path / "workspace",
        bundle_root=tmp_path / "workspace" / "extracted_bundle",
    )
    check_result = SimpleNamespace(metadata=metadata, extraction=extraction)
    inspect_result = SimpleNamespace(check=check_result)
    launcher_resolution = SimpleNamespace(
        launcher_path=tmp_path / "workspace" / "extracted_bundle" / "run_with_patchops.ps1",
        mode="verify",
        launcher_kind="root_single",
    )
    plan_result = SimpleNamespace(
        inspect=inspect_result,
        launcher_invocation=SimpleNamespace(resolution=launcher_resolution),
    )

    apply_result = SimpleNamespace(
        plan=plan_result,
        prepared_manifest_path=tmp_path / "workspace" / "prepared_apply.json",
        workflow_result=SimpleNamespace(
            report_path=tmp_path / "reports" / "apply.txt",
            result_label="PASS",
            exit_code=0,
        ),
    )
    verify_result = SimpleNamespace(
        plan=plan_result,
        prepared_manifest_path=tmp_path / "workspace" / "prepared_verify.json",
        workflow_result=SimpleNamespace(
            report_path=tmp_path / "reports" / "verify.txt",
            result_label="PASS",
            exit_code=0,
        ),
    )

    apply_payload = bundle_apply_result_as_dict(apply_result)
    verify_payload = bundle_verify_result_as_dict(verify_result)

    assert apply_payload["patch_name"] == "patch_16_payload_apply"
    assert apply_payload["report_chain"]["launcher_path"].endswith("run_with_patchops.ps1")
    assert apply_payload["report_chain"]["launcher_mode"] == "verify"
    assert apply_payload["report_chain"]["final_report_path"].endswith("apply.txt")

    assert verify_payload["patch_name"] == "patch_16_payload_apply"
    assert verify_payload["report_chain"]["launcher_kind"] == "root_single"
    assert verify_payload["report_chain"]["final_report_path"].endswith("verify.txt")
