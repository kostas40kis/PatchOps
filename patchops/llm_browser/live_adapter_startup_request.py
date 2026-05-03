"""Passive startup request model for the PatchOps LLM browser live adapter.

L1.x models startup requests only. It performs no Selenium import, browser
startup, click, download, paste, send, or PatchOps package run.
"""
from __future__ import annotations

import argparse
import json
from typing import Iterable, Sequence

NAME = "llm_browser_live_adapter_startup_decision_request_model"
PHASE = "L1"
LEGACY_PATCH = "L1.6"
PATCH = "L1.7"
STATUS = "PASSIVE_STARTUP_REQUEST_MODEL"
NEXT_PATCH = "L1.8 Live adapter startup request contract gate"
LEGACY_NEXT_PATCH = "L1.7 Live adapter startup request CLI flags"

ALLOWED_BROWSERS = ("edge", "opera")
REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS = (
    "operator_confirms_dedicated_browser_profile",
    "operator_confirms_manual_login_only",
    "operator_confirms_no_auto_send",
    "operator_confirms_visible_artifact_only",
    "operator_confirms_patchops_remains_source_of_truth",
)
SIDE_EFFECT_OPERATIONS = (
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
)
FORBIDDEN_IMPORT_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil")


class CallableTuple(tuple):
    """Tuple that also works as a zero-argument compatibility method."""
    def __new__(cls, values: Iterable[str] = ()):  # type: ignore[override]
        return super().__new__(cls, tuple(values or ()))

    def __call__(self) -> tuple[str, ...]:
        return tuple(self)


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values or ():
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return tuple(out)


class StartupDecisionRequest:
    """JSON-safe passive startup request with tuple/callable compat surfaces."""
    def __init__(
        self,
        requested_browser: str = "edge",
        *,
        browser: str | None = None,
        acknowledgements: Iterable[str] = (),
        requested_operations: Iterable[str] = (),
        allow_browser_start: bool = False,
        allow_optional_browser_dependencies: bool = False,
        allow_click_download: bool = False,
        allow_run_patchops_package: bool = False,
        allow_paste_to_composer: bool = False,
        allow_send_or_submit: bool = False,
        operator_note: str = "",
    ) -> None:
        self.requested_browser = str(browser if browser is not None else requested_browser or "edge")
        self.acknowledgements = CallableTuple(_unique(acknowledgements))
        self.requested_operations = CallableTuple(_unique(requested_operations))
        self.allow_browser_start = bool(allow_browser_start)
        self.allow_optional_browser_dependencies = bool(allow_optional_browser_dependencies)
        self.allow_click_download = bool(allow_click_download)
        self.allow_run_patchops_package = bool(allow_run_patchops_package)
        self.allow_paste_to_composer = bool(allow_paste_to_composer)
        self.allow_send_or_submit = bool(allow_send_or_submit)
        self.operator_note = str(operator_note or "")
        self.browser_started = False
        self.browser_session_created = False
        self.side_effects_performed = CallableTuple(())
        self.optional_browser_dependencies_required = False

    def normalized_browser(self) -> str:
        return str(self.requested_browser or "edge").strip().lower()

    @property
    def missing_acknowledgements(self) -> CallableTuple:
        supplied = set(self.acknowledgements)
        return CallableTuple(item for item in REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS if item not in supplied)

    @property
    def requested_side_effects(self) -> CallableTuple:
        requested = list(self.requested_operations)
        if self.allow_browser_start:
            requested.append("start_browser")
        if self.allow_click_download:
            requested.append("click_download")
        if self.allow_run_patchops_package:
            requested.append("run_patchops_package")
        if self.allow_paste_to_composer:
            requested.append("paste_to_composer")
        if self.allow_send_or_submit:
            requested.append("send_or_submit")
        return CallableTuple(item for item in _unique(requested) if item in SIDE_EFFECT_OPERATIONS)

    def to_payload(self) -> dict[str, object]:
        return {
            "name": NAME,
            "phase": PHASE,
            "patch": PATCH,
            "requested_browser": self.normalized_browser(),
            "allowed_browsers": list(ALLOWED_BROWSERS),
            "acknowledgements": list(self.acknowledgements),
            "missing_acknowledgements": list(self.missing_acknowledgements),
            "requested_operations": list(self.requested_operations),
            "requested_side_effects": list(self.requested_side_effects),
            "allow_browser_start": self.allow_browser_start,
            "allow_optional_browser_dependencies": self.allow_optional_browser_dependencies,
            "allow_click_download": self.allow_click_download,
            "allow_run_patchops_package": self.allow_run_patchops_package,
            "allow_paste_to_composer": self.allow_paste_to_composer,
            "allow_send_or_submit": self.allow_send_or_submit,
            "operator_note": self.operator_note,
            "browser_started": False,
            "browser_session_created": False,
            "optional_browser_dependencies_required": False,
            "side_effects_performed": [],
        }

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "StartupDecisionRequest":
        return cls(
            requested_browser=str(payload.get("requested_browser") or payload.get("browser") or "edge"),
            acknowledgements=tuple(payload.get("acknowledgements") or ()),  # type: ignore[arg-type]
            requested_operations=tuple(payload.get("requested_operations") or ()),  # type: ignore[arg-type]
            allow_browser_start=bool(payload.get("allow_browser_start", False)),
            allow_optional_browser_dependencies=bool(payload.get("allow_optional_browser_dependencies", False)),
            allow_click_download=bool(payload.get("allow_click_download", False)),
            allow_run_patchops_package=bool(payload.get("allow_run_patchops_package", False)),
            allow_paste_to_composer=bool(payload.get("allow_paste_to_composer", False)),
            allow_send_or_submit=bool(payload.get("allow_send_or_submit", False)),
            operator_note=str(payload.get("operator_note") or ""),
        )


LiveAdapterStartupRequest = StartupDecisionRequest


class StartupDecision:
    def __init__(self, request: StartupDecisionRequest) -> None:
        self.request = request
        self.invalid_fields = CallableTuple(("requested_browser",) if request.normalized_browser() not in ALLOWED_BROWSERS else ())
        blockers = [
            "l1_6_request_model_does_not_start_browsers",
            "l1_7_request_cli_flags_do_not_start_browsers",
            "live_browser_startup_requires_a_later_explicit_phase",
            "selenium_dependency_boundary_is_not_enabled_here",
        ]
        if request.requested_side_effects:
            blockers.append("requested_side_effects_are_not_enabled_in_l1")
        if request.allow_optional_browser_dependencies:
            blockers.append("optional_browser_dependencies_remain_disabled_in_l1_6")
            blockers.append("optional_browser_dependencies_remain_disabled_in_l1_7")
        if self.invalid_fields:
            blockers.append("invalid_startup_request_fields")
            blockers.append("startup_request_has_invalid_fields")
        self.blockers = CallableTuple(_unique(blockers))

    def to_payload(self) -> dict[str, object]:
        return {
            "name": NAME,
            "phase": PHASE,
            "patch": PATCH,
            "status": "BLOCKED_REQUEST_MODEL_ONLY",
            "ok": True,
            "startup_allowed": False,
            "browser_started": False,
            "browser_session_created": False,
            "optional_browser_dependencies_required": False,
            "requested_browser": self.request.normalized_browser(),
            "missing_acknowledgements": list(self.request.missing_acknowledgements),
            "requested_side_effects": list(self.request.requested_side_effects),
            "side_effects_performed": [],
            "required_explicit_acknowledgements": list(REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS),
            "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
            "forbidden_import_roots": list(FORBIDDEN_IMPORT_ROOTS),
            "invalid_fields": list(self.invalid_fields),
            "blockers": list(self.blockers),
            "reason": "L1 only models startup requests. Browser startup remains blocked; a later live-browser phase must wire implementation and safety checks.",
            "request": self.request.to_payload(),
            "next_patch": NEXT_PATCH,
        }


def build_startup_request(
    browser: str | None = None,
    *,
    requested_browser: str | None = None,
    acknowledgements: Iterable[str] = (),
    requested_operations: Iterable[str] = (),
    allow_browser_start: bool = False,
    allow_optional_browser_dependencies: bool = False,
    allow_click_download: bool = False,
    allow_run_patchops_package: bool = False,
    allow_paste_to_composer: bool = False,
    allow_send_or_submit: bool = False,
    operator_note: str = "",
) -> StartupDecisionRequest:
    return StartupDecisionRequest(
        requested_browser=requested_browser or browser or "edge",
        acknowledgements=acknowledgements,
        requested_operations=requested_operations,
        allow_browser_start=allow_browser_start,
        allow_optional_browser_dependencies=allow_optional_browser_dependencies,
        allow_click_download=allow_click_download,
        allow_run_patchops_package=allow_run_patchops_package,
        allow_paste_to_composer=allow_paste_to_composer,
        allow_send_or_submit=allow_send_or_submit,
        operator_note=operator_note,
    )


def build_default_request() -> StartupDecisionRequest:
    return build_startup_request()


def build_fully_acknowledged_startup_request(**kwargs: object) -> StartupDecisionRequest:
    acknowledgements = kwargs.pop("acknowledgements", REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS)
    if "allow_browser_start" not in kwargs:
        kwargs["allow_browser_start"] = True
    if "allow_optional_browser_dependencies" not in kwargs:
        kwargs["allow_optional_browser_dependencies"] = True
    if "requested_operations" not in kwargs:
        kwargs["requested_operations"] = ("start_browser",)
    return build_startup_request(acknowledgements=acknowledgements, **kwargs)  # type: ignore[arg-type]


def evaluate_startup_request(request: StartupDecisionRequest | None = None) -> StartupDecision:
    return StartupDecision(request or build_default_request())


def decide_startup_request(request: StartupDecisionRequest | None = None) -> StartupDecision:
    return evaluate_startup_request(request)


def _base_readback(*, patch: str, next_patch: str) -> dict[str, object]:
    default_request = build_default_request()
    fully_acknowledged_request = build_fully_acknowledged_startup_request()
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": patch,
        "status": STATUS,
        "ok": True,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "optional_browser_dependencies_required": False,
        "side_effects_performed": [],
        "allowed_browsers": list(ALLOWED_BROWSERS),
        "required_explicit_acknowledgements": list(REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS),
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "forbidden_import_roots": list(FORBIDDEN_IMPORT_ROOTS),
        "default_decision": evaluate_startup_request(default_request).to_payload(),
        "fully_acknowledged_decision": evaluate_startup_request(fully_acknowledged_request).to_payload(),
        "next_patch": next_patch,
    }


def build_request_model_readback() -> dict[str, object]:
    return _base_readback(patch=LEGACY_PATCH, next_patch=LEGACY_NEXT_PATCH)


def build_startup_request_readback(request: StartupDecisionRequest | None = None) -> dict[str, object]:
    payload = _base_readback(patch=PATCH, next_patch=NEXT_PATCH)
    requested_request = request or build_fully_acknowledged_startup_request()
    requested_decision = evaluate_startup_request(requested_request).to_payload()
    payload["requested_decision"] = requested_decision
    payload["cli_request"] = requested_request.to_payload()
    payload["cli_decision"] = requested_decision
    return payload


def build_startup_request_flags_readback(request: StartupDecisionRequest | None = None) -> dict[str, object]:
    return build_startup_request_readback(request)


def build_request_from_args(args: argparse.Namespace) -> StartupDecisionRequest:
    acknowledgements = list(getattr(args, "acknowledgements", None) or ())
    if getattr(args, "acknowledge_all", False) or getattr(args, "ack_all", False):
        acknowledgements = list(REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS)
    operations = list(getattr(args, "operations", None) or ())
    operations.extend(list(getattr(args, "request_operations", None) or ()))
    operations.extend(list(getattr(args, "requested_operations", None) or ()))
    return build_startup_request(
        browser=getattr(args, "browser", None) or getattr(args, "requested_browser", None) or "edge",
        acknowledgements=acknowledgements,
        requested_operations=tuple(operations),
        allow_browser_start=bool(getattr(args, "allow_browser_start", False)),
        allow_optional_browser_dependencies=bool(getattr(args, "allow_optional_browser_dependencies", False)),
        allow_click_download=bool(getattr(args, "allow_click_download", False)),
        allow_run_patchops_package=bool(getattr(args, "allow_run_patchops_package", False)),
        allow_paste_to_composer=bool(getattr(args, "allow_paste_to_composer", False)),
        allow_send_or_submit=bool(getattr(args, "allow_send_or_submit", False)),
        operator_note=str(getattr(args, "operator_note", "") or ""),
    )


def startup_request_from_args(args: argparse.Namespace) -> StartupDecisionRequest:
    return build_request_from_args(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchops llm-browser startup-request")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--browser", default="edge")
    parser.add_argument("--operation", dest="operations", action="append", default=[])
    parser.add_argument("--request-operation", dest="operations", action="append")
    parser.add_argument("--acknowledge", dest="acknowledgements", action="append", default=[])
    parser.add_argument("--ack", dest="acknowledgements", action="append")
    parser.add_argument("--acknowledge-all", dest="acknowledge_all", action="store_true")
    parser.add_argument("--ack-all", dest="acknowledge_all", action="store_true")
    parser.add_argument("--allow-browser-start", action="store_true")
    parser.add_argument("--allow-optional-browser-dependencies", action="store_true")
    parser.add_argument("--allow-click-download", action="store_true")
    parser.add_argument("--allow-run-patchops-package", action="store_true")
    parser.add_argument("--allow-paste-to-composer", action="store_true")
    parser.add_argument("--allow-send-or-submit", action="store_true")
    parser.add_argument("--operator-note", default="")
    return parser


def render_startup_request_text(payload: dict[str, object] | None = None) -> str:
    payload = payload or build_startup_request_readback()
    lines = [
        "PatchOps LLM browser live adapter startup request flags",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Startup    : allowed={payload.get('startup_allowed')}",
        "Browser    : not started",
        f"SideEffects: {payload.get('side_effects_performed')}",
        "Required acknowledgements:",
    ]
    for item in payload.get("required_explicit_acknowledgements", []) or []:  # type: ignore[assignment]
        lines.append(f"- {item}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def render_startup_request_readback(payload: dict[str, object] | None = None) -> str:
    return render_startup_request_text(payload)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    request = build_request_from_args(args)
    payload = build_startup_request_readback(request)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_startup_request_text(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
