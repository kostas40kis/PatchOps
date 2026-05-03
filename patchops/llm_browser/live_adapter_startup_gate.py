"""Explicit startup gate scaffold for the PatchOps LLM browser live adapter.

L1.4 is still a no-side-effect scaffold. It defines the startup decision contract
that a later live-browser phase must satisfy before any browser session can be
created. This module deliberately does not import Selenium, webdriver-manager,
psutil, pyperclip, or browser drivers.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from . import live_adapter

GATE_NAME = "llm_browser_live_adapter_explicit_startup_gate_scaffold"
GATE_PHASE = "L1"
GATE_PATCH = "L1.4"
GATE_STATUS = "PASSIVE_STARTUP_GATE_SCAFFOLD"
DECISION_STATUS_BLOCKED = "BLOCKED_SCAFFOLD_ONLY"
NEXT_PATCH = "L1.5 Live adapter startup gate CLI/readback"

FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
)

REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS: tuple[str, ...] = (
    "operator_confirms_dedicated_browser_profile",
    "operator_confirms_manual_login_only",
    "operator_confirms_no_auto_send",
    "operator_confirms_visible_artifact_only",
    "operator_confirms_patchops_remains_source_of_truth",
)

STARTUP_PHASE_BLOCKERS: tuple[str, ...] = (
    "l1_4_scaffold_does_not_start_browsers",
    "live_browser_startup_requires_a_later_explicit_phase",
    "selenium_dependency_boundary_is_not_enabled_here",
)

SIDE_EFFECT_OPERATION_NAMES: tuple[str, ...] = (
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
)


@dataclass(frozen=True)
class LiveAdapterStartupRequest:
    """Operator request shape reserved for a later live startup phase.

    Even when every acknowledgement is set to true, L1.4 still blocks startup
    because this patch only creates the passive startup gate scaffold.
    """

    browser: str = "edge"
    requested: bool = False
    operator_confirms_dedicated_browser_profile: bool = False
    operator_confirms_manual_login_only: bool = False
    operator_confirms_no_auto_send: bool = False
    operator_confirms_visible_artifact_only: bool = False
    operator_confirms_patchops_remains_source_of_truth: bool = False
    allow_start_browser: bool = False
    allow_read_page: bool = False
    allow_click_download: bool = False
    allow_patchops_run: bool = False
    allow_paste_to_composer: bool = False
    allow_send_submit: bool = False

    def acknowledgement_payload(self) -> dict[str, bool]:
        return {
            name: bool(getattr(self, name))
            for name in REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS
        }


@dataclass(frozen=True)
class LiveAdapterStartupDecision:
    """Startup gate result. Safe blocking is considered an OK gate outcome."""

    name: str
    phase: str
    patch: str
    ok: bool
    status: str
    startup_allowed: bool
    browser_started: bool
    browser_session_created: bool
    optional_browser_dependencies_required: bool
    side_effects_performed: tuple[str, ...]
    requested_browser: str
    missing_acknowledgements: tuple[str, ...]
    blockers: tuple[str, ...]
    reason: str
    next_patch: str

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "phase": self.phase,
            "patch": self.patch,
            "ok": self.ok,
            "status": self.status,
            "startup_allowed": self.startup_allowed,
            "browser_started": self.browser_started,
            "browser_session_created": self.browser_session_created,
            "optional_browser_dependencies_required": self.optional_browser_dependencies_required,
            "side_effects_performed": list(self.side_effects_performed),
            "requested_browser": self.requested_browser,
            "missing_acknowledgements": list(self.missing_acknowledgements),
            "blockers": list(self.blockers),
            "reason": self.reason,
            "next_patch": self.next_patch,
        }


def _missing_acknowledgements(request: LiveAdapterStartupRequest) -> tuple[str, ...]:
    acknowledgements = request.acknowledgement_payload()
    return tuple(name for name in REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS if not acknowledgements.get(name))


def evaluate_startup_request(request: LiveAdapterStartupRequest | None = None) -> dict[str, object]:
    """Evaluate a future startup request without performing startup.

    L1.4 always returns ``startup_allowed=False``. It is a scaffold for the
    eventual explicit startup gate and not an implementation of browser startup.
    """

    request = request or LiveAdapterStartupRequest()
    missing = _missing_acknowledgements(request)
    reason = (
        "L1.4 is scaffold-only: browser startup remains blocked even if a request "
        "sets permissive flags. A later explicit live-browser phase must wire the "
        "actual startup implementation and its safety checks."
    )
    return LiveAdapterStartupDecision(
        name=GATE_NAME,
        phase=GATE_PHASE,
        patch=GATE_PATCH,
        ok=True,
        status=DECISION_STATUS_BLOCKED,
        startup_allowed=False,
        browser_started=False,
        browser_session_created=False,
        optional_browser_dependencies_required=False,
        side_effects_performed=(),
        requested_browser=request.browser,
        missing_acknowledgements=missing,
        blockers=STARTUP_PHASE_BLOCKERS,
        reason=reason,
        next_patch=NEXT_PATCH,
    ).to_payload()


def build_startup_gate_readback() -> dict[str, object]:
    live_payload = live_adapter.build_live_adapter_readback()
    default_decision = evaluate_startup_request()
    permissive_decision = evaluate_startup_request(
        LiveAdapterStartupRequest(
            browser="edge",
            requested=True,
            operator_confirms_dedicated_browser_profile=True,
            operator_confirms_manual_login_only=True,
            operator_confirms_no_auto_send=True,
            operator_confirms_visible_artifact_only=True,
            operator_confirms_patchops_remains_source_of_truth=True,
            allow_start_browser=True,
            allow_read_page=True,
            allow_click_download=True,
            allow_patchops_run=True,
            allow_paste_to_composer=True,
            allow_send_submit=False,
        )
    )
    return {
        "name": GATE_NAME,
        "phase": GATE_PHASE,
        "patch": GATE_PATCH,
        "status": GATE_STATUS,
        "ok": True,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "optional_browser_dependencies_required": False,
        "side_effects_performed": [],
        "required_explicit_acknowledgements": list(REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS),
        "side_effect_operations": list(SIDE_EFFECT_OPERATION_NAMES),
        "existing_live_adapter_status": live_payload.get("status"),
        "existing_live_adapter_blocked_operations": list(live_payload.get("blocked_operations", ())),
        "default_startup_decision": default_decision,
        "permissive_startup_decision": permissive_decision,
        "forbidden_import_roots": list(FORBIDDEN_IMPORT_ROOTS),
        "next_patch": NEXT_PATCH,
    }


def assert_startup_gate_safe() -> bool:
    payload = build_startup_gate_readback()
    if payload["startup_allowed"]:
        raise AssertionError("L1.4 startup gate unexpectedly allowed browser startup")
    if payload["browser_started"]:
        raise AssertionError("L1.4 startup gate unexpectedly started a browser")
    if payload["browser_session_created"]:
        raise AssertionError("L1.4 startup gate unexpectedly created a browser session")
    if payload["optional_browser_dependencies_required"]:
        raise AssertionError("L1.4 startup gate unexpectedly required browser optional dependencies")
    if payload["side_effects_performed"]:
        raise AssertionError("L1.4 startup gate unexpectedly recorded side effects")
    for key in ("default_startup_decision", "permissive_startup_decision"):
        decision = payload[key]
        if not isinstance(decision, Mapping):
            raise AssertionError(f"{key} is not a mapping")
        if decision.get("startup_allowed") is not False:
            raise AssertionError(f"{key} unexpectedly allowed startup")
        if decision.get("browser_started") is not False:
            raise AssertionError(f"{key} unexpectedly started a browser")
        if decision.get("side_effects_performed") != []:
            raise AssertionError(f"{key} unexpectedly recorded side effects")
    return True


def _render_text(payload: Mapping[str, object]) -> str:
    lines = [
        "PatchOps LLM browser live adapter startup gate scaffold",
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
    lines.extend(f"- {name}" for name in payload.get("required_explicit_acknowledgements", ()))
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m patchops.llm_browser.live_adapter_startup_gate",
        description="Read back the passive L1.4 live-adapter explicit startup gate scaffold.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON readback.")
    parser.add_argument("--compact", action="store_true", help="Use compact JSON when --json is supplied.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    # L1.4c note: do not coerce argv=None to an empty list; argparse must read sys.argv for module CLI.
    args = build_arg_parser().parse_args(argv)
    payload = build_startup_gate_readback()
    if args.json:
        print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    else:
        print(_render_text(payload), end="")
    return 0


__all__ = [
    "DECISION_STATUS_BLOCKED",
    "FORBIDDEN_IMPORT_ROOTS",
    "GATE_NAME",
    "GATE_PATCH",
    "GATE_PHASE",
    "GATE_STATUS",
    "LiveAdapterStartupDecision",
    "LiveAdapterStartupRequest",
    "NEXT_PATCH",
    "REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS",
    "SIDE_EFFECT_OPERATION_NAMES",
    "STARTUP_PHASE_BLOCKERS",
    "assert_startup_gate_safe",
    "build_startup_gate_readback",
    "evaluate_startup_request",
    "main",
]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
