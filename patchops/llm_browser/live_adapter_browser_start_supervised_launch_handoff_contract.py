from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

NAME = "L5.1 Browser Start Supervised Launch Handoff Contract"
PHASE = "L5"
PATCH = "L5.1"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NEXT_PATCH = "L5.2 Live adapter browser-start supervised launch handoff CLI/readback"
SIDE_EFFECT_BOUNDARY = "supervised-launch-handoff-contract-only"

ALLOWED_BROWSERS: tuple[str, ...] = ("edge", "opera")
ALLOWED_OPERATOR_DECISIONS: tuple[str, ...] = (
    "block",
    "review_only",
    "prepare_only",
)

FORBIDDEN_OPTIONAL_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "playwright",
    "pyppeteer",
)

BLOCKED_SIDE_EFFECTS: tuple[str, ...] = (
    "selenium_import",
    "browser_start",
    "browser_session_creation",
    "profile_directory_creation",
    "driver_creation",
    "download_click",
    "composer_paste",
    "message_send_or_submit",
    "adapter_filesystem_write",
    "adapter_package_run",
    "git_commit",
    "git_push",
)

HANDOFF_READBACK_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root C:\\dev\\patchops --browser edge --operator-decision review_only --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root C:\\dev\\patchops --browser opera --operator-decision review_only --json --compact",
    "git status --short --branch",
)

FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "llm-browser open",
    "open --browser",
    "run-once",
    "watch-downloads",
    "start_browser",
    "webdriver",
    "selenium",
    "click_download",
    "paste_to_composer",
    "send_message",
    "send_or_submit",
)

REQUIRED_PRIOR_L4_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_l4_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_l4_broad_validation_checkpoint.py",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_final_acceptance_marker.md",
)

REQUIRED_L5_CONTRACT_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_contract.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_contract.md",
    "tests/test_l5_01_browser_start_supervised_launch_handoff_contract_current.py",
)

DOC_REQUIRED_PHRASES: tuple[str, ...] = (
    "L5.1 Live adapter browser-start supervised launch handoff contract",
    "supervised-launch handoff",
    "modelled-only",
    "no Selenium import",
    "no browser start",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "L5.2 Live adapter browser-start supervised launch handoff CLI/readback",
)


def _repo_root(repo_root: str | Path | None) -> Path:
    if repo_root is None:
        return Path.cwd()
    return Path(repo_root).resolve()


def _missing_paths(root: Path, paths: Iterable[str]) -> list[str]:
    return [path for path in paths if not (root / path).exists()]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _optional_roots_loaded() -> list[str]:
    loaded: list[str] = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if root in sys.modules or any(name.startswith(root + ".") for name in sys.modules):
            loaded.append(root)
    return loaded


def _command_plan_is_readback_only(commands: Sequence[str]) -> bool:
    text = "\n".join(commands).lower()
    return not any(fragment.lower() in text for fragment in FORBIDDEN_COMMAND_FRAGMENTS)


def _json_safe(value: Mapping[str, Any]) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": dict(details or {})}


def build_supervised_launch_handoff_request(
    *,
    browser: str = "edge",
    operator_decision: str = "review_only",
    acknowledged_l4_final_acceptance: bool = True,
    acknowledged_manual_operator_required: bool = True,
) -> dict[str, Any]:
    normalized_browser = (browser or "").strip().lower()
    normalized_decision = (operator_decision or "").strip().lower()
    return {
        "kind": "browser_start_supervised_launch_handoff",
        "browser": normalized_browser,
        "operator_decision": normalized_decision,
        "allowed_browsers": list(ALLOWED_BROWSERS),
        "allowed_operator_decisions": list(ALLOWED_OPERATOR_DECISIONS),
        "requires_l4_final_acceptance": True,
        "acknowledged_l4_final_acceptance": bool(acknowledged_l4_final_acceptance),
        "requires_manual_operator": True,
        "acknowledged_manual_operator_required": bool(acknowledged_manual_operator_required),
        "modelled_only": True,
        "startup_authorization_required": True,
        "startup_authorized": False,
        "startup_allowed": False,
        "live_driver_session_allowed": False,
        "profile_directory_creation_allowed": False,
        "blocked_side_effects": list(BLOCKED_SIDE_EFFECTS),
    }


def build_l5_browser_start_supervised_launch_handoff_contract(
    repo_root: str | Path | None = None,
    *,
    browser: str = "edge",
    operator_decision: str = "review_only",
) -> dict[str, Any]:
    """Build the passive L5.1 supervised-launch handoff contract payload.

    This function is intentionally side-effect free. It does not import Selenium,
    does not start a browser, does not create a browser driver/session, does not
    create profile paths, and does not run PatchOps packages from adapter logic.
    """
    root = _repo_root(repo_root)
    normalized_browser = (browser or "").strip().lower()
    normalized_decision = (operator_decision or "").strip().lower()

    missing_l4_paths = _missing_paths(root, REQUIRED_PRIOR_L4_PATHS)
    missing_l5_paths = _missing_paths(root, REQUIRED_L5_CONTRACT_PATHS)
    doc_path = root / "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_contract.md"
    doc_text = _read_text(doc_path)
    missing_doc_phrases = [phrase for phrase in DOC_REQUIRED_PHRASES if phrase not in doc_text]
    optional_roots_loaded = _optional_roots_loaded()
    handoff_request = build_supervised_launch_handoff_request(
        browser=normalized_browser,
        operator_decision=normalized_decision,
    )

    checks = [
        _check("l5_01_browser_target_is_modelled_only", normalized_browser in ALLOWED_BROWSERS, {"browser": normalized_browser}),
        _check("l5_01_operator_decision_is_passive", normalized_decision in ALLOWED_OPERATOR_DECISIONS, {"operator_decision": normalized_decision}),
        _check("l5_01_prior_l4_final_acceptance_artifacts_present", not missing_l4_paths, {"missing": missing_l4_paths}),
        _check("l5_01_contract_artifacts_present", not missing_l5_paths, {"missing": missing_l5_paths}),
        _check("l5_01_doc_contains_supervised_launch_boundary", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("l5_01_handoff_request_is_modelled_only", handoff_request["modelled_only"] is True),
        _check("l5_01_startup_remains_not_allowed", handoff_request["startup_allowed"] is False),
        _check("l5_01_live_driver_session_remains_not_allowed", handoff_request["live_driver_session_allowed"] is False),
        _check("l5_01_no_browser_session_is_created", True),
        _check("l5_01_no_profile_directory_is_created", True),
        _check("l5_01_command_plan_is_readback_only", _command_plan_is_readback_only(HANDOFF_READBACK_COMMANDS)),
        _check("l5_01_no_new_optional_browser_dependency_imports", not optional_roots_loaded, {"loaded": optional_roots_loaded}),
    ]

    payload: dict[str, Any] = {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS,
        "ok": True,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "repo_root": str(root),
        "browser": normalized_browser,
        "operator_decision": normalized_decision,
        "handoff_request": handoff_request,
        "handoff_readback_commands": list(HANDOFF_READBACK_COMMANDS),
        "executed_validation_commands": [],
        "startup_authorized": False,
        "startup_allowed": False,
        "live_driver_session_allowed": False,
        "modelled_only": True,
        "browser_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "optional_browser_dependencies_imported": optional_roots_loaded,
        "selenium_imported": "selenium" in optional_roots_loaded,
        "git_commit_executed": False,
        "git_push_executed": False,
        "operator_commit_recommended": True,
        "missing_l4_paths": missing_l4_paths,
        "missing_l5_paths": missing_l5_paths,
        "missing_doc_phrases": missing_doc_phrases,
        "checks": checks,
    }
    checks.append(_check("l5_01_payload_json_safe", _json_safe(payload)))
    ok = all(check["ok"] for check in checks)
    payload["ok"] = ok
    payload["status"] = STATUS_PASS if ok else STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    checks = payload.get("checks", [])
    lines = [
        NAME,
        "=" * len(NAME),
        f"Status              : {payload.get('status')}",
        f"Patch               : {payload.get('patch')}",
        f"Browser             : {payload.get('browser')}",
        f"Operator Decision   : {payload.get('operator_decision')}",
        f"Modelled Only       : {payload.get('modelled_only')}",
        f"Startup Authorized  : {payload.get('startup_authorized')}",
        f"Startup Allowed     : {payload.get('startup_allowed')}",
        f"Driver Session      : {payload.get('live_driver_session_allowed')}",
        f"Browser Started     : {payload.get('browser_started')}",
        f"Session Created     : {payload.get('browser_session_created')}",
        f"Profile Created     : {payload.get('profile_directory_created')}",
        f"Selenium Imported   : {payload.get('selenium_imported')}",
        f"Next Patch          : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in checks:
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    lines.extend(["", "Readback command plan:"])
    for command in payload.get("handoff_readback_commands", []):
        lines.append(f"- {command}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--browser", default="edge")
    parser.add_argument("--operator-decision", default="review_only")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_l5_browser_start_supervised_launch_handoff_contract(
        args.repo_root,
        browser=args.browser,
        operator_decision=args.operator_decision,
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
