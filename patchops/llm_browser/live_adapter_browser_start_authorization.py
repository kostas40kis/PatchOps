from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

NAME = "llm_browser_live_adapter_browser_start_authorization"
PHASE = "L3"
PATCH = "L3.1"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NEXT_PATCH = "L3.2 Live adapter explicit browser-start authorization CLI/readback"

SUPPORTED_BROWSERS: tuple[str, ...] = ("edge", "opera")
FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "playwright",
    "pyppeteer",
)
LIVE_SIDE_EFFECT_OPERATIONS: tuple[str, ...] = (
    "start_browser",
    "create_browser_session",
    "create_profile_directory",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
)
REQUIRED_ACKNOWLEDGEMENTS: tuple[str, ...] = (
    "ack_manual_login_required",
    "ack_dedicated_profile_required",
    "ack_no_download_click",
    "ack_no_composer_paste",
    "ack_no_send_or_submit",
    "ack_patchops_remains_source_of_truth",
)
PASSIVE_READBACK_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_start_authorization --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_authorization --repo-root C:\\dev\\patchops",
)
FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "llm-browser open",
    "open --browser",
    "run-once",
    "watch-downloads",
    "click_download",
    "paste_to_composer",
    "send_or_submit",
)


@dataclass(frozen=True)
class BrowserStartAuthorizationRequest:
    requested_browser: str = "edge"
    requested_profile_mode: str = "dedicated"
    requested_profile_name: str = "patchops_llm_browser"
    allow_browser_start: bool = False
    allow_profile_directory_creation: bool = False
    allow_live_driver_session: bool = False
    ack_manual_login_required: bool = False
    ack_dedicated_profile_required: bool = False
    ack_no_download_click: bool = False
    ack_no_composer_paste: bool = False
    ack_no_send_or_submit: bool = False
    ack_patchops_remains_source_of_truth: bool = False
    requested_side_effects: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BrowserStartAuthorizationDecision:
    ok: bool
    status: str
    patch: str
    next_patch: str
    requested_browser: str
    startup_authorized: bool
    authorization_state: str
    invalid_fields: tuple[str, ...]
    missing_acknowledgements: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    side_effects_requested: tuple[str, ...]
    side_effects_performed: tuple[str, ...]
    filesystem_writes_performed: tuple[str, ...]
    browser_started: bool
    browser_session_created: bool
    profile_directory_created: bool
    selenium_imported: bool
    optional_browser_dependencies_required: bool
    command_plan: tuple[str, ...]

    def to_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["phase"] = PHASE
        payload["name"] = NAME
        payload["supported_browsers"] = list(SUPPORTED_BROWSERS)
        payload["required_acknowledgements"] = list(REQUIRED_ACKNOWLEDGEMENTS)
        return payload


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root:
        candidate = Path(repo_root)
        if str(candidate) == ".":
            return Path.cwd().resolve()
        return candidate.resolve()
    return _repo_root_from_here()


def _new_forbidden_imports(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(set(found))


def _loaded_forbidden_imports() -> list[str]:
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in sys.modules):
            found.append(root)
    return sorted(set(found))


def _request_to_mapping(request: BrowserStartAuthorizationRequest | Mapping[str, Any] | None) -> Mapping[str, Any]:
    if request is None:
        return asdict(BrowserStartAuthorizationRequest())
    if isinstance(request, BrowserStartAuthorizationRequest):
        return asdict(request)
    return dict(request)


def _bool_field(data: Mapping[str, Any], name: str) -> bool:
    return bool(data.get(name) is True)


def _string_field(data: Mapping[str, Any], name: str, default: str) -> str:
    value = data.get(name, default)
    return str(value).strip() if value is not None else default


def _tuple_field(data: Mapping[str, Any], name: str) -> tuple[str, ...]:
    value = data.get(name, ())
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence):
        return tuple(str(item) for item in value)
    return ()


def build_browser_start_authorization_request(
    *,
    browser: str = "edge",
    profile_name: str = "patchops_llm_browser",
    allow_browser_start: bool = False,
    allow_profile_directory_creation: bool = False,
    allow_live_driver_session: bool = False,
    ack_all: bool = False,
    requested_side_effects: Sequence[str] = (),
) -> BrowserStartAuthorizationRequest:
    acknowledgements = {name: bool(ack_all) for name in REQUIRED_ACKNOWLEDGEMENTS}
    return BrowserStartAuthorizationRequest(
        requested_browser=browser,
        requested_profile_name=profile_name,
        allow_browser_start=bool(allow_browser_start),
        allow_profile_directory_creation=bool(allow_profile_directory_creation),
        allow_live_driver_session=bool(allow_live_driver_session),
        requested_side_effects=tuple(str(item) for item in requested_side_effects),
        **acknowledgements,
    )


def evaluate_browser_start_authorization(
    request: BrowserStartAuthorizationRequest | Mapping[str, Any] | None = None,
    *,
    repo_root: str | Path | None = None,
) -> BrowserStartAuthorizationDecision:
    del repo_root  # Kept for stable call shape; this passive patch does not inspect or write paths.
    before_modules = set(sys.modules)
    data = _request_to_mapping(request)
    requested_browser = _string_field(data, "requested_browser", "edge").lower()
    requested_profile_mode = _string_field(data, "requested_profile_mode", "dedicated").lower()
    requested_side_effects = _tuple_field(data, "requested_side_effects")

    invalid_fields: list[str] = []
    blocked_reasons: list[str] = []

    if requested_browser not in SUPPORTED_BROWSERS:
        invalid_fields.append("requested_browser")
        blocked_reasons.append("unsupported_browser")

    if requested_profile_mode != "dedicated":
        invalid_fields.append("requested_profile_mode")
        blocked_reasons.append("default_or_shared_profile_not_allowed")

    missing_acknowledgements = tuple(
        name for name in REQUIRED_ACKNOWLEDGEMENTS if not _bool_field(data, name)
    )
    if missing_acknowledgements:
        blocked_reasons.append("missing_acknowledgements")

    if not _bool_field(data, "allow_browser_start"):
        blocked_reasons.append("browser_start_flag_not_enabled")
    if not _bool_field(data, "allow_profile_directory_creation"):
        blocked_reasons.append("profile_directory_creation_flag_not_enabled")
    if not _bool_field(data, "allow_live_driver_session"):
        blocked_reasons.append("live_driver_session_flag_not_enabled")

    forbidden_requested = tuple(
        item for item in requested_side_effects if item in LIVE_SIDE_EFFECT_OPERATIONS
    )
    if forbidden_requested:
        blocked_reasons.append("live_side_effects_requested_but_modelled_only")

    newly_loaded_forbidden = _new_forbidden_imports(before_modules)
    loaded_forbidden = _loaded_forbidden_imports()
    if newly_loaded_forbidden:
        blocked_reasons.append("forbidden_optional_dependency_imported")

    startup_authorized = False
    authorization_state = "blocked_model_only"
    ok = (
        invalid_fields == []
        and set(newly_loaded_forbidden) == set()
        and startup_authorized is False
    )

    return BrowserStartAuthorizationDecision(
        ok=ok,
        status=STATUS_PASS if ok else STATUS_FAIL,
        patch=PATCH,
        next_patch=NEXT_PATCH,
        requested_browser=requested_browser,
        startup_authorized=startup_authorized,
        authorization_state=authorization_state,
        invalid_fields=tuple(sorted(set(invalid_fields))),
        missing_acknowledgements=missing_acknowledgements,
        blocked_reasons=tuple(dict.fromkeys(blocked_reasons)),
        side_effects_requested=requested_side_effects,
        side_effects_performed=(),
        filesystem_writes_performed=(),
        browser_started=False,
        browser_session_created=False,
        profile_directory_created=False,
        selenium_imported=("selenium" in loaded_forbidden or "selenium" in newly_loaded_forbidden),
        optional_browser_dependencies_required=False,
        command_plan=PASSIVE_READBACK_COMMANDS,
    )


def build_l3_browser_start_authorization_contract(repo_root: str | Path | None = None) -> Dict[str, Any]:
    root = resolve_repo_root(repo_root)
    default_decision = evaluate_browser_start_authorization(
        build_browser_start_authorization_request(browser="edge"),
        repo_root=root,
    )
    acknowledged_decision = evaluate_browser_start_authorization(
        build_browser_start_authorization_request(
            browser="opera",
            ack_all=True,
            allow_browser_start=True,
            allow_profile_directory_creation=True,
            allow_live_driver_session=True,
            requested_side_effects=("start_browser", "create_profile_directory", "create_browser_session"),
        ),
        repo_root=root,
    )
    invalid_decision = evaluate_browser_start_authorization(
        build_browser_start_authorization_request(browser="firefox", ack_all=True),
        repo_root=root,
    )

    decisions = (
        default_decision.to_payload(),
        acknowledged_decision.to_payload(),
        invalid_decision.to_payload(),
    )
    command_plan_passive = not any(
        fragment in "\n".join(PASSIVE_READBACK_COMMANDS).lower()
        for fragment in FORBIDDEN_COMMAND_FRAGMENTS
    )
    no_side_effects = all(
        item.get("startup_authorized") is False
        and item.get("browser_started") is False
        and item.get("browser_session_created") is False
        and item.get("profile_directory_created") is False
        and item.get("side_effects_performed") == ()
        and item.get("filesystem_writes_performed") == ()
        for item in decisions
    )
    # Tuples from dataclasses become tuples here; json.dumps below proves they are still serializable.
    payload: Dict[str, Any] = {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if (command_plan_passive and no_side_effects and default_decision.ok and not invalid_decision.ok) else STATUS_FAIL,
        "ok": bool(command_plan_passive and no_side_effects and default_decision.ok and not invalid_decision.ok),
        "next_patch": NEXT_PATCH,
        "repo_root": str(root),
        "supported_browsers": list(SUPPORTED_BROWSERS),
        "required_acknowledgements": list(REQUIRED_ACKNOWLEDGEMENTS),
        "command_plan": list(PASSIVE_READBACK_COMMANDS),
        "command_plan_passive": command_plan_passive,
        "startup_authorized": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "side_effects_performed": [],
        "filesystem_writes_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": "selenium" in _loaded_forbidden_imports(),
        "decisions": decisions,
        "checks": [
            {"name": "default_request_safely_blocked", "ok": default_decision.ok, "status": default_decision.status},
            {"name": "acknowledged_request_still_modelled_only", "ok": acknowledged_decision.ok, "status": acknowledged_decision.status},
            {"name": "invalid_browser_rejected", "ok": not invalid_decision.ok and "requested_browser" in invalid_decision.invalid_fields, "status": STATUS_PASS if "requested_browser" in invalid_decision.invalid_fields else STATUS_FAIL},
            {"name": "command_plan_passive", "ok": command_plan_passive, "status": STATUS_PASS if command_plan_passive else STATUS_FAIL},
            {"name": "no_side_effects_performed", "ok": no_side_effects, "status": STATUS_PASS if no_side_effects else STATUS_FAIL},
        ],
    }
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "L3.1 Browser Start Authorization Contract",
        "-----------------------------------------",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Startup    : authorized={payload.get('startup_authorized')}",
        "Browser    : not started" if payload.get("browser_started") is False else "Browser    : started",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Next patch : {payload.get('next_patch')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read back the passive L3.1 browser-start authorization contract.")
    parser.add_argument("--repo-root", default=None, help="PatchOps repository root. Defaults to the current module's repository root.")
    parser.add_argument("--browser", default="edge", choices=SUPPORTED_BROWSERS, help="Requested browser to model.")
    parser.add_argument("--ack-all", action="store_true", help="Model all required acknowledgements as present.")
    parser.add_argument("--allow-browser-start", action="store_true", help="Model explicit browser-start permission. L3.1 still does not execute it.")
    parser.add_argument("--allow-profile-directory-creation", action="store_true", help="Model explicit profile-directory permission. L3.1 still does not execute it.")
    parser.add_argument("--allow-live-driver-session", action="store_true", help="Model explicit live-driver-session permission. L3.1 still does not execute it.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of operator text.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when --json is used.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or []))
    payload = build_l3_browser_start_authorization_contract(args.repo_root)
    modelled_request = build_browser_start_authorization_request(
        browser=args.browser,
        ack_all=args.ack_all,
        allow_browser_start=args.allow_browser_start,
        allow_profile_directory_creation=args.allow_profile_directory_creation,
        allow_live_driver_session=args.allow_live_driver_session,
        requested_side_effects=(
            ("start_browser", "create_profile_directory", "create_browser_session")
            if (args.allow_browser_start or args.allow_profile_directory_creation or args.allow_live_driver_session)
            else ()
        ),
    )
    payload["requested_decision"] = evaluate_browser_start_authorization(modelled_request, repo_root=args.repo_root).to_payload()

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
