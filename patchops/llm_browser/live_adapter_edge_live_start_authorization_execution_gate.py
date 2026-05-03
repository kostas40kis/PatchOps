"""L15.1 passive Microsoft Edge live-start authorization/execution gate.

This is the first L15 surface after the accepted L14.9 dedicated-profile
lifecycle final marker. It defines the explicit authorization and token gate
needed before any future Microsoft Edge live-start proof can be considered.

L15.1 is still passive. It does not import Selenium, start Edge, create a
browser session, create or mutate a profile directory, click, download, paste,
send, run a package from the browser, start localhost, use a browser extension,
commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_dedicated_profile_lifecycle_final_acceptance_marker as l14_09

PATCH = "L15.1"
PHASE = "L15"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L15.1 Microsoft Edge live-start authorization/execution gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker"
NEXT_PATCH = "L15.2 Microsoft Edge live-start authorization/execution gate CLI readback"
AUTHORIZATION_FLAG = "--allow-live-start"
AUTHORIZATION_TOKEN_ARGUMENT = "--authorization-token"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED"
BROWSER_PRIORITY = ("edge", "opera")
ACTIVE_BROWSER = "edge"
OPERA_STATUS = "second-priority-not-active-in-l15-1"
SIDE_EFFECT_BOUNDARY = "edge-live-start-authorization-execution-gate-passive-only"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

DEFAULT_PROFILE_MARKERS = (
    "microsoft/edge/user data/default",
    "microsoft\\edge\\user data\\default",
    "/edge/user data/default",
    "\\edge\\user data\\default",
    "user data/default",
    "user data\\default",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_live_start_authorization_execution_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_dedicated_profile_lifecycle_final_acceptance_marker.md",
    "docs/llm_browser_live_adapter_edge_live_start_authorization_execution_gate.md",
    "scripts/patch_l15_01_brief_validate.py",
    "tests/test_l15_01_edge_live_start_authorization_execution_gate_current.py",
)

SAFETY_PHRASES = (
    "Microsoft Edge first",
    "Opera second",
    "explicit live-start authorization flag required",
    "explicit live-start authorization token required",
    "dedicated profile candidate inherited from L14.9",
    "default Microsoft Edge profile rejected",
    "launch execution allowed: false",
    "L15.1 is passive",
    "no Selenium import",
    "no browser start",
    "no Edge process start",
    "no browser session creation",
    "no driver creation",
    "no profile directory creation",
    "no profile directory mutation",
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    NEXT_PATCH,
)


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _repo_root(repo_root: str | Path | None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    candidate = Path(repo_root)
    if str(candidate) == ".":
        return Path.cwd().resolve()
    return candidate.resolve()


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _missing_doc_phrases(root: Path) -> list[str]:
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_live_start_authorization_execution_gate.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _command_names() -> tuple[str, ...]:
    try:
        from patchops.llm_browser import commands
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _looks_like_default_edge_profile(value: str | None) -> bool:
    if not value:
        return False
    normalized = value.replace("\\", "/").lower()
    return any(marker.replace("\\", "/").lower() in normalized for marker in DEFAULT_PROFILE_MARKERS)


def _source_l14_09_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L14.9"
        and source.get("l14_complete") is True
        and source.get("remaining_l14_patches") == []
        and source.get("profile_final_marker_truthful") is True
        and source.get("profile_final_marker_is_passive") is True
        and source.get("profile_candidate_under_allowed_runtime_root") is True
        and source.get("profile_lifecycle_steps_are_passive") is True
        and source.get("profile_directory_created") is False
        and source.get("profile_directory_mutated") is False
        and source.get("filesystem_writes_performed") == []
        and source.get("adapter_filesystem_writes_performed") == []
        and source.get("side_effects_performed") == []
        and source.get("launch_execution_allowed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("browser_session_created") is False
        and source.get("driver_created") is False
        and source.get("selenium_imported_by_readback") is False
    )


def build_edge_live_start_authorization_execution_gate(
    repo_root: str | Path | None = None,
    *,
    browser: str = ACTIVE_BROWSER,
    allow_live_start: bool = False,
    authorization_token: str | None = None,
    profile_relative_path: str | None = None,
) -> dict[str, Any]:
    """Build the passive L15.1 live-start authorization/execution gate payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    source = l14_09.build_edge_dedicated_profile_lifecycle_final_acceptance_marker(
        root,
        profile_relative_path=profile_relative_path,
    )

    required = _required_paths_status(root)
    command_names = _command_names()
    missing_commands = [COMMAND_NAME] if COMMAND_NAME not in command_names else []
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    normalized_browser = (browser or "").strip().lower()
    edge_is_active_target = normalized_browser == ACTIVE_BROWSER
    source_safe = _source_l14_09_safe(source)
    profile_candidate_path = source.get("profile_candidate_path") if isinstance(source.get("profile_candidate_path"), str) else None
    profile_candidate_present = bool(profile_candidate_path)
    default_profile_requested = _looks_like_default_edge_profile(profile_relative_path) or _looks_like_default_edge_profile(profile_candidate_path)
    dedicated_profile_candidate_ready = source_safe and profile_candidate_present and not default_profile_requested

    explicit_flag_present = bool(allow_live_start)
    explicit_token_present = authorization_token == REQUIRED_AUTHORIZATION_TOKEN
    operator_authorization_complete = explicit_flag_present and explicit_token_present

    # L15.1 deliberately never crosses the execution boundary. The flag/token
    # prove the authorization surface only. L15.2 is expected to add a compact
    # CLI/readback wrapper over this same gate, still before any live open proof.
    launch_execution_allowed = False

    checks = [
        _check("source_l14_09_final_marker_accepted", source_safe, {"source_patch": source.get("patch"), "l14_complete": source.get("l14_complete")}),
        _check("microsoft_edge_is_active_l15_target", edge_is_active_target, {"browser": normalized_browser}),
        _check("opera_remains_second_priority", True, {"opera_status": OPERA_STATUS}),
        _check("dedicated_profile_candidate_inherited_from_l14_09", dedicated_profile_candidate_ready, {"profile_candidate_path": profile_candidate_path}),
        _check("default_edge_profile_rejected", not default_profile_requested, {"profile_relative_path": profile_relative_path}),
        _check("explicit_authorization_flag_surface_present", AUTHORIZATION_FLAG == "--allow-live-start"),
        _check("explicit_authorization_token_surface_present", REQUIRED_AUTHORIZATION_TOKEN == "PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED"),
        _check("missing_or_incomplete_authorization_keeps_execution_blocked", (operator_authorization_complete or not launch_execution_allowed)),
        _check("authorization_surface_readback_truthful", (operator_authorization_complete == (explicit_flag_present and explicit_token_present))),
        _check("l15_1_is_passive", launch_execution_allowed is False),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l15_1_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("no_forbidden_optional_browser_imports", not forbidden_imports_newly_loaded, {"newly_loaded": forbidden_imports_newly_loaded}),
    ]
    ok = all(item["ok"] for item in checks)

    return {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "source_patch": "L14.9",
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "browser": normalized_browser,
        "microsoft_edge_first": True,
        "opera_second": True,
        "active_browser": ACTIVE_BROWSER,
        "opera_active_implementation_target": False,
        "source_l14_09_final_marker_accepted": source_safe,
        "source_l14_09_status": {
            "ok": source.get("ok"),
            "status": source.get("status"),
            "patch": source.get("patch"),
            "l14_complete": source.get("l14_complete"),
            "remaining_l14_patches": source.get("remaining_l14_patches"),
            "profile_final_marker_truthful": source.get("profile_final_marker_truthful"),
            "profile_final_marker_is_passive": source.get("profile_final_marker_is_passive"),
            "profile_candidate_under_allowed_runtime_root": source.get("profile_candidate_under_allowed_runtime_root"),
            "profile_directory_created": source.get("profile_directory_created"),
            "profile_directory_mutated": source.get("profile_directory_mutated"),
            "launch_execution_allowed": source.get("launch_execution_allowed"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
        },
        "explicit_live_start_authorization_flag_required": True,
        "explicit_live_start_authorization_flag": AUTHORIZATION_FLAG,
        "explicit_live_start_authorization_flag_present": explicit_flag_present,
        "explicit_live_start_authorization_token_required": True,
        "explicit_live_start_authorization_token_argument": AUTHORIZATION_TOKEN_ARGUMENT,
        "explicit_live_start_authorization_token_present": explicit_token_present,
        "required_authorization_token_value": REQUIRED_AUTHORIZATION_TOKEN,
        "live_start_operator_authorization_complete": operator_authorization_complete,
        "authorization_missing_keeps_execution_blocked": not operator_authorization_complete and launch_execution_allowed is False,
        "authorization_present_is_readback_only_in_l15_1": operator_authorization_complete and launch_execution_allowed is False,
        "dedicated_profile_required": True,
        "dedicated_profile_candidate_inherited_from_l14_09": dedicated_profile_candidate_ready,
        "profile_relative_path": profile_relative_path,
        "profile_candidate_path": profile_candidate_path,
        "profile_candidate_under_allowed_runtime_root": source.get("profile_candidate_under_allowed_runtime_root"),
        "default_edge_profile_rejected": not default_profile_requested,
        "default_edge_profile_requested": default_profile_requested,
        "default_profile_use_allowed": False,
        "manual_user_login_required_later": True,
        "auto_send_default": False,
        "auto_send_allowed": False,
        "live_start_execution_gate_enforced": True,
        "live_start_execution_gate_truthful": True,
        "live_start_execution_gate_passive": True,
        "first_real_edge_start_allowed_in_l15_1": False,
        "launch_execution_allowed": launch_execution_allowed,
        "browser_process_launch_requested": False,
        "browser_process_launch_authorized": operator_authorization_complete,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "profile_directory_creation_allowed": False,
        "profile_directory_mutation_allowed": False,
        "profile_directory_created": False,
        "profile_directory_mutated": False,
        "filesystem_writes_performed": [],
        "adapter_filesystem_writes_performed": [],
        "side_effects_performed": [],
        "click_download_performed": False,
        "download_performed": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "localhost_patchops_server_started": False,
        "browser_extension_used": False,
        "git_commit_executed": False,
        "git_push_executed": False,
        "operator_review_required_before_live_start": True,
        "l15_1_complete": ok,
        "remaining_l15_1_patches": [] if ok else [PATCH],
        "required_repo_paths": required,
        "missing_commands": missing_commands,
        "missing_doc_phrases": missing_doc_phrases,
        "forbidden_optional_browser_imports_newly_loaded": forbidden_imports_newly_loaded,
        "checks": checks,
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch              : {payload.get('patch')}",
        f"Status             : {payload.get('status')}",
        f"Command            : {payload.get('command_name')}",
        f"Source Command     : {payload.get('source_command_name')}",
        f"Browser            : {payload.get('browser')}",
        f"Edge First         : {payload.get('microsoft_edge_first')}",
        f"Opera Second       : {payload.get('opera_second')}",
        f"Flag Required      : {payload.get('explicit_live_start_authorization_flag')}",
        f"Token Required     : {payload.get('required_authorization_token_value')}",
        f"Operator Authorized: {payload.get('live_start_operator_authorization_complete')}",
        f"Launch Allowed     : {payload.get('launch_execution_allowed')}",
        f"Browser Started    : {payload.get('browser_started')}",
        f"Edge Process Start : {payload.get('edge_process_started')}",
        f"Profile Created    : {payload.get('profile_directory_created')}",
        f"Default Rejected   : {payload.get('default_edge_profile_rejected')}",
        f"Next Patch         : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--browser", default=ACTIVE_BROWSER, choices=("edge", "opera"))
    parser.add_argument("--allow-live-start", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--profile-relative-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_live_start_authorization_execution_gate(
        args.repo_root,
        browser=args.browser,
        allow_live_start=args.allow_live_start,
        authorization_token=args.authorization_token,
        profile_relative_path=args.profile_relative_path,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
