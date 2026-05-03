"""L14.8 passive broad-validation checkpoint for Microsoft Edge dedicated profile lifecycle.

The checkpoint sits over the accepted L14.7 aggregate-gate CLI/readback layer.
It exposes a planned L14 broad-validation command list, confirms the dedicated
profile lifecycle stack remains truthful, rooted under the allowed runtime
profile area, and passive, and deliberately does not execute validation commands
from inside adapter logic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_dedicated_profile_lifecycle_aggregate_gate_cli_readback as l14_07

PATCH = "L14.8"
PHASE = "L14"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L14.8 Microsoft Edge dedicated profile lifecycle broad validation checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-broad-validation-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-aggregate-gate-cli-readback"
NEXT_PATCH = "L14.9 Microsoft Edge dedicated profile lifecycle final acceptance marker, still no launch"
BROWSER_PRIORITY = ("edge", "opera")

L14_TESTS = (
    "tests/test_l14_01_edge_launch_readiness_consolidation_current.py",
    "tests/test_l14_02_edge_launch_authorization_gate_current.py",
    "tests/test_l14_03_edge_launch_dry_run_plan_readback_current.py",
    "tests/test_l14_04_edge_dedicated_profile_lifecycle_preflight_current.py",
    "tests/test_l14_05_edge_dedicated_profile_lifecycle_cli_readback_current.py",
    "tests/test_l14_06_edge_dedicated_profile_lifecycle_aggregate_gate_current.py",
    "tests/test_l14_07_edge_dedicated_profile_lifecycle_aggregate_gate_cli_readback_current.py",
    "tests/test_l14_08_edge_dedicated_profile_lifecycle_broad_validation_checkpoint_current.py",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_launch_readiness_consolidation.py",
    "patchops/llm_browser/live_adapter_edge_launch_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_launch_dry_run_plan_readback.py",
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_preflight.py",
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_aggregate_gate.py",
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_aggregate_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_broad_validation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_dedicated_profile_lifecycle_aggregate_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_dedicated_profile_lifecycle_broad_validation_checkpoint.md",
    "scripts/patch_l14_06_brief_validate.py",
    "scripts/patch_l14_07_brief_validate.py",
    "scripts/patch_l14_08_brief_validate.py",
) + L14_TESTS


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _source_l14_07_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L14.7"
        and source.get("source_l13_complete") is True
        and source.get("dedicated_profile_lifecycle_aggregate_gate_enforced") is True
        and source.get("dedicated_profile_lifecycle_aggregate_gate_cli_readback_enforced") is True
        and source.get("profile_aggregate_truthful") is True
        and source.get("profile_aggregate_gate_is_passive") is True
        and source.get("profile_aggregate_cli_readback_truthful") is True
        and source.get("profile_aggregate_cli_readback_is_passive") is True
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


def _planned_commands() -> list[str]:
    tests = " ".join(L14_TESTS)
    return [
        "py -m compileall patchops/llm_browser " + tests + " scripts/patch_l14_08_brief_validate.py",
        "py -m pytest -q " + tests,
        "py -m patchops.cli llm-browser " + SOURCE_COMMAND_NAME + " --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser " + COMMAND_NAME + " --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]


def _planned_commands_are_passive(commands: Sequence[str]) -> bool:
    forbidden = (
        " apply ",
        " run-package ",
        " --allow-browser-start",
        " --allow-edge-start",
        " --allow-selenium",
        " --allow-profile-create",
        " --allow-profile-delete",
        " --allow-profile-cleanup",
        " --allow-download-click",
        " --allow-paste",
        " --allow-send",
        " --allow-patchops-run",
        " git commit",
        " git push",
        " selenium",
        " webdriver",
        " msedge.exe",
        " opera.exe",
    )
    padded = [" " + item.lower() + " " for item in commands]
    return not any(token in item for item in padded for token in forbidden)


def build_edge_dedicated_profile_lifecycle_broad_validation_checkpoint(
    repo_root: str | Path | None = None,
    *,
    profile_relative_path: str | None = None,
) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = l14_07.build_edge_dedicated_profile_lifecycle_aggregate_gate_cli_readback(root, profile_relative_path=profile_relative_path)
    required = _required_paths_status(root)
    planned = _planned_commands()
    planned_passive = _planned_commands_are_passive(planned)
    source_safe = _source_l14_07_safe(source)
    checkpoint_truthful = (
        source.get("profile_aggregate_cli_readback_truthful") is True
        and source.get("profile_aggregate_cli_readback_is_passive") is True
        and source.get("profile_candidate_under_allowed_runtime_root") is True
        and isinstance(source.get("profile_candidate_path"), str)
    )
    checkpoint_passive = (
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
        _check("l14_07_profile_lifecycle_aggregate_gate_cli_readback_remains_accepted", source_safe),
        _check("dedicated_profile_lifecycle_broad_validation_checkpoint_enforced", True),
        _check("planned_broad_validation_commands_are_passive", planned_passive),
        _check("broad_validation_commands_not_executed_by_checkpoint", True),
        _check("profile_broad_checkpoint_truthful", checkpoint_truthful),
        _check("profile_broad_checkpoint_is_passive", checkpoint_passive),
        _check("profile_directory_still_not_created", source.get("profile_directory_created") is False),
        _check("profile_directory_still_not_mutated", source.get("profile_directory_mutated") is False),
        _check("required_l14_profile_broad_checkpoint_paths_exist", bool(required["ok"]), {"missing": required["missing"]}),
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
        "source_patch": "L14.7",
        "source_l13_complete": source.get("source_l13_complete"),
        "remaining_l13_patches": source.get("remaining_l13_patches"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "launch_authorization_granted_for_future_stage": source.get("launch_authorization_granted_for_future_stage") is True,
        "dry_run_plan_readback_enforced": source.get("dry_run_plan_readback_enforced") is True,
        "dry_run_plan_is_passive": source.get("dry_run_plan_is_passive") is True,
        "dedicated_profile_lifecycle_preflight_enforced": source.get("dedicated_profile_lifecycle_preflight_enforced") is True,
        "dedicated_profile_lifecycle_cli_readback_enforced": source.get("dedicated_profile_lifecycle_cli_readback_enforced") is True,
        "dedicated_profile_lifecycle_aggregate_gate_enforced": source.get("dedicated_profile_lifecycle_aggregate_gate_enforced") is True,
        "dedicated_profile_lifecycle_aggregate_gate_cli_readback_enforced": source.get("dedicated_profile_lifecycle_aggregate_gate_cli_readback_enforced") is True,
        "dedicated_profile_lifecycle_broad_validation_checkpoint_enforced": True,
        "profile_readback_truthful": source.get("profile_readback_truthful"),
        "profile_lifecycle_cli_readback_is_passive": source.get("profile_lifecycle_cli_readback_is_passive"),
        "profile_aggregate_truthful": source.get("profile_aggregate_truthful"),
        "profile_aggregate_gate_is_passive": source.get("profile_aggregate_gate_is_passive"),
        "profile_aggregate_cli_readback_truthful": source.get("profile_aggregate_cli_readback_truthful"),
        "profile_aggregate_cli_readback_is_passive": source.get("profile_aggregate_cli_readback_is_passive"),
        "profile_broad_checkpoint_truthful": checkpoint_truthful,
        "profile_broad_checkpoint_is_passive": checkpoint_passive,
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
        "planned_broad_validation_commands": planned,
        "planned_broad_validation_commands_are_passive": planned_passive,
        "broad_validation_commands_executed_by_checkpoint": False,
        "required_repo_paths": required,
        "source_l14_07_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "profile_aggregate_cli_readback_truthful": source.get("profile_aggregate_cli_readback_truthful"),
            "profile_aggregate_cli_readback_passive": source.get("profile_aggregate_cli_readback_is_passive"),
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
        f"Checkpoint Truthful: {payload.get('profile_broad_checkpoint_truthful')}",
        f"Checkpoint Passive : {payload.get('profile_broad_checkpoint_is_passive')}",
        f"Plan Passive       : {payload.get('planned_broad_validation_commands_are_passive')}",
        f"Plan Executed      : {payload.get('broad_validation_commands_executed_by_checkpoint')}",
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
    payload = build_edge_dedicated_profile_lifecycle_broad_validation_checkpoint(args.repo_root, profile_relative_path=args.profile_relative_path)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
