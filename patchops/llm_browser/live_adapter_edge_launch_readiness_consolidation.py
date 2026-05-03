"""L14.1 passive Microsoft Edge launch-readiness consolidation.

This module starts the post-L13 Microsoft Edge browser-runner stream without
starting a browser. It consumes the accepted post-L13 frontier-selection marker,
confirms L13 is complete, and consolidates the next safe Edge-first launch
readiness frontier. It does not import Selenium, start Edge, create a browser
session, create a driver, create a profile directory, click, download, paste,
send, run packages, commit, push, start localhost services, or use extensions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from patchops.llm_browser import post_l13_frontier_selection as post_l13

PATCH = "L14.1"
PHASE = "L14"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L14.1 Microsoft Edge launch-readiness consolidation"
COMMAND_NAME = "browser-start-supervised-launch-edge-launch-readiness-consolidation"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-post-l13-frontier-selection"
NEXT_PATCH = "L14.2 Microsoft Edge supervised launch authorization gate, still no launch by default"
ACTIVE_FRONTIER = "l14_01_edge_launch_readiness_consolidation"
ACTIVE_FRONTIER_GOAL = "passive Microsoft Edge live-start readiness consolidation before any browser process launch"
BROWSER_PRIORITY = ("edge", "opera")

READINESS_GATES = (
    "l13_complete",
    "post_l13_frontier_selection_accepted",
    "edge_first_priority_preserved",
    "opera_second_priority_preserved",
    "launch_execution_not_authorized",
    "browser_process_launch_not_requested",
    "selenium_not_required",
    "profile_creation_not_allowed",
    "operator_review_required_before_live_start",
)


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _source_post_l13_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "post-L13"
        and source.get("source_l13_complete") is True
        and source.get("remaining_l13_patches") == []
        and source.get("frontier_selected") is False
        and source.get("recommended_safe_next_patch_name") == ACTIVE_FRONTIER
        and source.get("no_selenium_import") is True
        and source.get("no_browser_start") is True
        and source.get("no_edge_process_start") is True
        and source.get("no_browser_session_creation") is True
        and source.get("no_driver_creation") is True
        and source.get("no_profile_directory_creation") is True
        and source.get("no_click_download_paste_send_package_run") is True
        and source.get("no_git_commit_or_push") is True
        and source.get("no_localhost_patchops_server") is True
        and source.get("no_browser_extension") is True
    )


def build_edge_launch_readiness_consolidation(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = post_l13.build_post_l13_frontier_selection(root)
    source_safe = _source_post_l13_safe(source)

    readiness = {
        "l13_complete": source.get("source_l13_complete") is True,
        "post_l13_frontier_selection_accepted": source_safe,
        "edge_first_priority_preserved": source.get("microsoft_edge_first") is True,
        "opera_second_priority_preserved": source.get("opera_second") is True,
        "launch_execution_not_authorized": True,
        "browser_process_launch_not_requested": True,
        "selenium_not_required": True,
        "profile_creation_not_allowed": True,
        "operator_review_required_before_live_start": True,
    }
    missing = [gate for gate in READINESS_GATES if readiness.get(gate) is not True]
    checks = [
        _check("post_l13_frontier_selection_remains_accepted", source_safe),
        _check("l13_complete_before_l14", source.get("source_l13_complete") is True),
        _check("remaining_l13_patches_none", source.get("remaining_l13_patches") == []),
        _check("active_frontier_matches_recommended_safe_next_patch", source.get("recommended_safe_next_patch_name") == ACTIVE_FRONTIER),
        _check("launch_readiness_consolidated", not missing, {"missing_gates": missing}),
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
        "source_patch": "post-L13",
        "source_l13_complete": source.get("source_l13_complete"),
        "remaining_l13_patches": source.get("remaining_l13_patches"),
        "active_frontier": ACTIVE_FRONTIER,
        "active_frontier_goal": ACTIVE_FRONTIER_GOAL,
        "source_recommended_safe_next_patch_name": source.get("recommended_safe_next_patch_name"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "readiness_gates": readiness,
        "missing_readiness_gates": missing,
        "launch_readiness_consolidated": not missing,
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
        "source_post_l13_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "frontier_selected": source.get("frontier_selected"),
            "recommended_safe_next_patch_name": source.get("recommended_safe_next_patch_name"),
        },
        "checks": checks,
        "executed_validation_commands": [],
        "next_patch": NEXT_PATCH,
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        f"Status              : {payload.get('status')}",
        f"Command             : {payload.get('command_name')}",
        f"Source Command      : {payload.get('source_command_name')}",
        f"Source Patch        : {payload.get('source_patch')}",
        f"L13 Complete        : {payload.get('source_l13_complete')}",
        f"Active Frontier     : {payload.get('active_frontier')}",
        f"Readiness Consolidated: {payload.get('launch_readiness_consolidated')}",
        f"Launch Authorized   : {payload.get('launch_execution_allowed')}",
        f"Browser Started     : {payload.get('browser_started')}",
        f"Next Patch          : {payload.get('next_patch')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_launch_readiness_consolidation(args.repo_root)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
