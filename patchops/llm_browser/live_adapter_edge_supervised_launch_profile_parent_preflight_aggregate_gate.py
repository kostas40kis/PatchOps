"""L5.30 passive Microsoft Edge profile-parent preflight aggregate gate.

This gate aggregates the accepted L5.28 profile-parent preflight contract and
L5.29 CLI/readback layer. It is still passive: no Selenium import, browser
start, Edge process, driver/session creation, profile directory creation,
profile-parent filesystem probe, click/download, paste/send, package-run,
commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback as l5_29

PATCH = "L5.30"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.30 Microsoft Edge Supervised Launch Profile Parent Preflight Aggregate Gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-readback"
NEXT_PATCH = "L5.31 Live adapter Microsoft Edge supervised launch profile parent preflight aggregate gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-profile-parent-preflight-aggregate-gate-only"
AUTHORIZATION_FLAG = "--allow-live-start"
PROFILE_DIR_ARGUMENT = "--profile-dir"
BROWSER_PRIORITY = ("edge", "opera")

FORBIDDEN_OPTIONAL_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "playwright",
    "pyppeteer",
)

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_contract.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_contract.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate.md",
    "tests/test_l5_28_edge_supervised_launch_profile_parent_preflight_contract_current.py",
    "tests/test_l5_29_edge_supervised_launch_profile_parent_preflight_cli_readback_current.py",
    "tests/test_l5_30_edge_supervised_launch_profile_parent_preflight_aggregate_gate_current.py",
)

DOC_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback.md": (
        "L5.29 Microsoft Edge supervised launch profile parent preflight CLI/readback",
        SOURCE_COMMAND_NAME,
        "profile parent filesystem probe not performed",
        "profile parent directory not created",
        "L5.30 Live adapter Microsoft Edge supervised launch profile parent preflight aggregate gate",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate.md": (
        "L5.30 Microsoft Edge supervised launch profile parent preflight aggregate gate",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "Microsoft Edge first",
        "Opera second",
        "--allow-live-start",
        "--profile-dir",
        "profile parent preflight aggregate gate",
        "L5.28 profile parent preflight contract remains accepted",
        "L5.29 profile parent preflight CLI/readback remains accepted",
        "profile parent path derived",
        "profile parent filesystem probe not performed",
        "profile parent directory not created",
        "dedicated non-default profile required",
        "default Microsoft Edge profile remains forbidden",
        "manual user login required",
        "silent auto-submit remains false",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "L5.31 Live adapter Microsoft Edge supervised launch profile parent preflight aggregate gate CLI/readback",
    ),
}

COMMAND_PLAN: tuple[str, ...] = (
    "python -m compileall patchops/llm_browser tests scripts/patch_l5_30_wire_edge_profile_parent_preflight_aggregate_gate.py",
    "python -m pytest -q tests/test_l5_28_edge_supervised_launch_profile_parent_preflight_contract_current.py tests/test_l5_29_edge_supervised_launch_profile_parent_preflight_cli_readback_current.py tests/test_l5_30_edge_supervised_launch_profile_parent_preflight_aggregate_gate_current.py",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\dev\\patchops\\data\\runtime\\browser_profiles\\edge_l5_30_candidate --json --compact",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\Users\\kostas\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-gate --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\dev\\patchops\\data\\runtime\\browser_profiles\\edge_l5_30_candidate --json --compact",
    "git status --short --branch",
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    return Path(repo_root).resolve()


def _missing_paths(root: Path, rel_paths: Iterable[str]) -> list[str]:
    return [rel for rel in rel_paths if not (root / rel).exists()]


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _forbidden_optional_imports_newly_loaded(before: set[str]) -> list[str]:
    after = set(sys.modules)
    newly_loaded = after - before
    found: list[str] = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(found)


def _loaded_forbidden_modules() -> list[str]:
    found: list[str] = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in sys.modules):
            found.append(root)
    return sorted(found)


def _command_static_presence(command_name: str) -> dict[str, Any]:
    try:
        from patchops.llm_browser import commands

        names = tuple(commands.llm_browser_command_names())
        commands_path = Path(commands.__file__).resolve()
        text = commands_path.read_text(encoding="utf-8")
        return {
            "ok": command_name in names,
            "command_name": command_name,
            "commands_path": str(commands_path),
            "sentinel_present": command_name in text,
        }
    except Exception as exc:
        return {"ok": False, "command_name": command_name, "error": f"{type(exc).__name__}: {exc}"}


def _doc_state(repo_root: Path) -> dict[str, Any]:
    state: dict[str, dict[str, Any]] = {}
    missing_docs: list[str] = []
    missing_phrases: dict[str, list[str]] = {}
    for rel, phrases in DOC_REQUIREMENTS.items():
        path = repo_root / rel
        if not path.exists():
            state[rel] = {"exists": False, "missing_phrases": list(phrases)}
            missing_docs.append(rel)
            missing_phrases[rel] = list(phrases)
            continue
        text = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in phrases if phrase not in text]
        state[rel] = {"exists": True, "missing_phrases": missing}
        if missing:
            missing_phrases[rel] = missing
    return {
        "ok": not missing_docs and not missing_phrases,
        "missing_docs": missing_docs,
        "missing_phrases": missing_phrases,
        "doc_state": state,
    }


def _command_plan_state() -> dict[str, Any]:
    forbidden = [
        "--target-root",
        "--auto-send",
        "--allow-send-or-submit",
        "selenium webdriver",
        "Start-Process msedge",
        "msedge.exe --user-data-dir",
    ]
    forbidden_present = [item for item in forbidden if any(item in command for command in COMMAND_PLAN)]
    required_fragments = [
        "compileall",
        "pytest",
        "--json --compact",
        COMMAND_NAME,
        "git status --short --branch",
    ]
    missing_fragments = [frag for frag in required_fragments if not any(frag in command for command in COMMAND_PLAN)]
    return {
        "ok": not forbidden_present and not missing_fragments,
        "planned_commands": list(COMMAND_PLAN),
        "forbidden_present": forbidden_present,
        "missing_fragments": missing_fragments,
        "executed_by_adapter_logic": [],
    }


def _source_l5_29_is_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L5.29"
        and summary.get("status") == STATUS_PASS
        and summary.get("ok") is True
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("startup_allowed") is False
        and summary.get("live_start_performed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("profile_parent_directory_created") is False
        and summary.get("profile_parent_filesystem_probe_performed") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
        and summary.get("source_l5_28_summary", {}).get("patch") == "L5.28"
        and summary.get("source_l5_28_summary", {}).get("ok") is True
        and summary.get("source_l5_28_summary", {}).get("status") == STATUS_PASS
    )


def _aggregate_state(source_summary: Mapping[str, Any]) -> dict[str, Any]:
    l5_28 = source_summary.get("source_l5_28_summary", {})
    if not isinstance(l5_28, Mapping):
        l5_28 = {}
    return {
        "profile_parent_preflight_aggregate_gate_enforced": True,
        "profile_parent_preflight_aggregate_status": "BLOCKED_PROFILE_PARENT_PREFLIGHT_AGGREGATE_MODEL_ONLY",
        "profile_parent_preflight_aggregate_reason": "L5.30 aggregates L5.28/L5.29 passive profile-parent preflight surfaces but still cannot start Edge.",
        "l5_28_profile_parent_preflight_contract_ok": l5_28.get("ok") is True and l5_28.get("status") == STATUS_PASS,
        "l5_29_profile_parent_preflight_cli_readback_ok": source_summary.get("ok") is True and source_summary.get("status") == STATUS_PASS,
        "profile_parent_path_derived": source_summary.get("profile_parent_path_derived") is True,
        "profile_parent_path": source_summary.get("profile_parent_path"),
        "profile_parent_filesystem_probe_performed": False,
        "profile_parent_directory_created": False,
        "profile_parent_probe_required_before_future_live_start": source_summary.get("profile_parent_probe_required_before_future_live_start") is True,
        "profile_parent_must_exist_before_future_live_start": source_summary.get("profile_parent_must_exist_before_future_live_start") is True,
        "startup_allowed": False,
        "live_start_performed": False,
    }


def build_edge_supervised_launch_profile_parent_preflight_aggregate_gate(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    source_summary = l5_29.build_edge_supervised_launch_profile_parent_preflight_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
    )
    aggregate_state = _aggregate_state(source_summary)
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    command_plan_state = _command_plan_state()
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    newly_loaded_forbidden = _forbidden_optional_imports_newly_loaded(before_modules)
    loaded_forbidden = _loaded_forbidden_modules()

    checks = [
        _check("l5_29_profile_parent_preflight_cli_readback_still_passes", _source_l5_29_is_safe(source_summary), source_summary),
        _check("l5_29_profile_parent_preflight_cli_readback_remains_passive", _source_l5_29_is_safe(source_summary), source_summary),
        _check("l5_28_source_contract_is_in_l5_29_chain", aggregate_state.get("l5_28_profile_parent_preflight_contract_ok") is True, aggregate_state),
        _check("l5_29_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("l5_30_profile_parent_preflight_aggregate_command_registered", command_state.get("ok") is True, command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_l5_docs_contain_profile_parent_preflight_aggregate_boundary", doc_state.get("ok") is True, doc_state),
        _check("l5_30_command_plan_is_readback_only", command_plan_state.get("ok") is True, command_plan_state),
        _check("adapter_logic_executes_no_validation_commands", command_plan_state.get("executed_by_adapter_logic") == [], command_plan_state),
        _check("profile_parent_preflight_aggregate_gate_is_enforced", aggregate_state.get("profile_parent_preflight_aggregate_gate_enforced") is True, aggregate_state),
        _check("profile_parent_path_is_derived_by_aggregate_chain", (not source_summary.get("profile_dir_argument_present")) or source_summary.get("profile_parent_path_derived") is True, source_summary),
        _check("profile_parent_filesystem_probe_stays_false", source_summary.get("profile_parent_filesystem_probe_performed") is False and aggregate_state.get("profile_parent_filesystem_probe_performed") is False, source_summary),
        _check("profile_parent_directory_stays_uncreated", source_summary.get("profile_parent_directory_created") is False and aggregate_state.get("profile_parent_directory_created") is False, source_summary),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("selenium_not_imported_by_profile_parent_preflight_aggregate", not newly_loaded_forbidden and "selenium" not in loaded_forbidden, {"newly_loaded_forbidden": newly_loaded_forbidden, "loaded_forbidden": loaded_forbidden}),
        _check(
            "no_browser_profile_or_adapter_side_effects",
            all(
                [
                    source_summary.get("startup_allowed") is False,
                    source_summary.get("live_start_performed") is False,
                    source_summary.get("browser_started") is False,
                    source_summary.get("edge_process_started") is False,
                    source_summary.get("browser_session_created") is False,
                    source_summary.get("driver_created") is False,
                    source_summary.get("profile_directory_created") is False,
                    source_summary.get("profile_parent_directory_created") is False,
                    source_summary.get("profile_parent_filesystem_probe_performed") is False,
                    source_summary.get("filesystem_writes_performed") == [],
                    source_summary.get("adapter_filesystem_writes_performed") == [],
                    source_summary.get("side_effects_performed") == [],
                    source_summary.get("click_download_performed") is False,
                    source_summary.get("download_performed") is False,
                    source_summary.get("paste_performed") is False,
                    source_summary.get("send_or_submit_performed") is False,
                    source_summary.get("package_run_performed_by_adapter") is False,
                    source_summary.get("git_commit_executed") is False,
                    source_summary.get("git_push_executed") is False,
                    aggregate_state.get("startup_allowed") is False,
                    aggregate_state.get("live_start_performed") is False,
                    not newly_loaded_forbidden,
                ]
            ),
            {
                "startup_allowed": False,
                "live_start_performed": False,
                "browser_started": False,
                "edge_process_started": False,
                "browser_session_created": False,
                "driver_created": False,
                "profile_directory_created": False,
                "profile_parent_directory_created": False,
                "profile_parent_filesystem_probe_performed": False,
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
                "selenium_imported_by_readback": False,
            },
        ),
    ]

    ok = all(check["ok"] for check in checks)
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "next_patch": NEXT_PATCH,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "repo_root": str(root),
        "browser_priority": list(BROWSER_PRIORITY),
        "edge_first": True,
        "opera_second": True,
        "authorization_flag_required": AUTHORIZATION_FLAG,
        "profile_dir_argument_required": PROFILE_DIR_ARGUMENT,
        "dedicated_profile_required": True,
        "manual_user_login_required": True,
        "silent_auto_submit_default": False,
        "silent_auto_submit_must_remain_false": True,
        "browser_extension_required": False,
        "localhost_patchops_server_required": False,
        "optional_browser_dependencies_required": False,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "profile_parent_directory_created": False,
        "profile_parent_filesystem_probe_performed": False,
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
        "startup_authorized": bool(allow_live_start),
        "startup_allowed": False,
        "live_start_requested": bool(allow_live_start),
        "live_start_performed": False,
        "source_l5_29_summary": dict(source_summary),
        "l5_29_summary": dict(source_summary),
        "source_l5_28_summary": dict(source_summary.get("source_l5_28_summary", {})) if isinstance(source_summary.get("source_l5_28_summary"), Mapping) else {},
        "profile_parent_preflight_aggregate": aggregate_state,
        "profile_parent_preflight_aggregate_gate_enforced": aggregate_state["profile_parent_preflight_aggregate_gate_enforced"],
        "profile_parent_preflight_aggregate_status": aggregate_state["profile_parent_preflight_aggregate_status"],
        "profile_parent_preflight_aggregate_reason": aggregate_state["profile_parent_preflight_aggregate_reason"],
        "profile_parent_preflight_status": source_summary.get("profile_parent_preflight_status"),
        "profile_parent_preflight_reason": source_summary.get("profile_parent_preflight_reason"),
        "profile_parent_path_derived": source_summary.get("profile_parent_path_derived"),
        "profile_parent_path": source_summary.get("profile_parent_path"),
        "profile_parent_probe_required_before_future_live_start": source_summary.get("profile_parent_probe_required_before_future_live_start"),
        "profile_parent_must_exist_before_future_live_start": source_summary.get("profile_parent_must_exist_before_future_live_start"),
        "profile_parent_creation_allowed_in_l5_28": source_summary.get("profile_parent_creation_allowed_in_l5_28"),
        "profile_dir_argument_present": source_summary.get("profile_dir_argument_present"),
        "profile_dir_argument_value": source_summary.get("profile_dir_argument_value"),
        "dedicated_non_default_profile_present": source_summary.get("dedicated_non_default_profile_present"),
        "default_profile_candidate_detected": source_summary.get("default_profile_candidate_detected"),
        "default_profile_path_rejected": source_summary.get("default_profile_path_rejected"),
        "default_microsoft_edge_profile_forbidden": source_summary.get("default_microsoft_edge_profile_forbidden"),
        "command_static_presence": command_state,
        "source_command_static_presence": source_command_state,
        "command_state": {"ok": command_state.get("ok") is True and source_command_state.get("ok") is True, "command_states": {COMMAND_NAME: command_state, SOURCE_COMMAND_NAME: source_command_state}},
        "doc_requirements": {key: list(value) for key, value in DOC_REQUIREMENTS.items()},
        "doc_state": doc_state,
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "missing_repo_paths": missing_repo_paths,
        "command_plan": list(COMMAND_PLAN),
        "command_plan_state": command_plan_state,
        "executed_validation_commands": [],
        "checks": checks,
    }
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        f"{NAME}",
        f"Status          : {payload.get('status')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Aggregate       : {payload.get('profile_parent_preflight_aggregate_status')}",
        f"Parent Derived  : {payload.get('profile_parent_path_derived')}",
        f"Parent Path     : {payload.get('profile_parent_path')}",
        f"Parent Probe    : {payload.get('profile_parent_filesystem_probe_performed')}",
        f"Parent Created  : {payload.get('profile_parent_directory_created')}",
        f"Browser Started : {payload.get('browser_started')}",
        f"Selenium Import : {payload.get('selenium_imported_by_readback')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_supervised_launch_profile_parent_preflight_aggregate_gate(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
    )
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
