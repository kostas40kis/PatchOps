"""Passive L5.14 Microsoft Edge supervised-launch fixture matrix.

This module models the first Edge-specific supervised-launch scenarios without
performing live browser automation. It does not import Selenium, start Edge,
create a driver/session/profile directory, click/download, paste/send, run a
package, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_edge_supervised_launch_readiness_cli_readback as edge_readback

PATCH = "L5.14"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.14 Microsoft Edge Supervised Launch Fixture Matrix"
COMMAND_NAME = "browser-start-supervised-launch-edge-fixtures"
SOURCE_COMMAND_NAME = edge_readback.COMMAND_NAME
NEXT_PATCH = "L5.15 Live adapter Microsoft Edge supervised launch fixture matrix CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-fixture-matrix-readback-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_edge_supervised_launch_readiness_contract.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_readiness_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_contract.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix.md",
    "tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py",
    "tests/test_l5_14_edge_supervised_launch_fixture_matrix_current.py",
)

PASSIVE_INVARIANTS: Mapping[str, Any] = {
    "startup_authorized": False,
    "startup_allowed": False,
    "browser_started": False,
    "edge_process_started": False,
    "browser_session_created": False,
    "driver_created": False,
    "profile_directory_created": False,
    "adapter_filesystem_writes_performed": [],
    "filesystem_writes_performed": [],
    "side_effects_performed": [],
    "click_download_performed": False,
    "download_performed": False,
    "paste_performed": False,
    "send_or_submit_performed": False,
    "package_run_performed_by_adapter": False,
    "git_commit_executed": False,
    "git_push_executed": False,
    "optional_browser_dependencies_required": False,
    "selenium_required": False,
    "selenium_imported_by_readback": False,
}


def _fixture_case(
    case_id: str,
    title: str,
    expected: str,
    rationale: str,
    *,
    edge_first: bool = True,
    dedicated_profile_required: bool = True,
    manual_user_login_required: bool = True,
    default_profile_forbidden: bool = True,
    silent_auto_submit_default: bool = False,
    browser_extension_required: bool = False,
    localhost_patchops_server_required: bool = False,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "title": title,
        "browser": "edge",
        "expected": expected,
        "rationale": rationale,
        "edge_first": edge_first,
        "dedicated_profile_required": dedicated_profile_required,
        "manual_user_login_required": manual_user_login_required,
        "default_profile_forbidden": default_profile_forbidden,
        "silent_auto_submit_default": silent_auto_submit_default,
        "browser_extension_required": browser_extension_required,
        "localhost_patchops_server_required": localhost_patchops_server_required,
        "current_patch_launches_browser": False,
        "current_patch_imports_selenium": False,
        "current_patch_creates_profile_directory": False,
        "current_patch_clicks_download": False,
        "current_patch_pastes_or_sends": False,
        "current_patch_runs_package_from_adapter": False,
        "passive_only": True,
    }


EDGE_FIXTURE_CASES: tuple[Mapping[str, Any], ...] = (
    _fixture_case(
        "edge_future_launch_user_visible",
        "Future Edge launch is supervised and user-visible",
        "future_live_phase_may_open_edge_only_after_explicit_authorization",
        "The operator must see and control the browser; this patch only models that rule.",
    ),
    _fixture_case(
        "edge_dedicated_profile_required",
        "Dedicated PatchOps Edge profile is required",
        "future_live_phase_must_use_dedicated_profile_path",
        "Default personal/work profiles are forbidden for automation safety and repeatability.",
    ),
    _fixture_case(
        "edge_manual_login_required",
        "Manual ChatGPT login is required",
        "future_live_phase_waits_for_user_login_without_secret_handling",
        "The adapter must not handle credentials or bypass normal login.",
    ),
    _fixture_case(
        "edge_no_silent_auto_submit",
        "Silent auto-submit remains disabled",
        "future_live_phase_may_insert_pasteback_for_review_but_not_send_by_default",
        "Human review remains the boundary before a message is submitted.",
    ),
    _fixture_case(
        "edge_no_extension_no_localhost",
        "No browser extension or localhost PatchOps server",
        "future_live_phase_uses_browser_driver_control_without_extra_server_surface",
        "The current plan excludes a browser extension and a localhost PatchOps server.",
        browser_extension_required=False,
        localhost_patchops_server_required=False,
    ),
    _fixture_case(
        "edge_no_current_side_effects",
        "Current fixture matrix performs no live side effects",
        "current_patch_readback_only",
        "L5.14 must not start Edge, create profiles, click downloads, paste, send, or run packages.",
    ),
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    return Path(repo_root).resolve()


def _missing_paths(root: Path, rel_paths: Iterable[str]) -> list[str]:
    return [rel for rel in rel_paths if not (root / rel).exists()]


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _json_safe(value: object) -> bool:
    try:
        json.dumps(value, sort_keys=True)
        return True
    except TypeError:
        return False


def _command_static_presence(root: Path, command_name: str, sentinel: str | None = None) -> dict[str, Any]:
    commands_path = root / "patchops" / "llm_browser" / "commands.py"
    if not commands_path.exists():
        return {"ok": False, "commands_path": str(commands_path), "reason": "commands.py missing", "command_name": command_name}
    text = commands_path.read_text(encoding="utf-8", errors="replace")
    payload: dict[str, Any] = {
        "ok": command_name in text,
        "commands_path": str(commands_path),
        "command_name": command_name,
    }
    if sentinel is not None:
        payload["sentinel_present"] = sentinel in text
        payload["ok"] = bool(payload["ok"] and payload["sentinel_present"])
    return payload


def _fixture_matrix_summary(cases: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    case_list = [dict(case) for case in cases]
    return {
        "case_count": len(case_list),
        "case_ids": [case["case_id"] for case in case_list],
        "all_edge": all(case.get("browser") == "edge" for case in case_list),
        "all_passive_only": all(case.get("passive_only") is True for case in case_list),
        "all_block_current_launch": all(case.get("current_patch_launches_browser") is False for case in case_list),
        "all_block_selenium_import": all(case.get("current_patch_imports_selenium") is False for case in case_list),
        "all_block_profile_creation": all(case.get("current_patch_creates_profile_directory") is False for case in case_list),
        "all_block_click_download": all(case.get("current_patch_clicks_download") is False for case in case_list),
        "all_block_paste_or_send": all(case.get("current_patch_pastes_or_sends") is False for case in case_list),
        "all_block_package_run": all(case.get("current_patch_runs_package_from_adapter") is False for case in case_list),
    }


def build_edge_supervised_launch_fixture_matrix(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_13 = edge_readback.build_edge_supervised_launch_readiness_cli_readback(root)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.13 START")
    matrix_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.14 START")
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    matrix_summary = _fixture_matrix_summary(EDGE_FIXTURE_CASES)
    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    command_plan = [
        "python -m compileall patchops/llm_browser tests scripts/patch_l5_14_wire_edge_fixture_matrix.py",
        "python -m pytest -q tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py tests/test_l5_14_edge_supervised_launch_fixture_matrix_current.py",
        "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_fixture_matrix --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]

    checks = [
        _check("l5_13_edge_readiness_cli_readback_still_passes", l5_13.get("ok") is True and l5_13.get("status") == STATUS_PASS, {"patch": l5_13.get("patch")}),
        _check("l5_13_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_14_edge_fixture_matrix_command_registered", matrix_command_static.get("ok") is True, matrix_command_static),
        _check("edge_fixture_matrix_has_expected_cases", matrix_summary["case_count"] == 6 and matrix_summary["all_edge"] is True, matrix_summary),
        _check("edge_fixture_matrix_blocks_live_side_effects", all(matrix_summary[key] is True for key in ("all_passive_only", "all_block_current_launch", "all_block_selenium_import", "all_block_profile_creation", "all_block_click_download", "all_block_paste_or_send", "all_block_package_run")), matrix_summary),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("l5_14_artifacts_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("selenium_not_imported_by_readback", selenium_imported_by_readback is False, {"selenium_imported_by_readback": selenium_imported_by_readback}),
        _check("no_browser_or_adapter_side_effects", PASSIVE_INVARIANTS["browser_started"] is False and PASSIVE_INVARIANTS["side_effects_performed"] == [], dict(PASSIVE_INVARIANTS)),
    ]

    ok = all(check["ok"] for check in checks)
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "phase": PHASE,
        "patch": PATCH,
        "name": NAME,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "browser_priority": list(BROWSER_PRIORITY),
        "edge_first": True,
        "repo_root": str(root),
        "l5_13_edge_readiness_cli_readback": l5_13,
        "edge_fixture_cases": [dict(case) for case in EDGE_FIXTURE_CASES],
        "edge_fixture_matrix_summary": matrix_summary,
        "source_command_static_presence": source_command_static,
        "matrix_command_static_presence": matrix_command_static,
        "missing_repo_paths": missing_repo_paths,
        "command_plan": command_plan,
        "checks": checks,
        "executed_validation_commands": [],
        **PASSIVE_INVARIANTS,
        "selenium_imported_by_readback": selenium_imported_by_readback,
    }
    payload["payload_json_safe"] = _json_safe(payload)
    if not payload["payload_json_safe"]:
        payload["ok"] = False
        payload["status"] = STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    summary = payload.get("edge_fixture_matrix_summary", {})
    lines = [
        "PatchOps L5.14 Microsoft Edge supervised-launch fixture matrix",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Case Count      : {summary.get('case_count') if isinstance(summary, Mapping) else None}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
        f"Browser Started : {payload.get('browser_started')}",
        f"Edge Started    : {payload.get('edge_process_started')}",
        f"Session Created : {payload.get('browser_session_created')}",
        f"Driver Created  : {payload.get('driver_created')}",
        f"Profile Created : {payload.get('profile_directory_created')}",
        f"SideEffects     : {payload.get('side_effects_performed')}",
        f"Filesystem      : writes={payload.get('filesystem_writes_performed')}",
        f"Adapter Writes  : {payload.get('adapter_filesystem_writes_performed')}",
        f"Selenium Import : {payload.get('selenium_imported_by_readback')}",
        f"MissingPath     : {payload.get('missing_repo_paths')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next Patch      : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_supervised_launch_fixture_matrix(args.repo_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())