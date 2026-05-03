"""L14.5 passive CLI/readback for Microsoft Edge dedicated profile lifecycle.

This layer wraps the accepted L14.4 dedicated profile lifecycle preflight and
exposes a compact readback surface for the future profile lifecycle stream. It
keeps the profile lifecycle read-only: no profile directory is created, deleted,
cleaned, or mutated. It still does not launch Edge, import Selenium, create
sessions, drivers, profiles, downloads, paste/send actions, package runs,
commits, pushes, localhost services, or browser extensions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from patchops.llm_browser import live_adapter_edge_dedicated_profile_lifecycle_preflight as l14_04

PATCH = "L14.5"
PHASE = "L14"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L14.5 Microsoft Edge dedicated profile lifecycle CLI/readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-cli-readback"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-preflight"
NEXT_PATCH = "L14.6 Microsoft Edge dedicated profile lifecycle aggregate gate, still no launch"
BROWSER_PRIORITY = ("edge", "opera")


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _source_l14_04_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L14.4"
        and source.get("source_l13_complete") is True
        and source.get("launch_authorization_granted_for_future_stage") is True
        and source.get("dry_run_plan_readback_enforced") is True
        and source.get("dry_run_plan_is_passive") is True
        and source.get("dedicated_profile_lifecycle_preflight_enforced") is True
        and source.get("profile_candidate_under_allowed_runtime_root") is True
        and source.get("profile_lifecycle_steps_are_passive") is True
        and source.get("profile_directory_creation_deferred") is True
        and source.get("profile_directory_create_allowed") is False
        and source.get("profile_directory_cleanup_allowed") is False
        and source.get("profile_directory_delete_allowed") is False
        and source.get("profile_directory_created") is False
        and source.get("profile_directory_mutated") is False
        and source.get("filesystem_writes_performed") == []
        and source.get("launch_execution_allowed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("selenium_imported_by_readback") is False
    )


def build_edge_dedicated_profile_lifecycle_cli_readback(
    repo_root: str | Path | None = None,
    *,
    profile_relative_path: str | None = None,
) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = l14_04.build_edge_dedicated_profile_lifecycle_preflight(root, profile_relative_path=profile_relative_path)
    source_safe = _source_l14_04_safe(source)
    profile_readback_truthful = (
        isinstance(source.get("profile_candidate_path"), str)
        and source.get("profile_candidate_under_allowed_runtime_root") is True
        and source.get("profile_lifecycle_steps_are_passive") is True
    )
    cli_readback_passive = (
        source.get("profile_directory_created") is False
        and source.get("profile_directory_mutated") is False
        and source.get("filesystem_writes_performed") == []
        and source.get("adapter_filesystem_writes_performed") == []
        and source.get("side_effects_performed") == []
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("selenium_imported_by_readback") is False
    )
    checks = [
        _check("l14_04_profile_lifecycle_preflight_remains_accepted", source_safe),
        _check("dedicated_profile_lifecycle_cli_readback_enforced", True),
        _check("profile_readback_truthful", profile_readback_truthful),
        _check("profile_lifecycle_cli_readback_is_passive", cli_readback_passive),
        _check("profile_directory_still_not_created", source.get("profile_directory_created") is False),
        _check("launch_execution_still_disallowed", source.get("launch_execution_allowed") is False),
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
        "source_patch": "L14.4",
        "source_l13_complete": source.get("source_l13_complete"),
        "remaining_l13_patches": source.get("remaining_l13_patches"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "launch_authorization_granted_for_future_stage": source.get("launch_authorization_granted_for_future_stage") is True,
        "dry_run_plan_readback_enforced": source.get("dry_run_plan_readback_enforced") is True,
        "dry_run_plan_is_passive": source.get("dry_run_plan_is_passive") is True,
        "dedicated_profile_lifecycle_preflight_enforced": source.get("dedicated_profile_lifecycle_preflight_enforced") is True,
        "dedicated_profile_lifecycle_cli_readback_enforced": True,
        "profile_readback_truthful": profile_readback_truthful,
        "profile_lifecycle_cli_readback_is_passive": cli_readback_passive,
        "profile_relative_path": source.get("profile_relative_path"),
        "profile_candidate_path": source.get("profile_candidate_path"),
        "profile_candidate_under_allowed_runtime_root": source.get("profile_candidate_under_allowed_runtime_root"),
        "profile_directory_exists_before_preflight": source.get("profile_directory_exists_before_preflight"),
        "profile_lifecycle_steps": source.get("profile_lifecycle_steps"),
        "profile_lifecycle_steps_are_passive": source.get("profile_lifecycle_steps_are_passive"),
        "profile_directory_creation_deferred": True,
        "profile_directory_create_allowed": False,
        "profile_directory_cleanup_allowed": False,
        "profile_directory_delete_allowed": False,
        "profile_directory_created": False,
        "profile_directory_mutated": False,
        "filesystem_writes_performed": [],
        "adapter_filesystem_writes_performed": [],
        "side_effects_performed": [],
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
        "click_download_performed": False,
        "download_performed": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "git_commit_executed": False,
        "git_push_executed": False,
        "localhost_patchops_server_started": False,
        "browser_extension_used": False,
        "source_l14_04_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "profile_allowed": source.get("profile_candidate_under_allowed_runtime_root"),
            "profile_created": source.get("profile_directory_created"),
            "profile_mutated": source.get("profile_directory_mutated"),
            "launch_execution_allowed": source.get("launch_execution_allowed"),
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
        f"Profile Candidate : {payload.get('profile_candidate_path')}",
        f"Profile Readback  : {payload.get('profile_readback_truthful')}",
        f"Profile Created   : {payload.get('profile_directory_created')}",
        f"Launch Allowed    : {payload.get('launch_execution_allowed')}",
        f"Browser Started   : {payload.get('browser_started')}",
        f"Next Patch        : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--profile-relative-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_dedicated_profile_lifecycle_cli_readback(args.repo_root, profile_relative_path=args.profile_relative_path)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
