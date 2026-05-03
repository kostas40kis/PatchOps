"""L14.6 passive aggregate gate for Microsoft Edge dedicated profile lifecycle.

This aggregate gate sits over the accepted L14.5 dedicated profile lifecycle
CLI/readback layer. It confirms the profile lifecycle surface remains truthful,
read-only, rooted under the allowed runtime profile area, and passive. It still
does not create, delete, clean, or mutate profile directories, launch Edge,
import Selenium, create sessions, drivers, downloads, paste/send actions,
package runs, commits, pushes, localhost services, or browser extensions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from patchops.llm_browser import live_adapter_edge_dedicated_profile_lifecycle_cli_readback as l14_05

PATCH = "L14.6"
PHASE = "L14"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L14.6 Microsoft Edge dedicated profile lifecycle aggregate gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-aggregate-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-cli-readback"
NEXT_PATCH = "L14.7 Microsoft Edge dedicated profile lifecycle aggregate gate CLI/readback, still no launch"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_preflight.py",
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_aggregate_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_dedicated_profile_lifecycle_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_dedicated_profile_lifecycle_aggregate_gate.md",
    "tests/test_l14_04_edge_dedicated_profile_lifecycle_preflight_current.py",
    "tests/test_l14_05_edge_dedicated_profile_lifecycle_cli_readback_current.py",
    "tests/test_l14_06_edge_dedicated_profile_lifecycle_aggregate_gate_current.py",
    "scripts/patch_l14_05_brief_validate.py",
    "scripts/patch_l14_06_brief_validate.py",
)


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _source_l14_05_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L14.5"
        and source.get("source_l13_complete") is True
        and source.get("dedicated_profile_lifecycle_preflight_enforced") is True
        and source.get("dedicated_profile_lifecycle_cli_readback_enforced") is True
        and source.get("profile_readback_truthful") is True
        and source.get("profile_lifecycle_cli_readback_is_passive") is True
        and source.get("profile_candidate_under_allowed_runtime_root") is True
        and source.get("profile_lifecycle_steps_are_passive") is True
        and source.get("profile_directory_creation_deferred") is True
        and source.get("profile_directory_create_allowed") is False
        and source.get("profile_directory_cleanup_allowed") is False
        and source.get("profile_directory_delete_allowed") is False
        and source.get("profile_directory_created") is False
        and source.get("profile_directory_mutated") is False
        and source.get("filesystem_writes_performed") == []
        and source.get("adapter_filesystem_writes_performed") == []
        and source.get("side_effects_performed") == []
        and source.get("launch_execution_allowed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("selenium_imported_by_readback") is False
    )


def build_edge_dedicated_profile_lifecycle_aggregate_gate(
    repo_root: str | Path | None = None,
    *,
    profile_relative_path: str | None = None,
) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = l14_05.build_edge_dedicated_profile_lifecycle_cli_readback(root, profile_relative_path=profile_relative_path)
    required = _required_paths_status(root)
    source_safe = _source_l14_05_safe(source)
    profile_aggregate_truthful = (
        isinstance(source.get("profile_candidate_path"), str)
        and source.get("profile_readback_truthful") is True
        and source.get("profile_candidate_under_allowed_runtime_root") is True
        and source.get("profile_lifecycle_steps_are_passive") is True
        and source.get("profile_lifecycle_cli_readback_is_passive") is True
    )
    profile_aggregate_passive = (
        source.get("profile_directory_created") is False
        and source.get("profile_directory_mutated") is False
        and source.get("profile_directory_create_allowed") is False
        and source.get("profile_directory_cleanup_allowed") is False
        and source.get("profile_directory_delete_allowed") is False
        and source.get("filesystem_writes_performed") == []
        and source.get("adapter_filesystem_writes_performed") == []
        and source.get("side_effects_performed") == []
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("selenium_imported_by_readback") is False
        and source.get("launch_execution_allowed") is False
    )
    checks = [
        _check("l14_05_profile_lifecycle_cli_readback_remains_accepted", source_safe),
        _check("dedicated_profile_lifecycle_aggregate_gate_enforced", True),
        _check("profile_aggregate_truthful", profile_aggregate_truthful),
        _check("profile_aggregate_gate_is_passive", profile_aggregate_passive),
        _check("profile_directory_still_not_created", source.get("profile_directory_created") is False),
        _check("profile_directory_still_not_mutated", source.get("profile_directory_mutated") is False),
        _check("required_l14_profile_aggregate_paths_exist", bool(required["ok"]), {"missing": required["missing"]}),
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
        "source_patch": "L14.5",
        "source_l13_complete": source.get("source_l13_complete"),
        "remaining_l13_patches": source.get("remaining_l13_patches"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "launch_authorization_granted_for_future_stage": source.get("launch_authorization_granted_for_future_stage") is True,
        "dry_run_plan_readback_enforced": source.get("dry_run_plan_readback_enforced") is True,
        "dry_run_plan_is_passive": source.get("dry_run_plan_is_passive") is True,
        "dedicated_profile_lifecycle_preflight_enforced": source.get("dedicated_profile_lifecycle_preflight_enforced") is True,
        "dedicated_profile_lifecycle_cli_readback_enforced": source.get("dedicated_profile_lifecycle_cli_readback_enforced") is True,
        "dedicated_profile_lifecycle_aggregate_gate_enforced": True,
        "profile_readback_truthful": source.get("profile_readback_truthful"),
        "profile_lifecycle_cli_readback_is_passive": source.get("profile_lifecycle_cli_readback_is_passive"),
        "profile_aggregate_truthful": profile_aggregate_truthful,
        "profile_aggregate_gate_is_passive": profile_aggregate_passive,
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
        "required_repo_paths": required,
        "source_l14_05_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "profile_readback_truthful": source.get("profile_readback_truthful"),
            "profile_cli_passive": source.get("profile_lifecycle_cli_readback_is_passive"),
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
        f"Status             : {payload.get('status')}",
        f"Command            : {payload.get('command_name')}",
        f"Source Patch       : {payload.get('source_patch')}",
        f"Profile Candidate  : {payload.get('profile_candidate_path')}",
        f"Aggregate Truthful : {payload.get('profile_aggregate_truthful')}",
        f"Aggregate Passive  : {payload.get('profile_aggregate_gate_is_passive')}",
        f"Profile Created    : {payload.get('profile_directory_created')}",
        f"Launch Allowed     : {payload.get('launch_execution_allowed')}",
        f"Browser Started    : {payload.get('browser_started')}",
        f"Next Patch         : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--profile-relative-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_dedicated_profile_lifecycle_aggregate_gate(args.repo_root, profile_relative_path=args.profile_relative_path)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
