from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .live_adapter_browser_start_supervised_launch_handoff_contract import (
    ALLOWED_BROWSERS,
    ALLOWED_OPERATOR_DECISIONS,
    BLOCKED_SIDE_EFFECTS,
    FORBIDDEN_OPTIONAL_ROOTS,
    STATUS_FAIL,
    STATUS_PASS,
    build_l5_browser_start_supervised_launch_handoff_contract,
)

PATCH = "L5.3"
NAME = "L5.3 Browser Start Supervised Launch Handoff Fixture Matrix"
NEXT_PATCH = "L5.4 Live adapter browser-start supervised launch handoff fixture matrix CLI/readback"
SIDE_EFFECT_BOUNDARY = "supervised-launch-handoff-fixture-matrix-only"

REQUIRED_PRIOR_L5_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_contract.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_contract.md",
    "tests/test_l5_01_browser_start_supervised_launch_handoff_contract_current.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_cli_readback.md",
    "tests/test_l5_02_browser_start_supervised_launch_handoff_cli_readback_current.py",
)

REQUIRED_L5_03_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_fixtures.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix.md",
    "tests/test_l5_03_browser_start_supervised_launch_handoff_fixture_matrix_current.py",
)

DOC_REQUIRED_PHRASES: tuple[str, ...] = (
    "L5.3 Live adapter browser-start supervised launch handoff fixture matrix",
    "supervised-launch handoff",
    "fixture matrix",
    "modelled-only",
    "no Selenium import",
    "no browser start",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "L5.4 Live adapter browser-start supervised launch handoff fixture matrix CLI/readback",
)

FORBIDDEN_MATRIX_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "llm-browser open",
    "open --browser",
    "run-once",
    "watch-downloads",
    "selenium",
    "webdriver",
    "start_browser",
    "click_download",
    "paste_to_composer",
    "send_message",
    "send_or_submit",
)

READBACK_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root C:\\dev\\patchops --browser edge --operator-decision review_only --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root C:\\dev\\patchops --browser opera --operator-decision prepare_only --json --compact",
    "git status --short --branch",
)


@dataclass(frozen=True)
class SupervisedLaunchHandoffFixtureCase:
    case_id: str
    description: str
    browser: str
    operator_decision: str
    expected_ok: bool
    expected_status: str
    expected_normalized_browser: str | None = None
    expected_normalized_decision: str | None = None

    def run(self, *, repo_root: str | Path | None = None) -> dict[str, Any]:
        return build_l5_browser_start_supervised_launch_handoff_contract(
            repo_root,
            browser=self.browser,
            operator_decision=self.operator_decision,
        )


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
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


def _forbidden_imports_loaded_since(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(set(found))


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


def fixture_cases() -> tuple[SupervisedLaunchHandoffFixtureCase, ...]:
    return (
        SupervisedLaunchHandoffFixtureCase(
            case_id="edge_review_only_passive",
            description="Edge review-only handoff remains modelled-only and startup-blocked.",
            browser="edge",
            operator_decision="review_only",
            expected_ok=True,
            expected_status=STATUS_PASS,
            expected_normalized_browser="edge",
            expected_normalized_decision="review_only",
        ),
        SupervisedLaunchHandoffFixtureCase(
            case_id="opera_prepare_only_passive",
            description="Opera prepare-only handoff remains modelled-only and startup-blocked.",
            browser="opera",
            operator_decision="prepare_only",
            expected_ok=True,
            expected_status=STATUS_PASS,
            expected_normalized_browser="opera",
            expected_normalized_decision="prepare_only",
        ),
        SupervisedLaunchHandoffFixtureCase(
            case_id="mixed_case_browser_and_decision_normalized",
            description="Browser and operator-decision values are normalized as data only.",
            browser="EDGE",
            operator_decision="REVIEW_ONLY",
            expected_ok=True,
            expected_status=STATUS_PASS,
            expected_normalized_browser="edge",
            expected_normalized_decision="review_only",
        ),
        SupervisedLaunchHandoffFixtureCase(
            case_id="unsupported_browser_rejected_without_startup",
            description="Unsupported browsers fail the handoff contract without startup.",
            browser="firefox",
            operator_decision="review_only",
            expected_ok=False,
            expected_status=STATUS_FAIL,
            expected_normalized_browser="firefox",
            expected_normalized_decision="review_only",
        ),
        SupervisedLaunchHandoffFixtureCase(
            case_id="invalid_operator_decision_rejected_without_startup",
            description="Unknown operator decisions fail the handoff contract without startup.",
            browser="edge",
            operator_decision="launch_now",
            expected_ok=False,
            expected_status=STATUS_FAIL,
            expected_normalized_browser="edge",
            expected_normalized_decision="launch_now",
        ),
    )


def evaluate_fixture_case(case: SupervisedLaunchHandoffFixtureCase, *, repo_root: str | Path | None = None) -> dict[str, Any]:
    before_modules = set(sys.modules)
    result = case.run(repo_root=repo_root)
    newly_loaded_forbidden_imports = _forbidden_imports_loaded_since(before_modules)
    handoff_request = result.get("handoff_request", {})

    expectations = [
        _check("expected_ok", result.get("ok") is case.expected_ok, {"actual": result.get("ok"), "expected": case.expected_ok}),
        _check("expected_status", result.get("status") == case.expected_status, {"actual": result.get("status"), "expected": case.expected_status}),
        _check("expected_browser_normalization", result.get("browser") == case.expected_normalized_browser),
        _check("expected_operator_decision_normalization", result.get("operator_decision") == case.expected_normalized_decision),
        _check("handoff_request_modelled_only", handoff_request.get("modelled_only") is True),
        _check("startup_authorized_false", result.get("startup_authorized") is False),
        _check("startup_allowed_false", result.get("startup_allowed") is False),
        _check("live_driver_session_allowed_false", result.get("live_driver_session_allowed") is False),
        _check("browser_not_started", result.get("browser_started") is False),
        _check("browser_session_not_created", result.get("browser_session_created") is False),
        _check("driver_not_created", result.get("driver_created") is False),
        _check("profile_directory_not_created", result.get("profile_directory_created") is False),
        _check("no_adapter_filesystem_writes", result.get("filesystem_writes_performed") == []),
        _check("no_side_effects_performed", result.get("side_effects_performed") == []),
        _check("no_optional_browser_dependencies_required", result.get("optional_browser_dependencies_required") is False),
        _check("no_selenium_imported", result.get("selenium_imported") is False),
        _check("no_new_forbidden_optional_imports", not newly_loaded_forbidden_imports, {"loaded": newly_loaded_forbidden_imports}),
        _check("no_validation_commands_executed_by_adapter", result.get("executed_validation_commands") == []),
    ]
    return {
        "case_id": case.case_id,
        "description": case.description,
        "browser": case.browser,
        "operator_decision": case.operator_decision,
        "expected_ok": case.expected_ok,
        "expected_status": case.expected_status,
        "result": result,
        "checks": expectations,
        "case_ok": all(check["ok"] for check in expectations),
        "startup_allowed": result.get("startup_allowed"),
        "browser_started": result.get("browser_started"),
        "browser_session_created": result.get("browser_session_created"),
        "profile_directory_created": result.get("profile_directory_created"),
        "side_effects_performed": result.get("side_effects_performed"),
        "filesystem_writes_performed": result.get("filesystem_writes_performed"),
    }


def build_supervised_launch_handoff_fixture_matrix(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = resolve_repo_root(repo_root)
    missing_prior_l5_paths = _missing_paths(root, REQUIRED_PRIOR_L5_PATHS)
    missing_l5_03_paths = _missing_paths(root, REQUIRED_L5_03_PATHS)
    doc_text = _read_text(root / "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix.md")
    missing_doc_phrases = [phrase for phrase in DOC_REQUIRED_PHRASES if phrase not in doc_text]
    optional_roots_loaded = _optional_roots_loaded()
    cases = [evaluate_fixture_case(case, repo_root=root) for case in fixture_cases()]

    checks = [
        _check("l5_03_prior_l5_contract_and_cli_artifacts_present", not missing_prior_l5_paths, {"missing": missing_prior_l5_paths}),
        _check("l5_03_fixture_matrix_artifacts_present", not missing_l5_03_paths, {"missing": missing_l5_03_paths}),
        _check("l5_03_docs_contain_fixture_matrix_boundary", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("l5_03_allowed_browsers_remain_edge_and_opera", tuple(ALLOWED_BROWSERS) == ("edge", "opera"), {"allowed_browsers": list(ALLOWED_BROWSERS)}),
        _check("l5_03_operator_decisions_remain_passive", set(ALLOWED_OPERATOR_DECISIONS) == {"block", "review_only", "prepare_only"}),
        _check("l5_03_cases_cover_edge_opera_and_rejections", {case["case_id"] for case in cases} >= {"edge_review_only_passive", "opera_prepare_only_passive", "unsupported_browser_rejected_without_startup", "invalid_operator_decision_rejected_without_startup"}),
        _check("l5_03_all_fixture_cases_match_expectations", all(case["case_ok"] for case in cases)),
        _check("l5_03_command_plan_is_readback_only", _command_plan_is_readback_only(READBACK_COMMANDS)),
        _check("l5_03_no_optional_browser_dependency_imports", not optional_roots_loaded, {"loaded": optional_roots_loaded}),
    ]

    payload: dict[str, Any] = {
        "name": NAME,
        "phase": "L5",
        "patch": PATCH,
        "status": STATUS_PASS,
        "ok": True,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "repo_root": str(root),
        "allowed_browsers": list(ALLOWED_BROWSERS),
        "allowed_operator_decisions": list(ALLOWED_OPERATOR_DECISIONS),
        "case_count": len(cases),
        "case_ids": [case["case_id"] for case in cases],
        "cases": cases,
        "readback_commands": list(READBACK_COMMANDS),
        "modelled_only": True,
        "startup_authorized": False,
        "startup_allowed": False,
        "live_driver_session_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "blocked_side_effects": list(BLOCKED_SIDE_EFFECTS),
        "optional_browser_dependencies_required": False,
        "optional_browser_dependencies_imported": optional_roots_loaded,
        "selenium_imported": "selenium" in optional_roots_loaded,
        "executed_validation_commands": [],
        "git_commit_executed": False,
        "git_push_executed": False,
        "missing_prior_l5_paths": missing_prior_l5_paths,
        "missing_l5_03_paths": missing_l5_03_paths,
        "missing_doc_phrases": missing_doc_phrases,
        "checks": checks,
    }
    checks.append(_check("l5_03_payload_json_safe", _json_safe(payload)))
    ok = all(check["ok"] for check in checks)
    payload["ok"] = ok
    payload["status"] = STATUS_PASS if ok else STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Status              : {payload.get('status')}",
        f"Patch               : {payload.get('patch')}",
        f"Cases               : {payload.get('case_count')}",
        f"Modelled Only       : {payload.get('modelled_only')}",
        f"Startup Authorized  : {payload.get('startup_authorized')}",
        f"Startup Allowed     : {payload.get('startup_allowed')}",
        f"Browser Started     : {payload.get('browser_started')}",
        f"Session Created     : {payload.get('browser_session_created')}",
        f"Profile Created     : {payload.get('profile_directory_created')}",
        f"Selenium Imported   : {payload.get('selenium_imported')}",
        f"Next Patch          : {payload.get('next_patch')}",
        "",
        "Fixture Cases:",
    ]
    for case in payload.get("cases", []):
        state = "PASS" if case.get("case_ok") else "FAIL"
        lines.append(f"- {state}: {case.get('case_id')} ({case.get('browser')} / {case.get('operator_decision')})")
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

    payload = build_supervised_launch_handoff_fixture_matrix(args.repo_root)
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
