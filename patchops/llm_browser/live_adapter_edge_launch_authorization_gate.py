"""L14.2 passive Microsoft Edge supervised launch authorization gate.

This layer introduces an explicit authorization gate for a future Microsoft Edge
supervised launch stream. It can record that the operator requested and reviewed
launch authorization, but it still does not allow execution, launch Edge, import
Selenium, create sessions, drivers, profiles, downloads, paste/send actions,
package runs, commits, pushes, localhost servers, or browser extensions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from patchops.llm_browser import live_adapter_edge_launch_readiness_consolidation as l14_01

PATCH = "L14.2"
PHASE = "L14"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L14.2 Microsoft Edge supervised launch authorization gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-launch-authorization-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-launch-readiness-consolidation"
NEXT_PATCH = "L14.3 Microsoft Edge supervised launch dry-run plan readback, still no launch"
AUTHORIZATION_TOKEN = "EDGE_LAUNCH_AUTH_REVIEWED_NO_EXECUTION"
BROWSER_PRIORITY = ("edge", "opera")


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _source_l14_01_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L14.1"
        and source.get("launch_readiness_consolidated") is True
        and source.get("source_l13_complete") is True
        and source.get("remaining_l13_patches") == []
        and source.get("browser_process_launch_requested") is False
        and source.get("browser_process_launch_authorized") is False
        and source.get("launch_execution_allowed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("selenium_imported_by_readback") is False
    )


def build_edge_launch_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    request_launch_authorization: bool = False,
    operator_confirmation_token: str | None = None,
) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = l14_01.build_edge_launch_readiness_consolidation(root)
    source_safe = _source_l14_01_safe(source)
    token_valid = operator_confirmation_token == AUTHORIZATION_TOKEN
    authorization_granted_for_future_stage = bool(request_launch_authorization and token_valid)
    authorization_denied_reason = None
    if request_launch_authorization and not token_valid:
        authorization_denied_reason = "missing_or_invalid_operator_confirmation_token"
    elif not request_launch_authorization:
        authorization_denied_reason = "launch_authorization_not_requested"

    checks = [
        _check("l14_01_launch_readiness_consolidation_remains_accepted", source_safe),
        _check("supervised_launch_authorization_gate_enforced", True),
        _check("launch_execution_still_disallowed", True),
        _check("browser_process_launch_still_not_requested", True),
        _check("browser_process_launch_still_not_authorized_for_execution", True),
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
        "source_patch": "L14.1",
        "source_l13_complete": source.get("source_l13_complete"),
        "remaining_l13_patches": source.get("remaining_l13_patches"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "launch_readiness_consolidated": source.get("launch_readiness_consolidated") is True,
        "launch_authorization_gate_enforced": True,
        "supervised_launch_authorization_gate_enforced": True,
        "request_launch_authorization_observed": bool(request_launch_authorization),
        "operator_confirmation_token_required": True,
        "operator_confirmation_token_valid": token_valid,
        "authorization_token_echoed": False,
        "launch_authorization_granted_for_future_stage": authorization_granted_for_future_stage,
        "launch_authorization_denied_reason": authorization_denied_reason,
        "launch_authorization_effective_for_execution": False,
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
        "source_l14_01_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "launch_readiness_consolidated": source.get("launch_readiness_consolidated"),
            "launch_execution_allowed": source.get("launch_execution_allowed"),
        },
        "checks": checks,
        "executed_validation_commands": [],
        "next_patch": NEXT_PATCH,
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        f"Status               : {payload.get('status')}",
        f"Command              : {payload.get('command_name')}",
        f"Source Patch         : {payload.get('source_patch')}",
        f"Launch Auth Requested: {payload.get('request_launch_authorization_observed')}",
        f"Future Auth Granted  : {payload.get('launch_authorization_granted_for_future_stage')}",
        f"Execution Allowed    : {payload.get('launch_execution_allowed')}",
        f"Browser Started      : {payload.get('browser_started')}",
        f"Next Patch           : {payload.get('next_patch')}",
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
    payload = build_edge_launch_authorization_gate(
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
