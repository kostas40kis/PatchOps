from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_discovery_passive_contract.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_discovery_passive_contract.md")
TEST_PATH = Path("tests/test_l6_01_edge_executable_discovery_passive_contract_current.py")
VALIDATE_PATH = Path("scripts/patch_l6_01_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L6.1 passive Microsoft Edge executable-discovery contract.

This is the first L6 slice after the accepted L5 profile-parent preflight final
marker. It defines the future Edge executable discovery contract without probing
the filesystem and without starting a browser.

No Selenium import, browser start, Edge process, driver/session creation,
profile directory creation, executable filesystem probe, click/download,
paste/send, package-run, commit, or push is performed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker as l5_33

PATCH = "L6.1"
PHASE = "L6"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L6.1 Microsoft Edge Executable Discovery Passive Contract"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-discovery-contract"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-final-acceptance-marker"
NEXT_PATCH = "L6.2 Live adapter Microsoft Edge executable discovery CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-discovery-passive-contract-only"
AUTHORIZATION_FLAG = "--allow-live-start"
PROFILE_DIR_ARGUMENT = "--profile-dir"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

EDGE_EXECUTABLE_CANDIDATES = (
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_passive_contract.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker.md",
    "docs/llm_browser_live_adapter_edge_executable_discovery_passive_contract.md",
    "tests/test_l5_33_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker_current.py",
    "tests/test_l6_01_edge_executable_discovery_passive_contract_current.py",
    "scripts/patch_l5_33_brief_validate.py",
    "scripts/patch_l6_01_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker.md": (
        "L5.33 Microsoft Edge supervised launch profile parent preflight final acceptance marker",
        SOURCE_COMMAND_NAME,
        "profile parent preflight slice accepted",
        "L6.1 Live adapter Microsoft Edge executable discovery passive contract",
    ),
    "docs/llm_browser_live_adapter_edge_executable_discovery_passive_contract.md": (
        "L6.1 Microsoft Edge executable discovery passive contract",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "Microsoft Edge first",
        "Opera second",
        "brief validation output",
        "L5.33 profile parent preflight final marker remains accepted",
        "Edge executable candidate paths modeled",
        "msedge.exe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L6.2 Live adapter Microsoft Edge executable discovery CLI/readback",
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


def _source_l5_33_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L5.33"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("profile_parent_preflight_slice_accepted") is True
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


def _executable_discovery_state() -> dict[str, Any]:
    candidates = list(EDGE_EXECUTABLE_CANDIDATES)
    return {
        "edge_executable_discovery_contract_enforced": True,
        "edge_executable_candidate_paths_modeled": True,
        "edge_executable_candidates": candidates,
        "edge_executable_candidate_count": len(candidates),
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_selected_path": None,
        "edge_executable_launch_attempted": False,
        "edge_process_started": False,
        "phase_allows_executable_probe": False,
        "phase_allows_live_start": False,
    }


def build_edge_executable_discovery_passive_contract(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l5_33.build_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
    )
    discovery = _executable_discovery_state()
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l5_33_profile_parent_preflight_final_marker_still_passes", _source_l5_33_safe(source), {"patch": source.get("patch"), "ok": source.get("ok"), "status": source.get("status")}),
        _check("l5_33_profile_parent_preflight_final_marker_remains_passive", _source_l5_33_safe(source), {"browser_started": source.get("browser_started"), "profile_directory_created": source.get("profile_directory_created")}),
        _check("l6_01_executable_discovery_command_registered", command_state.get("ok") is True, command_state),
        _check("l5_33_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l6_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l6_docs_contain_executable_discovery_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("edge_executable_candidate_paths_are_modeled", discovery["edge_executable_candidate_paths_modeled"] and discovery["edge_executable_candidate_count"] >= 3, discovery),
        _check("edge_executable_filesystem_probe_stays_false", discovery["edge_executable_filesystem_probe_performed"] is False, discovery),
        _check("edge_executable_path_not_selected_in_l6_01", discovery["edge_executable_path_selected"] is False and discovery["edge_executable_selected_path"] is None, discovery),
        _check("edge_executable_launch_not_attempted", discovery["edge_executable_launch_attempted"] is False and discovery["edge_process_started"] is False, discovery),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", _source_l5_33_safe(source), {}),
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
        "l5_33_profile_parent_preflight_final_marker_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "profile_parent_preflight_slice_accepted": source.get("profile_parent_preflight_slice_accepted") is True,
        "source_l5_33_summary": source,
        **discovery,
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
        f"L5.33 Accepted  : {payload.get('l5_33_profile_parent_preflight_final_marker_remains_accepted')}",
        f"Candidate Count : {payload.get('edge_executable_candidate_count')}",
        f"Exe Probe       : {payload.get('edge_executable_filesystem_probe_performed')}",
        f"Exe Selected    : {payload.get('edge_executable_path_selected')}",
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
    payload = build_edge_executable_discovery_passive_contract(
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
'''

DOC_CONTENT = r'''# L6.1 Microsoft Edge executable discovery passive contract

L6.1 starts the Microsoft Edge executable-discovery slice after the accepted L5 profile-parent preflight final marker.

Command:

`browser-start-supervised-launch-edge-executable-discovery-contract`

Source command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-final-acceptance-marker`

This patch preserves brief validation output: validation captures large JSON internally and prints only short PASS summaries.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- L5.33 profile parent preflight final marker remains accepted.
- Edge executable candidate paths modeled.
- `msedge.exe` candidates are listed for future discovery logic.
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

`L6.2 Live adapter Microsoft Edge executable discovery CLI/readback`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_discovery_passive_contract as contract

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-discovery-contract"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-final-acceptance-marker"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_01_candidate"
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


def test_l6_01_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l6_01_edge_executable_contract_dedicated_profile_passes_passively() -> None:
    payload = contract.build_edge_executable_discovery_passive_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L6.1"
    assert payload["phase"] == "L6"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l5_33_profile_parent_preflight_final_marker_remains_accepted"] is True
    assert payload["profile_parent_preflight_slice_accepted"] is True
    assert payload["edge_executable_discovery_contract_enforced"] is True
    assert payload["edge_executable_candidate_paths_modeled"] is True
    assert payload["edge_executable_candidate_count"] >= 3
    assert all("msedge.exe" in candidate.lower() for candidate in payload["edge_executable_candidates"])
    assert payload["next_patch"] == "L6.2 Live adapter Microsoft Edge executable discovery CLI/readback"
    _assert_passive(payload)


def test_l6_01_default_and_missing_profile_cases_are_passive() -> None:
    default_payload = contract.build_edge_executable_discovery_passive_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_payload = contract.build_edge_executable_discovery_passive_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )
    assert default_payload["ok"] is True
    assert default_payload["source_l5_33_summary"]["source_l5_32_summary"]["source_l5_31_summary"]["source_l5_30_summary"]["default_profile_candidate_detected"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l5_33_summary"]["source_l5_32_summary"]["source_l5_31_summary"]["source_l5_30_summary"]["profile_parent_path_derived"] is False
    _assert_passive(missing_payload)


def test_l6_01_patchops_cli_json_readback_is_parseable_and_passive() -> None:
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
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L6.1"
    _assert_passive(payload)


def test_l6_01_doc_mentions_executable_discovery_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_discovery_passive_contract.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L6.1 Microsoft Edge executable discovery passive contract",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "L5.33 profile parent preflight final marker remains accepted",
        "Edge executable candidate paths modeled",
        "msedge.exe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L6.2 Live adapter Microsoft Edge executable discovery CLI/readback",
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

from patchops.llm_browser import live_adapter_edge_executable_discovery_passive_contract as contract

COMMAND = "browser-start-supervised-launch-edge-executable-discovery-contract"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_01_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l5_33_profile_parent_preflight_final_marker_remains_accepted"] is True
    assert payload["edge_executable_candidate_paths_modeled"] is True
    assert payload["edge_executable_candidate_count"] >= 3
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


def main() -> int:
    cases = [
        ("no_auth_dedicated", False, DEDICATED),
        ("auth_dedicated", True, DEDICATED),
        ("auth_default", True, DEFAULT),
        ("missing_profile", True, None),
    ]
    for name, allow, profile in cases:
        payload = contract.build_edge_executable_discovery_passive_contract(
            ROOT,
            allow_live_start=allow,
            profile_dir=profile,
        )
        assert_passive(payload)
        print(
            "PASS {0}: patch={1} candidates={2} exe_probe={3}".format(
                name,
                payload["patch"],
                payload["edge_executable_candidate_count"],
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
            "--json",
            "--compact",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    payload = json.loads(completed.stdout)
    assert_passive(payload)
    print("PASS main_cli: compact JSON parsed; full JSON intentionally not echoed")
    print("PASS L6.1 brief validation: executable discovery modeled with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L6.1 START
# Passive Microsoft Edge executable discovery contract.
import sys as _patchops_l6_01_sys

_PATCHOPS_L6_01_COMMAND = "browser-start-supervised-launch-edge-executable-discovery-contract"

try:
    _PATCHOPS_L6_01_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L6_01_PREV_BUILD_PARSER = None

if _PATCHOPS_L6_01_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L6_01_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L6_01_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L6_01_COMMAND, help="Read back passive Edge executable discovery contract.")
                        p.add_argument("--repo-root", default=None)
                        p.add_argument("--allow-live-start", action="store_true")
                        p.add_argument("--profile-dir", default=None)
                        p.add_argument("--json", action="store_true")
                        p.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_executable_discovery_contract(args) -> int:
    from . import live_adapter_edge_executable_discovery_passive_contract
    module_args = []
    repo_root = getattr(args, "repo_root", None)
    if repo_root:
        module_args.extend(["--repo-root", str(repo_root)])
    if getattr(args, "allow_live_start", False):
        module_args.append("--allow-live-start")
    profile_dir = getattr(args, "profile_dir", None)
    if profile_dir:
        module_args.extend(["--profile-dir", str(profile_dir)])
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_executable_discovery_passive_contract.main(module_args)

try:
    _PATCHOPS_L6_01_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L6_01_PREV_COMMAND_NAMES = None

if _PATCHOPS_L6_01_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L6_01_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L6_01_COMMAND,) if name not in names)

_PATCHOPS_L6_01_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l6_01_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L6_01_COMMAND:
        from . import live_adapter_edge_executable_discovery_passive_contract
        return live_adapter_edge_executable_discovery_passive_contract.main(arg_list[1:])
    return _PATCHOPS_L6_01_PREV_MAIN(argv)
# PATCHOPS L6.1 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L6.1 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L6.1 command wrapper appended")
    else:
        print("L6.1 command wrapper already present")


def _append_l5_33_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L6.1 Live adapter Microsoft Edge executable discovery passive contract"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the profile-parent preflight slice:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L5.33 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l5_33_doc_pointer()
    print("L6.1 files written; validation is intentionally brief")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())