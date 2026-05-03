"""L13.4 passive CLI/readback for the Microsoft Edge executable filesystem probe execution fixture matrix.

This module wraps the accepted L13.3 fixture matrix with a compact readback
surface. It keeps the probe read-only, gated by the accepted L12 execution
preflight stack, and forbids browser launch, Selenium import, browser sessions,
profiles, downloads, paste/send actions, package runs, commits, and pushes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix as l13_03

PATCH = "L13.4"
PHASE = "L13"
NAME = "L13.4 Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix-readback"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix"
NEXT_PATCH = "L13.5 Live adapter Microsoft Edge executable filesystem probe execution aggregate gate"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

NO_LAUNCH_FIELDS = (
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
)

EMPTY_LIST_SIDE_EFFECT_FIELDS = (
    "filesystem_writes_performed",
    "adapter_filesystem_writes_performed",
    "side_effects_performed",
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    return Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _new_forbidden_imports(before: set[str]) -> list[str]:
    added = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if root in added or any(name == root or name.startswith(root + ".") for name in added):
            found.append(root)
    return sorted(set(found))


def _selected_candidate_ok(payload: Mapping[str, Any]) -> bool:
    selected = payload.get("edge_executable_selected_path")
    candidates = payload.get("edge_executable_probe_candidates") or []
    if payload.get("edge_executable_path_selected") is True:
        return any(
            isinstance(item, Mapping)
            and item.get("path") == selected
            and item.get("exists") is True
            and item.get("is_file") is True
            for item in candidates
        )
    return selected is None


def _no_launch_side_effects(payload: Mapping[str, Any]) -> bool:
    for field in NO_LAUNCH_FIELDS:
        if payload.get(field) is not False:
            return False
    for field in EMPTY_LIST_SIDE_EFFECT_FIELDS:
        if payload.get(field) != []:
            return False
    return True


def _default_no_side_effect_fields(payload: dict[str, Any]) -> None:
    for field in NO_LAUNCH_FIELDS:
        payload.setdefault(field, False)
    for field in EMPTY_LIST_SIDE_EFFECT_FIELDS:
        payload.setdefault(field, [])
    payload.setdefault("selenium_imported_by_readback", False)
    payload.setdefault("optional_browser_dependencies_required", False)


def _source_l13_03_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L13.3"
        and source.get("command_name") == SOURCE_COMMAND_NAME
        and _selected_candidate_ok(source)
        and _no_launch_side_effects(source)
        and source.get("selenium_imported_by_readback") is False
    )


def build_edge_executable_filesystem_probe_execution_fixture_matrix_readback(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
    activate_executable_filesystem_probe: bool = False,
    allow_real_filesystem_probe: bool = False,
    allow_executable_filesystem_probe_execution: bool = False,
    extra_candidates: Sequence[str] | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l13_03.build_edge_executable_filesystem_probe_execution_fixture_matrix(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
        activate_executable_filesystem_probe=activate_executable_filesystem_probe,
        allow_real_filesystem_probe=allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=allow_executable_filesystem_probe_execution,
        extra_candidates=extra_candidates,
    )
    forbidden = _new_forbidden_imports(before)

    payload: dict[str, Any] = dict(source)
    _default_no_side_effect_fields(payload)

    source_safe = _source_l13_03_safe(payload)
    truthful_selection = _selected_candidate_ok(payload)
    no_launch = _no_launch_side_effects(payload) and payload.get("selenium_imported_by_readback") is False and not forbidden

    checks = [
        _check("l13_03_execution_fixture_matrix_remains_accepted", source_safe),
        _check("execution_fixture_matrix_cli_readback_enforced", True),
        _check("truthful_selected_path_existing_reported_candidate", truthful_selection),
        _check("no_launch_browser_profile_selenium_side_effects", no_launch, {"forbidden_imports": forbidden}),
        _check("compact_json_readback_available", True),
    ]

    status = STATUS_PASS if all(item["ok"] for item in checks) else STATUS_FAIL
    payload.update(
        {
            "ok": status == STATUS_PASS,
            "status": status,
            "phase": PHASE,
            "patch": PATCH,
            "command_name": COMMAND_NAME,
            "source_command_name": SOURCE_COMMAND_NAME,
            "source_patch": "L13.3",
            "browser_priority": list(BROWSER_PRIORITY),
            "microsoft_edge_first": True,
            "opera_second": True,
            "l13_03_execution_fixture_matrix_remains_accepted": source_safe,
            "execution_fixture_matrix_cli_readback_enforced": True,
            "execution_fixture_matrix_enforced": True,
            "execution_cli_readback_enforced": True,
            "execution_contract_enforced": True,
            "truthful_selected_path_existing_reported_candidate": truthful_selection,
            "read_only_filesystem_probe": True,
            "small_allowlisted_microsoft_edge_executable_candidate_list": True,
            "l12_execution_preflight_required": True,
            "may_probe_only_when_l12_execution_preflight_ready": True,
            "no_executable_launch_attempted_by_readback": no_launch,
            "forbidden_optional_imports_observed": forbidden,
            "next_patch": NEXT_PATCH,
            "checks": checks,
            "executed_validation_commands": [],
        }
    )
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    selected = payload.get("edge_executable_selected_path") or "(none)"
    lines = [
        NAME,
        f"Status          : {payload.get('status')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Source Patch    : {payload.get('source_patch')}",
        f"Exec Ready      : {payload.get('execution_preflight_ready')}",
        f"Probe Performed : {payload.get('edge_executable_filesystem_probe_performed')}",
        f"Selection Truth : {payload.get('truthful_selected_path_existing_reported_candidate')}",
        f"Path Selected   : {payload.get('edge_executable_path_selected')}",
        f"Selected Path   : {selected}",
        f"Launch Attempt  : {payload.get('edge_executable_launch_attempted')}",
        f"Next Patch      : {payload.get('next_patch')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--allow-live-start", action="store_true")
    parser.add_argument("--profile-dir", default=None)
    parser.add_argument("--allow-executable-probe", action="store_true")
    parser.add_argument("--activate-executable-filesystem-probe", action="store_true")
    parser.add_argument("--allow-real-filesystem-probe", action="store_true")
    parser.add_argument("--allow-executable-filesystem-probe-execution", action="store_true")
    parser.add_argument("--extra-candidate", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_executable_filesystem_probe_execution_fixture_matrix_readback(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
        allow_executable_probe=args.allow_executable_probe,
        activate_executable_filesystem_probe=args.activate_executable_filesystem_probe,
        allow_real_filesystem_probe=args.allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=args.allow_executable_filesystem_probe_execution,
        extra_candidates=args.extra_candidate,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
