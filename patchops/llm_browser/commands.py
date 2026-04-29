from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from . import dependency_check
from .audit_log import AuditLog, event_from_dry_run_result, event_from_integration_result
from .broad_validation_report import (
    parse_broad_validation_report_file,
    render_broad_validation_report_summary,
)
from .config import DEFAULT_CHAT_URL, build_browser_run_config
from .dry_mode_checkpoint import evaluate_dry_mode_checkpoint, render_checkpoint_report
from .dry_mode_release_gate import evaluate_dry_mode_release_gate, render_release_gate_report
from . import edge_controller
from . import opera_controller
from .chat_page_contract import snapshot_from_file, snapshot_from_html
from .dry_run_orchestrator import dry_run_orchestrate_once
from .patchops_runner import PatchOpsRunCommand, PatchOpsRunResult
from .report_locator import CanonicalReportLocation, parse_report_summary
from .runner_integration import (
    BrowserRunnerAdapters,
    BrowserRunnerIntegrationOptions,
    BrowserRunnerSafetyPolicy,
    run_browser_runner_integration_once,
)


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
    # Deliberately no --auto-send flag.

    dry_run = subparsers.add_parser(
        "dry-run",
        help="Run the browser-runner decision loop from saved/synthetic metadata without side effects.",
    )
    snapshot_group = dry_run.add_mutually_exclusive_group(required=True)
    snapshot_group.add_argument("--snapshot-file", default=None, help="HTML snapshot file to inspect.")
    snapshot_group.add_argument("--snapshot-html", default=None, help="Inline HTML snapshot to inspect.")
    dry_run.add_argument("--browser", choices=("edge", "opera"), default="edge")
    dry_run.add_argument("--processed-artifact", action="append", default=[])
    dry_run.add_argument("--downloaded-path", default=None)
    dry_run.add_argument("--runner-status", choices=("pass", "fail"), default=None)
    dry_run.add_argument("--runner-reason", default=None)
    dry_run.add_argument("--runner-exit-code", type=int, default=None)
    dry_run.add_argument("--report-path", default=None)
    dry_run.add_argument("--audit-log", default=None, help="Append one compact JSONL dry-run audit event to this path.")
    dry_run.add_argument("--audit-source", default="llm_browser_dry_run_cli")
    dry_run.add_argument("--json", action="store_true")
    dry_run.add_argument("--strict", action="store_true", help="Return nonzero when the dry run blocks.")

    run_once = subparsers.add_parser(
        "run-once",
        help="Run one browser-runner integration pass. D0.23 supports dry-run mode only.",
    )
    run_once.add_argument("--dry-run", action="store_true", help="Required in D0.23; do not perform side effects.")
    snapshot_group = run_once.add_mutually_exclusive_group()
    snapshot_group.add_argument("--snapshot-file", default=None, help="HTML snapshot file to inspect in dry-run mode.")
    snapshot_group.add_argument("--snapshot-html", default=None, help="Inline HTML snapshot to inspect in dry-run mode.")
    run_once.add_argument("--browser", choices=("edge", "opera"), default="edge")
    run_once.add_argument("--processed-artifact", action="append", default=[])
    run_once.add_argument("--audit-log", default=None, help="Append one compact JSONL integration audit event to this path.")
    run_once.add_argument("--audit-source", default="llm_browser_run_once_cli")
    run_once.add_argument("--json", action="store_true")
    run_once.add_argument("--strict", action="store_true", help="Return nonzero when the integration dry run blocks.")
    run_once.add_argument("--allow-download-click", action="store_true", help=argparse.SUPPRESS)
    run_once.add_argument("--allow-patchops-run", action="store_true", help=argparse.SUPPRESS)
    run_once.add_argument("--allow-paste", action="store_true", help=argparse.SUPPRESS)
    # Deliberately no --auto-send / --allow-send option.

    audit = subparsers.add_parser(
        "audit-log",
        help="Read compact llm-browser audit JSONL events without side effects.",
    )
    audit.add_argument("--path", default=None, help="Audit JSONL path. Defaults to the configured llm-browser audit path.")
    audit.add_argument("--limit", type=int, default=10, help="Maximum number of latest events to display. Use 0 for all.")
    audit.add_argument("--event-type", default=None, help="Filter by event_type.")
    audit.add_argument("--status", default=None, help="Filter by status, such as PASS, FAIL, or UNKNOWN.")
    audit.add_argument("--json", action="store_true")
    # Deliberately no mutation, cleanup, browser, or send flags.

    release_gate = subparsers.add_parser(
        "release-gate",
        help="Run the passive dry-mode browser-runner release gate.",
    )
    release_gate.add_argument("--repo-root", default=None, help="Repository root used for documentation checks.")
    release_gate.add_argument("--json", action="store_true")
    # The release gate exits nonzero when checks fail.

    checkpoint = subparsers.add_parser(
        "checkpoint",
        help="Show passive commit and broad-validation checkpoint guidance.",
    )
    checkpoint.add_argument("--repo-root", default=None, help="Repository root used for release-gate and git status checks.")
    checkpoint.add_argument("--commit-message", default="D0.29 checkpoint browser runner dry mode")
    checkpoint.add_argument("--json", action="store_true")
    # Deliberately no --commit, --push, --run-tests, --auto-send, or --live flag.

    broad_report = subparsers.add_parser(
        "broad-report",
        help="Parse a llm-browser broad-validation txt report.",
    )
    broad_report.add_argument("--path", required=True, help="Path to a broad-validation txt report.")
    broad_report.add_argument("--json", action="store_true")
    broad_report.add_argument("--strict", action="store_true", help="Return nonzero when the parsed report is not PASS.")

    return parser


def llm_browser_command_names() -> tuple[str, ...]:
    return ("doctor", "open", "dry-run", "run-once", "audit-log", "release-gate", "checkpoint", "broad-report")


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


def _load_snapshot(args: argparse.Namespace):
    if getattr(args, "snapshot_file", None):
        return snapshot_from_file(args.snapshot_file)
    if getattr(args, "snapshot_html", None):
        return snapshot_from_html(args.snapshot_html)
    raise ValueError("dry mode requires --snapshot-file or --snapshot-html")


def _build_dry_run_runner_result(args: argparse.Namespace) -> PatchOpsRunResult | None:
    if getattr(args, "runner_status", None) is None:
        return None

    downloaded_path = Path(args.downloaded_path or "dry_run_downloaded_patchops_bundle.zip")
    wrapper_root = Path.cwd()
    ok = args.runner_status == "pass"
    reason = args.runner_reason or ("success" if ok else "patchops_payload_ok_false")
    exit_code = args.runner_exit_code
    if exit_code is None:
        exit_code = 0 if ok else 1

    command = PatchOpsRunCommand(
        command=(
            "dry-run",
            "patchops.cli",
            "run-package",
            str(downloaded_path),
            "--wrapper-root",
            str(wrapper_root),
        ),
        cwd=wrapper_root,
        timeout_seconds=0.0,
        artifact_path=downloaded_path,
        wrapper_root=wrapper_root,
    )
    return PatchOpsRunResult(
        command=command,
        exit_code=exit_code,
        stdout=json.dumps({"ok": ok}),
        stderr="",
        timed_out=False,
        ok=ok,
        reason=reason,
        report_path=args.report_path,
        failure_category=None if ok else "target_content_failure",
        parsed_payload={"ok": ok},
    )


def _build_dry_run_report_location(args: argparse.Namespace) -> CanonicalReportLocation | None:
    if getattr(args, "report_path", None) is None:
        return None

    path = Path(args.report_path)
    if path.exists() and path.is_file():
        summary = parse_report_summary(path)
        return CanonicalReportLocation(
            found=True,
            path=path,
            reason="explicit_report_path_found",
            source="dry_run_cli",
            summary=summary,
            candidates_seen=(path,),
        )

    return CanonicalReportLocation(
        found=False,
        path=None,
        reason="explicit_report_paths_missing",
        source="dry_run_cli",
        summary=None,
        candidates_seen=(path,),
    )


def _append_audit_if_requested(path: str | None, event) -> None:
    if path:
        AuditLog(path).append_event(event)


def run_dry_run(args: argparse.Namespace) -> int:
    snapshot = _load_snapshot(args)
    runner_result = _build_dry_run_runner_result(args)
    report_location = _build_dry_run_report_location(args)

    result = dry_run_orchestrate_once(
        snapshot,
        browser=args.browser,
        processed_artifacts=args.processed_artifact,
        downloaded_path=args.downloaded_path,
        runner_result=runner_result,
        report_location=report_location,
    )

    _append_audit_if_requested(
        args.audit_log,
        event_from_dry_run_result(result, source=args.audit_source),
    )

    if args.json:
        print(json.dumps(result.to_payload(), indent=2))
    else:
        print(result.pasteback_summary.text)
        print("")
        print("Planned actions:")
        for action in result.planned_actions:
            print(f"- {action}")
        print("")
        print("Side effects performed: none")
        if args.audit_log:
            print(f"Audit log: {args.audit_log}")

    if args.strict and result.blocked:
        return 1
    return 0


def run_run_once(args: argparse.Namespace) -> int:
    if not args.dry_run:
        print("run-once live mode is not enabled in D0.23. Re-run with --dry-run.")
        return 2

    if not args.snapshot_file and not args.snapshot_html:
        print("run-once --dry-run requires --snapshot-file or --snapshot-html.")
        return 2

    snapshot = _load_snapshot(args)
    options = BrowserRunnerIntegrationOptions(
        browser=args.browser,
        processed_artifacts=tuple(args.processed_artifact or ()),
        dry_run_only=True,
        safety=BrowserRunnerSafetyPolicy(
            allow_download_click=bool(args.allow_download_click),
            allow_patchops_run=bool(args.allow_patchops_run),
            allow_paste=bool(args.allow_paste),
            allow_send=False,
        ),
    )

    result = run_browser_runner_integration_once(
        BrowserRunnerAdapters(snapshot_provider=lambda: snapshot),
        options=options,
    )

    _append_audit_if_requested(
        args.audit_log,
        event_from_integration_result(result, source=args.audit_source),
    )

    if args.json:
        print(json.dumps(result.to_payload(), indent=2))
    else:
        print(result.dry_run.pasteback_summary.text)
        print("")
        print("Integration planned actions:")
        for action in result.dry_run.planned_actions:
            print(f"- {action}")
        print("")
        print("Integration side effects performed: none")
        if args.audit_log:
            print(f"Audit log: {args.audit_log}")

    if args.strict and result.blocked:
        return 1
    return 0


def _filtered_audit_events(args: argparse.Namespace):
    log = AuditLog(args.path)
    events = list(log.read_events(limit=None))

    if args.event_type:
        events = [event for event in events if event.event_type == args.event_type]

    if args.status:
        wanted = args.status.strip().upper()
        events = [event for event in events if (event.status or "").strip().upper() == wanted]

    limit = args.limit
    if limit < 0:
        raise ValueError("--limit must not be negative")
    if limit:
        events = events[-limit:]

    return log, events


def _audit_readback_payload(log: AuditLog, events) -> dict[str, object]:
    return {
        "path": str(log.path),
        "exists": log.path.exists(),
        "count": len(events),
        "events": [event.to_payload() for event in events],
    }


def _render_audit_event(event, index: int) -> list[str]:
    payload = event.to_payload()
    lines: list[str] = []
    header_parts = [
        f"{index}.",
        payload.get("timestamp", ""),
        payload.get("event_type", ""),
    ]
    if payload.get("status"):
        header_parts.append(str(payload["status"]))
    if payload.get("state"):
        header_parts.append(f"state={payload['state']}")
    lines.append(" ".join(str(part) for part in header_parts if str(part)))

    for label, key in (
        ("Patch", "patch"),
        ("Artifact", "artifact_filename"),
        ("Report", "report_path"),
        ("Reason", "reason"),
    ):
        value = payload.get(key)
        if value:
            lines.append(f"   {label}: {value}")

    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        planned = metadata.get("planned_actions")
        if isinstance(planned, list):
            lines.append("   Planned actions: " + ", ".join(str(item) for item in planned))
        side_effects = metadata.get("side_effects_performed")
        if isinstance(side_effects, list):
            rendered = ", ".join(str(item) for item in side_effects) if side_effects else "none"
            lines.append("   Side effects: " + rendered)

    return lines


def run_audit_log(args: argparse.Namespace) -> int:
    log, events = _filtered_audit_events(args)

    if args.json:
        print(json.dumps(_audit_readback_payload(log, events), indent=2))
        return 0

    print(f"Audit log: {log.path}")
    print(f"Exists   : {log.path.exists()}")
    print(f"Events   : {len(events)}")
    print("")
    if not events:
        print("No audit events found.")
        return 0

    for index, event in enumerate(events, start=1):
        for line in _render_audit_event(event, index):
            print(line)
        print("")

    return 0


def run_release_gate(args: argparse.Namespace) -> int:
    report = evaluate_dry_mode_release_gate(
        repo_root=args.repo_root,
        cli_surface_names=llm_browser_command_names(),
    )
    if args.json:
        print(json.dumps(report.to_payload(), indent=2))
    else:
        print(render_release_gate_report(report), end="")
    return report.exit_code


def run_checkpoint(args: argparse.Namespace) -> int:
    report = evaluate_dry_mode_checkpoint(
        repo_root=args.repo_root,
        commit_message=args.commit_message,
    )
    if args.json:
        print(json.dumps(report.to_payload(), indent=2))
    else:
        print(render_checkpoint_report(report), end="")
    return report.exit_code


def run_broad_report(args: argparse.Namespace) -> int:
    report = parse_broad_validation_report_file(args.path)
    if args.json:
        print(json.dumps(report.to_payload(), indent=2))
    else:
        print(render_broad_validation_report_summary(report), end="")
    if args.strict and not report.ok:
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "doctor":
        return run_doctor(args)
    if args.command == "open":
        return run_open(args)
    if args.command == "dry-run":
        return run_dry_run(args)
    if args.command == "run-once":
        return run_run_once(args)
    if args.command == "audit-log":
        return run_audit_log(args)
    if args.command == "release-gate":
        return run_release_gate(args)
    if args.command == "checkpoint":
        return run_checkpoint(args)
    if args.command == "broad-report":
        return run_broad_report(args)

    parser.print_help()
    return 0
