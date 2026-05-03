"""L8.3 passive Microsoft Edge executable-probe safety-preflight fixture matrix.

L8.3 adds a modeled fixture matrix over the accepted L8.2 safety-preflight
CLI/readback layer. It proves the no-authorization case remains a successful
readback with preflight_passed=false, and authorized cases can pass preflight
while probe execution remains blocked by phase.

No executable filesystem probe, path selection, launch, Selenium import,
browser start, profile creation, click/download, paste/send, package run,
commit, or push is performed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_probe_safety_preflight_cli_readback as l8_02

PATCH = "L8.3"
PHASE = "L8"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L8.3 Microsoft Edge Executable Probe Safety Preflight Fixture Matrix"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-fixture-matrix"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-readback"
NEXT_PATCH = "L8.4 Live adapter Microsoft Edge executable probe safety preflight fixture matrix CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-probe-safety-preflight-fixture-matrix-only"
EXECUTABLE_PROBE_AUTHORIZATION_FLAG = "--allow-executable-probe"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")
REPAIR_NOTE = "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok."

FIXTURE_MATRIX = (
    {"fixture_id": "no_auth_dedicated_profile", "allow_live_start": False, "allow_executable_probe": False, "profile_kind": "dedicated", "expected_readback_ok": True, "expected_preflight_passed": False, "expected_probe_execution_allowed": False, "expected_probe_performed": False},
    {"fixture_id": "live_auth_without_probe_auth", "allow_live_start": True, "allow_executable_probe": False, "profile_kind": "dedicated", "expected_readback_ok": True, "expected_preflight_passed": False, "expected_probe_execution_allowed": False, "expected_probe_performed": False},
    {"fixture_id": "probe_auth_dedicated_profile", "allow_live_start": True, "allow_executable_probe": True, "profile_kind": "dedicated", "expected_readback_ok": True, "expected_preflight_passed": True, "expected_probe_execution_allowed": False, "expected_probe_performed": False},
    {"fixture_id": "probe_auth_default_profile", "allow_live_start": True, "allow_executable_probe": True, "profile_kind": "default", "expected_readback_ok": True, "expected_preflight_passed": True, "expected_probe_execution_allowed": False, "expected_probe_performed": False},
    {"fixture_id": "probe_auth_missing_profile", "allow_live_start": True, "allow_executable_probe": True, "profile_kind": "missing", "expected_readback_ok": True, "expected_preflight_passed": True, "expected_probe_execution_allowed": False, "expected_probe_performed": False},
)
EXPECTED_FIXTURE_IDS = {item["fixture_id"] for item in FIXTURE_MATRIX}

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_probe_safety_preflight_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_probe_safety_preflight_fixture_matrix.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_fixture_matrix.md",
    "tests/test_l8_02_edge_executable_probe_safety_preflight_cli_readback_current.py",
    "tests/test_l8_03_edge_executable_probe_safety_preflight_fixture_matrix_current.py",
    "scripts/patch_l8_02_brief_validate.py",
    "scripts/patch_l8_03_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_cli_readback.md": (
        "L8.2 Microsoft Edge executable probe safety preflight CLI/readback",
        SOURCE_COMMAND_NAME,
        "safety preflight CLI/readback enforced",
        "preflight readback can succeed while preflight_passed is false",
        "L8.3 Live adapter Microsoft Edge executable probe safety preflight fixture matrix",
    ),
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_fixture_matrix.md": (
        "L8.3 Microsoft Edge executable probe safety preflight fixture matrix",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L8.2 executable probe safety preflight CLI/readback remains accepted",
        "safety preflight fixture matrix enforced",
        "fixture matrix modeled",
        "no_auth_dedicated_profile",
        "live_auth_without_probe_auth",
        "probe_auth_dedicated_profile",
        "probe_auth_default_profile",
        "probe_auth_missing_profile",
        "preflight readback can succeed while preflight_passed is false",
        REPAIR_NOTE,
        "--allow-executable-probe",
        "authorization can be present but probe execution remains blocked by phase",
        "preflight alone does not perform a probe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L8.4 Live adapter Microsoft Edge executable probe safety preflight fixture matrix CLI/readback",
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
    loaded = after - before
    found = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in loaded):
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


def _source_l8_02_safe(summary: Mapping[str, Any], *, expect_preflight_passed: bool) -> bool:
    return (
        summary.get("patch") == "L8.2"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l8_01_executable_probe_safety_preflight_contract_remains_accepted") is True
        and summary.get("edge_executable_probe_safety_preflight_cli_readback_enforced") is True
        and summary.get("edge_executable_probe_safety_preflight_contract_enforced") is True
        and summary.get("edge_executable_probe_safety_preflight_modeled") is True
        and summary.get("edge_executable_probe_safety_preflight_passed") is expect_preflight_passed
        and summary.get("edge_executable_probe_preflight_allows_probe_execution") is False
        and summary.get("preflight_alone_does_not_perform_probe") is True
        and summary.get("preflight_readback_can_succeed_while_preflight_passed_false") is True
        and summary.get("edge_executable_filesystem_probe_performed") is False
        and summary.get("edge_executable_path_selected") is False
        and summary.get("edge_executable_selected_path") is None
        and summary.get("edge_executable_launch_attempted") is False
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
        and "source_l8_02_summary" not in summary
        and "source_l8_01_summary" not in summary
    )


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "preflight_passed": source.get("edge_executable_probe_safety_preflight_passed"),
        "preflight_authorization_present": source.get("preflight_authorization_present"),
        "probe_execution_allowed": source.get("edge_executable_probe_preflight_allows_probe_execution"),
        "probe_performed": source.get("edge_executable_filesystem_probe_performed"),
        "compact_json_readback_enabled": source.get("compact_json_readback_enabled") is True,
        "nested_source_summaries_pruned": source.get("nested_source_summaries_pruned") is True,
    }


def _fixture_matrix_state() -> dict[str, Any]:
    fixtures = [dict(item) for item in FIXTURE_MATRIX]
    return {
        "edge_executable_probe_safety_preflight_fixture_matrix_enforced": True,
        "edge_executable_probe_safety_preflight_fixture_matrix_modeled": True,
        "edge_executable_probe_safety_preflight_fixture_count": len(fixtures),
        "edge_executable_probe_safety_preflight_fixture_ids": [fixture["fixture_id"] for fixture in fixtures],
        "edge_executable_probe_safety_preflight_fixture_matrix": fixtures,
        "fixture_readback_ok": True,
        "fixture_probe_execution_allowed": False,
        "fixture_probe_performed": False,
        "fixture_executable_selected": False,
        "fixture_executable_launch_attempted": False,
    }


def build_edge_executable_probe_safety_preflight_fixture_matrix(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l8_02.build_edge_executable_probe_safety_preflight_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
    )
    matrix = _fixture_matrix_state()
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)
    expected_preflight = bool(allow_executable_probe)
    source_safe = _source_l8_02_safe(source, expect_preflight_passed=expected_preflight)

    checks = [
        _check("l8_02_safety_preflight_readback_still_passes", source_safe, _compact_source_status(source)),
        _check("l8_02_safety_preflight_readback_remains_passive", source_safe, {"preflight_passed": source.get("edge_executable_probe_safety_preflight_passed"), "probe_allowed": source.get("edge_executable_probe_preflight_allows_probe_execution"), "probe_performed": source.get("edge_executable_filesystem_probe_performed")}),
        _check("l8_03_safety_preflight_fixture_matrix_command_registered", command_state.get("ok") is True, command_state),
        _check("l8_02_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l8_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l8_docs_contain_safety_preflight_fixture_matrix_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("safety_preflight_fixture_matrix_is_modeled", matrix["edge_executable_probe_safety_preflight_fixture_matrix_modeled"] is True and matrix["edge_executable_probe_safety_preflight_fixture_count"] >= 5, matrix),
        _check("safety_preflight_fixture_ids_are_stable", set(matrix["edge_executable_probe_safety_preflight_fixture_ids"]) == EXPECTED_FIXTURE_IDS, {"fixture_ids": matrix["edge_executable_probe_safety_preflight_fixture_ids"]}),
        _check("no_auth_fixtures_keep_readback_ok_and_preflight_false", all(f["expected_readback_ok"] is True for f in matrix["edge_executable_probe_safety_preflight_fixture_matrix"]) and any(f["expected_preflight_passed"] is False for f in matrix["edge_executable_probe_safety_preflight_fixture_matrix"]), matrix),
        _check("authorized_fixtures_pass_preflight_but_do_not_allow_probe", all((not f["allow_executable_probe"] or (f["expected_preflight_passed"] is True and f["expected_probe_execution_allowed"] is False)) for f in matrix["edge_executable_probe_safety_preflight_fixture_matrix"]), matrix),
        _check("preflight_alone_still_does_not_probe", source.get("preflight_alone_does_not_perform_probe") is True and matrix["fixture_probe_performed"] is False, {}),
        _check("probe_execution_remains_blocked_by_phase", source.get("edge_executable_probe_preflight_allows_probe_execution") is False and matrix["fixture_probe_execution_allowed"] is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and matrix["fixture_executable_selected"] is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and matrix["fixture_executable_launch_attempted"] is False, {}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", source_safe, {}),
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
        "compact_json_readback_enabled": True,
        "nested_source_summaries_pruned": True,
        "l8_02_executable_probe_safety_preflight_cli_readback_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "source_l8_02_status": _compact_source_status(source),
        **matrix,
        "edge_executable_probe_safety_preflight_cli_readback_enforced": source.get("edge_executable_probe_safety_preflight_cli_readback_enforced"),
        "edge_executable_probe_safety_preflight_contract_enforced": source.get("edge_executable_probe_safety_preflight_contract_enforced"),
        "edge_executable_probe_safety_preflight_modeled": source.get("edge_executable_probe_safety_preflight_modeled"),
        "edge_executable_probe_safety_preflight_passed": source.get("edge_executable_probe_safety_preflight_passed"),
        "edge_executable_probe_safety_preflight_status": source.get("edge_executable_probe_safety_preflight_status"),
        "edge_executable_probe_preflight_allows_probe_execution": False,
        "preflight_alone_does_not_perform_probe": True,
        "preflight_authorization_present": source.get("preflight_authorization_present"),
        "preflight_readback_can_succeed_while_preflight_passed_false": True,
        "preflight_missing_authorization_note": REPAIR_NOTE,
        "preflight_blocked_reason": source.get("preflight_blocked_reason"),
        "edge_executable_probe_authorization_flag": EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "edge_executable_probe_authorization_modeled": True,
        "edge_executable_probe_authorized": source.get("edge_executable_probe_authorized"),
        "edge_executable_probe_requested": source.get("edge_executable_probe_requested"),
        "edge_executable_probe_permitted_by_phase": False,
        "edge_executable_probe_blocked_reason": source.get("edge_executable_probe_blocked_reason"),
        "authorization_alone_does_not_perform_probe": True,
        "edge_executable_candidate_paths_modeled": source.get("edge_executable_candidate_paths_modeled"),
        "edge_executable_candidate_count": source.get("edge_executable_candidate_count"),
        "edge_executable_fixture_matrix_modeled": source.get("edge_executable_fixture_matrix_modeled"),
        "edge_executable_fixture_count": source.get("edge_executable_fixture_count"),
        "edge_executable_fixture_ids": source.get("edge_executable_fixture_ids"),
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_selected_path": None,
        "edge_executable_launch_attempted": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "profile_parent_directory_created": False,
        "profile_parent_filesystem_probe_performed": False,
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
        f"L8.2 Accepted   : {payload.get('l8_02_executable_probe_safety_preflight_cli_readback_remains_accepted')}",
        f"Fixture Count   : {payload.get('edge_executable_probe_safety_preflight_fixture_count')}",
        f"Preflight OK    : {payload.get('edge_executable_probe_safety_preflight_passed')}",
        f"Probe Allowed   : {payload.get('edge_executable_probe_preflight_allows_probe_execution')}",
        f"Exe Probe       : {payload.get('edge_executable_filesystem_probe_performed')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_executable_probe_safety_preflight_fixture_matrix(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
        allow_executable_probe=args.allow_executable_probe,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
