from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_discovery_aggregate_gate.py")
TEST_PATH = Path("tests/test_l6_05_edge_executable_discovery_aggregate_gate_current.py")
VALIDATE_PATH = Path("scripts/patch_l6_05_brief_validate.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_discovery_aggregate_gate.md")

MODULE_CONTENT = r'''"""L6.5 passive Microsoft Edge executable-discovery aggregate gate.

L6.5a repair note: the original L6.5 module returned full nested source
summaries from the entire L5/L6 chain. The direct checks passed, but the main
CLI `--json --compact` readback timed out while serializing/capturing that huge
payload. This repaired module keeps the same passive aggregate gate but returns
compact source-chain summaries suitable for CLI JSON readback.

No filesystem probe, executable selection, Selenium import, browser start, Edge
process, driver/session creation, profile creation, click/download, paste/send,
package-run, commit, or push is performed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_discovery_fixture_matrix_cli_readback as l6_04

PATCH = "L6.5"
PHASE = "L6"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L6.5 Microsoft Edge Executable Discovery Aggregate Gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-discovery-aggregate-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-discovery-fixture-matrix-readback"
NEXT_PATCH = "L6.6 Live adapter Microsoft Edge executable discovery aggregate gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-discovery-aggregate-gate-only"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_discovery_passive_contract.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_aggregate_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_discovery_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_discovery_aggregate_gate.md",
    "tests/test_l6_04_edge_executable_discovery_fixture_matrix_cli_readback_current.py",
    "tests/test_l6_05_edge_executable_discovery_aggregate_gate_current.py",
    "scripts/patch_l6_04_brief_validate.py",
    "scripts/patch_l6_05_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_discovery_fixture_matrix_cli_readback.md": (
        "L6.4 Microsoft Edge executable discovery fixture matrix CLI/readback",
        SOURCE_COMMAND_NAME,
        "fixture matrix CLI/readback enforced",
        "executable filesystem probe not performed",
        "L6.5 Live adapter Microsoft Edge executable discovery aggregate gate",
    ),
    "docs/llm_browser_live_adapter_edge_executable_discovery_aggregate_gate.md": (
        "L6.5 Microsoft Edge executable discovery aggregate gate",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L6.1 executable discovery passive contract remains accepted",
        "L6.2 executable discovery CLI/readback remains accepted",
        "L6.3 executable discovery fixture matrix remains accepted",
        "L6.4 executable discovery fixture matrix CLI/readback remains accepted",
        "executable discovery aggregate gate enforced",
        "Edge executable candidate paths remain modeled",
        "fixture matrix remains modeled",
        "msedge.exe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L6.6 Live adapter Microsoft Edge executable discovery aggregate gate CLI/readback",
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


def _source_l6_04_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L6.4"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l6_03_executable_discovery_fixture_matrix_remains_accepted") is True
        and summary.get("edge_executable_fixture_matrix_cli_readback_enforced") is True
        and summary.get("edge_executable_fixture_matrix_modeled") is True
        and summary.get("edge_executable_fixture_count", 0) >= 4
        and summary.get("edge_executable_candidate_paths_modeled") is True
        and summary.get("edge_executable_candidate_count", 0) >= 3
        and summary.get("edge_executable_filesystem_probe_performed") is False
        and summary.get("edge_executable_path_selected") is False
        and summary.get("edge_executable_selected_path") is None
        and summary.get("edge_executable_launch_attempted") is False
        and summary.get("edge_executable_fixture_filesystem_probe_performed") is False
        and summary.get("edge_executable_fixture_path_selected") is False
        and summary.get("edge_executable_fixture_launch_attempted") is False
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


def _source_status(summary: Mapping[str, Any], patch: str) -> dict[str, Any]:
    return {
        "patch": patch,
        "ok": summary.get("ok") is True,
        "status": summary.get("status"),
        "command_name": summary.get("command_name"),
    }


def _extract_chain_status(source: Mapping[str, Any]) -> dict[str, Any]:
    l6_03 = source.get("source_l6_03_summary", {}) if isinstance(source.get("source_l6_03_summary"), Mapping) else {}
    l6_02 = source.get("source_l6_02_summary", {}) if isinstance(source.get("source_l6_02_summary"), Mapping) else {}
    l6_01 = source.get("source_l6_01_summary", {}) if isinstance(source.get("source_l6_01_summary"), Mapping) else {}
    return {
        "l6_04": _source_status(source, "L6.4"),
        "l6_03": _source_status(l6_03, "L6.3"),
        "l6_02": _source_status(l6_02, "L6.2"),
        "l6_01": _source_status(l6_01, "L6.1"),
    }


def _aggregate_state(source: Mapping[str, Any]) -> dict[str, Any]:
    chain = _extract_chain_status(source)
    return {
        "edge_executable_discovery_aggregate_gate_enforced": True,
        "edge_executable_discovery_aggregate_status": "BLOCKED_EXECUTABLE_DISCOVERY_AGGREGATE_MODEL_ONLY",
        "edge_executable_discovery_aggregate_reason": "L6.5 aggregates L6.1-L6.4 but still performs no executable probe, selection, or browser start.",
        "l6_01_executable_discovery_passive_contract_ok": chain["l6_01"]["ok"] and chain["l6_01"]["status"] == STATUS_PASS,
        "l6_02_executable_discovery_cli_readback_ok": chain["l6_02"]["ok"] and chain["l6_02"]["status"] == STATUS_PASS,
        "l6_03_executable_discovery_fixture_matrix_ok": chain["l6_03"]["ok"] and chain["l6_03"]["status"] == STATUS_PASS,
        "l6_04_executable_discovery_fixture_matrix_cli_readback_ok": chain["l6_04"]["ok"] and chain["l6_04"]["status"] == STATUS_PASS,
        "edge_executable_candidate_paths_modeled": source.get("edge_executable_candidate_paths_modeled") is True,
        "edge_executable_fixture_matrix_modeled": source.get("edge_executable_fixture_matrix_modeled") is True,
        "edge_executable_candidate_count": source.get("edge_executable_candidate_count"),
        "edge_executable_fixture_count": source.get("edge_executable_fixture_count"),
        "edge_executable_fixture_ids": source.get("edge_executable_fixture_ids"),
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_launch_attempted": False,
        "startup_allowed": False,
        "live_start_performed": False,
        "chain_status": chain,
    }


def build_edge_executable_discovery_aggregate_gate(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l6_04.build_edge_executable_discovery_fixture_matrix_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
    )
    aggregate = _aggregate_state(source)
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    chain_ok = all(
        [
            aggregate["l6_01_executable_discovery_passive_contract_ok"],
            aggregate["l6_02_executable_discovery_cli_readback_ok"],
            aggregate["l6_03_executable_discovery_fixture_matrix_ok"],
            aggregate["l6_04_executable_discovery_fixture_matrix_cli_readback_ok"],
        ]
    )

    checks = [
        _check("l6_04_executable_discovery_fixture_matrix_readback_still_passes", _source_l6_04_safe(source), _source_status(source, "L6.4")),
        _check("l6_04_executable_discovery_fixture_matrix_readback_remains_passive", _source_l6_04_safe(source), {"exe_probe": source.get("edge_executable_filesystem_probe_performed"), "browser_started": source.get("browser_started")}),
        _check("l6_01_through_l6_04_chain_remains_accepted", chain_ok, aggregate["chain_status"]),
        _check("l6_05_aggregate_gate_command_registered", command_state.get("ok") is True, command_state),
        _check("l6_04_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l6_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l6_docs_contain_aggregate_gate_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("executable_discovery_aggregate_gate_is_enforced", aggregate["edge_executable_discovery_aggregate_gate_enforced"] is True, aggregate),
        _check("executable_candidates_and_fixtures_remain_modeled", aggregate["edge_executable_candidate_paths_modeled"] is True and aggregate["edge_executable_fixture_matrix_modeled"] is True, aggregate),
        _check("edge_executable_filesystem_probe_stays_false", source.get("edge_executable_filesystem_probe_performed") is False and aggregate["edge_executable_filesystem_probe_performed"] is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and aggregate["edge_executable_path_selected"] is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and aggregate["edge_executable_launch_attempted"] is False, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", _source_l6_04_safe(source), {}),
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
        "l6_01_executable_discovery_passive_contract_remains_accepted": aggregate["l6_01_executable_discovery_passive_contract_ok"],
        "l6_02_executable_discovery_cli_readback_remains_accepted": aggregate["l6_02_executable_discovery_cli_readback_ok"],
        "l6_03_executable_discovery_fixture_matrix_remains_accepted": aggregate["l6_03_executable_discovery_fixture_matrix_ok"],
        "l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted": aggregate["l6_04_executable_discovery_fixture_matrix_cli_readback_ok"],
        "source_chain_status": aggregate["chain_status"],
        "edge_executable_discovery_aggregate": aggregate,
        "edge_executable_discovery_aggregate_gate_enforced": aggregate["edge_executable_discovery_aggregate_gate_enforced"],
        "edge_executable_discovery_aggregate_status": aggregate["edge_executable_discovery_aggregate_status"],
        "edge_executable_candidate_paths_modeled": source.get("edge_executable_candidate_paths_modeled"),
        "edge_executable_candidate_count": source.get("edge_executable_candidate_count"),
        "edge_executable_fixture_matrix_modeled": source.get("edge_executable_fixture_matrix_modeled"),
        "edge_executable_fixture_count": source.get("edge_executable_fixture_count"),
        "edge_executable_fixture_ids": source.get("edge_executable_fixture_ids"),
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_selected_path": None,
        "edge_executable_launch_attempted": False,
        "edge_executable_fixture_filesystem_probe_performed": False,
        "edge_executable_fixture_path_selected": False,
        "edge_executable_fixture_launch_attempted": False,
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
        f"Compact JSON    : {payload.get('compact_json_readback_enabled')}",
        f"L6.1 Accepted   : {payload.get('l6_01_executable_discovery_passive_contract_remains_accepted')}",
        f"L6.2 Accepted   : {payload.get('l6_02_executable_discovery_cli_readback_remains_accepted')}",
        f"L6.3 Accepted   : {payload.get('l6_03_executable_discovery_fixture_matrix_remains_accepted')}",
        f"L6.4 Accepted   : {payload.get('l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted')}",
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
    payload = build_edge_executable_discovery_aggregate_gate(
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

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_discovery_aggregate_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-discovery-aggregate-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-discovery-fixture-matrix-readback"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_05_candidate"
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
    assert payload["edge_executable_fixture_filesystem_probe_performed"] is False
    assert payload["edge_executable_fixture_path_selected"] is False
    assert payload["edge_executable_fixture_launch_attempted"] is False
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


def test_l6_05_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l6_05_aggregate_gate_dedicated_profile_passes_passively_with_compact_chain() -> None:
    payload = gate.build_edge_executable_discovery_aggregate_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L6.5"
    assert payload["phase"] == "L6"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["compact_json_readback_enabled"] is True
    assert payload["nested_source_summaries_pruned"] is True
    assert payload["l6_01_executable_discovery_passive_contract_remains_accepted"] is True
    assert payload["l6_02_executable_discovery_cli_readback_remains_accepted"] is True
    assert payload["l6_03_executable_discovery_fixture_matrix_remains_accepted"] is True
    assert payload["l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_discovery_aggregate_gate_enforced"] is True
    assert payload["edge_executable_candidate_paths_modeled"] is True
    assert payload["edge_executable_fixture_matrix_modeled"] is True
    assert payload["next_patch"] == "L6.6 Live adapter Microsoft Edge executable discovery aggregate gate CLI/readback"
    assert "source_l6_04_summary" not in payload
    assert "source_chain_status" in payload
    _assert_passive(payload)


def test_l6_05_default_and_missing_profile_cases_are_passive() -> None:
    default_payload = gate.build_edge_executable_discovery_aggregate_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_payload = gate.build_edge_executable_discovery_aggregate_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )
    assert default_payload["ok"] is True
    assert default_payload["source_chain_status"]["l6_04"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_chain_status"]["l6_04"]["ok"] is True
    _assert_passive(missing_payload)


def test_l6_05_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 80000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L6.5"
    assert payload["compact_json_readback_enabled"] is True
    assert payload["nested_source_summaries_pruned"] is True
    assert "source_l6_04_summary" not in payload
    _assert_passive(payload)


def test_l6_05_doc_mentions_aggregate_gate_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_discovery_aggregate_gate.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L6.5 Microsoft Edge executable discovery aggregate gate",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L6.1 executable discovery passive contract remains accepted",
        "L6.2 executable discovery CLI/readback remains accepted",
        "L6.3 executable discovery fixture matrix remains accepted",
        "L6.4 executable discovery fixture matrix CLI/readback remains accepted",
        "executable discovery aggregate gate enforced",
        "Edge executable candidate paths remain modeled",
        "fixture matrix remains modeled",
        "msedge.exe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L6.6 Live adapter Microsoft Edge executable discovery aggregate gate CLI/readback",
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

from patchops.llm_browser import live_adapter_edge_executable_discovery_aggregate_gate as gate

COMMAND = "browser-start-supervised-launch-edge-executable-discovery-aggregate-gate"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_05_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["compact_json_readback_enabled"] is True
    assert payload["nested_source_summaries_pruned"] is True
    assert payload["l6_01_executable_discovery_passive_contract_remains_accepted"] is True
    assert payload["l6_02_executable_discovery_cli_readback_remains_accepted"] is True
    assert payload["l6_03_executable_discovery_fixture_matrix_remains_accepted"] is True
    assert payload["l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_discovery_aggregate_gate_enforced"] is True
    assert payload["edge_executable_candidate_paths_modeled"] is True
    assert payload["edge_executable_fixture_matrix_modeled"] is True
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
    assert "source_l6_04_summary" not in payload


def main() -> int:
    cases = [
        ("no_auth_dedicated", False, DEDICATED),
        ("auth_dedicated", True, DEDICATED),
        ("auth_default", True, DEFAULT),
        ("missing_profile", True, None),
    ]
    for name, allow, profile in cases:
        payload = gate.build_edge_executable_discovery_aggregate_gate(
            ROOT,
            allow_live_start=allow,
            profile_dir=profile,
        )
        assert_passive(payload)
        print(
            "PASS {0}: patch={1} compact_json={2} exe_probe={3}".format(
                name,
                payload["patch"],
                payload["compact_json_readback_enabled"],
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
        timeout=30,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    payload = json.loads(completed.stdout)
    assert len(completed.stdout) < 80000
    assert_passive(payload)
    print("PASS main_cli: compact JSON parsed quickly; full nested JSON intentionally pruned")
    print("PASS L6.5a repair: aggregate gate accepted with compact JSON and no browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

DOC_NOTE = r'''

## L6.5a compact JSON readback repair

L6.5a repairs the original L6.5 timeout by pruning full nested source summaries from the aggregate payload. The aggregate gate still proves L6.1 through L6.4 remain accepted, but exposes that proof as compact `source_chain_status` and boolean acceptance fields instead of echoing the entire nested chain.

This preserves brief validation output and makes `--json --compact` safe for CLI readback.
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    if DOC_PATH.exists():
        text = DOC_PATH.read_text(encoding="utf-8")
        if "compact JSON readback" not in text:
            text = text.replace("brief validation output.", "brief validation output.\n- compact JSON readback.")
        if "## L6.5a compact JSON readback repair" not in text:
            text = text.rstrip() + DOC_NOTE
        DOC_PATH.write_text(text, encoding="utf-8")
    else:
        DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
        DOC_PATH.write_text("# L6.5 Microsoft Edge executable discovery aggregate gate\n\n- brief validation output.\n- compact JSON readback.\n" + DOC_NOTE, encoding="utf-8")
    print("L6.5a compact JSON repair written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())