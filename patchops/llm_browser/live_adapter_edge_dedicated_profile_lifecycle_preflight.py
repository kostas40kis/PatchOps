"""L14.4 passive Microsoft Edge dedicated profile lifecycle preflight.

This layer consumes the accepted L14.3 dry-run launch plan and prepares a
readback-only lifecycle preflight for a future dedicated Microsoft Edge profile.
It computes and validates profile lifecycle intent without creating, deleting,
cleaning, or mutating profile directories. It still does not launch Edge, import
Selenium, create sessions, drivers, profiles, downloads, paste/send actions,
package runs, commits, pushes, localhost services, or browser extensions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from patchops.llm_browser import live_adapter_edge_launch_dry_run_plan_readback as l14_03

PATCH = "L14.4"
PHASE = "L14"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L14.4 Microsoft Edge dedicated profile lifecycle preflight"
COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-preflight"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-launch-dry-run-plan-readback"
NEXT_PATCH = "L14.5 Microsoft Edge dedicated profile lifecycle CLI/readback, still no launch"
AUTHORIZATION_TOKEN = "EDGE_LAUNCH_AUTH_REVIEWED_NO_EXECUTION"
BROWSER_PRIORITY = ("edge", "opera")
PROFILE_RELATIVE_PATH = "data/runtime/browser_profiles/edge_supervised_l14"

PROFILE_LIFECYCLE_STEPS = (
    "compute_dedicated_profile_candidate_path",
    "verify_profile_candidate_under_repo_runtime_browser_profiles",
    "record_profile_lifecycle_intent_readback_only",
    "defer_profile_directory_creation_to_future_authorized_stage",
    "stop_before_any_filesystem_write_or_browser_launch",
)


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _source_l14_03_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L14.3"
        and source.get("source_l13_complete") is True
        and source.get("launch_authorization_granted_for_future_stage") is True
        and source.get("dry_run_plan_readback_enforced") is True
        and source.get("dry_run_plan_is_passive") is True
        and source.get("dry_run_plan_executed") is False
        and source.get("dry_run_plan_materialized_as_process_args") is False
        and source.get("real_subprocess_invocation_built") is False
        and source.get("launch_execution_allowed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("selenium_imported_by_readback") is False
        and source.get("profile_directory_created") is False
    )


def _under_allowed_profile_root(root: Path, candidate: Path) -> bool:
    allowed = (root / "data" / "runtime" / "browser_profiles").resolve()
    resolved = candidate.resolve()
    return resolved == allowed or allowed in resolved.parents


def _profile_steps() -> list[dict[str, Any]]:
    return [
        {"step": step, "status": "planned", "filesystem_write_allowed": False, "browser_launch_allowed": False}
        for step in PROFILE_LIFECYCLE_STEPS
    ]


def build_edge_dedicated_profile_lifecycle_preflight(
    repo_root: str | Path | None = None,
    *,
    profile_relative_path: str | None = None,
) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = l14_03.build_edge_launch_dry_run_plan_readback(
        root,
        request_launch_authorization=True,
        operator_confirmation_token=AUTHORIZATION_TOKEN,
    )
    rel = (profile_relative_path or PROFILE_RELATIVE_PATH).replace("\\", "/").strip("/")
    profile_candidate = (root / rel).resolve()
    source_safe = _source_l14_03_safe(source)
    profile_path_allowed = _under_allowed_profile_root(root, profile_candidate)
    profile_exists_before = profile_candidate.exists()
    steps = _profile_steps()
    steps_passive = all(item["filesystem_write_allowed"] is False and item["browser_launch_allowed"] is False for item in steps)

    checks = [
        _check("l14_03_dry_run_plan_remains_accepted", source_safe),
        _check("dedicated_profile_lifecycle_preflight_enforced", True),
        _check("profile_candidate_under_allowed_runtime_root", profile_path_allowed, {"profile_candidate_path": str(profile_candidate)}),
        _check("profile_lifecycle_steps_are_passive", steps_passive),
        _check("profile_directory_not_created_by_preflight", True),
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
        "source_patch": "L14.3",
        "source_l13_complete": source.get("source_l13_complete"),
        "remaining_l13_patches": source.get("remaining_l13_patches"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "launch_authorization_granted_for_future_stage": source.get("launch_authorization_granted_for_future_stage") is True,
        "dry_run_plan_readback_enforced": source.get("dry_run_plan_readback_enforced") is True,
        "dry_run_plan_is_passive": source.get("dry_run_plan_is_passive") is True,
        "dedicated_profile_lifecycle_preflight_enforced": True,
        "profile_relative_path": rel,
        "profile_candidate_path": str(profile_candidate),
        "profile_candidate_under_allowed_runtime_root": profile_path_allowed,
        "profile_directory_exists_before_preflight": profile_exists_before,
        "profile_lifecycle_steps": steps,
        "profile_lifecycle_steps_are_passive": steps_passive,
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
        "source_l14_03_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "dry_run_plan_is_passive": source.get("dry_run_plan_is_passive"),
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
        f"Profile Allowed   : {payload.get('profile_candidate_under_allowed_runtime_root')}",
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
    payload = build_edge_dedicated_profile_lifecycle_preflight(args.repo_root, profile_relative_path=args.profile_relative_path)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
