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
    bootstrap_target_parser = subparsers.add_parser(
        "bootstrap-target",
        help="Generate onboarding bootstrap artifacts for a target project",
    )
    bootstrap_target_parser.description = (
        "Generate onboarding artifacts parallel to handoff for a target project."
    )
    bootstrap_target_parser.add_argument("--project-name", required=True, help="Human-readable target project name")
    bootstrap_target_parser.add_argument("--target-root", required=True, help="Target project root")
    bootstrap_target_parser.add_argument("--profile", required=True, help="PatchOps profile to anchor the onboarding bundle")
    bootstrap_target_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)
    bootstrap_target_parser.add_argument("--runtime-path", default=None, help="Optional runtime override")
    bootstrap_target_parser.add_argument(
        "--initial-goal",
        action="append",
        default=[],
        help="Optional onboarding goal line; may be supplied more than once.",
    )
    bootstrap_target_parser.add_argument(
        "--starter-intent",
        default="documentation_patch",
        help="Starter manifest intent label written into onboarding artifacts.",
    )

    return parser

    if args.command == "bootstrap-target":
        from patchops.project_packets import bootstrap_target_onboarding

        payload = bootstrap_target_onboarding(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            wrapper_project_root=args.wrapper_root,
            initial_goals=args.initial_goal,
            runtime_override=args.runtime_path,
            starter_intent=args.starter_intent,
        )
        print(json.dumps(payload, indent=2))
        return 0
