from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from patchops.doctor import run_doctor
from patchops.examples_index import list_examples
from patchops.manifest_checks import check_manifest_path
from patchops.manifest_loader import load_manifest
from patchops.manifest_reference import build_manifest_schema_summary
from patchops.manifest_templates import build_manifest_template
from patchops.planning import plan_manifest
from patchops.profile_summary import get_profile_summary, list_profile_summaries
from patchops.workflows.apply_patch import apply_manifest
from patchops.workflows.verify_only import verify_only
from patchops.workflows.wrapper_retry import execute_wrapper_only_retry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchops")
    subparsers = parser.add_subparsers(dest="command", required=True)

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
    bootstrap_target_parser.add_argument("--starter-intent", default="documentation_patch", help="Starter manifest intent")
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

    return parser


def _display_value(value: Any) -> str:
    if value is None:
        return "(none)"
    return str(value)


def _build_run_summary(result: Any, manifest_path: str | Path) -> str:
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
        f"ExitCode           : {_display_value(getattr(result, 'exit_code', None))}",
        f"Result             : {_display_value(getattr(result, 'result_label', None))}",
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
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "apply":
        result = apply_manifest(args.manifest, wrapper_project_root=args.wrapper_root)
        print(_build_run_summary(result, args.manifest))
        return int(result.exit_code)

    if args.command == "verify":
        result = verify_only(args.manifest, wrapper_project_root=args.wrapper_root)
        print(_build_run_summary(result, args.manifest))
        return int(result.exit_code)

    if args.command == "wrapper-retry":
        result = execute_wrapper_only_retry(
            args.manifest,
            wrapper_project_root=args.wrapper_root,
            reason=args.retry_reason,
        )
        print(_build_run_summary(result, args.manifest))
        return int(result.exit_code)


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
        from patchops.project_packets import bootstrap_target_onboarding

        payload = bootstrap_target_onboarding(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            runtime_override=args.runtime_path,
            wrapper_project_root=args.wrapper_root,
            initial_goals=args.initial_goal,
            starter_intent=args.starter_intent,
        )
        print(json.dumps(payload, indent=2))
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

    raise SystemExit(main())
