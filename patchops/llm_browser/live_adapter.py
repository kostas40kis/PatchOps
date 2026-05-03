"""Passive live-adapter skeleton for the PatchOps LLM browser stream.

L1 keeps this module safe-by-default. It provides the original L1.1
no-side-effect skeleton API and the L1.2 passive CLI/readback API. It must
remain importable without Selenium or browser optional dependencies installed.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

ADAPTER_NAME = "llm_browser_live_adapter_skeleton"
ADAPTER_PHASE = "L1"
ADAPTER_PATCH = "L1.2"
ADAPTER_STATUS = "PASSIVE_READBACK_ONLY"
NEXT_PATCH = "L1.3 Live adapter passive contract gate"

BLOCKED_OPERATION_NAMES: tuple[str, ...] = (
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
)

PASSIVE_OPERATION_NAMES: tuple[str, ...] = (
    "build_live_adapter_readback",
    "live_adapter_readback_json",
    "assert_live_adapter_skeleton_safe",
    "create_live_adapter_skeleton",
    "main",
)


class LiveAdapterStatus(str, Enum):
    """Stable result states for the L1 live-adapter skeleton."""

    BLOCKED = "BLOCKED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class LiveAdapterPolicy:
    """Explicit safety policy for future live-adapter work.

    Every side-effect flag defaults to false. Even a manually permissive policy
    does not unlock live side effects in this skeleton.
    """

    enable_live_browser: bool = False
    allow_download_click: bool = False
    allow_patchops_execution: bool = False
    allow_composer_paste: bool = False
    allow_send_submit: bool = False


@dataclass(frozen=True)
class LiveAdapterResult:
    """Result object returned by the compatibility skeleton methods."""

    status: LiveAdapterStatus
    ok: bool
    reason: str
    side_effects_performed: tuple[str, ...] = field(default_factory=tuple)
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "ok": self.ok,
            "reason": self.reason,
            "side_effects_performed": list(self.side_effects_performed),
            "details": dict(self.details),
        }


class LiveAdapterBlockedError(RuntimeError):
    """Raised by module-level L1.2 live operation stubs."""

    def __init__(self, operation: str, reason: str | None = None) -> None:
        self.operation = operation
        self.reason = reason or _blocked_reason(operation)
        super().__init__(f"live adapter operation blocked: {operation}: {self.reason}")

    def to_payload(self) -> dict[str, object]:
        return {
            "ok": False,
            "operation": self.operation,
            "status": "blocked",
            "reason": self.reason,
            "side_effect_performed": False,
        }


@dataclass(frozen=True)
class LiveAdapterCapability:
    operation: str
    status: str
    side_effect: bool
    reason: str

    def to_payload(self) -> dict[str, object]:
        return {
            "operation": self.operation,
            "status": self.status,
            "side_effect": self.side_effect,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class LiveAdapterReadback:
    name: str
    phase: str
    patch: str
    status: str
    ok: bool
    browser_started: bool
    browser_session_created: bool
    optional_browser_dependencies_required: bool
    side_effects_performed: tuple[str, ...]
    blocked_operations: tuple[str, ...]
    passive_operations: tuple[str, ...]
    capabilities: tuple[LiveAdapterCapability, ...]
    next_patch: str

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "phase": self.phase,
            "patch": self.patch,
            "status": self.status,
            "ok": self.ok,
            "browser_started": self.browser_started,
            "browser_session_created": self.browser_session_created,
            "optional_browser_dependencies_required": self.optional_browser_dependencies_required,
            "side_effects_performed": list(self.side_effects_performed),
            "blocked_operations": list(self.blocked_operations),
            "passive_operations": list(self.passive_operations),
            "capabilities": [capability.to_payload() for capability in self.capabilities],
            "next_patch": self.next_patch,
        }


def _blocked_reason(operation: str) -> str:
    return (
        f"{operation} is reserved for a later live-browser phase. "
        "L1.2 only exposes passive adapter readback and must perform no browser, "
        "download, paste, send, package-run, commit, or push side effects."
    )


def _module_blocked(operation: str) -> None:
    raise LiveAdapterBlockedError(operation)


class LiveAdapterSkeleton:
    """No-side-effect adapter interface retained from the L1.1 contract."""

    stream = "L1"
    phase = "L1.1"
    name = "live_adapter_skeleton"

    def __init__(self, policy: LiveAdapterPolicy | None = None) -> None:
        self.policy = policy or LiveAdapterPolicy()

    def describe_capabilities(self) -> dict[str, Any]:
        return {
            "stream": self.stream,
            "phase": self.phase,
            "name": self.name,
            "selenium_required": False,
            "browser_starts": False,
            "side_effects_supported": False,
            "supported_operations": [],
            "blocked_operations": list(BLOCKED_OPERATION_NAMES),
            "policy": {
                "enable_live_browser": self.policy.enable_live_browser,
                "allow_download_click": self.policy.allow_download_click,
                "allow_patchops_execution": self.policy.allow_patchops_execution,
                "allow_composer_paste": self.policy.allow_composer_paste,
                "allow_send_submit": self.policy.allow_send_submit,
            },
        }

    def _blocked_result(self, operation: str, reason: str) -> LiveAdapterResult:
        return LiveAdapterResult(
            status=LiveAdapterStatus.BLOCKED,
            ok=False,
            reason=reason,
            side_effects_performed=(),
            details={"operation": operation, "phase": self.phase, "skeleton": True},
        )

    def start_browser(self) -> LiveAdapterResult:
        return self._blocked_result("start_browser", "Live browser startup is not implemented in L1.1; wait for a later explicit browser startup gate.")

    def read_page(self) -> LiveAdapterResult:
        return self._blocked_result("read_page", "Live page reading is not implemented in L1.1; wait for a later read-only inspection gate.")

    def detect_latest_assistant_reply(self) -> LiveAdapterResult:
        return self._blocked_result("detect_latest_assistant_reply", "Latest assistant reply detection is not implemented in L1.1; wait for a later reply detection gate.")

    def click_download(self) -> LiveAdapterResult:
        return self._blocked_result("click_download", "Download clicks are not implemented in L1.1; wait for a later download click gate.")

    def run_patchops_package(self) -> LiveAdapterResult:
        return self._blocked_result("run_patchops_package", "Live PatchOps package execution is not implemented in L1.1; wait for a later execution gate.")

    def paste_to_composer(self) -> LiveAdapterResult:
        return self._blocked_result("paste_to_composer", "Composer paste is not implemented in L1.1; wait for a later composer paste gate.")

    def send_or_submit(self) -> LiveAdapterResult:
        return LiveAdapterResult(
            status=LiveAdapterStatus.UNSUPPORTED,
            ok=False,
            reason="Send/submit is unsupported in L1.1 and remains blocked until a separate explicit safety design exists.",
            side_effects_performed=(),
            details={"operation": "send_or_submit", "phase": self.phase, "auto_send_supported": False},
        )


def create_live_adapter_skeleton(policy: LiveAdapterPolicy | None = None) -> LiveAdapterSkeleton:
    return LiveAdapterSkeleton(policy=policy)


def build_live_adapter_capabilities() -> tuple[LiveAdapterCapability, ...]:
    blocked = tuple(
        LiveAdapterCapability(operation=operation, status="blocked", side_effect=True, reason=_blocked_reason(operation))
        for operation in BLOCKED_OPERATION_NAMES
    )
    passive = tuple(
        LiveAdapterCapability(operation=operation, status="available", side_effect=False, reason="Passive readback only; no browser or external process is started.")
        for operation in PASSIVE_OPERATION_NAMES
    )
    return blocked + passive


def build_live_adapter_readback() -> dict[str, object]:
    return LiveAdapterReadback(
        name=ADAPTER_NAME,
        phase=ADAPTER_PHASE,
        patch=ADAPTER_PATCH,
        status=ADAPTER_STATUS,
        ok=True,
        browser_started=False,
        browser_session_created=False,
        optional_browser_dependencies_required=False,
        side_effects_performed=(),
        blocked_operations=BLOCKED_OPERATION_NAMES,
        passive_operations=PASSIVE_OPERATION_NAMES,
        capabilities=build_live_adapter_capabilities(),
        next_patch=NEXT_PATCH,
    ).to_payload()


def live_adapter_readback_json(*, indent: int | None = 2) -> str:
    return json.dumps(build_live_adapter_readback(), indent=indent, sort_keys=True)


def assert_live_adapter_skeleton_safe() -> bool:
    payload = build_live_adapter_readback()
    if payload["browser_started"]:
        raise AssertionError("live adapter skeleton unexpectedly started a browser")
    if payload["browser_session_created"]:
        raise AssertionError("live adapter skeleton unexpectedly created a browser session")
    if payload["side_effects_performed"]:
        raise AssertionError("live adapter skeleton unexpectedly recorded side effects")
    missing = set(BLOCKED_OPERATION_NAMES) - set(payload["blocked_operations"])
    if missing:
        raise AssertionError(f"live adapter skeleton is missing blocked operations: {sorted(missing)}")
    return True


def start_browser(*args: Any, **kwargs: Any) -> None:
    _module_blocked("start_browser")


def read_page(*args: Any, **kwargs: Any) -> None:
    _module_blocked("read_page")


def detect_latest_assistant_reply(*args: Any, **kwargs: Any) -> None:
    _module_blocked("detect_latest_assistant_reply")


def click_download(*args: Any, **kwargs: Any) -> None:
    _module_blocked("click_download")


def run_patchops_package(*args: Any, **kwargs: Any) -> None:
    _module_blocked("run_patchops_package")


def paste_to_composer(*args: Any, **kwargs: Any) -> None:
    _module_blocked("paste_to_composer")


def send_or_submit(*args: Any, **kwargs: Any) -> None:
    _module_blocked("send_or_submit")


def _render_text(payload: Mapping[str, object]) -> str:
    lines = [
        "PatchOps LLM browser live adapter skeleton readback",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        "Browser    : not started",
        f"SideEffects: {payload.get('side_effects_performed')}",
        "Blocked operations:",
    ]
    lines.extend(f"- {operation}" for operation in payload.get("blocked_operations", ()))
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m patchops.llm_browser.live_adapter",
        description="Read back the passive L-phase live adapter skeleton capability contract.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON readback.")
    parser.add_argument("--compact", action="store_true", help="Use compact JSON when --json is supplied.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or ()))
    payload = build_live_adapter_readback()
    if args.json:
        print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    else:
        print(_render_text(payload), end="")
    return 0


__all__ = [
    "LiveAdapterBlockedError",
    "LiveAdapterCapability",
    "LiveAdapterPolicy",
    "LiveAdapterReadback",
    "LiveAdapterResult",
    "LiveAdapterSkeleton",
    "LiveAdapterStatus",
    "assert_live_adapter_skeleton_safe",
    "build_live_adapter_capabilities",
    "build_live_adapter_readback",
    "click_download",
    "create_live_adapter_skeleton",
    "detect_latest_assistant_reply",
    "live_adapter_readback_json",
    "main",
    "paste_to_composer",
    "read_page",
    "run_patchops_package",
    "send_or_submit",
    "start_browser",
]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
