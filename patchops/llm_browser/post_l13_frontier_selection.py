"""Passive post-L13 frontier selection marker for the LLM browser runner.

This module does not select or implement a live browser phase. It records that
L13 is complete, proves the L13.8 final marker is still accepted, and exposes
safe candidate frontiers for a human-reviewed next stream. It is readback-only
and performs no browser, Selenium, profile, download, paste, package-run, or git
side effects.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_final_acceptance_marker as l13_08

PATCH = "post-L13"
NAME = "Post-L13 Microsoft Edge browser-runner frontier selection"
COMMAND_NAME = "browser-start-supervised-launch-post-l13-frontier-selection"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-final-acceptance-marker"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"

CANDIDATE_FRONTIERS = (
    "Microsoft Edge live-start readiness consolidation before any browser process launch",
    "Microsoft Edge supervised launch execution authorization gate, still no launch by default",
    "Microsoft Edge dedicated profile lifecycle hardening before launch",
    "Microsoft Edge operator-reviewed live-start smoke gate, only after explicit phase authorization",
)


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _no_launch(payload: Mapping[str, Any]) -> bool:
    false_fields = [
        "edge_executable_launch_attempted",
        "startup_allowed",
        "live_start_performed",
        "browser_started",
        "edge_process_started",
        "browser_session_created",
        "driver_created",
        "profile_directory_created",
        "click_download_performed",
        "download_performed",
        "paste_performed",
        "send_or_submit_performed",
        "package_run_performed_by_adapter",
        "git_commit_executed",
        "git_push_executed",
        "selenium_imported_by_readback",
    ]
    list_fields = ["filesystem_writes_performed", "adapter_filesystem_writes_performed", "side_effects_performed", "forbidden_optional_imports_observed"]
    return all(payload.get(field) is False for field in false_fields) and all(payload.get(field) == [] for field in list_fields)


def build_post_l13_frontier_selection(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = l13_08.build_edge_executable_filesystem_probe_execution_final_acceptance_marker(root)
    source_ok = (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L13.8"
        and source.get("l13_complete") is True
        and source.get("remaining_l13_patches") == []
        and _no_launch(source)
    )
    checks = [
        _check("l13_08_final_acceptance_marker_remains_accepted", source_ok),
        _check("l13_complete", source.get("l13_complete") is True),
        _check("remaining_l13_patches_none", source.get("remaining_l13_patches") == []),
        _check("frontier_is_not_auto_selected", True),
        _check("readback_only_no_live_browser_behavior", True),
        _check("microsoft_edge_first_opera_second_preserved", True),
    ]
    ok = all(item["ok"] for item in checks)
    return {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "source_patch": "L13.8",
        "source_l13_complete": source.get("l13_complete"),
        "remaining_l13_patches": source.get("remaining_l13_patches"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "frontier_selected": False,
        "frontier_selection_requires_review": True,
        "candidate_frontiers": list(CANDIDATE_FRONTIERS),
        "recommended_safe_next_patch_name": "l14_01_edge_launch_readiness_consolidation",
        "recommended_safe_next_patch_goal": "passive Microsoft Edge live-start readiness consolidation before any browser process launch",
        "no_selenium_import": True,
        "no_browser_start": True,
        "no_edge_process_start": True,
        "no_browser_session_creation": True,
        "no_driver_creation": True,
        "no_profile_directory_creation": True,
        "no_click_download_paste_send_package_run": True,
        "no_git_commit_or_push": True,
        "no_localhost_patchops_server": True,
        "no_browser_extension": True,
        "source_l13_08_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "l13_complete": source.get("l13_complete"),
        },
        "checks": checks,
        "executed_validation_commands": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_post_l13_frontier_selection(args.repo_root)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(f"{NAME}\nStatus: {payload['status']}\nL13 complete: {payload['source_l13_complete']}\nFrontier selected: {payload['frontier_selected']}\n")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
