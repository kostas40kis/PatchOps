from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _stringify_path(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _nested_attr(obj: Any, *names: str) -> Any:
    current = obj
    for name in names:
        if current is None:
            return None
        current = getattr(current, name, None)
    return current


def _bundle_metadata(result: Any) -> Any:
    for path in (
        ("metadata",),
        ("check", "metadata"),
        ("inspect", "metadata"),
        ("plan", "metadata"),
        ("inspect", "check", "metadata"),
        ("plan", "inspect", "metadata"),
        ("plan", "inspect", "check", "metadata"),
    ):
        candidate = _nested_attr(result, *path)
        if candidate is not None:
            return candidate
    return None


def _bundle_extraction(result: Any) -> Any:
    for path in (
        ("extraction",),
        ("check", "extraction"),
        ("inspect", "check", "extraction"),
        ("plan", "inspect", "check", "extraction"),
    ):
        candidate = _nested_attr(result, *path)
        if candidate is not None:
            return candidate
    return None


def _resolved_layout(result: Any) -> Any:
    for path in (
        ("resolved_layout",),
        ("inspect", "resolved_layout"),
        ("plan", "inspect", "resolved_layout"),
    ):
        candidate = _nested_attr(result, *path)
        if candidate is not None:
            return candidate
    return None


def _launcher_invocation(result: Any) -> Any:
    for path in (
        ("launcher_invocation",),
        ("plan", "launcher_invocation"),
        ("inspect", "launcher_invocation"),
    ):
        candidate = _nested_attr(result, *path)
        if candidate is not None:
            return candidate
    return None


@dataclass(frozen=True)
class BundleReportChain:
    patch_name: str | None
    recommended_profile: str | None
    bundle_zip_path: str | None
    workspace_root: str | None
    extracted_bundle_root: str | None
    launcher_path: str | None
    launcher_mode: str | None
    launcher_kind: str | None
    manifest_path: str | None
    prepared_manifest_path: str | None
    target_project_root: str | None
    final_report_path: str | None
    inner_report_path: str | None


def build_bundle_report_chain(result: Any) -> BundleReportChain:
    metadata = _bundle_metadata(result)
    extraction = _bundle_extraction(result)
    resolved_layout = _resolved_layout(result)
    launcher_invocation = _launcher_invocation(result)
    resolution = getattr(launcher_invocation, "resolution", None)
    workflow_result = getattr(result, "workflow_result", None)

    final_report_path = _stringify_path(
        getattr(result, "report_path", getattr(workflow_result, "report_path", None))
    )
    explicit_inner_report_path = _stringify_path(
        getattr(result, "inner_report_path", getattr(workflow_result, "inner_report_path", None))
    )
    if explicit_inner_report_path is not None:
        inner_report_path = explicit_inner_report_path
    elif getattr(result, "report_path", None) is not None and final_report_path is not None:
        inner_report_path = _stringify_path(getattr(workflow_result, "report_path", None))
    else:
        inner_report_path = None

    manifest_path = _stringify_path(
        getattr(result, "manifest_path", getattr(resolved_layout, "manifest_path", None))
    )

    return BundleReportChain(
        patch_name=getattr(result, "patch_name", getattr(metadata, "patch_name", None)),
        recommended_profile=getattr(
            result,
            "recommended_profile",
            getattr(result, "resolved_profile", getattr(metadata, "recommended_profile", None)),
        ),
        bundle_zip_path=_stringify_path(
            getattr(result, "bundle_zip_path", getattr(extraction, "bundle_zip_path", None))
        ),
        workspace_root=_stringify_path(
            getattr(result, "workspace_root", getattr(extraction, "run_root", None))
        ),
        extracted_bundle_root=_stringify_path(
            getattr(result, "extracted_bundle_root", getattr(extraction, "bundle_root", None))
        ),
        launcher_path=_stringify_path(
            getattr(result, "launcher_path", _nested_attr(resolution, "launcher_path"))
        ),
        launcher_mode=getattr(result, "launcher_mode", _nested_attr(resolution, "mode")),
        launcher_kind=getattr(result, "launcher_kind", _nested_attr(resolution, "launcher_kind")),
        manifest_path=manifest_path,
        prepared_manifest_path=_stringify_path(getattr(result, "prepared_manifest_path", None)),
        target_project_root=_stringify_path(
            getattr(result, "target_project_root", _nested_attr(result, "plan", "target_project_root"))
        ),
        final_report_path=final_report_path,
        inner_report_path=inner_report_path,
    )


def bundle_report_chain_as_dict(result: Any) -> dict[str, str | None]:
    chain = build_bundle_report_chain(result)
    return {
        "patch_name": chain.patch_name,
        "recommended_profile": chain.recommended_profile,
        "bundle_zip_path": chain.bundle_zip_path,
        "workspace_root": chain.workspace_root,
        "extracted_bundle_root": chain.extracted_bundle_root,
        "launcher_path": chain.launcher_path,
        "launcher_mode": chain.launcher_mode,
        "launcher_kind": chain.launcher_kind,
        "manifest_path": chain.manifest_path,
        "prepared_manifest_path": chain.prepared_manifest_path,
        "target_project_root": chain.target_project_root,
        "final_report_path": chain.final_report_path,
        "inner_report_path": chain.inner_report_path,
    }
