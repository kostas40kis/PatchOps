from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from patchops.planning import build_execution_plan
from patchops.workflows.apply_patch import apply_manifest
from patchops.workflows.verify_only import verify_only


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchops")
    subparsers = parser.add_subparsers(dest="command", required=True)

    apply_parser = subparsers.add_parser("apply", help="Apply a manifest-driven patch")
    apply_parser.add_argument("manifest", help="Path to the manifest JSON file")
    apply_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)

    verify_parser = subparsers.add_parser("verify", help="Run verify-only flow")
    verify_parser.add_argument("manifest", help="Path to the manifest JSON file")
    verify_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)

    inspect_parser = subparsers.add_parser("inspect", help="Load a manifest and print normalized JSON")
    inspect_parser.add_argument("manifest", help="Path to the manifest JSON file")

    plan_parser = subparsers.add_parser(
        "plan",
        help="Resolve a manifest into a pre-apply execution preview without writing files or running commands",
    )
    plan_parser.add_argument("manifest", help="Path to the manifest JSON file")
    plan_parser.add_argument(
        "--mode",
        choices=["apply", "verify"],
        default="apply",
        help="Preview the resolved apply or verify plan",
    )
    plan_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)

    return parser


def _print_run_summary(result) -> None:
    manifest_path = getattr(result, "manifest_path", None)
    if manifest_path is None:
        manifest_path = Path.cwd()

    print(f"Mode               : {result.mode}")
    print(f"Patch Name         : {result.manifest.patch_name}")
    print(f"Manifest Path      : {manifest_path}")
    print(f"Active Profile     : {result.resolved_profile.name}")
    print(f"Target Project Root: {result.target_project_root}")
    print(f"Report Path        : {result.report_path}")
    print(f"ExitCode           : {result.exit_code}")
    print(f"Result             : {result.result_label}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "apply":
        result = apply_manifest(args.manifest, wrapper_project_root=args.wrapper_root)
        _print_run_summary(result)
        return result.exit_code

    if args.command == "verify":
        result = verify_only(args.manifest, wrapper_project_root=args.wrapper_root)
        _print_run_summary(result)
        return result.exit_code

    if args.command == "inspect":
        from patchops.manifest_loader import load_manifest

        manifest = load_manifest(Path(args.manifest))
        print(json.dumps(asdict(manifest), indent=2))
        return 0

    if args.command == "plan":
        plan = build_execution_plan(
            args.manifest,
            wrapper_project_root=args.wrapper_root,
            mode=args.mode,
        )
        print(json.dumps(plan, indent=2))
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())