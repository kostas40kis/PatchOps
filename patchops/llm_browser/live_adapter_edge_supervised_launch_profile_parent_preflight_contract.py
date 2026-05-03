"""L5.28 passive Microsoft Edge supervised-launch profile-parent preflight contract.

This readback models the next safety boundary for future live Edge startup:
a dedicated, non-default profile path must have a parent directory that is
ready before any future browser launch can create/use the child profile.

L5.28 is still passive. It does not import Selenium, start Edge, create a
browser session/driver, probe or create profile directories, click/download,
paste/send, run packages, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_supervised_launch_default_profile_rejection_gate as l5_27

PATCH = "L5.28"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.28 Microsoft Edge Supervised Launch Profile Parent Preflight Contract"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-contract"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate"
NEXT_PATCH = "L5.29 Live adapter Microsoft Edge supervised launch profile parent preflight CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-profile-parent-preflight-contract-only"
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
    "patchops/llm_browser/live_adapter_edge_supervised_launch_default_profile_rejection_gate.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_contract.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_contract.md",
    "tests/test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py",
    "tests/test_l5_28_edge_supervised_launch_profile_parent_preflight_contract_current.py",
)

DOC_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md": (
        "L5.27 Microsoft Edge supervised launch default profile rejection gate",
        SOURCE_COMMAND_NAME,
        "default profile path rejected",
        "no profile directory creation",
        "L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_contract.md": (
        "L5.28 Microsoft Edge supervised launch profile parent preflight contract",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "Microsoft Edge first",
        "Opera second",
        "--allow-live-start",
        "--profile-dir",
        "profile parent preflight contract",
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
        "L5.29 Live adapter Microsoft Edge supervised launch profile parent preflight CLI/readback",
    ),
}

COMMAND_PLAN: tuple[str, ...] = (
    "python -m compileall patchops/llm_browser tests scripts/patch_l5_28_wire_edge_profile_parent_preflight_contract.py",
    "python -m pytest -q tests/test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py tests/test_l5_28_edge_supervised_launch_profile_parent_preflight_contract_current.py",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_profile_parent_preflight_contract --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\dev\\patchops\\data\\runtime\\browser_profiles\\edge_l5_28_candidate --json --compact",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_profile_parent_preflight_contract --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\Users\\kostas\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-profile-parent-preflight-contract --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\dev\\patchops\\data\\runtime\\browser_profiles\\edge_l5_28_candidate --json --compact",
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
        return {
            "ok": command_name in names,
            "command_name": command_name,
            "commands_path": str(Path(commands.__file__).resolve()),
            "sentinel_present": command_name in Path(commands.__file__).read_text(encoding="utf-8"),
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


def _derive_parent_path(profile_dir: str | Path | None) -> str | None:
    if profile_dir is None:
        return None
    raw = str(profile_dir).strip()
    if not raw:
        return None
    if "\\" in raw or (len(raw) >= 2 and raw[1] == ":"):
        return str(PureWindowsPath(raw).parent)
    return str(PurePosixPath(raw).parent)


def _profile_parent_preflight_state(
    *,
    allow_live_start: bool,
    profile_dir: str | Path | None,
    source_summary: Mapping[str, Any],
) -> dict[str, Any]:
    parent_path = _derive_parent_path(profile_dir)
    profile_present = profile_dir is not None and str(profile_dir).strip() != ""
    default_candidate = source_summary.get("default_profile_candidate_detected") is True
    dedicated_candidate = bool(profile_present and not default_candidate)

    if not allow_live_start:
        status = "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
        reason = "Missing --allow-live-start keeps startup blocked before profile-parent preflight can pass."
    elif not profile_present:
        status = "BLOCKED_MISSING_DEDICATED_PROFILE_DIR"
        reason = "Missing --profile-dir keeps startup blocked before profile-parent preflight can pass."
    elif default_candidate:
        status = "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"
        reason = "The normal/default Microsoft Edge profile remains forbidden before profile-parent preflight."
    else:
        status = "BLOCKED_PROFILE_PARENT_PREFLIGHT_MODEL_ONLY"
        reason = "Dedicated non-default profile parent is derived, but L5.28 is still passive and performs no filesystem probe or creation."

    return {
        "profile_parent_preflight_contract_enforced": True,
        "profile_parent_preflight_required": True,
        "profile_parent_preflight_status": status,
        "profile_parent_preflight_reason": reason,
        "profile_parent_path_derived": parent_path is not None,
        "profile_parent_path": parent_path,
        "profile_parent_filesystem_probe_performed": False,
        "profile_parent_probe_required_before_future_live_start": True,
        "profile_parent_must_exist_before_future_live_start": True,
        "profile_parent_directory_created": False,
        "profile_parent_creation_allowed_in_l5_28": False,
        "profile_dir_argument_present": profile_present,
        "profile_dir_argument_required": PROFILE_DIR_ARGUMENT,
        "profile_dir_argument_value": None if profile_dir is None else str(profile_dir),
        "dedicated_non_default_profile_present": dedicated_candidate,
        "dedicated_non_default_profile_required": True,
        "default_profile_candidate_detected": default_candidate,
        "default_profile_path_rejected": source_summary.get("default_profile_path_rejected") is True,
        "default_microsoft_edge_profile_forbidden": True,
        "explicit_operator_authorization_required": True,
        "explicit_operator_authorization_present": bool(allow_live_start),
        "manual_user_login_required": True,
        "silent_auto_submit_default": False,
        "silent_auto_submit_must_remain_false": True,
        "browser_extension_required": False,
        "localhost_patchops_server_required": False,
        "phase_allows_live_start": False,
        "live_start_requested": bool(allow_live_start),
        "live_start_performed": False,
        "startup_authorized": bool(allow_live_start),
        "startup_allowed": False,
        "profile_directory_created": False,
    }


def _source_l5_27_is_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L5.27"
        and summary.get("status") == STATUS_PASS
        and summary.get("ok") is True
        and summary.get("startup_allowed") is False
        and summary.get("live_start_performed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
    )


def build_edge_supervised_launch_profile_parent_preflight_contract(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    source_summary = l5_27.build_edge_supervised_launch_default_profile_rejection_gate(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
    )
    parent_state = _profile_parent_preflight_state(
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        source_summary=source_summary,
    )
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    command_plan_state = _command_plan_state()
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    newly_loaded_forbidden = _forbidden_optional_imports_newly_loaded(before_modules)
    loaded_forbidden = _loaded_forbidden_modules()

    checks = [
        _check("l5_27_default_profile_rejection_gate_still_passes", _source_l5_27_is_safe(source_summary), source_summary),
        _check("l5_27_default_profile_rejection_gate_remains_passive", _source_l5_27_is_safe(source_summary), source_summary),
        _check("l5_27_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("l5_28_profile_parent_preflight_command_registered", command_state.get("ok") is True, command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_l5_docs_contain_profile_parent_preflight_boundary", doc_state.get("ok") is True, doc_state),
        _check("l5_28_command_plan_is_readback_only", command_plan_state.get("ok") is True, command_plan_state),
        _check("adapter_logic_executes_no_validation_commands", command_plan_state.get("executed_by_adapter_logic") == [], command_plan_state),
        _check("profile_parent_preflight_contract_is_enforced", parent_state.get("profile_parent_preflight_contract_enforced") is True, parent_state),
        _check("profile_parent_path_is_derived_when_profile_is_present", (not parent_state.get("profile_dir_argument_present")) or parent_state.get("profile_parent_path_derived") is True, parent_state),
        _check("profile_parent_filesystem_probe_is_not_performed", parent_state.get("profile_parent_filesystem_probe_performed") is False, parent_state),
        _check("profile_parent_directory_is_not_created", parent_state.get("profile_parent_directory_created") is False, parent_state),
        _check("dedicated_non_default_profile_still_cannot_start_edge_in_l5_28", parent_state.get("startup_allowed") is False and parent_state.get("live_start_performed") is False, parent_state),
        _check("default_profile_remains_forbidden_before_parent_preflight", ((not parent_state.get("default_profile_candidate_detected")) or parent_state.get("default_profile_path_rejected") is True) and parent_state.get("startup_allowed") is False, parent_state),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("selenium_not_imported_by_profile_parent_preflight", not newly_loaded_forbidden and "selenium" not in loaded_forbidden, {"newly_loaded_forbidden": newly_loaded_forbidden, "loaded_forbidden": loaded_forbidden}),
        _check(
            "no_browser_profile_or_adapter_side_effects",
            all(
                [
                    parent_state.get("startup_allowed") is False,
                    parent_state.get("live_start_performed") is False,
                    source_summary.get("browser_started") is False,
                    source_summary.get("edge_process_started") is False,
                    source_summary.get("browser_session_created") is False,
                    source_summary.get("driver_created") is False,
                    source_summary.get("profile_directory_created") is False,
                    parent_state.get("profile_parent_directory_created") is False,
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
        "source_l5_27_summary": dict(source_summary),
        "l5_27_summary": dict(source_summary),
        "profile_parent_preflight": parent_state,
        "profile_parent_preflight_contract_enforced": parent_state["profile_parent_preflight_contract_enforced"],
        "profile_parent_preflight_status": parent_state["profile_parent_preflight_status"],
        "profile_parent_preflight_reason": parent_state["profile_parent_preflight_reason"],
        "profile_parent_path_derived": parent_state["profile_parent_path_derived"],
        "profile_parent_path": parent_state["profile_parent_path"],
        "profile_parent_filesystem_probe_performed": parent_state["profile_parent_filesystem_probe_performed"],
        "profile_parent_probe_required_before_future_live_start": parent_state["profile_parent_probe_required_before_future_live_start"],
        "profile_parent_must_exist_before_future_live_start": parent_state["profile_parent_must_exist_before_future_live_start"],
        "profile_parent_directory_created": parent_state["profile_parent_directory_created"],
        "profile_parent_creation_allowed_in_l5_28": parent_state["profile_parent_creation_allowed_in_l5_28"],
        "profile_dir_argument_present": parent_state["profile_dir_argument_present"],
        "profile_dir_argument_value": parent_state["profile_dir_argument_value"],
        "dedicated_non_default_profile_present": parent_state["dedicated_non_default_profile_present"],
        "default_profile_candidate_detected": parent_state["default_profile_candidate_detected"],
        "default_profile_path_rejected": parent_state["default_profile_path_rejected"],
        "default_microsoft_edge_profile_forbidden": parent_state["default_microsoft_edge_profile_forbidden"],
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

    payload = build_edge_supervised_launch_profile_parent_preflight_contract(
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
