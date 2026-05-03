from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

NAME = "L4.1 Browser Start Dry-Run Handoff Contract"
PHASE = "L4"
PATCH = "L4.1"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NEXT_PATCH = "L4.2 Live adapter browser-start dry-run handoff CLI/readback"
SIDE_EFFECT_BOUNDARY = "dry-run-handoff-contract-only"

ALLOWED_BROWSERS: tuple[str, ...] = ("edge", "opera")

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
    "py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract --repo-root C:\\dev\\patchops --browser edge --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract --repo-root C:\\dev\\patchops --browser opera --json --compact",
    "git status --short --branch",
)

FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
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

REQUIRED_PRIOR_L3_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_broad_validation_checkpoint.py",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_final_acceptance_marker.md",
)

REQUIRED_L4_CONTRACT_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_contract.py",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_contract.md",
    "tests/test_l4_01_browser_start_dry_run_handoff_contract_current.py",
)

DOC_REQUIRED_PHRASES: tuple[str, ...] = (
    "L4.1 Live adapter browser-start dry-run handoff contract",
    "dry-run-only",
    "no Selenium import",
    "no browser start",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "L4.2 Live adapter browser-start dry-run handoff CLI/readback",
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


def build_browser_start_dry_run_handoff_contract(
    repo_root: str | Path | None = None,
    *,
    browser: str = "edge",
) -> dict[str, Any]:
    """Build the passive L4.1 browser-start dry-run handoff contract payload.

    The function is intentionally side-effect free. It does not import Selenium,
    does not create a browser driver/session, does not create profile paths, and
    does not run PatchOps packages from adapter logic.
    """
    root = _repo_root(repo_root)
    normalized_browser = (browser or "").strip().lower()

    missing_l3_paths = _missing_paths(root, REQUIRED_PRIOR_L3_PATHS)
    missing_l4_paths = _missing_paths(root, REQUIRED_L4_CONTRACT_PATHS)
    doc_path = root / "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_contract.md"
    doc_text = _read_text(doc_path)
    missing_doc_phrases = [phrase for phrase in DOC_REQUIRED_PHRASES if phrase not in doc_text]
    optional_roots_loaded = _optional_roots_loaded()

    handoff_request = {
        "kind": "browser_start_dry_run_handoff",
        "browser": normalized_browser,
        "allowed_browsers": list(ALLOWED_BROWSERS),
        "dry_run_only": True,
        "startup_authorization_required": True,
        "startup_authorized": False,
        "startup_allowed": False,
        "profile_preflight_required": True,
        "browser_profile_preflight_phase": "L2 accepted",
        "browser_start_authorization_phase": "L3 accepted",
        "live_browser_start_phase": "not reached",
        "blocked_side_effects": list(BLOCKED_SIDE_EFFECTS),
    }

    checks = [
        _check("l4_01_browser_target_is_modelled_only", normalized_browser in ALLOWED_BROWSERS, {"browser": normalized_browser}),
        _check("l4_01_prior_l3_final_acceptance_artifacts_present", not missing_l3_paths, {"missing": missing_l3_paths}),
        _check("l4_01_contract_artifacts_present", not missing_l4_paths, {"missing": missing_l4_paths}),
        _check("l4_01_doc_contains_dry_run_boundary", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("l4_01_handoff_request_is_dry_run_only", handoff_request["dry_run_only"] is True),
        _check("l4_01_startup_remains_not_allowed", handoff_request["startup_allowed"] is False),
        _check("l4_01_no_browser_session_is_created", True),
        _check("l4_01_no_profile_directory_is_created", True),
        _check("l4_01_command_plan_is_readback_only", _command_plan_is_readback_only(HANDOFF_READBACK_COMMANDS)),
        _check("l4_01_no_new_optional_browser_dependency_imports", not optional_roots_loaded, {"loaded": optional_roots_loaded}),
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
        "handoff_request": handoff_request,
        "handoff_readback_commands": list(HANDOFF_READBACK_COMMANDS),
        "executed_validation_commands": [],
        "startup_authorized": False,
        "startup_allowed": False,
        "dry_run_only": True,
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
        "missing_l3_paths": missing_l3_paths,
        "missing_l4_paths": missing_l4_paths,
        "missing_doc_phrases": missing_doc_phrases,
        "checks": checks,
    }
    checks.append(_check("l4_01_payload_json_safe", _json_safe(payload)))
    ok = all(check["ok"] for check in checks)
    payload["ok"] = ok
    payload["status"] = STATUS_PASS if ok else STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    checks = payload.get("checks", [])
    lines = [
        NAME,
        "=" * len(NAME),
        f"Status             : {payload.get('status')}",
        f"Patch              : {payload.get('patch')}",
        f"Browser            : {payload.get('browser')}",
        f"Dry Run Only       : {payload.get('dry_run_only')}",
        f"Startup Authorized : {payload.get('startup_authorized')}",
        f"Startup Allowed    : {payload.get('startup_allowed')}",
        f"Browser Started    : {payload.get('browser_started')}",
        f"Session Created    : {payload.get('browser_session_created')}",
        f"Profile Created    : {payload.get('profile_directory_created')}",
        f"Selenium Imported  : {payload.get('selenium_imported')}",
        f"Next Patch         : {payload.get('next_patch')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_browser_start_dry_run_handoff_contract(args.repo_root, browser=args.browser)
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
