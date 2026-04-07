from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from patchops.workflows.apply_patch import apply_manifest

from .planner import BundlePlanResult, plan_bundle_zip


@dataclass(frozen=True)
class BundleApplyResult:
    plan: BundlePlanResult
    prepared_manifest_path: Path | None
    workflow_result: Any | None

    @property
    def is_valid_bundle(self) -> bool:
        return self.plan.is_valid

    @property
    def run_executed(self) -> bool:
        return self.workflow_result is not None

    @property
    def report_path(self) -> Path | None:
        report = getattr(self.workflow_result, "report_path", None)
        return Path(report) if report is not None else None


def _load_manifest_object(manifest_path: Path) -> dict[str, Any]:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Bundle manifest must be a JSON object.")
    return raw


def _normalize_bundle_relative_path(value: str) -> str:
    text = str(value or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    if not text:
        raise ValueError("Bundle content_path must not be empty.")
    if text.startswith("/") or text.startswith("../") or "/../" in text:
        raise ValueError(f"Bundle content_path must stay relative to the extracted bundle root: {value!r}")
    return text


def _rewrite_manifest_for_extracted_bundle(manifest: dict[str, Any], bundle_root: Path) -> dict[str, Any]:
    rewritten = json.loads(json.dumps(manifest))
    files_to_write = rewritten.get("files_to_write", [])
    if not isinstance(files_to_write, list):
        return rewritten

    for entry in files_to_write:
        if not isinstance(entry, dict):
            continue
        if entry.get("content") is not None:
            continue
        if "content_path" not in entry:
            continue
        relative_content_path = _normalize_bundle_relative_path(str(entry.get("content_path", "")))
        entry["content_path"] = str((bundle_root / relative_content_path).resolve())
    return rewritten


def apply_bundle_zip(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> BundleApplyResult:
    plan_result = plan_bundle_zip(
        bundle_zip_path,
        wrapper_project_root,
        timestamp_token=timestamp_token,
    )
    if not plan_result.is_valid or plan_result.resolved_layout is None:
        return BundleApplyResult(
            plan=plan_result,
            prepared_manifest_path=None,
            workflow_result=None,
        )

    manifest = _load_manifest_object(plan_result.resolved_layout.manifest_path)
    rewritten_manifest = _rewrite_manifest_for_extracted_bundle(manifest, plan_result.bundle_root)

    prepared_manifest_path = (
        plan_result.inspect.check.extraction.run_root / "prepared_apply_bundle_manifest.json"
    )
    prepared_manifest_path.write_text(
        json.dumps(rewritten_manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    workflow_result = apply_manifest(
        prepared_manifest_path,
        wrapper_project_root=wrapper_project_root,
    )
    return BundleApplyResult(
        plan=plan_result,
        prepared_manifest_path=prepared_manifest_path,
        workflow_result=workflow_result,
    )
