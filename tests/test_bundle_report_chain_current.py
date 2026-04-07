from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.bundles.report_chain import build_bundle_report_chain, bundle_report_chain_as_dict


def test_build_bundle_report_chain_supports_nested_apply_shape_with_launcher_and_inner_report(tmp_path: Path) -> None:
    metadata = SimpleNamespace(
        patch_name="patch_16_chain",
        recommended_profile="generic_python",
    )
    extraction = SimpleNamespace(
        bundle_zip_path=tmp_path / "patch_16_chain.zip",
        run_root=tmp_path / "workspace",
        bundle_root=tmp_path / "workspace" / "extracted_bundle",
    )
    check_result = SimpleNamespace(
        metadata=metadata,
        extraction=extraction,
    )
    resolved_layout = SimpleNamespace(
        manifest_path=tmp_path / "workspace" / "extracted_bundle" / "manifest.json",
        content_root_path=tmp_path / "workspace" / "extracted_bundle" / "content",
    )
    inspect_result = SimpleNamespace(
        check=check_result,
        resolved_layout=resolved_layout,
    )
    launcher_resolution = SimpleNamespace(
        launcher_path=tmp_path / "workspace" / "extracted_bundle" / "run_with_patchops.ps1",
        mode="apply",
        launcher_kind="root_single",
    )
    launcher_invocation = SimpleNamespace(
        resolution=launcher_resolution,
        stdout="launcher ok",
        stderr="",
        exit_code=0,
    )
    plan_result = SimpleNamespace(
        inspect=inspect_result,
        resolved_profile="generic_python",
        target_project_root=r"C:\dev\patchops",
        launcher_invocation=launcher_invocation,
    )
    result = SimpleNamespace(
        plan=plan_result,
        prepared_manifest_path=tmp_path / "workspace" / "prepared_apply.json",
        workflow_result=SimpleNamespace(
            report_path=tmp_path / "reports" / "inner_apply.txt",
            result_label="PASS",
            exit_code=0,
        ),
        report_path=tmp_path / "reports" / "outer_bundle_apply.txt",
    )

    chain = build_bundle_report_chain(result)

    assert chain.patch_name == "patch_16_chain"
    assert chain.bundle_zip_path is not None and chain.bundle_zip_path.endswith("patch_16_chain.zip")
    assert chain.extracted_bundle_root is not None and chain.extracted_bundle_root.endswith("extracted_bundle")
    assert chain.launcher_path is not None and chain.launcher_path.endswith("run_with_patchops.ps1")
    assert chain.launcher_mode == "apply"
    assert chain.launcher_kind == "root_single"
    assert chain.manifest_path is not None and chain.manifest_path.endswith("manifest.json")
    assert chain.prepared_manifest_path is not None and chain.prepared_manifest_path.endswith("prepared_apply.json")
    assert chain.target_project_root == r"C:\dev\patchops"
    assert chain.final_report_path is not None and chain.final_report_path.endswith("outer_bundle_apply.txt")
    assert chain.inner_report_path is not None and chain.inner_report_path.endswith("inner_apply.txt")


def test_bundle_report_chain_as_dict_preserves_none_for_unavailable_optional_fields(tmp_path: Path) -> None:
    metadata = SimpleNamespace(
        patch_name="patch_16_minimal",
        recommended_profile="generic_python",
    )
    extraction = SimpleNamespace(
        bundle_zip_path=tmp_path / "patch_16_minimal.zip",
        run_root=tmp_path / "workspace",
        bundle_root=tmp_path / "workspace" / "extracted_bundle",
    )
    result = SimpleNamespace(
        metadata=metadata,
        extraction=extraction,
    )

    payload = bundle_report_chain_as_dict(result)

    assert payload["patch_name"] == "patch_16_minimal"
    assert payload["bundle_zip_path"].endswith("patch_16_minimal.zip")
    assert payload["launcher_path"] is None
    assert payload["final_report_path"] is None
    assert payload["inner_report_path"] is None
