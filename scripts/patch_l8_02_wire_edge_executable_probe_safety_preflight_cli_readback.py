from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_probe_safety_preflight_cli_readback.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_cli_readback.md")
TEST_PATH = Path("tests/test_l8_02_edge_executable_probe_safety_preflight_cli_readback_current.py")
VALIDATE_PATH = Path("scripts/patch_l8_02_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L8.2 passive Microsoft Edge executable-probe safety-preflight CLI/readback.

L8.2 wraps the accepted L8.1 safety-preflight passive contract in a compact
CLI/readback layer. A missing `--allow-executable-probe` remains a successful
passive readback with preflight_passed=false. An authorized preflight can pass,
but probe execution is still blocked by phase.

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

from patchops.llm_browser import live_adapter_edge_executable_probe_safety_preflight_passive_contract as l8_01

PATCH = "L8.2"
PHASE = "L8"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L8.2 Microsoft Edge Executable Probe Safety Preflight CLI Readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-readback"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-contract"
NEXT_PATCH = "L8.3 Live adapter Microsoft Edge executable probe safety preflight fixture matrix"
SIDE_EFFECT_BOUNDARY = "edge-executable-probe-safety-preflight-cli-readback-only"
EXECUTABLE_PROBE_AUTHORIZATION_FLAG = "--allow-executable-probe"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")
REPAIR_NOTE = "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok."

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_probe_safety_preflight_passive_contract.py",
    "patchops/llm_browser/live_adapter_edge_executable_probe_safety_preflight_cli_readback.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_passive_contract.md",
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_cli_readback.md",
    "tests/test_l8_01_edge_executable_probe_safety_preflight_passive_contract_current.py",
    "tests/test_l8_02_edge_executable_probe_safety_preflight_cli_readback_current.py",
    "scripts/patch_l8_01_brief_validate.py",
    "scripts/patch_l8_02_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_passive_contract.md": (
        "L8.1 Microsoft Edge executable probe safety preflight passive contract",
        SOURCE_COMMAND_NAME,
        "safety preflight contract enforced",
        "preflight alone does not perform a probe",
        REPAIR_NOTE,
        "L8.2 Live adapter Microsoft Edge executable probe safety preflight CLI/readback",
    ),
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_cli_readback.md": (
        "L8.2 Microsoft Edge executable probe safety preflight CLI/readback",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L8.1 executable probe safety preflight passive contract remains accepted",
        "safety preflight CLI/readback enforced",
        "safety preflight modeled only",
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
        "L8.3 Live adapter Microsoft Edge executable probe safety preflight fixture matrix",
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


def _source_l8_01_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L8.1"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l7_08_executable_probe_authorization_final_marker_remains_accepted") is True
        and summary.get("l7_executable_probe_authorization_slice_accepted") is True
        and summary.get("edge_executable_probe_safety_preflight_contract_enforced") is True
        and summary.get("edge_executable_probe_safety_preflight_modeled") is True
        and summary.get("edge_executable_probe_safety_preflight_passed") is True
        and summary.get("edge_executable_probe_preflight_allows_probe_execution") is False
        and summary.get("preflight_alone_does_not_perform_probe") is True
        and summary.get("preflight_authorization_present") is True
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
        and "source_l8_01_summary" not in summary
        and "source_l7_08_summary" not in summary
    )


def _source_l8_01_no_auth_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L8.1"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("edge_executable_probe_safety_preflight_contract_enforced") is True
        and summary.get("edge_executable_probe_safety_preflight_modeled") is True
        and summary.get("edge_executable_probe_safety_preflight_passed") is False
        and summary.get("edge_executable_probe_preflight_allows_probe_execution") is False
        and summary.get("preflight_alone_does_not_perform_probe") is True
        and summary.get("preflight_authorization_present") is False
        and summary.get("edge_executable_filesystem_probe_performed") is False
        and summary.get("browser_started") is False
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
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


def build_edge_executable_probe_safety_preflight_cli_readback(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l8_01.build_edge_executable_probe_safety_preflight_passive_contract(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
    )
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)
    source_contract_safe = _source_l8_01_safe(source) if allow_executable_probe else _source_l8_01_no_auth_safe(source)

    checks = [
        _check("l8_01_safety_preflight_contract_still_passes", source_contract_safe, _compact_source_status(source)),
        _check("l8_01_safety_preflight_contract_remains_passive", source_contract_safe, {"preflight_passed": source.get("edge_executable_probe_safety_preflight_passed"), "probe_allowed": source.get("edge_executable_probe_preflight_allows_probe_execution"), "probe_performed": source.get("edge_executable_filesystem_probe_performed")}),
        _check("l8_02_safety_preflight_readback_command_registered", command_state.get("ok") is True, command_state),
        _check("l8_01_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l8_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l8_docs_contain_safety_preflight_readback_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("safety_preflight_readback_is_enforced", source.get("edge_executable_probe_safety_preflight_contract_enforced") is True, {}),
        _check("no_auth_readback_remains_ok_but_preflight_false", True if allow_executable_probe else _source_l8_01_no_auth_safe(source), _compact_source_status(source)),
        _check("preflight_alone_still_does_not_probe", source.get("preflight_alone_does_not_perform_probe") is True and source.get("edge_executable_filesystem_probe_performed") is False, {}),
        _check("probe_execution_remains_blocked_by_phase", source.get("edge_executable_probe_preflight_allows_probe_execution") is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False, {}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", source_contract_safe, {}),
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
        "l8_01_executable_probe_safety_preflight_contract_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "source_l8_01_status": _compact_source_status(source),
        "edge_executable_probe_safety_preflight_cli_readback_enforced": True,
        "edge_executable_probe_safety_preflight_contract_enforced": source.get("edge_executable_probe_safety_preflight_contract_enforced"),
        "edge_executable_probe_safety_preflight_modeled": source.get("edge_executable_probe_safety_preflight_modeled"),
        "edge_executable_probe_safety_preflight_passed": source.get("edge_executable_probe_safety_preflight_passed"),
        "edge_executable_probe_safety_preflight_status": source.get("edge_executable_probe_safety_preflight_status"),
        "edge_executable_probe_safety_preflight_checks": source.get("edge_executable_probe_safety_preflight_checks"),
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
        "fixture_probe_performed": False,
        "fixture_executable_selected": False,
        "fixture_executable_launch_attempted": False,
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
        f"L8.1 Accepted   : {payload.get('l8_01_executable_probe_safety_preflight_contract_remains_accepted')}",
        f"Preflight OK    : {payload.get('edge_executable_probe_safety_preflight_passed')}",
        f"Probe Auth      : {payload.get('edge_executable_probe_authorized')}",
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
    payload = build_edge_executable_probe_safety_preflight_cli_readback(
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
'''

DOC_CONTENT = r'''# L8.2 Microsoft Edge executable probe safety preflight CLI/readback

L8.2 adds a passive CLI/readback layer for the accepted L8.1 Microsoft Edge executable-probe safety preflight contract.

Command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-readback`

Source command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-contract`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L8.1 executable probe safety preflight passive contract remains accepted.
- safety preflight CLI/readback enforced.
- safety preflight modeled only.
- preflight readback can succeed while preflight_passed is false.
- Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.
- `--allow-executable-probe` remains the explicit future authorization flag.
- authorization can be present but probe execution remains blocked by phase.
- preflight alone does not perform a probe.
- executable filesystem probe not performed.
- executable path not selected.
- executable launch not attempted.
- no Selenium import.
- no browser start.
- no Edge process start.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L8.3 Live adapter Microsoft Edge executable probe safety preflight fixture matrix`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_probe_safety_preflight_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-contract"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l8_02_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def _assert_passive(payload: dict) -> None:
    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    assert payload["preflight_alone_does_not_perform_probe"] is True
    assert payload["authorization_alone_does_not_perform_probe"] is True
    assert payload["fixture_probe_performed"] is False
    assert payload["fixture_executable_selected"] is False
    assert payload["fixture_executable_launch_attempted"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert "source_l8_02_summary" not in payload
    assert "source_l8_01_summary" not in payload


def test_l8_02_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l8_02_no_auth_readback_ok_preflight_false_and_passive() -> None:
    payload = readback.build_edge_executable_probe_safety_preflight_cli_readback(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=False,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L8.2"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l8_01_executable_probe_safety_preflight_contract_remains_accepted"] is True
    assert payload["edge_executable_probe_safety_preflight_cli_readback_enforced"] is True
    assert payload["edge_executable_probe_safety_preflight_passed"] is False
    assert payload["preflight_authorization_present"] is False
    assert payload["preflight_readback_can_succeed_while_preflight_passed_false"] is True
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    _assert_passive(payload)


def test_l8_02_authorized_preflight_passes_but_probe_execution_stays_blocked() -> None:
    payload = readback.build_edge_executable_probe_safety_preflight_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L8"
    assert payload["edge_executable_probe_safety_preflight_passed"] is True
    assert payload["preflight_authorization_present"] is True
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    assert payload["next_patch"] == "L8.3 Live adapter Microsoft Edge executable probe safety preflight fixture matrix"
    _assert_passive(payload)


def test_l8_02_default_and_missing_profile_cases_are_passive_when_authorized() -> None:
    default_payload = readback.build_edge_executable_probe_safety_preflight_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True)
    missing_payload = readback.build_edge_executable_probe_safety_preflight_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l8_01_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l8_01_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l8_02_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-live-start",
            "--profile-dir",
            str(DEDICATED_PROFILE),
            "--allow-executable-probe",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 80000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L8.2"
    assert payload["edge_executable_probe_safety_preflight_passed"] is True
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    _assert_passive(payload)


def test_l8_02_doc_mentions_safety_preflight_readback_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_probe_safety_preflight_cli_readback.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L8.2 Microsoft Edge executable probe safety preflight CLI/readback",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L8.1 executable probe safety preflight passive contract remains accepted",
        "safety preflight CLI/readback enforced",
        "safety preflight modeled only",
        "preflight readback can succeed while preflight_passed is false",
        "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.",
        "--allow-executable-probe",
        "authorization can be present but probe execution remains blocked by phase",
        "preflight alone does not perform a probe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L8.3 Live adapter Microsoft Edge executable probe safety preflight fixture matrix",
    ]:
        assert phrase in text
'''

VALIDATE_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_probe_safety_preflight_cli_readback as readback

COMMAND = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-readback"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l8_02_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l8_01_executable_probe_safety_preflight_contract_remains_accepted"] is True
    assert payload["edge_executable_probe_safety_preflight_cli_readback_enforced"] is True
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    assert payload["preflight_alone_does_not_perform_probe"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []
    assert "source_l8_01_summary" not in payload


def main() -> int:
    no_auth = readback.build_edge_executable_probe_safety_preflight_cli_readback(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False)
    assert_passive(no_auth)
    assert no_auth["edge_executable_probe_safety_preflight_passed"] is False
    print("PASS no_probe_auth: patch=L8.2 readback_ok=True preflight_passed=False probe_execution_allowed=False exe_probe=False")

    cases = [
        ("probe_auth_dedicated", True, DEDICATED, True),
        ("probe_auth_default", True, DEFAULT, True),
        ("probe_auth_missing_profile", True, None, True),
    ]
    for name, live, profile, probe_auth in cases:
        payload = readback.build_edge_executable_probe_safety_preflight_cli_readback(
            ROOT,
            allow_live_start=live,
            profile_dir=profile,
            allow_executable_probe=probe_auth,
        )
        assert_passive(payload)
        assert payload["edge_executable_probe_safety_preflight_passed"] is True
        print(
            "PASS {0}: patch={1} source=L8.1 preflight_passed={2} probe_execution_allowed={3} exe_probe={4}".format(
                name,
                payload["patch"],
                payload["edge_executable_probe_safety_preflight_passed"],
                payload["edge_executable_probe_preflight_allows_probe_execution"],
                payload["edge_executable_filesystem_probe_performed"],
            )
        )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(ROOT),
            "--allow-live-start",
            "--profile-dir",
            str(DEDICATED),
            "--allow-executable-probe",
            "--json",
            "--compact",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    payload = json.loads(completed.stdout)
    assert len(completed.stdout) < 80000
    assert_passive(payload)
    print("PASS main_cli: compact JSON parsed quickly; safety preflight CLI/readback stayed passive")
    print("PASS L8.2 brief validation: safety preflight CLI/readback accepted with no executable probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L8.2 START
# Passive Microsoft Edge executable probe safety preflight CLI/readback.
import sys as _patchops_l8_02_sys

_PATCHOPS_L8_02_COMMAND = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-readback"

try:
    _PATCHOPS_L8_02_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L8_02_PREV_BUILD_PARSER = None

if _PATCHOPS_L8_02_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L8_02_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L8_02_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L8_02_COMMAND, help="Read back passive Edge executable probe safety preflight state.")
                        p.add_argument("--repo-root", default=None)
                        p.add_argument("--allow-live-start", action="store_true")
                        p.add_argument("--profile-dir", default=None)
                        p.add_argument("--allow-executable-probe", action="store_true")
                        p.add_argument("--json", action="store_true")
                        p.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_executable_probe_safety_preflight_readback(args) -> int:
    from . import live_adapter_edge_executable_probe_safety_preflight_cli_readback
    module_args = []
    repo_root = getattr(args, "repo_root", None)
    if repo_root:
        module_args.extend(["--repo-root", str(repo_root)])
    if getattr(args, "allow_live_start", False):
        module_args.append("--allow-live-start")
    profile_dir = getattr(args, "profile_dir", None)
    if profile_dir:
        module_args.extend(["--profile-dir", str(profile_dir)])
    if getattr(args, "allow_executable_probe", False):
        module_args.append("--allow-executable-probe")
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_executable_probe_safety_preflight_cli_readback.main(module_args)

try:
    _PATCHOPS_L8_02_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L8_02_PREV_COMMAND_NAMES = None

if _PATCHOPS_L8_02_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L8_02_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L8_02_COMMAND,) if name not in names)

_PATCHOPS_L8_02_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l8_02_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L8_02_COMMAND:
        from . import live_adapter_edge_executable_probe_safety_preflight_cli_readback
        return live_adapter_edge_executable_probe_safety_preflight_cli_readback.main(arg_list[1:])
    return _PATCHOPS_L8_02_PREV_MAIN(argv)
# PATCHOPS L8.2 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L8.2 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L8.2 command wrapper appended")
    else:
        print("L8.2 command wrapper already present")


def _append_l8_01_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_passive_contract.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L8.2 Live adapter Microsoft Edge executable probe safety preflight CLI/readback"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the executable probe safety preflight contract:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L8.1 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l8_01_doc_pointer()
    print("L8.2 files written; validation is intentionally brief and compact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())