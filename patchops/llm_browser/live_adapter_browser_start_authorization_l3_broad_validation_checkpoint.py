from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

NAME = "L3.10 Browser Start Authorization L3 Broad Validation Checkpoint"
PATCH = "L3.10"
PHASE = "L3"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NEXT_PATCH = "L3.11 Live adapter browser-start authorization L3 broad validation checkpoint CLI/readback"
SIDE_EFFECT_BOUNDARY = "passive-broad-validation-readback-only"

FORBIDDEN_OPTIONAL_ROOTS = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "playwright",
    "pyppeteer",
)

REQUIRED_L1_L2_PATHS = (
    "patchops/llm_browser/live_adapter_startup_request_l1_final_acceptance_marker.py",
    "docs/llm_browser_live_adapter_startup_request_l1_final_acceptance_marker.md",
    "tests/test_llm_browser_live_adapter_startup_request_l1_final_acceptance_marker_current.py",
    "patchops/llm_browser/live_adapter_browser_profile_l2_final_acceptance_marker.py",
    "patchops/llm_browser/l2_10_broad_validation.py",
    "docs/llm_browser_live_adapter_browser_profile_l2_final_acceptance_marker.md",
    "docs/llm_browser_l2_12_final_acceptance_marker.md",
    "tests/test_l2_10_broad_validation_current.py",
    "tests/test_l2_11_broad_validation_cli_readback_current.py",
    "tests/test_l2_12_final_acceptance_marker_current.py",
)

REQUIRED_L3_PATHS = (
    "patchops/llm_browser/live_adapter_browser_start_authorization.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_fixtures.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_aggregate_readiness_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_documentation_checkpoint.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_broad_validation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_browser_start_authorization.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_aggregate_readiness_gate.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_readiness_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_documentation_freeze_readiness_checkpoint.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_broad_validation_checkpoint.md",
    "tests/test_l3_browser_start_authorization_current.py",
    "tests/test_l3_02_browser_start_authorization_cli_readback_current.py",
    "tests/test_l3_03_browser_start_authorization_fixture_matrix_current.py",
    "tests/test_l3_04_browser_start_authorization_fixture_matrix_cli_readback_current.py",
    "tests/test_l3_05_browser_start_authorization_fixture_matrix_contract_gate_current.py",
    "tests/test_l3_06_browser_start_authorization_contract_gate_cli_readback_current.py",
    "tests/test_l3_07_browser_start_authorization_l3_aggregate_readiness_gate_current.py",
    "tests/test_l3_08_browser_start_authorization_l3_readiness_cli_readback_current.py",
    "tests/test_l3_09_browser_start_authorization_l3_documentation_checkpoint_current.py",
    "tests/test_l3_10_browser_start_authorization_l3_broad_validation_checkpoint_current.py",
)

REQUIRED_COMMANDS = (
    "browser-start-authorization",
    "browser-start-authorization-fixtures",
    "browser-start-authorization-contract-gate",
    "browser-start-authorization-l3-readiness",
)

COMMAND_PLAN = (
    "py -m compileall patchops/llm_browser tests",
    "py -m pytest -q tests/test_l3_browser_start_authorization_current.py tests/test_l3_02_browser_start_authorization_cli_readback_current.py tests/test_l3_03_browser_start_authorization_fixture_matrix_current.py tests/test_l3_04_browser_start_authorization_fixture_matrix_cli_readback_current.py tests/test_l3_05_browser_start_authorization_fixture_matrix_contract_gate_current.py tests/test_l3_06_browser_start_authorization_contract_gate_cli_readback_current.py tests/test_l3_07_browser_start_authorization_l3_aggregate_readiness_gate_current.py tests/test_l3_08_browser_start_authorization_l3_readiness_cli_readback_current.py tests/test_l3_09_browser_start_authorization_l3_documentation_checkpoint_current.py tests/test_l3_10_browser_start_authorization_l3_broad_validation_checkpoint_current.py",
    "py -m patchops.llm_browser.live_adapter_browser_start_authorization_l3_broad_validation_checkpoint --repo-root C:\\dev\\patchops --json --compact",
    "git status --short --branch",
)

FORBIDDEN_COMMAND_FRAGMENTS = (
    "git commit",
    "git push",
    "run-package",
    "open --browser",
    "run-once",
    "watch-downloads",
    "start_browser",
    "click_download",
    "paste_to_composer",
    "send_message",
    "send_or_submit",
)

LIVE_SIDE_EFFECT_OPERATIONS = (
    "import_selenium",
    "start_browser",
    "create_browser_session",
    "create_profile_directory",
    "adapter_filesystem_write",
    "read_provider_page",
    "click_download",
    "paste_to_composer",
    "send_message",
    "run_downloaded_package",
    "commit",
    "push",
)

SAFETY_PHRASES = (
    "no Selenium import",
    "no browser start",
    "no browser session creation",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "no commit or push",
)

PROGRESSION_PHRASES = (
    "L3.1 explicit browser-start authorization contract",
    "L3.8 aggregate readiness gate CLI/readback",
    "L3.9 documentation freeze/readiness checkpoint",
    NEXT_PATCH,
)


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root:
        candidate = Path(repo_root)
        if str(candidate) == ".":
            return Path.cwd().resolve()
        return candidate.resolve()
    return _repo_root_from_here()


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _json_safe(value: Any) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _forbidden_imports_present() -> list[str]:
    return sorted({root for root in FORBIDDEN_OPTIONAL_ROOTS if any(name == root or name.startswith(root + ".") for name in sys.modules)})


def _forbidden_imports_loaded_since(before_modules: set[str]) -> list[str]:
    newly_loaded = set(sys.modules) - before_modules
    return sorted({root for root in FORBIDDEN_OPTIONAL_ROOTS if any(name == root or name.startswith(root + ".") for name in newly_loaded)})


def _missing_paths(repo_root: Path, paths: Sequence[str]) -> list[str]:
    return sorted(path for path in paths if not (repo_root / path).exists())


def _read_text(repo_root: Path, rel_path: str) -> str:
    try:
        path = repo_root / rel_path
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        return ""
    return ""


def _missing_phrases(text: str, phrases: Sequence[str]) -> list[str]:
    return [phrase for phrase in phrases if phrase not in text]


def _command_plan_is_passive(commands: Sequence[str]) -> tuple[bool, list[str]]:
    lowered = "\n".join(commands).lower()
    found = [fragment for fragment in FORBIDDEN_COMMAND_FRAGMENTS if fragment in lowered]
    return found == [], found


def _payload_ok(payload: Mapping[str, Any]) -> bool:
    return bool(payload.get("ok") is True and str(payload.get("status")) == STATUS_PASS)


def _payload_no_live_effects(payload: Mapping[str, Any]) -> bool:
    return bool(
        payload.get("startup_allowed", payload.get("startup_authorized", False)) is False
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and payload.get("profile_directory_created", False) is False
        and _as_list(payload.get("filesystem_writes_performed")) == []
        and _as_list(payload.get("side_effects_performed")) == []
        and payload.get("optional_browser_dependencies_required") in (False, None)
    )


def _safe_call(name: str, func: Any, repo_root: Path) -> tuple[Mapping[str, Any], str | None]:
    try:
        return _as_mapping(func(repo_root)), None
    except Exception as exc:  # pragma: no cover - report diagnostic fallback
        return {}, f"{name}: {exc.__class__.__name__}: {exc}"


def build_l3_browser_start_authorization_broad_validation_checkpoint(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _resolve_repo_root(repo_root)
    before_modules = set(sys.modules)

    from patchops.llm_browser import commands
    from patchops.llm_browser import live_adapter_browser_start_authorization_l3_aggregate_readiness_gate as readiness_gate
    from patchops.llm_browser import live_adapter_browser_start_authorization_l3_documentation_checkpoint as documentation_checkpoint

    readiness_payload, readiness_error = _safe_call(
        "l3_aggregate_readiness_gate",
        readiness_gate.build_l3_browser_start_authorization_aggregate_readiness_gate,
        root,
    )
    doc_payload, doc_error = _safe_call(
        "l3_documentation_checkpoint",
        documentation_checkpoint.build_l3_browser_start_authorization_documentation_checkpoint,
        root,
    )

    command_names = set(commands.llm_browser_command_names())
    missing_commands = sorted(command for command in REQUIRED_COMMANDS if command not in command_names)
    missing_l1_l2_paths = _missing_paths(root, REQUIRED_L1_L2_PATHS)
    missing_l3_paths = _missing_paths(root, REQUIRED_L3_PATHS)
    doc_text = _read_text(root, "docs/llm_browser_live_adapter_browser_start_authorization_l3_broad_validation_checkpoint.md")
    missing_safety_phrases = _missing_phrases(doc_text, SAFETY_PHRASES)
    missing_progression_phrases = _missing_phrases(doc_text, PROGRESSION_PHRASES)
    command_plan_passive, forbidden_command_fragments = _command_plan_is_passive(COMMAND_PLAN)
    loaded_forbidden = _forbidden_imports_present()
    newly_loaded_forbidden = _forbidden_imports_loaded_since(before_modules)
    executed_validation_commands: list[str] = []

    readiness_ok = _payload_ok(readiness_payload)
    doc_ok = _payload_ok(doc_payload)
    readiness_no_effects = _payload_no_live_effects(readiness_payload) if readiness_payload else False
    doc_no_effects = _payload_no_live_effects(doc_payload) if doc_payload else False

    broad_summary = {
        "l1_l2_path_count": len(REQUIRED_L1_L2_PATHS),
        "l3_path_count": len(REQUIRED_L3_PATHS),
        "command_count": len(REQUIRED_COMMANDS),
        "planned_command_count": len(COMMAND_PLAN),
        "readiness_patch": readiness_payload.get("patch"),
        "documentation_patch": doc_payload.get("patch"),
    }

    checks = [
        _check("l3_aggregate_readiness_gate_still_passes", readiness_ok, {"patch": readiness_payload.get("patch"), "status": readiness_payload.get("status"), "error": readiness_error}),
        _check("l3_documentation_checkpoint_still_passes", doc_ok, {"patch": doc_payload.get("patch"), "status": doc_payload.get("status"), "error": doc_error}),
        _check("l3_accepted_cli_surfaces_present", missing_commands == [], {"missing_commands": missing_commands, "required_commands": list(REQUIRED_COMMANDS)}),
        _check("l1_l2_accepted_surfaces_remain_present", missing_l1_l2_paths == [], {"missing_paths": missing_l1_l2_paths, "required_count": len(REQUIRED_L1_L2_PATHS)}),
        _check("l3_accepted_surfaces_remain_present", missing_l3_paths == [], {"missing_paths": missing_l3_paths, "required_count": len(REQUIRED_L3_PATHS)}),
        _check("l3_broad_validation_doc_contains_safety_boundary", missing_safety_phrases == [], {"missing_phrases": missing_safety_phrases}),
        _check("l3_broad_validation_doc_contains_progression_and_next_patch", missing_progression_phrases == [], {"missing_phrases": missing_progression_phrases}),
        _check("l3_broad_validation_command_plan_is_readback_only", command_plan_passive, {"forbidden_fragments": forbidden_command_fragments, "planned_commands": list(COMMAND_PLAN)}),
        _check("l3_broad_validation_does_not_execute_planned_commands", executed_validation_commands == [], {"executed_validation_commands": executed_validation_commands}),
        _check("l3_broad_validation_keeps_readiness_gate_passive", readiness_no_effects, {"readiness_no_effects": readiness_no_effects}),
        _check("l3_broad_validation_keeps_documentation_checkpoint_passive", doc_no_effects, {"documentation_no_effects": doc_no_effects}),
        _check("l3_broad_validation_no_new_optional_browser_dependency_imports", newly_loaded_forbidden == [], {"newly_loaded_forbidden_modules": newly_loaded_forbidden, "loaded_forbidden_modules": loaded_forbidden}),
        _check("l3_broad_validation_selenium_not_imported", "selenium" not in loaded_forbidden and "selenium" not in newly_loaded_forbidden, {"loaded_forbidden_modules": loaded_forbidden}),
        _check("l3_broad_validation_payload_json_safe", _json_safe(broad_summary), broad_summary),
    ]

    ok = all(check["ok"] for check in checks)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": bool(ok),
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "startup_authorized": False,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": "selenium" in loaded_forbidden or "selenium" in newly_loaded_forbidden,
        "executed_validation_commands": executed_validation_commands,
        "command_plan": list(COMMAND_PLAN),
        "side_effect_operations": list(LIVE_SIDE_EFFECT_OPERATIONS),
        "required_commands": list(REQUIRED_COMMANDS),
        "missing_commands": missing_commands,
        "required_l1_l2_paths": list(REQUIRED_L1_L2_PATHS),
        "required_l3_paths": list(REQUIRED_L3_PATHS),
        "missing_l1_l2_paths": missing_l1_l2_paths,
        "missing_l3_paths": missing_l3_paths,
        "missing_safety_phrases": missing_safety_phrases,
        "missing_progression_phrases": missing_progression_phrases,
        "readiness_gate": dict(readiness_payload),
        "documentation_checkpoint": dict(doc_payload),
        "loaded_forbidden_modules": loaded_forbidden,
        "newly_loaded_forbidden_modules": newly_loaded_forbidden,
        "checks": checks,
    }


def build_broad_validation_checkpoint(repo_root: str | Path | None = None) -> dict[str, Any]:
    return build_l3_browser_start_authorization_broad_validation_checkpoint(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    checks = _as_list(payload.get("checks"))
    lines = [
        "PatchOps LLM browser browser-start authorization L3 broad validation checkpoint",
        "PatchOps LLM browser live adapter browser-start authorization L3 broad validation checkpoint",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Startup    : authorized={str(payload.get('startup_authorized')).lower()} allowed={str(payload.get('startup_allowed')).lower()}",
        f"Browser    : started={payload.get('browser_started')}",
        f"Session    : created={payload.get('browser_session_created')}",
        f"ProfileDir : created={payload.get('profile_directory_created')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Commands   : required={len(_as_list(payload.get('required_commands')))} missing={len(_as_list(payload.get('missing_commands')))} planned={len(_as_list(payload.get('command_plan')))} executed={len(_as_list(payload.get('executed_validation_commands')))}",
        f"L1/L2 Paths: required={len(_as_list(payload.get('required_l1_l2_paths')))} missing={len(_as_list(payload.get('missing_l1_l2_paths')))}",
        f"L3 Paths   : required={len(_as_list(payload.get('required_l3_paths')))} missing={len(_as_list(payload.get('missing_l3_paths')))}",
        "Checks:",
    ]
    for check in checks:
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
            if check.get("ok") is not True:
                lines.append(f"  details: {json.dumps(check.get('details', {}), sort_keys=True)}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L3 broad validation checkpoint for browser-start authorization.")
    parser.add_argument("--repo-root", default=None, help="PatchOps repository root. Defaults to current module's repository root.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or []))
    payload = build_l3_browser_start_authorization_broad_validation_checkpoint(args.repo_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
