from __future__ import annotations

import argparse
import json
import sys
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
    create_starter_bundle,
    resolve_bundle_execution_metadata,
    resolve_bundle_workflow_mode,
    run_bundle_authoring_self_check,
    run_bundle_doctor,
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
from patchops.bundles.cli_commands import run_verify_bundle_command
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
        help="Validate a PatchOps bundle root or raw bundle zip",
    )
    check_bundle_parser.description = (
        "Validate a PatchOps bundle root or raw bundle zip before execution."
    )
    check_bundle_parser.add_argument(
        "bundle_path",
        help="Path to the PatchOps bundle root directory or bundle zip file",
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
    doctor_parser.description = "Inspect environment and profile readiness before template, check, plan, apply, verify, wrapper-retry, or release-readiness."
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
        payload = plan_bundle_path(args.bundle_zip_path)
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "inspect-bundle":
        payload = inspect_bundle_path(args.bundle_zip_path)
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "check-bundle":
        bundle_path = Path(args.bundle_path)
        if bundle_path.suffix.lower() == ".zip":
            payload = check_bundle_zip(bundle_path)
        else:
            result = run_bundle_authoring_self_check(bundle_path)
            payload = {
                "bundle_root": str(result.bundle_root),
                "exists": result.bundle_root.exists(),
                "ok": result.is_valid,
                "issue_count": result.issue_count,
                "shape_issue_count": len(result.shape_messages),
                "launcher_issue_count": len(result.launcher_messages),
                "issues": [message.to_dict() for message in result.messages],
            }
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "check-launcher":
        payload = check_launcher_path(args.launcher_path)
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "release-readiness":
        from patchops.readiness import (
            build_release_readiness_snapshot,
            release_readiness_as_dict,
            render_release_readiness_report_lines,
            write_release_readiness_report,
        )

        wrapper_root = (
            Path(args.wrapper_root).resolve()
            if args.wrapper_root
            else Path(__file__).resolve().parents[1]
        )
        profile_summaries = list_profile_summaries(wrapper_project_root=wrapper_root)
        available_profiles = [item["name"] for item in profile_summaries]
        core_tests_state = "green" if args.core_tests_green else "unknown"

        snapshot = build_release_readiness_snapshot(
            wrapper_root,
            available_profiles=available_profiles,
            core_tests_state=core_tests_state,
        )
        payload = release_readiness_as_dict(snapshot)
        payload["wrapper_project_root"] = str(wrapper_root)
        payload["profile_summaries"] = (
            [get_profile_summary(args.profile, wrapper_project_root=wrapper_root)]
            if args.profile
            else profile_summaries
        )
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
        return 0 if payload["status"] != "not_ready" else 1

    if args.command == "profiles":
        if args.name:
            summary = get_profile_summary(args.name, wrapper_project_root=args.wrapper_root)
            print(json.dumps(summary, indent=2))
        else:
            summaries = list_profile_summaries(wrapper_project_root=args.wrapper_root)
            print(json.dumps(summaries, indent=2))
        return 0

    if args.command == "template":
        template = build_manifest_template(
            profile_name=args.profile,
            wrapper_project_root=args.wrapper_root,
            mode=args.mode,
            patch_name=args.patch_name,
            target_root=args.target_root,
        )
        if args.output_path:
            written_path = _write_json_file(args.output_path, template)
            print(json.dumps({
                "written": True,
                "output_path": str(written_path),
                "active_profile": template["active_profile"],
                "patch_name": template["patch_name"],
                "mode": args.mode,
            }, indent=2))
        else:
            print(json.dumps(template, indent=2))
        return 0

    if args.command == "doctor":
        result = run_doctor(profile_name=args.profile, target_root=args.target_root)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "examples":
        result = list_examples(profile_name=args.profile)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "schema":
        payload = build_manifest_schema_summary()
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "init-project-doc":
        from patchops.project_packets import scaffold_project_packet

        payload = scaffold_project_packet(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            runtime_path=args.runtime_path,
            wrapper_project_root=args.wrapper_root,
            output_path=args.output_path,
            initial_goals=args.initial_goal,
        )
        print(json.dumps(payload, indent=2))
        return 0


    if args.command == "refresh-project-doc":
        from patchops.project_packets import refresh_project_packet

        payload = refresh_project_packet(
            project_name=args.project_name,
            wrapper_project_root=args.wrapper_root,
            packet_path=args.packet_path,
            handoff_json_path=args.handoff_json_path,
            latest_report_path=args.report_path,
            current_phase=args.current_phase,
            current_objective=args.current_objective,
            latest_passed_patch=args.latest_passed_patch,
            latest_attempted_patch=args.latest_attempted_patch,
            current_recommendation=args.current_recommendation,
            next_action=args.next_action,
            current_blockers=args.blocker,
            outstanding_risks=args.risk,
        )
        print(json.dumps(payload, indent=2))
        return 0


    if args.command == "bootstrap-target":
        import argparse

        from patchops.project_packets import build_onboarding_bootstrap

        bootstrap_parser = argparse.ArgumentParser(prog="patchops bootstrap-target")
        bootstrap_parser.add_argument("--project-name", required=True)
        bootstrap_parser.add_argument("--target-root", required=True)
        bootstrap_parser.add_argument("--profile", required=True)
        bootstrap_parser.add_argument("--wrapper-root", default=".")
        bootstrap_parser.add_argument("--runtime-override", default=None)
        bootstrap_parser.add_argument("--starter-intent", default="documentation_patch")
        bootstrap_parser.add_argument("--initial-goal", action="append", default=[])

        bootstrap_argv = sys.argv[2:] if argv is None else argv[1:]
        bootstrap_args = bootstrap_parser.parse_args(bootstrap_argv)

        payload = build_onboarding_bootstrap(
            project_name=bootstrap_args.project_name,
            target_root=bootstrap_args.target_root,
            profile_name=bootstrap_args.profile,
            wrapper_project_root=bootstrap_args.wrapper_root,
            runtime_path=bootstrap_args.runtime_override,
            initial_goals=list(bootstrap_args.initial_goal or []),
            current_stage="Initial onboarding",
        )
        print(json.dumps(payload, indent=2))
        return 0
    if args.command == "bootstrap-target":
        from patchops.project_packets import build_onboarding_bootstrap

        payload = build_onboarding_bootstrap(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            runtime_path=args.runtime_path,
            wrapper_project_root=args.wrapper_root,
            initial_goals=args.initial_goal,
            current_stage=args.current_stage,
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


    if args.command == "bundle-entry":
        bundle_root = Path(args.bundle_root).resolve()
        metadata = resolve_bundle_execution_metadata(bundle_root)
        workflow_mode = resolve_bundle_workflow_mode(metadata)

        commands = [
            ["check-bundle", str(bundle_root)],
            ["check", str(metadata.manifest_path)],
            ["inspect", str(metadata.manifest_path)],
            ["plan", str(metadata.manifest_path)],
        ]
        final_command = [workflow_mode, str(metadata.manifest_path)]
        if args.wrapper_root:
            final_command.extend(["--wrapper-root", args.wrapper_root])
        commands.append(final_command)

        for nested_argv in commands:
            exit_code = main(nested_argv)
            if exit_code != 0:
                return exit_code
        return 0
    if args.command == "make-bundle":
        wrapper_root = (
            str(Path(args.wrapper_root).resolve())
            if args.wrapper_root
            else str(Path(__file__).resolve().parents[1])
        )
        target_root = args.target_root or wrapper_root
        result = create_starter_bundle(
            args.bundle_root,
            patch_name=args.patch_name,
            target_project=args.target_project,
            target_project_root=target_root,
            wrapper_project_root=wrapper_root,
            recommended_profile=args.profile,
            mode=args.mode,
        )
        self_check = run_bundle_authoring_self_check(result.bundle_root)
        payload = {
            "bundle_root": str(result.bundle_root),
            "manifest_path": str(result.manifest_path),
            "bundle_meta_path": str(result.bundle_meta_path),
            "readme_path": str(result.readme_path),
            "launcher_path": str(result.launcher_path),
            "content_root": str(result.content_root),
            "patch_name": args.patch_name,
            "target_project": args.target_project,
            "target_project_root": target_root,
            "wrapper_project_root": wrapper_root,
            "recommended_profile": args.profile,
            "bundle_mode": args.mode,
            "ok": self_check.is_valid,
            "issue_count": self_check.issue_count,
            "issues": [message.to_dict() for message in self_check.messages],
        }
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "build-bundle":
        result = build_bundle_zip(args.bundle_root, args.output)
        payload = {
            "bundle_root": str(result.bundle_root),
            "output_zip": str(result.output_zip),
            "root_folder_name": result.root_folder_name,
            "member_count": result.member_count,
            "ok": result.ok,
            "issue_count": result.issue_count,
            "issues": [message.to_dict() for message in result.issues],
        }
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "bundle-doctor":
        result = run_bundle_doctor(args.bundle_path)
        payload = result.to_dict()
        print(json.dumps(payload, indent=2))
        return 0 if payload["ok"] else 1

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

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())




