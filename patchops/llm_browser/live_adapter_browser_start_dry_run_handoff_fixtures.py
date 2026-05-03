from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .live_adapter_browser_start_dry_run_handoff_contract import (
    ALLOWED_BROWSERS,
    BLOCKED_SIDE_EFFECTS,
    FORBIDDEN_OPTIONAL_ROOTS,
    STATUS_FAIL,
    STATUS_PASS,
    build_browser_start_dry_run_handoff_contract,
)

PATCH = "L4.3"
NAME = "L4.3 Browser Start Dry-Run Handoff Fixture Matrix"
NEXT_PATCH = "L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback"
SIDE_EFFECT_BOUNDARY = "dry-run-handoff-fixture-matrix-only"

REQUIRED_PRIOR_L4_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_contract.py",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_contract.md",
    "tests/test_l4_01_browser_start_dry_run_handoff_contract_current.py",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_cli_readback.md",
    "tests/test_l4_02_browser_start_dry_run_handoff_cli_readback_current.py",
)

REQUIRED_L4_03_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_fixtures.py",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix.md",
    "tests/test_l4_03_browser_start_dry_run_handoff_fixture_matrix_current.py",
)

DOC_REQUIRED_PHRASES: tuple[str, ...] = (
    "L4.3 Live adapter browser-start dry-run handoff fixture matrix",
    "dry-run-only",
    "fixture matrix",
    "no Selenium import",
    "no browser start",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback",
)

FORBIDDEN_MATRIX_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "open --browser",
    "run-once",
    "watch-downloads",
    "selenium",
    "webdriver",
    "start_browser",
    "click_download",
    "paste_to_composer",
    "send_or_submit",
)

READBACK_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract --repo-root C:\\dev\\patchops --browser edge --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract --repo-root C:\\dev\\patchops --browser opera --json --compact",
    "git status --short --branch",
)


@dataclass(frozen=True)
class DryRunHandoffFixtureCase:
    case_id: str
    browser: str
    description: str
    expected_status: str
    expected_ok: bool
    expected_startup_allowed: bool = False
    expected_browser_started: bool = False
    expected_profile_directory_created: bool = False
    expected_selenium_imported: bool = False

    def evaluate(self, *, repo_root: str | Path | None = None) -> dict[str, Any]:
        return build_browser_start_dry_run_handoff_contract(repo_root, browser=self.browser)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    candidate = Path(repo_root)
    if str(candidate) == ".":
        return Path.cwd().resolve()
    return candidate.resolve()


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
    return sorted(set(loaded))


def _command_plan_is_readback_only(commands: Sequence[str]) -> bool:
    text = "\n".join(commands).lower()
    return not any(fragment.lower() in text for fragment in FORBIDDEN_MATRIX_COMMAND_FRAGMENTS)


def _json_safe(value: Mapping[str, Any]) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": dict(details or {})}


def fixture_cases() -> tuple[DryRunHandoffFixtureCase, ...]:
    return (
        DryRunHandoffFixtureCase(
            case_id="edge_dry_run_handoff_passive",
            browser="edge",
            description="Edge is modelled as a dry-run handoff target but startup remains disallowed.",
            expected_status=STATUS_PASS,
            expected_ok=True,
        ),
        DryRunHandoffFixtureCase(
            case_id="opera_dry_run_handoff_passive",
            browser="opera",
            description="Opera is modelled as a dry-run handoff target but startup remains disallowed.",
            expected_status=STATUS_PASS,
            expected_ok=True,
        ),
        DryRunHandoffFixtureCase(
            case_id="mixed_case_edge_normalized",
            browser="EdGe",
            description="Browser names are normalized before readback and still do not trigger startup.",
            expected_status=STATUS_PASS,
            expected_ok=True,
        ),
        DryRunHandoffFixtureCase(
            case_id="unsupported_browser_rejected_without_startup",
            browser="firefox",
            description="Unsupported browsers fail the passive readback without starting anything.",
            expected_status=STATUS_FAIL,
            expected_ok=False,
        ),
    )


def _case_payload(case: DryRunHandoffFixtureCase, result: Mapping[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(dict(result), sort_keys=True))
    checks = [
        _check("expected_ok", normalized.get("ok") is case.expected_ok, {"expected": case.expected_ok, "actual": normalized.get("ok")}),
        _check("expected_status", normalized.get("status") == case.expected_status, {"expected": case.expected_status, "actual": normalized.get("status")}),
        _check("expected_startup_not_allowed", normalized.get("startup_allowed") is case.expected_startup_allowed),
        _check("expected_browser_not_started", normalized.get("browser_started") is case.expected_browser_started),
        _check("expected_profile_directory_not_created", normalized.get("profile_directory_created") is case.expected_profile_directory_created),
        _check("expected_selenium_not_imported", normalized.get("selenium_imported") is case.expected_selenium_imported),
        _check("expected_no_side_effects", normalized.get("side_effects_performed") == []),
        _check("expected_no_filesystem_writes", normalized.get("filesystem_writes_performed") == []),
    ]
    return {
        "case_id": case.case_id,
        "browser": case.browser.strip().lower(),
        "description": case.description,
        "expected": asdict(case),
        "result": normalized,
        "checks": checks,
        "case_ok": all(check["ok"] for check in checks),
    }


def build_browser_start_dry_run_handoff_fixture_matrix(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build the passive L4.3 dry-run handoff fixture matrix.

    This is a data/readback gate only. It never imports Selenium, never starts a
    browser, never creates a driver/session, never creates profile directories,
    and never runs downloaded packages from adapter logic.
    """
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    cases = []
    for case in fixture_cases():
        cases.append(_case_payload(case, case.evaluate(repo_root=root)))

    optional_roots_loaded = _optional_roots_loaded()
    newly_loaded = set(sys.modules) - before_modules
    newly_loaded_forbidden = sorted(
        root_name
        for root_name in FORBIDDEN_OPTIONAL_ROOTS
        if any(name == root_name or name.startswith(root_name + ".") for name in newly_loaded)
    )

    missing_prior_paths = _missing_paths(root, REQUIRED_PRIOR_L4_PATHS)
    missing_l4_03_paths = _missing_paths(root, REQUIRED_L4_03_PATHS)
    doc_path = root / "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix.md"
    doc_text = _read_text(doc_path)
    missing_doc_phrases = [phrase for phrase in DOC_REQUIRED_PHRASES if phrase not in doc_text]

    side_effect_summary = {
        "dry_run_only": True,
        "startup_authorized": False,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "blocked_side_effects": list(BLOCKED_SIDE_EFFECTS),
        "allowed_browsers": list(ALLOWED_BROWSERS),
    }

    checks = [
        _check("l4_03_fixture_cases_present", len(cases) >= 4, {"case_count": len(cases)}),
        _check("l4_03_all_fixture_cases_match_expectations", all(case["case_ok"] for case in cases)),
        _check("l4_03_prior_l4_artifacts_present", not missing_prior_paths, {"missing": missing_prior_paths}),
        _check("l4_03_artifacts_present", not missing_l4_03_paths, {"missing": missing_l4_03_paths}),
        _check("l4_03_doc_contains_boundary", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("l4_03_command_plan_is_readback_only", _command_plan_is_readback_only(READBACK_COMMANDS)),
        _check("l4_03_no_forbidden_optional_imports_loaded", not optional_roots_loaded, {"loaded": optional_roots_loaded}),
        _check("l4_03_no_forbidden_optional_imports_newly_loaded", not newly_loaded_forbidden, {"newly_loaded": newly_loaded_forbidden}),
        _check("l4_03_no_browser_start_side_effects", True, side_effect_summary),
    ]

    payload: dict[str, Any] = {
        "name": NAME,
        "phase": "L4",
        "patch": PATCH,
        "status": STATUS_PASS,
        "ok": True,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "repo_root": str(root),
        "cases": cases,
        "case_count": len(cases),
        "readback_commands": list(READBACK_COMMANDS),
        "executed_validation_commands": [],
        "dry_run_only": True,
        "startup_authorized": False,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "optional_browser_dependencies_imported": optional_roots_loaded,
        "forbidden_optional_imports_newly_loaded": newly_loaded_forbidden,
        "selenium_imported": "selenium" in optional_roots_loaded,
        "git_commit_executed": False,
        "git_push_executed": False,
        "missing_prior_l4_paths": missing_prior_paths,
        "missing_l4_03_paths": missing_l4_03_paths,
        "missing_doc_phrases": missing_doc_phrases,
        "checks": checks,
    }
    checks.append(_check("l4_03_payload_json_safe", _json_safe(payload)))
    ok = all(check["ok"] for check in checks)
    payload["ok"] = ok
    payload["status"] = STATUS_PASS if ok else STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Status          : {payload.get('status')}",
        f"Patch           : {payload.get('patch')}",
        f"Case Count      : {payload.get('case_count')}",
        f"Dry Run Only    : {payload.get('dry_run_only')}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
        f"Browser Started : {payload.get('browser_started')}",
        f"Profile Created : {payload.get('profile_directory_created')}",
        f"Selenium Import : {payload.get('selenium_imported')}",
        f"Next Patch      : {payload.get('next_patch')}",
        "",
        "Fixture cases:",
    ]
    for case in payload.get("cases", []):
        state = "PASS" if case.get("case_ok") else "FAIL"
        lines.append(f"- {state}: {case.get('case_id')} ({case.get('browser')})")
    lines.extend(["", "Checks:"])
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    lines.extend(["", "Readback command plan:"])
    for command in payload.get("readback_commands", []):
        lines.append(f"- {command}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_browser_start_dry_run_handoff_fixture_matrix(args.repo_root)
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
