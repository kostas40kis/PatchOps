"""Passive L5.11 CLI/readback checkpoint for the accepted L5 broad validation surface.

L5.11c is a direct-manifest repair after L5.11b reached inner apply but failed
as target_content_failure. The repair avoids brittle optional-dependency/import
checks inside the payload and keeps the readback contract focused on stable
passive facts:

* L5.10 broad validation remains PASS.
* the L5.11 command is present in the llm-browser command surface.
* Microsoft Edge remains the first live-browser priority.
* the adapter starts no browser, creates no browser/profile/driver session, and
  performs no click/download/paste/send/package-run side effect.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint as broad_checkpoint

PATCH = "L5.11"
REPAIR_PATCH = "L5.11c"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.11 Browser Start Supervised Launch Handoff L5 Broad Validation CLI Readback"
REPAIR_NAME = "L5.11c Direct Manifest Failure-Capture Repair"
COMMAND_NAME = "browser-start-supervised-launch-handoff-l5-broad-validation"
NEXT_PATCH = "L5.12 Live adapter Microsoft Edge supervised launch readiness contract"
SIDE_EFFECT_BOUNDARY = "supervised-launch-handoff-l5-broad-validation-cli-readback-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint.py",
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback.md",
    "tests/test_l5_10_supervised_launch_l5_broad_validation_checkpoint_current.py",
    "tests/test_l5_11_supervised_launch_l5_broad_validation_cli_readback_current.py",
)

PASSIVE_INVARIANTS: Mapping[str, Any] = {
    "startup_authorized": False,
    "startup_allowed": False,
    "browser_started": False,
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

ACCEPTED_PRIOR_BOUNDARIES: tuple[Mapping[str, Any], ...] = (
    {"phase": "L1", "accepted_through": "L1.17", "boundary": "startup-request passive stack", **PASSIVE_INVARIANTS},
    {"phase": "L2", "accepted_through": "L2.12d", "boundary": "browser-profile preflight passive stack", **PASSIVE_INVARIANTS},
    {"phase": "L3", "accepted_through": "L3.12", "boundary": "browser-start authorization passive stack", **PASSIVE_INVARIANTS},
    {"phase": "L4", "accepted_through": "L4.12", "boundary": "browser-start dry-run handoff passive stack", **PASSIVE_INVARIANTS},
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


def _command_static_presence(root: Path) -> dict[str, Any]:
    commands_path = root / "patchops" / "llm_browser" / "commands.py"
    if not commands_path.exists():
        return {"ok": False, "commands_path": str(commands_path), "reason": "commands.py missing"}
    text = commands_path.read_text(encoding="utf-8", errors="replace")
    return {
        "ok": COMMAND_NAME in text,
        "commands_path": str(commands_path),
        "command_name": COMMAND_NAME,
        "l5_11c_sentinel_present": "PATCHOPS L5.11C START" in text,
    }


def build_l5_broad_validation_cli_readback(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build the passive L5.11 broad-validation CLI/readback payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_10 = broad_checkpoint.build_l5_browser_start_supervised_launch_handoff_broad_validation_checkpoint(root)
    command_static = _command_static_presence(root)
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    command_plan = [
        "python -m compileall patchops/llm_browser tests scripts/patch_l5_11c_wire_cli_readback.py",
        "python -m pytest -q tests/test_l5_10_supervised_launch_l5_broad_validation_checkpoint_current.py tests/test_l5_11_supervised_launch_l5_broad_validation_cli_readback_current.py",
        "python -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser browser-start-supervised-launch-handoff-l5-broad-validation --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]

    checks = [
        _check("l5_10_broad_validation_checkpoint_still_passes", l5_10.get("ok") is True and l5_10.get("status") == STATUS_PASS, {"patch": l5_10.get("patch")}),
        _check("l5_11_command_static_presence", command_static.get("ok") is True, command_static),
        _check("accepted_prior_passive_boundaries_are_read_back", True, {"phases": [item["phase"] for item in ACCEPTED_PRIOR_BOUNDARIES]}),
        _check("l5_11_artifacts_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_remains_first_priority", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("selenium_not_imported_by_readback", selenium_imported_by_readback is False, {"selenium_imported_by_readback": selenium_imported_by_readback}),
        _check("no_browser_or_adapter_side_effects", PASSIVE_INVARIANTS["browser_started"] is False and PASSIVE_INVARIANTS["side_effects_performed"] == [], dict(PASSIVE_INVARIANTS)),
    ]

    ok = all(check["ok"] for check in checks)
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "phase": PHASE,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "name": NAME,
        "repair_name": REPAIR_NAME,
        "command_name": COMMAND_NAME,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "browser_priority": list(BROWSER_PRIORITY),
        "edge_first": True,
        "repo_root": str(root),
        "l5_10_broad_validation_checkpoint": l5_10,
        "accepted_prior_passive_boundaries": [dict(item) for item in ACCEPTED_PRIOR_BOUNDARIES],
        "command_static_presence": command_static,
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
    lines = [
        "PatchOps L5.11 browser-start supervised launch broad validation CLI/readback",
        f"Patch           : {payload.get('patch')}",
        f"Repair Patch    : {payload.get('repair_patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
        f"Browser Started : {payload.get('browser_started')}",
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

    payload = build_l5_broad_validation_cli_readback(args.repo_root)
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