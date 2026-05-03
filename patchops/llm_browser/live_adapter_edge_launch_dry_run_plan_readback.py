"""L14.3 passive Microsoft Edge supervised-launch dry-run plan readback.

This layer consumes the accepted L14.2 authorization gate and emits a dry-run
launch plan for a future Microsoft Edge supervised-launch stage. The dry-run plan
is readback only: it does not build a real subprocess invocation, launch Edge,
import Selenium, create sessions, drivers, profiles, downloads, paste/send
actions, package runs, commits, pushes, localhost services, or browser
extensions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from patchops.llm_browser import live_adapter_edge_launch_authorization_gate as l14_02

PATCH = "L14.3"
PHASE = "L14"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L14.3 Microsoft Edge supervised launch dry-run plan readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-launch-dry-run-plan-readback"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-launch-authorization-gate"
NEXT_PATCH = "L14.4 Microsoft Edge dedicated profile lifecycle preflight, still no launch"
AUTHORIZATION_TOKEN = "EDGE_LAUNCH_AUTH_REVIEWED_NO_EXECUTION"
BROWSER_PRIORITY = ("edge", "opera")

DRY_RUN_PLAN_STEPS = (
    "verify_l13_complete",
    "verify_l14_01_readiness_consolidated",
    "verify_l14_02_authorization_gate",
    "resolve_edge_executable_from_existing_l13_read_only_probe_evidence",
    "prepare_future_dedicated_profile_preflight_inputs",
    "prepare_future_supervised_launch_arguments_readback_only",
    "stop_before_any_process_start",
)


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _source_l14_02_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L14.2"
        and source.get("source_l13_complete") is True
        and source.get("launch_readiness_consolidated") is True
        and source.get("launch_authorization_gate_enforced") is True
        and source.get("launch_authorization_granted_for_future_stage") is True
        and source.get("launch_authorization_effective_for_execution") is False
        and source.get("launch_execution_allowed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("selenium_imported_by_readback") is False
        and source.get("profile_directory_created") is False
    )


def _dry_run_plan() -> list[dict[str, Any]]:
    return [
        {"step": step, "status": "planned", "execution_allowed": False, "side_effect_allowed": False}
        for step in DRY_RUN_PLAN_STEPS
    ]


def build_edge_launch_dry_run_plan_readback(
    repo_root: str | Path | None = None,
    *,
    request_launch_authorization: bool = False,
    operator_confirmation_token: str | None = None,
) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = l14_02.build_edge_launch_authorization_gate(
        root,
        request_launch_authorization=request_launch_authorization,
        operator_confirmation_token=operator_confirmation_token,
    )
    source_safe = _source_l14_02_safe(source)
    plan = _dry_run_plan()
    plan_passive = all(item.get("execution_allowed") is False and item.get("side_effect_allowed") is False for item in plan)
    launch_plan_materialized_as_process_args = False
    checks = [
        _check("l14_02_authorization_gate_remains_accepted", source_safe),
        _check("dry_run_plan_readback_enforced", True),
        _check("dry_run_plan_is_passive", plan_passive),
        _check("dry_run_plan_not_materialized_as_process_args", not launch_plan_materialized_as_process_args),
        _check("launch_execution_still_disallowed", True),
        _check("no_live_browser_behavior", True),
        _check("compact_json_readback_available", True),
    ]
    ok = all(item["ok"] for item in checks)
    return {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "source_patch": "L14.2",
        "source_l13_complete": source.get("source_l13_complete"),
        "remaining_l13_patches": source.get("remaining_l13_patches"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "launch_readiness_consolidated": source.get("launch_readiness_consolidated") is True,
        "launch_authorization_gate_enforced": source.get("launch_authorization_gate_enforced") is True,
        "launch_authorization_granted_for_future_stage": source.get("launch_authorization_granted_for_future_stage") is True,
        "launch_authorization_effective_for_execution": False,
        "dry_run_plan_readback_enforced": True,
        "dry_run_plan": plan,
        "dry_run_plan_steps": list(DRY_RUN_PLAN_STEPS),
        "dry_run_plan_is_passive": plan_passive,
        "dry_run_plan_executed": False,
        "dry_run_plan_materialized_as_process_args": launch_plan_materialized_as_process_args,
        "real_subprocess_invocation_built": False,
        "browser_process_launch_requested": False,
        "browser_process_launch_authorized": False,
        "launch_execution_allowed": False,
        "operator_review_required_before_live_start": True,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "adapter_filesystem_writes_performed": [],
        "side_effects_performed": [],
        "click_download_performed": False,
        "download_performed": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "git_commit_executed": False,
        "git_push_executed": False,
        "localhost_patchops_server_started": False,
        "browser_extension_used": False,
        "source_l14_02_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "future_stage_granted": source.get("launch_authorization_granted_for_future_stage"),
            "execution_allowed": source.get("launch_execution_allowed"),
        },
        "checks": checks,
        "executed_validation_commands": [],
        "next_patch": NEXT_PATCH,
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        f"Status            : {payload.get('status')}",
        f"Command           : {payload.get('command_name')}",
        f"Source Patch      : {payload.get('source_patch')}",
        f"Future Auth       : {payload.get('launch_authorization_granted_for_future_stage')}",
        f"Plan Passive      : {payload.get('dry_run_plan_is_passive')}",
        f"Plan Executed     : {payload.get('dry_run_plan_executed')}",
        f"Launch Allowed    : {payload.get('launch_execution_allowed')}",
        f"Browser Started   : {payload.get('browser_started')}",
        f"Next Patch        : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--request-launch-authorization", action="store_true")
    parser.add_argument("--operator-confirmation-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_launch_dry_run_plan_readback(
        args.repo_root,
        request_launch_authorization=args.request_launch_authorization,
        operator_confirmation_token=args.operator_confirmation_token,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
