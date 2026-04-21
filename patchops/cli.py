from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from patchops.doctor import run_doctor
from patchops.examples_index import list_examples
from patchops.manifest_checks import check_manifest_path
from patchops.bundles.launcher_self_check import check_launcher_path
from patchops.bundles.bundle_zip_check import check_bundle_zip
from patchops.bundles.authoring import (
    build_bundle_zip,
    create_proof_bundle,
    create_starter_bundle,
    resolve_bundle_execution_metadata,
    resolve_bundle_workflow_mode,
    run_bundle_authoring_self_check,
    run_bundle_doctor,
    run_bundle_execution_entry,
)
from patchops.manifest_loader import load_manifest
from patchops.manifest_reference import build_manifest_schema_summary
from patchops.manifest_templates import build_manifest_template
from patchops.planning import plan_manifest
from patchops.profile_summary import get_profile_summary, list_profile_summaries
from patchops.result_integrity import derive_effective_summary_fields
from patchops.workflows.apply_patch import apply_manifest
from patchops.workflows.verify_only import verify_only
from patchops.workflows.wrapper_retry import execute_wrapper_only_retry


from patchops.bundles.bundle_zip_inspect import inspect_bundle_path
from patchops.bundles.bundle_zip_plan import plan_bundle_path
from patchops.bundles.bundle_zip_apply import apply_bundle_path
from patchops.bundles.cli_commands import (
    run_inspect_bundle_command,
    run_plan_bundle_command,
    run_verify_bundle_command,
)

_REJECT_LAUNCHER_REVIEW_PATTERNS = (
    "convertfrom-json",
    "py -c",
    "inline python",
    "here-string",
    "manual copy",
    "copy-item",
    "throw",
    "missing",
    "not found",
    "syntax",
    "parse",
    "invalid",
)


def _launcher_issue_code_from_message(message: str, *, index: int) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", message.lower()).strip("_")
    if not cleaned:
        cleaned = f"launcher_issue_{index}"
    parts = [part for part in cleaned.split("_") if part]
    stem = "_".join(parts[:6]) if parts else f"launcher_issue_{index}"
    return stem or f"launcher_issue_{index}"


def _launcher_review_status(issues: list[str]) -> str:
    if not issues:
        return "safe"
    flattened = "\n".join(issues).lower()
    if any(pattern in flattened for pattern in _REJECT_LAUNCHER_REVIEW_PATTERNS):
        return "reject"
    return "warning"


def _build_launcher_review_payload(*, launcher_path: str | None, issues: list[str]) -> dict[str, Any]:
    status = _launcher_review_status(issues)
    normalized_issues = [
        {
            "code": _launcher_issue_code_from_message(message, index=index),
            "message": message,
            "path": launcher_path,
        }
        for index, message in enumerate(issues, start=1)
    ]
    return {
        "status": status,
        "launcher_path": launcher_path,
        "issue_count": len(normalized_issues),
        "issues": normalized_issues,
    }


def _candidate_bundle_launcher_paths_for_directory(bundle_root: Path) -> list[Path]:
    root = Path(bundle_root).resolve()
    return [
        root / "run_with_patchops.ps1",
        root / "launchers" / "apply_with_patchops.ps1",
        root / "launchers" / "verify_with_patchops.ps1",
    ]


def _candidate_bundle_launcher_members(root: str) -> list[str]:
    return [
        f"{root}/run_with_patchops.ps1",
        f"{root}/launchers/apply_with_patchops.ps1",
        f"{root}/launchers/verify_with_patchops.ps1",
    ]


def _read_root_launcher_review_from_directory(bundle_root: Path) -> dict[str, Any]:
    candidates = _candidate_bundle_launcher_paths_for_directory(bundle_root)
    for launcher_path in candidates:
        if launcher_path.is_file():
            launcher_payload = check_launcher_path(launcher_path)
            return _build_launcher_review_payload(
                launcher_path=str(launcher_path),
                issues=[str(item) for item in launcher_payload.get("issues") or []],
            )
    return _build_launcher_review_payload(
        launcher_path=str(candidates[0]),
        issues=[
            "Saved bundle launcher is missing. Looked for: " + ", ".join(str(path) for path in candidates)
        ],
    )


def _read_root_launcher_review_from_zip(bundle_zip_path: Path) -> dict[str, Any]:
    zip_path = Path(bundle_zip_path).resolve()
    if not zip_path.exists():
        return _build_launcher_review_payload(
            launcher_path=None,
            issues=[f"Bundle zip path does not exist: {zip_path}"],
        )
    if zip_path.is_dir():
        return _build_launcher_review_payload(
            launcher_path=None,
            issues=[f"Bundle zip path is a directory, not a zip file: {zip_path}"],
        )

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            member_names = [name for name in archive.namelist() if name and not name.endswith("/")]
            roots = sorted({name.split("/", 1)[0] for name in member_names})
            if len(roots) != 1:
                return _build_launcher_review_payload(
                    launcher_path=None,
                    issues=[f"Bundle zip must contain exactly one top-level root folder. Found: {roots}"],
                )

            root = roots[0]
            candidates = _candidate_bundle_launcher_members(root)
            launcher_member = next((candidate for candidate in candidates if candidate in member_names), None)
            if launcher_member is None:
                return _build_launcher_review_payload(
                    launcher_path=candidates[0],
                    issues=[
                        "Saved bundle launcher is missing from bundle zip. Looked for: " + ", ".join(candidates)
                    ],
                )

            with tempfile.TemporaryDirectory(prefix="patchops_bundle_review_") as temp_dir:
                archive.extractall(temp_dir)
                launcher_path = Path(temp_dir) / launcher_member
                launcher_payload = check_launcher_path(launcher_path)
                return _build_launcher_review_payload(
                    launcher_path=launcher_member,
                    issues=[str(item) for item in launcher_payload.get("issues") or []],
                )
    except zipfile.BadZipFile:
        return _build_launcher_review_payload(
            launcher_path=None,
            issues=[f"Bundle zip is not a valid zip archive: {zip_path}"],
        )


def _augment_bundle_review_payload(payload: dict[str, Any], *, bundle_path: Path) -> dict[str, Any]:
    review = (
        _read_root_launcher_review_from_zip(bundle_path)
        if bundle_path.suffix.lower() == ".zip"
        else _read_root_launcher_review_from_directory(bundle_path)
    )

    base_issues = [str(item) for item in (payload.get("issues") or [])]
    launcher_messages = [str(item.get("message", "")) for item in review.get("issues", []) if str(item.get("message", ""))]
    combined_issues = list(base_issues)
    for message in launcher_messages:
        if message not in combined_issues:
            combined_issues.append(message)

    payload["launcher_review"] = review
    payload["launcher_status"] = review["status"]
    payload["launcher_issue_count"] = review["issue_count"]
    payload["launcher_issue_codes"] = [item["code"] for item in review["issues"]]
    payload["issues"] = combined_issues
    payload["issue_count"] = len(combined_issues)
    payload["ok"] = len(combined_issues) == 0
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchops")
    subparsers = parser.add_subparsers(dest="command", required=True)
    apply_bundle_parser = subparsers.add_parser(
        "apply-bundle",
        help="Extract a bundle zip and invoke the bundled apply launcher",
    )
    apply_bundle_parser.description = (
        "Extract a bundle zip and invoke the bundled apply launcher."
    )
    apply_bundle_parser.add_argument("bundle_zip_path", help="Path to the bundle zip file")
    apply_bundle_parser.add_argument(
        "--wrapper-root",
        dest="bundle_wrapper_root",
        help="Optional explicit PatchOps wrapper root passed to the launcher",
    )
    apply_bundle_parser.add_argument(
        "--extract-root",
        dest="bundle_extract_root",
        help="Optional explicit extraction root for the bundle run",
    )


    verify_bundle_parser = subparsers.add_parser(
        "verify-bundle",
        help="Verify a raw zip patch bundle through the verify-only flow",
    )
    verify_bundle_parser.description = (
        "Verify a raw zip patch bundle through the verify-only flow."
    )
    verify_bundle_parser.add_argument("bundle_zip_path", help="Path to the bundle zip file")
    verify_bundle_parser.add_argument(
        "--wrapper-root",
        dest="bundle_wrapper_root",
        required=True,
        help="PatchOps wrapper repo root used for extracted bundle verification",
    )


    plan_bundle_parser = subparsers.add_parser(
        "plan-bundle",
        help="Plan a raw zip patch bundle before execution",
    )
    plan_bundle_parser.description = (
        "Plan a raw zip patch bundle before execution."
    )
    plan_bundle_parser.add_argument(
        "bundle_zip_path",
        help="Path to the raw patch bundle zip file",
    )

    inspect_bundle_parser = subparsers.add_parser(
        "inspect-bundle",
        help="Inspect a raw zip patch bundle before execution",
    )
    inspect_bundle_parser.description = (
        "Inspect a raw zip patch bundle before execution."
    )
    inspect_bundle_parser.add_argument(
        "bundle_zip_path",
        help="Path to the raw patch bundle zip file",
    )

    check_bundle_parser = subparsers.add_parser(
        "check-bundle",
        help="Validate a PatchOps bundle root or raw bundle zip before execution.",
        description="Validate a PatchOps bundle root or raw bundle zip before execution.",
    )
    check_bundle_parser.add_argument(
        "bundle_path",
        metavar="bundle_zip_path",
        help="Path to the PatchOps bundle root directory or bundle zip file",
    )
    check_bundle_parser.add_argument(
        "--profile",
        dest="profile",
        help="Optional requested profile for bundle validation output",
    )
    bundle_entry_parser = subparsers.add_parser(
    "bundle-entry",
    help="Run a bundle root through metadata-driven apply or verify selection",
)
    bundle_entry_parser.description = (
    "Run a checked bundle root through metadata-driven apply or verify selection."
)
    bundle_entry_parser.add_argument("bundle_root", help="Path to the bundle root directory")
    bundle_entry_parser.add_argument(
        "--wrapper-root",
        default=None,
        help="Override wrapper project root for the delegated manifest workflow",
    )

    apply_parser = subparsers.add_parser("apply", help="Apply a manifest-driven patch")
    apply_parser.add_argument("manifest", help="Path to the manifest JSON file")
    apply_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)

    verify_parser = subparsers.add_parser("verify", help="Run verify-only flow")
    verify_parser.add_argument("manifest", help="Path to the manifest JSON file")
    verify_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)

    wrapper_retry_parser = subparsers.add_parser(
        "wrapper-retry",
        help="Run the narrow wrapper-only retry flow",
    )
    wrapper_retry_parser.add_argument("manifest", help="Path to the manifest JSON file")
    wrapper_retry_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)
    wrapper_retry_parser.add_argument(
        "--retry-reason",
        default=None,
        help="Optional reason recorded for the wrapper-only retry intent.",
    )

    inspect_parser = subparsers.add_parser("inspect", help="Load a manifest and print normalized JSON")
    inspect_parser.add_argument("manifest", help="Path to the manifest JSON file")

    check_parser = subparsers.add_parser("check", help="Validate a manifest and flag starter placeholders")
    check_parser.description = "Validate a manifest and flag starter placeholders before apply or verify."
    check_parser.epilog = "Use this command to catch starter placeholders before apply or verify flows."
    check_parser.add_argument("manifest", help="Path to the manifest JSON file")
    check_launcher_parser = subparsers.add_parser(
        "check-launcher",
        help="Audit a bundled PowerShell launcher for common risks",
    )
    check_launcher_parser.description = (
        "Audit a bundled PowerShell launcher for common risks before execution."
    )
    check_launcher_parser.add_argument(
        "launcher_path",
        help="Path to the bundled PowerShell launcher",
    )

    plan_parser = subparsers.add_parser("plan", help="Preview resolved manifest execution details")
    plan_parser.add_argument("manifest", help="Path to the manifest JSON file")
    plan_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)
    plan_parser.add_argument("--mode", choices=["apply", "verify", "wrapper_retry"], default="apply")
    plan_parser.add_argument(
        "--retry-reason",
        default=None,
        help="Optional reason surfaced when previewing wrapper-only retry mode.",
    )

    release_readiness_parser = subparsers.add_parser(
        "release-readiness",
        help="Summarize release/freeze readiness from repo state",
    )
    release_readiness_parser.description = (
        "Summarize release/freeze readiness from repo state without guessing hidden state."
    )
    release_readiness_parser.add_argument(
        "--wrapper-root",
        help="Override wrapper project root",
        default=None,
    )
    release_readiness_parser.add_argument(
        "--profile",
        help="Optional profile name to focus on",
        default=None,
    )
    release_readiness_parser.add_argument(
        "--core-tests-green",
        action="store_true",
        help="Mark core test state as green when it has already been proven externally.",
    )
    release_readiness_parser.add_argument(
        "--report-path",
        help="Optional path to write deterministic release-readiness evidence text.",
        default=None,
    )

    maintenance_gate_parser = subparsers.add_parser(
        "maintenance-gate",
        help="Run the maintained combined wrapper health gate",
    )
    maintenance_gate_parser.description = (
        "Run the maintained combined wrapper health gate across regression, smoke, and release-readiness surfaces."
    )
    maintenance_gate_parser.add_argument(
        "--wrapper-root",
        help="Override wrapper project root",
        default=None,
    )
    maintenance_gate_parser.add_argument(
        "--profile",
        help="Optional profile name to focus on",
        default=None,
    )
    maintenance_gate_parser.add_argument(
        "--core-tests-green",
        action="store_true",
        help="Mark core test state as green when it has already been proven externally.",
    )
    maintenance_gate_parser.add_argument(
        "--report-path",
        help="Optional path to write deterministic maintenance-gate evidence text.",
        default=None,
    )

    emit_operator_script_parser = subparsers.add_parser(
        "emit-operator-script",
        help="Emit a maintained operator helper script from Python-owned templates",
    )
    emit_operator_script_parser.description = (
        "Emit a maintained operator helper script so common PowerShell helper actions reuse one repo-owned template instead of ad hoc shell authoring."
    )
    emit_operator_script_parser.add_argument(
        "script_kind",
        choices=["run-package-zip", "maintenance-gate", "patchops-entry-ps1"],
        help="Operator helper script kind to emit.",
    )
    emit_operator_script_parser.add_argument(
        "output_path",
        help="Output .ps1 path for the emitted operator helper script.",
    )
    emit_operator_script_parser.add_argument(
        "--wrapper-root",
        help="Wrapper repo root embedded into the emitted script.",
        default=None,
    )
    emit_operator_script_parser.add_argument(
        "--bundle-zip-path",
        help="Default bundle zip path embedded into the run-package helper script.",
        default=r"D:\patch_bundle.zip",
    )

    setup_windows_env_parser = subparsers.add_parser(
        "setup-windows-env",
        help="Create the maintained Windows PatchOps environment variables and report directories",
    )
    setup_windows_env_parser.description = (
        "Create the maintained Windows PatchOps environment variables, bin path, and per-project report directories without widening PowerShell into a second workflow engine."
    )
    setup_windows_env_parser.add_argument(
        "--wrapper-root",
        help="Override wrapper project root embedded into PATCHOPS_WRAPPER_ROOT.",
        default=None,
    )
    setup_windows_env_parser.add_argument(
        "--reports-root",
        help="Optional explicit reports root. Defaults to Desktop\\PatchOpsReports under the current user profile.",
        default=None,
    )
    setup_windows_env_parser.add_argument(
        "--bin-root",
        help="Optional explicit bin root to append to PATH. Defaults to %%USERPROFILE%%\\bin\\PatchOps.",
        default=None,
    )
    setup_windows_env_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned environment changes without persisting them.",
    )


    bootstrap_repair_parser = subparsers.add_parser(
        "bootstrap-repair",
        help="Apply a narrow bootstrap recovery payload when normal CLI bootability is degraded",
    )
    bootstrap_repair_parser.description = (
        "Apply a narrow bootstrap recovery payload so a few known files can be restored and py_compile-checked before normal PatchOps use resumes."
    )
    bootstrap_repair_parser.add_argument(
        "payload_root",
        help="Directory containing replacement files in target-relative shape.",
    )
    bootstrap_repair_parser.add_argument(
        "--target-root",
        default=None,
        help="Target project root to repair. Defaults to the wrapper root.",
    )
    bootstrap_repair_parser.add_argument(
        "--path",
        action="append",
        required=True,
        help="Relative file path to restore from the payload root. May be supplied more than once.",
    )
    bootstrap_repair_parser.add_argument(
        "--py-compile-path",
        action="append",
        default=[],
        help="Relative Python file path to validate with py_compile after restore. May be supplied more than once.",
    )
    bootstrap_repair_parser.add_argument(
        "--backup-root",
        default=None,
        help="Optional explicit backup root. Defaults under target_root/data/runtime/bootstrap_repairs/.",
    )

    profiles_parser = subparsers.add_parser("profiles", help="List available profiles and their defaults")
    profiles_parser.add_argument("--name", help="Return only one profile summary", default=None)
    profiles_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)

    template_parser = subparsers.add_parser("template", help="Generate a profile-aware starter manifest template")
    template_parser.add_argument("--profile", required=True, help="Profile name to scaffold against")
    template_parser.add_argument("--mode", choices=["apply", "verify"], default="apply")
    template_parser.add_argument("--patch-name", default="template_patch", help="Starter patch name")
    template_parser.add_argument("--target-root", default=None, help="Override target project root in the template")
    template_parser.add_argument("--output-path", default=None, help="Optional JSON file path to write the starter template")
    template_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)

    doctor_parser = subparsers.add_parser("doctor", help="Inspect environment and profile readiness")
    doctor_parser.description = "Inspect environment and profile readiness before template, check, plan, apply, verify, wrapper-retry, release-readiness, or maintenance-gate."
    doctor_parser.add_argument("--profile", default="trader", help="Profile name to inspect")
    doctor_parser.add_argument("--target-root", default=None, help="Optional target project root override")

    examples_parser = subparsers.add_parser("examples", help="List bundled example manifests")
    examples_parser.description = "List bundled example manifests and their intended usage."
    examples_parser.add_argument("--profile", default=None, help="Optional profile filter")

    schema_parser = subparsers.add_parser("schema", help="Print manifest field reference and starter guidance")
    schema_parser.description = "Print a stable manifest field reference and starter guidance for PatchOps manifests."


    export_handoff_parser = subparsers.add_parser(
        "export-handoff",
        help="Generate the current handoff bundle from a canonical report",
    )
    export_handoff_parser.description = (
        "Generate current_handoff files, latest report artifacts, and a compact handoff bundle directory."
    )
    export_handoff_parser.add_argument(
        "--report-path",
        default=None,
        help="Optional path to the latest canonical PatchOps report.",
    )
    export_handoff_parser.add_argument(
        "--wrapper-root",
        help="Override wrapper project root",
        default=None,
    )
    export_handoff_parser.add_argument(
        "--current-stage",
        default="Stage 2 in progress",
        help="Stage label to write into the exported handoff files.",
    )
    export_handoff_parser.add_argument(
        "--bundle-name",
        default="current",
        help="Bundle directory name under handoff/bundle.",
    )

    init_project_doc_parser = subparsers.add_parser(
        "init-project-doc",
        help="Generate a starter project packet under docs/projects/",
    )
    init_project_doc_parser.description = (
        "Generate a starter project packet from explicit target inputs without guessing hidden state."
    )
    init_project_doc_parser.add_argument("--project-name", required=True, help="Human-readable project name")
    init_project_doc_parser.add_argument("--target-root", required=True, help="Target project root for this packet")
    init_project_doc_parser.add_argument("--profile", required=True, help="PatchOps profile to anchor the packet")
    init_project_doc_parser.add_argument("--runtime-path", default=None, help="Optional explicit runtime override")
    init_project_doc_parser.add_argument(
        "--initial-goal",
        action="append",
        default=[],
        help="Optional initial goal line; may be supplied more than once.",
    )
    init_project_doc_parser.add_argument("--output-path", default=None, help="Optional explicit markdown output path")
    init_project_doc_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)


    refresh_project_doc_parser = subparsers.add_parser(
        "refresh-project-doc",
        help="Refresh the mutable section of an existing project packet under docs/projects/",
    )
    refresh_project_doc_parser.description = (
        "Refresh the mutable packet state from explicit inputs and optional handoff/report artifacts."
    )
    refresh_project_doc_parser.add_argument("--project-name", required=True, help="Human-readable project name")
    refresh_project_doc_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)
    refresh_project_doc_parser.add_argument("--packet-path", default=None, help="Optional explicit markdown packet path")
    refresh_project_doc_parser.add_argument("--handoff-json-path", default=None, help="Optional handoff JSON path")
    refresh_project_doc_parser.add_argument("--report-path", default=None, help="Optional latest report path")
    refresh_project_doc_parser.add_argument("--current-phase", default=None, help="Optional current phase override")
    refresh_project_doc_parser.add_argument("--current-objective", default=None, help="Optional current objective override")
    refresh_project_doc_parser.add_argument("--latest-passed-patch", default=None, help="Optional latest passed patch override")
    refresh_project_doc_parser.add_argument("--latest-attempted-patch", default=None, help="Optional latest attempted patch override")
    refresh_project_doc_parser.add_argument("--current-recommendation", default=None, help="Optional recommendation override")
    refresh_project_doc_parser.add_argument("--next-action", default=None, help="Optional next action override")
    refresh_project_doc_parser.add_argument("--blocker", action="append", default=[], help="Optional current blocker line; may be supplied more than once.")
    refresh_project_doc_parser.add_argument("--risk", action="append", default=[], help="Optional outstanding risk line; may be supplied more than once.")



    bootstrap_target_parser = subparsers.add_parser(
        "bootstrap-target",
        help="Generate onboarding bootstrap artifacts under onboarding/",
    )
    bootstrap_target_parser.description = (
        "Generate onboarding artifacts that sit parallel to handoff and help the first LLM start conservatively."
    )
    bootstrap_target_parser.add_argument("--project-name", required=True, help="Human-readable project name")
    bootstrap_target_parser.add_argument("--target-root", required=True, help="Target project root for onboarding")
    bootstrap_target_parser.add_argument("--profile", required=True, help="PatchOps profile for the target")
    bootstrap_target_parser.add_argument("--runtime-path", default=None, help="Optional explicit runtime override")
    bootstrap_target_parser.add_argument(
        "--initial-goal",
        action="append",
        default=[],
        help="Optional initial goal line; may be supplied more than once.",
    )
    bootstrap_target_parser.add_argument(
        "--current-stage",
        default="Initial onboarding",
        help="Stage label to include in the onboarding artifacts.",
    )
    bootstrap_target_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)

    recommend_profile_parser = subparsers.add_parser("recommend-profile")
    recommend_profile_parser.add_argument("--target-root", required=True)
    recommend_profile_parser.add_argument("--wrapper-root")

    starter_parser = subparsers.add_parser("starter")
    starter_parser.add_argument("--profile", required=True)
    starter_parser.add_argument("--intent", required=True)
    starter_parser.add_argument("--target-root")
    starter_parser.add_argument("--patch-name")
    starter_parser.add_argument("--wrapper-root")

    make_bundle_parser = subparsers.add_parser(
        "make-bundle",
        help="Generate a canonical PatchOps bundle scaffold from Python-owned templates",
    )
    make_bundle_parser.description = (
        "Generate a canonical PatchOps bundle scaffold that already matches the maintained single-launcher authoring contract."
    )
    make_bundle_parser.add_argument(
        "bundle_root",
        help="Path to the bundle root directory to create or refresh",
    )
    make_bundle_parser.add_argument(
        "--mode",
        choices=["apply", "verify", "proof"],
        default="apply",
        help="Starter bundle mode written into bundle_meta.json.",
    )
    make_bundle_parser.add_argument(
        "--patch-name",
        default="starter_bundle",
        help="Patch name written into manifest.json and bundle_meta.json.",
    )
    make_bundle_parser.add_argument(
        "--target-project",
        default="patchops",
        help="Human-readable target project label written into bundle_meta.json.",
    )
    make_bundle_parser.add_argument(
        "--target-root",
        default=None,
        help="Target project root written into the starter manifest and bundle metadata.",
    )
    make_bundle_parser.add_argument(
        "--profile",
        default="generic_python",
        help="Recommended PatchOps profile written into the generated bundle.",
    )
    make_bundle_parser.add_argument(
        "--wrapper-root",
        default=None,
        help="Wrapper project root written into bundle metadata and used for launcher emission.",
    )

    make_proof_bundle_parser = subparsers.add_parser(
        "make-proof-bundle",
        help="Generate a known-good PatchOps proof bundle for apply, verify, or launcher-risk surfaces",
    )
    make_proof_bundle_parser.description = (
        "Generate a known-good PatchOps proof bundle so operators and LLMs can reuse maintained proof shapes instead of improvising them."
    )
    make_proof_bundle_parser.add_argument(
        "bundle_root",
        help="Path to the proof bundle root directory to create or refresh",
    )
    make_proof_bundle_parser.add_argument(
        "--kind",
        choices=["apply", "verify", "launcher-risk"],
        required=True,
        help="Proof bundle kind to generate.",
    )
    make_proof_bundle_parser.add_argument(
        "--patch-name",
        default=None,
        help="Optional patch name override written into the generated proof bundle.",
    )
    make_proof_bundle_parser.add_argument(
        "--target-project",
        default="patchops",
        help="Human-readable target project label written into bundle metadata.",
    )
    make_proof_bundle_parser.add_argument(
        "--target-root",
        default=None,
        help="Target project root written into the generated proof bundle.",
    )
    make_proof_bundle_parser.add_argument(
        "--profile",
        default="generic_python",
        help="Recommended PatchOps profile written into the generated proof bundle.",
    )
    make_proof_bundle_parser.add_argument(
        "--wrapper-root",
        default=None,
        help="Wrapper project root written into bundle metadata and used for launcher emission.",
    )

    build_bundle_parser = subparsers.add_parser(
        "build-bundle",
        help="Build a deterministic PatchOps bundle zip from a validated bundle root",
    )
    build_bundle_parser.description = (
        "Build a deterministic PatchOps bundle zip from a validated bundle root."
    )
    build_bundle_parser.add_argument(
        "bundle_root",
        help="Path to the canonical PatchOps bundle root directory",
    )
    build_bundle_parser.add_argument(
        "--output",
        required=True,
        help="Output .zip path for the built bundle archive.",
    )


    bundle_doctor_parser = subparsers.add_parser(
        "bundle-doctor",
        help="Diagnose PatchOps bundle authoring problems from one high-signal entrypoint",
    )
    bundle_doctor_parser.description = (
        "Diagnose missing files, wrong root shape, launcher risks, content-path mismatches, and export mistakes for a bundle root or bundle zip."
    )
    bundle_doctor_parser.add_argument(
        "bundle_path",
        help="Path to the PatchOps bundle root directory or bundle zip file",
    )


    run_package_parser = subparsers.add_parser(
        "run-package",
        help="Run a ChatGPT delivery package zip or extracted folder through PatchOps.",
    )
    run_package_parser.add_argument(
        "source_path",
        help="Path to a delivery zip or extracted delivery folder.",
    )
    run_package_parser.add_argument(
        "--wrapper-root",
        required=True,
        help="PatchOps wrapper repo root.",
    )
    run_package_parser.add_argument(
        "--mode",
        choices=["apply", "verify"],
        default="apply",
    )
    run_package_parser.add_argument("--profile", default=None)
    run_package_parser.add_argument("--launcher-relative-path", default=None)
    run_package_parser.add_argument("--report-path", default=None)
    run_package_parser.add_argument("--powershell-exe", default=None)

    return parser


def _display_value(value: Any) -> str:
    if value is None:
        return "(none)"
    return str(value)


def _build_run_summary(result: Any, manifest_path: str | Path) -> str:
    effective = derive_effective_summary_fields(result)
    manifest_from_result = getattr(result, "manifest_path", None)
    effective_manifest_path = manifest_from_result if manifest_from_result is not None else Path(manifest_path).resolve()
    lines = [
        "PATCHOPS RUN SUMMARY",
        "--------------------",
        f"Mode               : {_display_value(getattr(result, 'mode', None))}",
        f"Patch Name         : {_display_value(getattr(getattr(result, 'manifest', None), 'patch_name', None))}",
        f"Manifest Path      : {_display_value(effective_manifest_path)}",
        f"Target Project Root: {_display_value(getattr(result, 'target_project_root', None))}",
        f"Active Profile     : {_display_value(getattr(getattr(result, 'resolved_profile', None), 'name', None))}",
        f"Runtime Path       : {_display_value(getattr(result, 'runtime_path', None))}",
        f"Report Path        : {_display_value(getattr(result, 'report_path', None))}",
        f"ExitCode           : {_display_value(effective['exit_code'])}",
        f"Result             : {_display_value(effective['result_label'])}",
    ]
    return "\n".join(lines)


def _write_json_file(path_value: str | Path, payload: dict[str, Any]) -> Path:
    output_path = Path(path_value)
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return output_path.resolve()


def main(argv: list[str] | None = None) -> int:
    import sys as _patchops_sys
    argv = list(_patchops_sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "run-package":
        from patchops.package_runner import cli_main as _patchops_run_package_cli_main
        return _patchops_run_package_cli_main(argv[1:])

    parser = build_parser()
    args = parser.parse_args(argv)

    # PATCHOPS_B2E_COMPAT_START
    if args.command == "inspect-bundle":
        from patchops.bundles.legacy_bundle_review import inspect_bundle_cli_payload_compat
        _bundle_source = getattr(args, "bundle_zip_path", None) or getattr(args, "bundle_path", None) or getattr(args, "source_path", None)
        _compat_payload = inspect_bundle_cli_payload_compat(_bundle_source)
        if _compat_payload is not None:
            import json as _json
            print(_json.dumps(_compat_payload, indent=2))
            return 0 if bool(_compat_payload.get("ok", False)) else 1

    if args.command == "plan-bundle":
        from patchops.bundles.legacy_bundle_review import plan_bundle_cli_payload_compat
        _bundle_source = getattr(args, "bundle_zip_path", None) or getattr(args, "bundle_path", None) or getattr(args, "source_path", None)
        _compat_payload = plan_bundle_cli_payload_compat(_bundle_source)
        if _compat_payload is not None:
            import json as _json
            print(_json.dumps(_compat_payload, indent=2))
            return 0 if bool(_compat_payload.get("ok", False)) else 1

    if args.command == "check-bundle":
        from patchops.bundles.legacy_bundle_review import check_bundle_cli_payload_compat
        _bundle_source = getattr(args, "bundle_path", None) or getattr(args, "bundle_zip_path", None) or getattr(args, "source_path", None)
        _compat_payload = check_bundle_cli_payload_compat(_bundle_source, profile_name=getattr(args, "profile", None))
        if _compat_payload is not None:
            import json as _json
            print(_json.dumps(_compat_payload, indent=2))
            return 0 if bool(_compat_payload.get("ok", False)) else 1
    # PATCHOPS_B2E_COMPAT_END




    if args.command == "apply-bundle":
        try:
            payload = apply_bundle_path(
                args.bundle_zip_path,
                wrapper_root=getattr(args, "bundle_wrapper_root", None),
                extract_root=getattr(args, "bundle_extract_root", None),
            )
        except Exception as exc:
            print(json.dumps({
                "bundle_zip_path": str(args.bundle_zip_path),
                "ok": False,
                "error": str(exc),
            }, indent=2))
            return 1
        print(json.dumps(payload, indent=2))
        return int(payload["exit_code"])

    if args.command == "verify-bundle":
        try:
            payload = run_verify_bundle_command(
                args.bundle_zip_path,
                getattr(args, "bundle_wrapper_root", None),
            )
        except Exception as exc:
            print(json.dumps({
                "bundle_zip_path": str(args.bundle_zip_path),
                "ok": False,
                "error": str(exc),
            }, indent=2))
            return 1
        print(json.dumps(payload, indent=2))
        exit_code = payload.get("exit_code")
        if exit_code is None:
            return 0 if payload.get("ok") else 1
        return int(exit_code)

    if args.command == "apply":
        result = apply_manifest(args.manifest, wrapper_project_root=args.wrapper_root)
        print(_build_run_summary(result, args.manifest))
        return int(derive_effective_summary_fields(result)["exit_code"])

    if args.command == "verify":
        result = verify_only(args.manifest, wrapper_project_root=args.wrapper_root)
        print(_build_run_summary(result, args.manifest))
        return int(derive_effective_summary_fields(result)["exit_code"])

    if args.command == "wrapper-retry":
        result = execute_wrapper_only_retry(
            args.manifest,
            wrapper_project_root=args.wrapper_root,
            reason=args.retry_reason,
        )
        print(_build_run_summary(result, args.manifest))
        return int(derive_effective_summary_fields(result)["exit_code"])


    if args.command == "export-handoff":
        from patchops.handoff import export_handoff_bundle

        payload = export_handoff_bundle(
            report_path=args.report_path,
            wrapper_project_root=args.wrapper_root,
            current_stage=args.current_stage,
            bundle_name=args.bundle_name,
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "inspect":
        manifest = load_manifest(Path(args.manifest))
        print(json.dumps(asdict(manifest), indent=2))
        return 0

    if args.command == "check":
        summary = check_manifest_path(args.manifest)
        print(json.dumps(summary, indent=2))
        return 0 if summary["ok"] else 1

    if args.command == "plan":
        preview = plan_manifest(
            args.manifest,
            wrapper_project_root=args.wrapper_root,
            mode=args.mode,
            retry_reason=args.retry_reason,
        )
        print(json.dumps(preview, indent=2))
        return 0



    if args.command == "plan-bundle":
        wrapper_root = Path(__file__).resolve().parents[1]
        payload = run_plan_bundle_command(args.bundle_zip_path, wrapper_root)
        payload = _augment_bundle_review_payload(payload, bundle_path=Path(args.bundle_zip_path))
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "inspect-bundle":
        wrapper_root = Path(__file__).resolve().parents[1]
        payload = run_inspect_bundle_command(args.bundle_zip_path, wrapper_root)
        payload = _augment_bundle_review_payload(payload, bundle_path=Path(args.bundle_zip_path))
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1
    if args.command == "check-bundle":
        from patchops.bundle_review import check_bundle_payload as _check_bundle_payload

        payload = _check_bundle_payload(
            Path(args.bundle_path),
            requested_profile=getattr(args, "profile", None),
        )
        command_payload = dict(payload)
        command_payload["issues"] = [
            issue.get("message", str(issue)) if isinstance(issue, dict) else str(issue)
            for issue in payload.get("issues", [])
        ]
        command_payload["issue_count"] = len(command_payload["issues"])
        print(json.dumps(command_payload, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "profiles":
        try:
            payload = (
                get_profile_summary(args.name, wrapper_project_root=args.wrapper_root)
                if args.name
                else list_profile_summaries(wrapper_project_root=args.wrapper_root)
            )
        except ValueError as exc:
            print(json.dumps({
                "ok": False,
                "error": str(exc),
                "profile_name": args.name,
            }, indent=2))
            return 1
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "doctor":
        payload = run_doctor(profile_name=args.profile, target_root=args.target_root)
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "examples":
        payload = list_examples(profile_name=args.profile)
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "schema":
        payload = build_manifest_schema_summary()
        print(json.dumps(payload, indent=2))
        return 0


    if args.command == "check-launcher":
        payload = check_launcher_path(Path(args.launcher_path))
        print(json.dumps(payload, indent=2))
        return 0 if bool(payload.get("ok")) else 1

# PATCHOPS_TRUE_EOF_MAIN_ENTRY_20260421

    if args.command == "release-readiness":
        from patchops.readiness import (
            build_release_readiness_snapshot,
            release_readiness_as_dict,
            release_readiness_exit_code,
            render_release_readiness_report_lines,
            render_release_readiness_scope_lines,
            write_release_readiness_report,
        )

        wrapper_root = (
            Path(args.wrapper_root).resolve()
            if args.wrapper_root
            else Path(__file__).resolve().parents[1]
        )
        profile_summaries = list_profile_summaries(wrapper_project_root=wrapper_root)
        available_profiles = [item["name"] for item in profile_summaries]
        snapshot = build_release_readiness_snapshot(
            wrapper_root,
            available_profiles=available_profiles,
            core_tests_state=("green" if args.core_tests_green else "unknown"),
        )
        payload = release_readiness_as_dict(snapshot)
        payload["wrapper_project_root"] = str(wrapper_root)
        payload["profile_summaries"] = (
            [get_profile_summary(args.profile, wrapper_project_root=wrapper_root)]
            if args.profile
            else profile_summaries
        )
        payload["scope_lines"] = list(render_release_readiness_scope_lines(snapshot))
        payload["report_lines"] = list(
            render_release_readiness_report_lines(
                snapshot,
                wrapper_project_root=wrapper_root,
                focused_profile=args.profile,
            )
        )
        if args.report_path:
            payload["report_path"] = write_release_readiness_report(
                args.report_path,
                snapshot,
                wrapper_project_root=wrapper_root,
                focused_profile=args.profile,
            )

        print(json.dumps(payload, indent=2))
        return release_readiness_exit_code(snapshot)


    if args.command == "init-project-doc":
        from patchops.project_packets import scaffold_project_packet

        payload = scaffold_project_packet(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            runtime_path=getattr(args, "runtime_path", None),
            wrapper_project_root=args.wrapper_root,
            output_path=getattr(args, "output_path", None),
            initial_goals=list(getattr(args, "initial_goal", []) or []),
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "bootstrap-target":
        from patchops.project_packets import build_onboarding_bootstrap

        payload = build_onboarding_bootstrap(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            wrapper_project_root=args.wrapper_root,
            runtime_path=getattr(args, "runtime_override", None) or getattr(args, "runtime_path", None),
            initial_goals=list(getattr(args, "initial_goal", []) or []),
            current_stage=getattr(args, "current_stage", "Initial onboarding"),
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "recommend-profile":
        from patchops.project_packets import recommend_profile_for_target

        payload = recommend_profile_for_target(
            target_root=args.target_root,
            wrapper_project_root=args.wrapper_root,
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "starter":
        from patchops.project_packets import build_starter_manifest_for_intent

        payload = build_starter_manifest_for_intent(
            profile_name=args.profile,
            intent=args.intent,
            target_root=args.target_root,
            patch_name=args.patch_name,
            wrapper_project_root=args.wrapper_root,
        )
        print(json.dumps(payload, indent=2))
        return 0

if __name__ == "__main__":
    import sys as _patchops_entry_sys

    if len(_patchops_entry_sys.argv) > 1 and _patchops_entry_sys.argv[1] == "check-bundle":
        from patchops.bundle_review import cli_check_bundle_main as _patchops_bundle_review_cli_check_bundle_main

        raise SystemExit(_patchops_bundle_review_cli_check_bundle_main(_patchops_entry_sys.argv[2:]))

    raise SystemExit(main())

