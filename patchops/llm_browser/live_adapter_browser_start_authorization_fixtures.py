from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from .live_adapter_browser_start_authorization import (
    FORBIDDEN_IMPORT_ROOTS,
    LIVE_SIDE_EFFECT_OPERATIONS,
    PHASE,
    STATUS_FAIL,
    STATUS_PASS,
    BrowserStartAuthorizationDecision,
    BrowserStartAuthorizationRequest,
    build_browser_start_authorization_request,
    evaluate_browser_start_authorization,
)

PATCH = "L3.3"
NAME = "llm_browser_live_adapter_browser_start_authorization_fixture_matrix"
NEXT_PATCH = "L3.4 Live adapter browser-start authorization fixture matrix CLI/readback"


@dataclass(frozen=True)
class BrowserStartAuthorizationFixtureCase:
    case_id: str
    description: str
    request: BrowserStartAuthorizationRequest
    expected_ok: bool
    expected_invalid_fields: tuple[str, ...] = ()
    expected_blocked_reasons: tuple[str, ...] = ()

    def evaluate(self, *, repo_root: str | Path | None = None) -> BrowserStartAuthorizationDecision:
        return evaluate_browser_start_authorization(self.request, repo_root=repo_root)


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root:
        candidate = Path(repo_root)
        if str(candidate) == ".":
            return Path.cwd().resolve()
        return candidate.resolve()
    return _repo_root_from_here()


def _forbidden_imports_loaded_since(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(set(found))


def fixture_cases() -> tuple[BrowserStartAuthorizationFixtureCase, ...]:
    return (
        BrowserStartAuthorizationFixtureCase(
            case_id="edge_default_missing_acknowledgements",
            description="Default Edge request remains passive and blocked from real startup.",
            request=build_browser_start_authorization_request(browser="edge"),
            expected_ok=True,
            expected_blocked_reasons=(
                "missing_acknowledgements",
                "browser_start_flag_not_enabled",
                "profile_directory_creation_flag_not_enabled",
                "live_driver_session_flag_not_enabled",
            ),
        ),
        BrowserStartAuthorizationFixtureCase(
            case_id="opera_ack_all_permission_flags_modelled_only",
            description="Even with all acknowledgements and permission flags, L3.3 remains model/readback only.",
            request=build_browser_start_authorization_request(
                browser="opera",
                ack_all=True,
                allow_browser_start=True,
                allow_profile_directory_creation=True,
                allow_live_driver_session=True,
                requested_side_effects=(
                    "start_browser",
                    "create_profile_directory",
                    "create_browser_session",
                ),
            ),
            expected_ok=True,
            expected_blocked_reasons=("live_side_effects_requested_but_modelled_only",),
        ),
        BrowserStartAuthorizationFixtureCase(
            case_id="unsupported_browser_rejected",
            description="Unsupported browsers are rejected before any live operation can be modelled as allowed.",
            request=BrowserStartAuthorizationRequest(
                requested_browser="firefox",
                ack_manual_login_required=True,
                ack_dedicated_profile_required=True,
                ack_no_download_click=True,
                ack_no_composer_paste=True,
                ack_no_send_or_submit=True,
                ack_patchops_remains_source_of_truth=True,
            ),
            expected_ok=False,
            expected_invalid_fields=("requested_browser",),
            expected_blocked_reasons=("unsupported_browser",),
        ),
        BrowserStartAuthorizationFixtureCase(
            case_id="shared_profile_rejected",
            description="Default/shared profile mode is rejected; only dedicated profile mode can be modelled.",
            request=BrowserStartAuthorizationRequest(
                requested_browser="edge",
                requested_profile_mode="default",
                ack_manual_login_required=True,
                ack_dedicated_profile_required=True,
                ack_no_download_click=True,
                ack_no_composer_paste=True,
                ack_no_send_or_submit=True,
                ack_patchops_remains_source_of_truth=True,
            ),
            expected_ok=False,
            expected_invalid_fields=("requested_profile_mode",),
            expected_blocked_reasons=("default_or_shared_profile_not_allowed",),
        ),
        BrowserStartAuthorizationFixtureCase(
            case_id="download_paste_send_side_effects_blocked",
            description="Download, paste, send, and PatchOps package-run side effects stay modelled-only.",
            request=build_browser_start_authorization_request(
                browser="edge",
                ack_all=True,
                requested_side_effects=(
                    "click_download",
                    "run_patchops_package",
                    "paste_to_composer",
                    "send_or_submit",
                ),
            ),
            expected_ok=True,
            expected_blocked_reasons=(
                "browser_start_flag_not_enabled",
                "profile_directory_creation_flag_not_enabled",
                "live_driver_session_flag_not_enabled",
                "live_side_effects_requested_but_modelled_only",
            ),
        ),
    )


def _case_payload(case: BrowserStartAuthorizationFixtureCase, decision: BrowserStartAuthorizationDecision) -> Dict[str, Any]:
    # Normalize tuple fields to JSON-style lists so direct Python readback matches CLI JSON readback.
    payload = json.loads(json.dumps(decision.to_payload(), sort_keys=True))
    expected_invalid_fields = set(case.expected_invalid_fields)
    expected_blocked_reasons = set(case.expected_blocked_reasons)
    actual_invalid_fields = set(decision.invalid_fields)
    actual_blocked_reasons = set(decision.blocked_reasons)
    expectations_met = (
        decision.ok is case.expected_ok
        and expected_invalid_fields.issubset(actual_invalid_fields)
        and expected_blocked_reasons.issubset(actual_blocked_reasons)
        and decision.startup_authorized is False
        and decision.browser_started is False
        and decision.browser_session_created is False
        and decision.profile_directory_created is False
        and decision.side_effects_performed == ()
        and decision.filesystem_writes_performed == ()
        and decision.optional_browser_dependencies_required is False
    )
    payload.update(
        {
            "case_id": case.case_id,
            "description": case.description,
            "expected_ok": case.expected_ok,
            "expected_invalid_fields": list(case.expected_invalid_fields),
            "expected_blocked_reasons": list(case.expected_blocked_reasons),
            "expectations_met": expectations_met,
        }
    )
    return payload


def build_l3_browser_start_authorization_fixture_matrix(repo_root: str | Path | None = None) -> Dict[str, Any]:
    root = resolve_repo_root(repo_root)
    before_modules = set(sys.modules)
    cases = fixture_cases()
    case_payloads = tuple(_case_payload(case, case.evaluate(repo_root=root)) for case in cases)
    newly_loaded_forbidden = _forbidden_imports_loaded_since(before_modules)
    no_side_effects = all(
        case_payload.get("startup_authorized") is False
        and case_payload.get("browser_started") is False
        and case_payload.get("browser_session_created") is False
        and case_payload.get("profile_directory_created") is False
        and case_payload.get("side_effects_performed") == []
        and case_payload.get("filesystem_writes_performed") == []
        for case_payload in case_payloads
    )
    all_expectations_met = all(bool(case_payload.get("expectations_met")) for case_payload in case_payloads)
    no_forbidden_imports = newly_loaded_forbidden == []
    ok = bool(all_expectations_met and no_side_effects and no_forbidden_imports)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": ok,
        "next_patch": NEXT_PATCH,
        "repo_root": str(root),
        "case_count": len(case_payloads),
        "case_ids": [case_payload["case_id"] for case_payload in case_payloads],
        "cases": list(case_payloads),
        "checks": [
            {"name": "all_fixture_expectations_met", "ok": all_expectations_met, "status": STATUS_PASS if all_expectations_met else STATUS_FAIL},
            {"name": "no_browser_start", "ok": no_side_effects, "status": STATUS_PASS if no_side_effects else STATUS_FAIL},
            {"name": "no_profile_directory_creation", "ok": no_side_effects, "status": STATUS_PASS if no_side_effects else STATUS_FAIL},
            {"name": "no_adapter_filesystem_writes", "ok": no_side_effects, "status": STATUS_PASS if no_side_effects else STATUS_FAIL},
            {"name": "no_selenium_or_optional_browser_dependency_import", "ok": no_forbidden_imports, "status": STATUS_PASS if no_forbidden_imports else STATUS_FAIL},
        ],
        "forbidden_optional_browser_imports_loaded": newly_loaded_forbidden,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "side_effects_performed": [],
        "filesystem_writes_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": False,
        "side_effect_boundary": "passive_fixture_matrix_only",
        "command_plan": [
            "py -m patchops.llm_browser.live_adapter_browser_start_authorization_fixtures --repo-root C:\\dev\\patchops --json --compact",
            "py -m pytest -q tests/test_l3_03_browser_start_authorization_fixture_matrix_current.py",
        ],
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "L3.3 Browser Start Authorization Fixture Matrix",
        "------------------------------------------------",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        f"Browser    : started={payload.get('browser_started')}",
        f"ProfileDir : created={payload.get('profile_directory_created')}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Next patch : {payload.get('next_patch')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read back the passive L3.3 browser-start authorization fixture matrix.")
    parser.add_argument("--repo-root", default=None, help="PatchOps repository root. Defaults to the current module's repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of operator text.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when --json is used.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or []))
    payload = build_l3_browser_start_authorization_fixture_matrix(args.repo_root)
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
