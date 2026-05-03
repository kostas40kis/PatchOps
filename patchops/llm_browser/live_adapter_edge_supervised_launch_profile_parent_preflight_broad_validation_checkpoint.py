"""L5.32 passive Edge profile-parent preflight broad validation checkpoint.

This checkpoint aggregates the accepted L5.28 through L5.31 parent-preflight
surfaces and keeps validation output brief. It remains passive: no Selenium
import, browser start, Edge process, driver/session creation, profile directory
creation, profile-parent filesystem probe, click/download, paste/send,
package-run, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback as l5_31

PATCH = "L5.32"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.32 Microsoft Edge Supervised Launch Profile Parent Preflight Broad Validation Checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-broad-validation-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-readback"
NEXT_PATCH = "L5.33 Live adapter Microsoft Edge supervised launch profile parent preflight final acceptance marker"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-profile-parent-preflight-broad-validation-checkpoint-only"
AUTHORIZATION_FLAG = "--allow-live-start"
PROFILE_DIR_ARGUMENT = "--profile-dir"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_contract.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_broad_validation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_contract.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_broad_validation_checkpoint.md",
    "tests/test_l5_28_edge_supervised_launch_profile_parent_preflight_contract_current.py",
    "tests/test_l5_29_edge_supervised_launch_profile_parent_preflight_cli_readback_current.py",
    "tests/test_l5_30_edge_supervised_launch_profile_parent_preflight_aggregate_gate_current.py",
    "tests/test_l5_31_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback_current.py",
    "tests/test_l5_32_edge_supervised_launch_profile_parent_preflight_broad_validation_checkpoint_current.py",
    "scripts/patch_l5_31_brief_validate.py",
    "scripts/patch_l5_32_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback.md": (
        "L5.31 Microsoft Edge supervised launch profile parent preflight aggregate gate CLI/readback",
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "L5.32 Live adapter Microsoft Edge supervised launch profile parent preflight broad validation checkpoint",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_broad_validation_checkpoint.md": (
        "L5.32 Microsoft Edge supervised launch profile parent preflight broad validation checkpoint",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "L5.28 profile parent preflight contract remains accepted",
        "L5.29 profile parent preflight CLI/readback remains accepted",
        "L5.30 profile parent preflight aggregate gate remains accepted",
        "L5.31 profile parent preflight aggregate CLI/readback remains accepted",
        "profile parent filesystem probe not performed",
        "profile parent directory not created",
        "default Microsoft Edge profile remains forbidden",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L5.33 Live adapter Microsoft Edge supervised launch profile parent preflight final acceptance marker",
    ),
}


def _repo_root(repo_root: str | Path | None = None) -> Path:
    return Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()


def _missing_paths(root: Path, rel_paths: Iterable[str]) -> list[str]:
    return [rel for rel in rel_paths if not (root / rel).exists()]


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _new_forbidden_imports(before: set[str]) -> list[str]:
    after = set(sys.modules)
    newly_loaded = after - before
    found = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(found)


def _command_static_presence(command_name: str) -> dict[str, Any]:
    try:
        from patchops.llm_browser import commands
        names = tuple(commands.llm_browser_command_names())
        path = Path(commands.__file__).resolve()
        text = path.read_text(encoding="utf-8")
        return {"ok": command_name in names, "command_name": command_name, "commands_path": str(path), "sentinel_present": command_name in text}
    except Exception as exc:
        return {"ok": False, "command_name": command_name, "error": f"{type(exc).__name__}: {exc}"}


def _doc_state(repo_root: Path) -> dict[str, Any]:
    missing_docs = []
    missing_phrases: dict[str, list[str]] = {}
    state = {}
    for rel, phrases in DOC_REQUIREMENTS.items():
        path = repo_root / rel
        if not path.exists():
            missing_docs.append(rel)
            missing_phrases[rel] = list(phrases)
            state[rel] = {"exists": False, "missing_phrases": list(phrases)}
            continue
        text = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in phrases if phrase not in text]
        state[rel] = {"exists": True, "missing_phrases": missing}
        if missing:
            missing_phrases[rel] = missing
    return {"ok": not missing_docs and not missing_phrases, "missing_docs": missing_docs, "missing_phrases": missing_phrases, "doc_state": state}


def _source_l5_31_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L5.31"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("source_l5_30_summary", {}).get("patch") == "L5.30"
        and summary.get("source_l5_30_summary", {}).get("ok") is True
        and summary.get("source_l5_29_summary", {}).get("patch") == "L5.29"
        and summary.get("source_l5_29_summary", {}).get("ok") is True
        and summary.get("source_l5_28_summary", {}).get("patch") == "L5.28"
        and summary.get("source_l5_28_summary", {}).get("ok") is True
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
    )


def build_edge_supervised_launch_profile_parent_preflight_broad_validation_checkpoint(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l5_31.build_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
    )
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    l5_30 = source.get("source_l5_30_summary", {}) if isinstance(source.get("source_l5_30_summary"), Mapping) else {}
    l5_29 = source.get("source_l5_29_summary", {}) if isinstance(source.get("source_l5_29_summary"), Mapping) else {}
    l5_28 = source.get("source_l5_28_summary", {}) if isinstance(source.get("source_l5_28_summary"), Mapping) else {}

    checks = [
        _check("l5_31_profile_parent_preflight_aggregate_readback_still_passes", _source_l5_31_safe(source), {"patch": source.get("patch"), "ok": source.get("ok"), "status": source.get("status")}),
        _check("l5_31_profile_parent_preflight_aggregate_readback_remains_passive", _source_l5_31_safe(source), {"browser_started": source.get("browser_started"), "profile_parent_directory_created": source.get("profile_parent_directory_created")}),
        _check("l5_30_aggregate_gate_remains_in_chain", l5_30.get("patch") == "L5.30" and l5_30.get("ok") is True, {"patch": l5_30.get("patch"), "ok": l5_30.get("ok")}),
        _check("l5_29_cli_readback_remains_in_chain", l5_29.get("patch") == "L5.29" and l5_29.get("ok") is True, {"patch": l5_29.get("patch"), "ok": l5_29.get("ok")}),
        _check("l5_28_contract_remains_in_chain", l5_28.get("patch") == "L5.28" and l5_28.get("ok") is True, {"patch": l5_28.get("patch"), "ok": l5_28.get("ok")}),
        _check("l5_32_broad_checkpoint_command_registered", command_state.get("ok") is True, command_state),
        _check("l5_31_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l5_docs_contain_broad_checkpoint_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("profile_parent_probe_stays_false", source.get("profile_parent_filesystem_probe_performed") is False, {}),
        _check("profile_parent_directory_stays_uncreated", source.get("profile_parent_directory_created") is False, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", _source_l5_31_safe(source), {}),
    ]
    ok = all(check["ok"] for check in checks)

    return {
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
        "brief_validation_output_enabled": True,
        "l5_28_profile_parent_preflight_contract_remains_accepted": l5_28.get("ok") is True and l5_28.get("status") == STATUS_PASS,
        "l5_29_profile_parent_preflight_cli_readback_remains_accepted": l5_29.get("ok") is True and l5_29.get("status") == STATUS_PASS,
        "l5_30_profile_parent_preflight_aggregate_gate_remains_accepted": l5_30.get("ok") is True and l5_30.get("status") == STATUS_PASS,
        "l5_31_profile_parent_preflight_aggregate_cli_readback_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "source_l5_31_summary": source,
        "source_l5_30_summary": l5_30,
        "source_l5_29_summary": l5_29,
        "source_l5_28_summary": l5_28,
        "profile_parent_preflight_status": source.get("profile_parent_preflight_status"),
        "profile_parent_preflight_aggregate_status": source.get("profile_parent_preflight_aggregate_status"),
        "profile_parent_path_derived": source.get("profile_parent_path_derived"),
        "profile_parent_path": source.get("profile_parent_path"),
        "profile_parent_filesystem_probe_performed": False,
        "profile_parent_directory_created": False,
        "profile_directory_created": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "startup_allowed": False,
        "live_start_performed": False,
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
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "optional_browser_dependencies_required": False,
        "command_static_presence": command_state,
        "source_command_static_presence": source_command_state,
        "doc_state": doc_state,
        "missing_repo_paths": missing_paths,
        "checks": checks,
        "executed_validation_commands": [],
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        f"Status          : {payload.get('status')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Brief Output    : {payload.get('brief_validation_output_enabled')}",
        f"L5.28 Accepted  : {payload.get('l5_28_profile_parent_preflight_contract_remains_accepted')}",
        f"L5.29 Accepted  : {payload.get('l5_29_profile_parent_preflight_cli_readback_remains_accepted')}",
        f"L5.30 Accepted  : {payload.get('l5_30_profile_parent_preflight_aggregate_gate_remains_accepted')}",
        f"L5.31 Accepted  : {payload.get('l5_31_profile_parent_preflight_aggregate_cli_readback_remains_accepted')}",
        f"Parent Probe    : {payload.get('profile_parent_filesystem_probe_performed')}",
        f"Parent Created  : {payload.get('profile_parent_directory_created')}",
        f"Browser Started : {payload.get('browser_started')}",
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
    payload = build_edge_supervised_launch_profile_parent_preflight_broad_validation_checkpoint(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
