from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from . import dependency_check
from .config import DEFAULT_CHAT_URL, build_browser_run_config
from . import edge_controller
from . import opera_controller


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchops llm-browser")
    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser(
        "doctor",
        help="Check optional browser-runner dependencies without opening a browser.",
    )
    doctor.add_argument("--browser", choices=("edge", "opera", "both", "none"), default="edge")
    doctor.add_argument("--wrapper-root", default=None)
    doctor.add_argument("--target-root", default=None)
    doctor.add_argument("--download-dir", default=None)
    doctor.add_argument("--json", action="store_true")

    open_cmd = subparsers.add_parser(
        "open",
        help="Open a supported browser in a dedicated PatchOps automation profile.",
    )
    open_cmd.add_argument("--browser", choices=("edge", "opera"), default="edge")
    open_cmd.add_argument("--wrapper-root", required=True)
    open_cmd.add_argument("--target-root", default=None)
    open_cmd.add_argument("--download-dir", required=True)
    open_cmd.add_argument("--profile-root", default=None)
    open_cmd.add_argument("--profile-dir", default=None)
    open_cmd.add_argument("--profile-name", default="chatgpt_default")
    open_cmd.add_argument("--chat-url", default=DEFAULT_CHAT_URL)
    open_cmd.add_argument("--auto-download", action="store_true")
    open_cmd.add_argument("--auto-paste", action="store_true")
    # Deliberately no --auto-send flag in D0.7.

    return parser


def run_doctor(args: argparse.Namespace) -> int:
    report = dependency_check.build_dependency_report(
        wrapper_root=args.wrapper_root,
        target_root=args.target_root,
        download_dir=args.download_dir,
        browser=args.browser,
    )
    if args.json:
        print(json.dumps(report.to_payload(), indent=2))
    else:
        print(dependency_check.render_dependency_report(report), end="")
    return report.exit_code


def run_open(args: argparse.Namespace) -> int:
    config = build_browser_run_config(
        browser=args.browser,
        wrapper_root=Path(args.wrapper_root),
        target_root=None if args.target_root is None else Path(args.target_root),
        download_dir=Path(args.download_dir),
        profile_root=None if args.profile_root is None else Path(args.profile_root),
        profile_dir=None if args.profile_dir is None else Path(args.profile_dir),
        profile_name=args.profile_name,
        chat_url=args.chat_url,
        auto_download=args.auto_download,
        auto_paste=args.auto_paste,
        auto_send=False,
        create_profile_dir=True,
    )

    if args.browser == "edge":
        result = edge_controller.open_edge(config)
        print(json.dumps(result.to_payload(), indent=2))
        return 0

    if args.browser == "opera":
        result = opera_controller.open_opera(config)
        print(json.dumps(result.to_payload(), indent=2))
        return 0

    raise ValueError(f"unsupported browser: {args.browser}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "doctor":
        return run_doctor(args)
    if args.command == "open":
        return run_open(args)

    parser.print_help()
    return 0
