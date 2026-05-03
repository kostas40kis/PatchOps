
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from . import live_adapter_startup_request_l1_final_acceptance_marker as l1_marker

NAME = "llm_browser_live_adapter_browser_profile_preflight"
PHASE = "L2"
PATCH = "L2.1"
NEXT_PATCH = "L2.2 Live adapter browser profile preflight CLI/readback"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_BLOCKED = "BLOCKED_PREFLIGHT_CONTRACT_ONLY"
SUPPORTED_BROWSERS: tuple[str, ...] = ("edge", "opera")
REQUIRED_ACKNOWLEDGEMENTS: tuple[str, ...] = (
    "operator_confirms_dedicated_browser_profile",
    "operator_confirms_manual_login_only",
    "operator_confirms_no_auto_send",
    "operator_confirms_visible_artifact_only",
    "operator_confirms_patchops_remains_source_of_truth",
)
SIDE_EFFECT_OPERATIONS: tuple[str, ...] = (
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
)
FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
)


@dataclass(frozen=True)
class BrowserProfilePreflightRequest:
    requested_browser: str = "edge"
    profile_mode: str = "dedicated"
    profile_root: str = ""
    profile_name: str = "patchops-llm-browser"
    acknowledgements: tuple[str, ...] = field(default_factory=tuple)
    allow_browser_start: bool = False
    allow_profile_directory_creation: bool = False
    allow_optional_browser_dependencies: bool = False
    manual_login_required: bool = True
    dedicated_profile_required: bool = True
    operator_note: str = "passive browser profile preflight contract"

    def normalized_browser(self) -> str:
        return str(self.requested_browser or "").strip().lower()

    def missing_acknowledgements(self) -> list[str]:
        present = set(self.acknowledgements)
        return [name for name in REQUIRED_ACKNOWLEDGEMENTS if name not in present]

    def invalid_fields(self) -> list[str]:
        invalid: list[str] = []
        if self.normalized_browser() not in SUPPORTED_BROWSERS:
            invalid.append("requested_browser")
        if self.profile_mode != "dedicated":
            invalid.append("profile_mode")
        if not self.manual_login_required:
            invalid.append("manual_login_required")
        if not self.dedicated_profile_required:
            invalid.append("dedicated_profile_required")
        return invalid

    def requested_side_effects(self) -> list[str]:
        effects: list[str] = []
        if self.allow_browser_start:
            effects.append("start_browser")
        if self.allow_profile_directory_creation:
            effects.append("create_profile_directory")
        return effects

    def as_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["acknowledgements"] = list(self.acknowledgements)
        payload["requested_browser"] = self.requested_browser
        payload["normalized_browser"] = self.normalized_browser()
        payload["supported_browsers"] = list(SUPPORTED_BROWSERS)
        payload["required_acknowledgements"] = list(REQUIRED_ACKNOWLEDGEMENTS)
        payload["missing_acknowledgements"] = self.missing_acknowledgements()
        payload["invalid_fields"] = self.invalid_fields()
        payload["requested_side_effects"] = self.requested_side_effects()
        payload["side_effects_performed"] = []
        payload["filesystem_writes_performed"] = []
        payload["browser_started"] = False
        payload["browser_session_created"] = False
        payload["startup_allowed"] = False
        payload["profile_directory_created"] = False
        payload["optional_browser_dependencies_required"] = False
        payload["phase"] = PHASE
        payload["patch"] = PATCH
        payload["name"] = NAME
        return payload


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _payload_ok(payload: Mapping[str, Any]) -> bool:
    return bool(payload.get("ok") is True and str(payload.get("status")) == STATUS_PASS)


def _forbidden_imports_present() -> list[str]:
    present: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in sys.modules):
            present.append(root)
    return sorted(present)


def _new_forbidden_imports(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(found)


def _checks_are_json_native(checks: Iterable[Mapping[str, Any]]) -> bool:
    try:
        json.dumps(list(checks), sort_keys=True)
        return True
    except TypeError:
        return False


def default_profile_root(repo_root: str | Path | None = None) -> str:
    root = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()
    return str(root / "data" / "runtime" / "llm_browser_profiles")


def build_browser_profile_preflight_request(
    repo_root: str | Path | None = None,
    requested_browser: str = "edge",
    profile_root: str | Path | None = None,
    profile_name: str = "patchops-llm-browser",
    acknowledgements: Sequence[str] | None = None,
    allow_browser_start: bool = False,
    allow_profile_directory_creation: bool = False,
    allow_optional_browser_dependencies: bool = False,
    operator_note: str = "passive browser profile preflight contract",
) -> BrowserProfilePreflightRequest:
    resolved_profile_root = str(Path(profile_root).resolve()) if profile_root is not None else default_profile_root(repo_root)
    return BrowserProfilePreflightRequest(
        requested_browser=requested_browser,
        profile_root=resolved_profile_root,
        profile_name=profile_name,
        acknowledgements=tuple(acknowledgements or ()),
        allow_browser_start=bool(allow_browser_start),
        allow_profile_directory_creation=bool(allow_profile_directory_creation),
        allow_optional_browser_dependencies=bool(allow_optional_browser_dependencies),
        operator_note=operator_note,
    )


def build_default_browser_profile_preflight(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return evaluate_browser_profile_preflight(build_browser_profile_preflight_request(repo_root), repo_root)


def build_fully_acknowledged_browser_profile_preflight(repo_root: str | Path | None = None) -> Dict[str, Any]:
    request = build_browser_profile_preflight_request(repo_root, acknowledgements=REQUIRED_ACKNOWLEDGEMENTS)
    return evaluate_browser_profile_preflight(request, repo_root)


def evaluate_browser_profile_preflight(
    request: BrowserProfilePreflightRequest | Mapping[str, Any] | None = None,
    repo_root: str | Path | None = None,
) -> Dict[str, Any]:
    root = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()
    before_modules = set(sys.modules)

    if request is None:
        preflight_request = build_browser_profile_preflight_request(root)
    elif isinstance(request, BrowserProfilePreflightRequest):
        preflight_request = request
    else:
        preflight_request = build_browser_profile_preflight_request(
            root,
            requested_browser=str(request.get("requested_browser", "edge")),
            profile_root=request.get("profile_root"),
            profile_name=str(request.get("profile_name", "patchops-llm-browser")),
            acknowledgements=_as_list(request.get("acknowledgements")),
            allow_browser_start=bool(request.get("allow_browser_start", False)),
            allow_profile_directory_creation=bool(request.get("allow_profile_directory_creation", False)),
            allow_optional_browser_dependencies=bool(request.get("allow_optional_browser_dependencies", False)),
            operator_note=str(request.get("operator_note", "passive browser profile preflight contract")),
        )

    request_payload = preflight_request.as_payload()
    invalid_fields = _as_list(request_payload.get("invalid_fields"))
    missing_acknowledgements = _as_list(request_payload.get("missing_acknowledgements"))
    requested_side_effects = _as_list(request_payload.get("requested_side_effects"))

    l1_payload = l1_marker.build_l1_final_acceptance_marker(root)
    forbidden_imports_present = _forbidden_imports_present()
    newly_loaded_forbidden = _new_forbidden_imports(before_modules)

    profile_root = Path(str(request_payload.get("profile_root")))
    profile_path = profile_root / str(request_payload.get("profile_name")) / str(request_payload.get("normalized_browser"))

    browser_started = False
    browser_session_created = False
    profile_directory_created = False
    startup_allowed = False
    side_effects_performed: list[str] = []
    filesystem_writes_performed: list[str] = []

    checks: list[Dict[str, Any]] = [
        _check("l1_final_acceptance_marker_still_passes", _payload_ok(l1_payload), {"patch": l1_payload.get("patch"), "status": l1_payload.get("status")}),
        _check("l2_profile_preflight_models_supported_browsers", request_payload.get("normalized_browser") in SUPPORTED_BROWSERS, {"requested_browser": request_payload.get("requested_browser"), "supported_browsers": list(SUPPORTED_BROWSERS), "invalid_fields": invalid_fields}),
        _check("l2_profile_preflight_requires_dedicated_profile", request_payload.get("profile_mode") == "dedicated" and request_payload.get("dedicated_profile_required") is True, {"profile_mode": request_payload.get("profile_mode"), "dedicated_profile_required": request_payload.get("dedicated_profile_required")}),
        _check("l2_profile_preflight_requires_manual_login_only", request_payload.get("manual_login_required") is True, {"manual_login_required": request_payload.get("manual_login_required"), "auto_login_supported": False}),
        _check("l2_profile_preflight_models_requested_side_effects_but_executes_none", side_effects_performed == [], {"requested_side_effects": requested_side_effects, "side_effects_performed": side_effects_performed}),
        _check("l2_profile_preflight_does_not_create_profile_or_browser", profile_directory_created is False and browser_started is False and browser_session_created is False and filesystem_writes_performed == [], {"profile_directory_created": profile_directory_created, "browser_started": browser_started, "browser_session_created": browser_session_created, "filesystem_writes_performed": filesystem_writes_performed}),
        _check("l2_profile_preflight_blocks_startup", startup_allowed is False, {"startup_allowed": startup_allowed, "status": STATUS_BLOCKED}),
        _check("l2_profile_preflight_acknowledgement_contract_reported", isinstance(missing_acknowledgements, list), {"required_acknowledgement_count": len(REQUIRED_ACKNOWLEDGEMENTS), "missing_acknowledgements": missing_acknowledgements}),
        _check("l2_profile_preflight_payload_json_safe", _checks_are_json_native([request_payload]), {"checks_are_json_native": _checks_are_json_native([request_payload])}),
        _check("no_optional_browser_dependency_imports", forbidden_imports_present == [], {"forbidden_import_roots_present": forbidden_imports_present}),
        _check("l2_profile_preflight_did_not_load_browser_optional_modules", newly_loaded_forbidden == [], {"newly_loaded_forbidden_modules": newly_loaded_forbidden}),
    ]

    ok = all(check["ok"] is True for check in checks)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "next_patch": NEXT_PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "request_status": STATUS_BLOCKED,
        "ok": ok,
        "side_effect_boundary": "passive-only",
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "side_effects_performed": side_effects_performed,
        "filesystem_writes_performed": filesystem_writes_performed,
        "startup_allowed": startup_allowed,
        "browser_started": browser_started,
        "browser_session_created": browser_session_created,
        "profile_directory_created": profile_directory_created,
        "optional_browser_dependencies_required": False,
        "supported_browsers": list(SUPPORTED_BROWSERS),
        "requested_browser": request_payload.get("requested_browser"),
        "normalized_browser": request_payload.get("normalized_browser"),
        "profile_mode": request_payload.get("profile_mode"),
        "profile_root": str(profile_root),
        "profile_path": str(profile_path),
        "profile_name": request_payload.get("profile_name"),
        "manual_login_required": True,
        "dedicated_profile_required": True,
        "required_acknowledgements": list(REQUIRED_ACKNOWLEDGEMENTS),
        "missing_acknowledgements": missing_acknowledgements,
        "invalid_fields": invalid_fields,
        "requested_side_effects": requested_side_effects,
        "request": request_payload,
        "l1_final_acceptance_marker": l1_payload,
        "checks": checks,
    }


def build_profile_preflight_contract(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_default_browser_profile_preflight(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser profile preflight contract",
        "PatchOps LLM browser live adapter browser profile preflight contract",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Request    : {payload.get('request_status')}",
        f"Browser    : {payload.get('normalized_browser')}",
        f"Profile    : mode={payload.get('profile_mode')} created={str(payload.get('profile_directory_created')).lower()}",
        f"Startup    : allowed={str(payload.get('startup_allowed')).lower()}",
        "BrowserRun : not started" if not payload.get("browser_started") else "BrowserRun : started",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        f"ManualLogin: required={str(payload.get('manual_login_required')).lower()}",
        "Checks:",
    ]
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L2 browser-profile preflight contract for the live adapter.")
    parser.add_argument("--repo-root", default=str(_repo_root_from_here()))
    parser.add_argument("--browser", default="edge", choices=SUPPORTED_BROWSERS)
    parser.add_argument("--profile-root", default=None)
    parser.add_argument("--profile-name", default="patchops-llm-browser")
    parser.add_argument("--ack-all", action="store_true", help="Model all required acknowledgements without enabling startup.")
    parser.add_argument("--allow-browser-start", action="store_true", help="Model a browser-start request; L2.1 still blocks it.")
    parser.add_argument("--allow-profile-directory-creation", action="store_true", help="Model profile directory creation; L2.1 still performs no writes.")
    parser.add_argument("--allow-optional-browser-dependencies", action="store_true", help="Model optional dependency request; L2.1 still imports none.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    acknowledgements = REQUIRED_ACKNOWLEDGEMENTS if args.ack_all else ()
    request = build_browser_profile_preflight_request(
        args.repo_root,
        requested_browser=args.browser,
        profile_root=args.profile_root,
        profile_name=args.profile_name,
        acknowledgements=acknowledgements,
        allow_browser_start=args.allow_browser_start,
        allow_profile_directory_creation=args.allow_profile_directory_creation,
        allow_optional_browser_dependencies=args.allow_optional_browser_dependencies,
    )
    payload = evaluate_browser_profile_preflight(request, args.repo_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
