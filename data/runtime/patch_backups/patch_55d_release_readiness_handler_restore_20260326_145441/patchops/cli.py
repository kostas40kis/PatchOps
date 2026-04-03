from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from patchops.manifest_checks import check_manifest_path
from patchops.manifest_loader import load_manifest
from patchops.manifest_templates import build_manifest_template
from patchops.planning import plan_manifest
from patchops.profile_summary import get_profile_summary, list_profile_summaries
from patchops.workflows.apply_patch import apply_manifest
from patchops.workflows.verify_only import verify_only
from patchops.workflows.wrapper_retry import execute_wrapper_only_retry
from patchops.doctor import run_doctor
from patchops.examples_index import list_examples
from patchops.manifest_reference import build_manifest_schema_summary


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
    doctor_parser.description = "Inspect environment and profile readiness before template, check, plan, apply, verify, or wrapper-retry."
    doctor_parser.add_argument("--profile", default="trader", help="Profile name to inspect")
    doctor_parser.add_argument("--target-root", default=None, help="Optional target project root override")

    examples_parser = subparsers.add_parser("examples", help="List bundled example manifests")
    examples_parser.description = "List bundled example manifests and their intended usage."
    examples_parser.add_argument("--profile", default=None, help="Optional profile filter")

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
    # PATCHOPS_PATCH55_RELEASE_READINESS_PARSER:END

    schema_parser = subparsers.add_parser("schema", help="Print manifest field reference and starter guidance")
    schema_parser.description = "Print a stable manifest field reference and starter guidance for PatchOps manifests."

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

    if args.command == "release-readiness":

        print(json.dumps(payload, indent=2))
        return 0 if payload["status"] != "not_ready" else 1

    if args.command == "schema":
        payload = build_manifest_schema_summary()
        print(json.dumps(payload, indent=2))
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())