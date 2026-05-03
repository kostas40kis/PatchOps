"""Passive contract gate for the PatchOps LLM browser live adapter.

L1.3 proves the L1 live-adapter surface is still passive after the L1.2
CLI/readback additions. This module does not import Selenium, start a browser,
click, download, paste, send, run PatchOps packages, commit, or push.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import live_adapter

GATE_NAME = "llm_browser_live_adapter_passive_contract_gate"
GATE_PHASE = "L1"
GATE_PATCH = "L1.3"
GATE_STATUS_PASS = "PASS"
GATE_STATUS_FAIL = "FAIL"
NEXT_PATCH = "L1.4 Live adapter explicit startup gate scaffold"

REQUIRED_BLOCKED_OPERATIONS: tuple[str, ...] = (
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
class PassiveContractCheck:
    name: str
    ok: bool
    status: str
    details: Mapping[str, Any]

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "ok": self.ok,
            "status": self.status,
            "details": dict(self.details),
        }


def _status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _check_readback_payload(payload: Mapping[str, object]) -> PassiveContractCheck:
    blocked = set(payload.get("blocked_operations", ()))
    missing = sorted(set(REQUIRED_BLOCKED_OPERATIONS) - blocked)
    ok = (
        payload.get("ok") is True
        and payload.get("status") == "PASSIVE_READBACK_ONLY"
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and payload.get("optional_browser_dependencies_required") is False
        and payload.get("side_effects_performed") == []
        and not missing
    )
    return PassiveContractCheck(
        name="live_adapter_readback_payload",
        ok=ok,
        status=_status(ok),
        details={
            "patch": payload.get("patch"),
            "status": payload.get("status"),
            "browser_started": payload.get("browser_started"),
            "browser_session_created": payload.get("browser_session_created"),
            "optional_browser_dependencies_required": payload.get("optional_browser_dependencies_required"),
            "side_effects_performed": payload.get("side_effects_performed"),
            "missing_blocked_operations": missing,
        },
    )


def _check_capability_consistency(payload: Mapping[str, object]) -> PassiveContractCheck:
    capabilities_raw = payload.get("capabilities", [])
    capabilities = {
        item.get("operation"): item
        for item in capabilities_raw
        if isinstance(item, Mapping)
    }
    failures: list[str] = []
    for operation in REQUIRED_BLOCKED_OPERATIONS:
        item = capabilities.get(operation)
        if not item:
            failures.append(f"{operation}: missing capability")
            continue
        if item.get("status") != "blocked":
            failures.append(f"{operation}: status={item.get('status')!r}")
        if item.get("side_effect") is not True:
            failures.append(f"{operation}: side_effect={item.get('side_effect')!r}")
    ok = not failures
    return PassiveContractCheck(
        name="blocked_capability_consistency",
        ok=ok,
        status=_status(ok),
        details={"failures": failures, "blocked_operation_count": len(REQUIRED_BLOCKED_OPERATIONS)},
    )


def _imported_roots_from_source(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except OSError:
        return set()
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    return imported_roots


def _check_no_optional_browser_dependency_imports() -> PassiveContractCheck:
    source_path = Path(getattr(live_adapter, "__file__", ""))
    imported_roots = _imported_roots_from_source(source_path) if source_path else set()
    forbidden = sorted(set(FORBIDDEN_IMPORT_ROOTS) & imported_roots)
    ok = not forbidden
    return PassiveContractCheck(
        name="no_optional_browser_dependency_imports",
        ok=ok,
        status=_status(ok),
        details={
            "source_path": str(source_path),
            "forbidden_import_roots": forbidden,
            "checked_import_roots": sorted(imported_roots),
        },
    )


def _check_module_level_operations_blocked() -> PassiveContractCheck:
    failures: list[str] = []
    for operation in REQUIRED_BLOCKED_OPERATIONS:
        fn = getattr(live_adapter, operation, None)
        if not callable(fn):
            failures.append(f"{operation}: missing callable")
            continue
        try:
            fn()
        except live_adapter.LiveAdapterBlockedError as exc:
            payload = exc.to_payload()
            if payload.get("operation") != operation:
                failures.append(f"{operation}: wrong exception operation {payload.get('operation')!r}")
            if payload.get("status") != "blocked":
                failures.append(f"{operation}: wrong exception status {payload.get('status')!r}")
            if payload.get("side_effect_performed") is not False:
                failures.append(f"{operation}: side_effect_performed was not false")
        except Exception as exc:  # pragma: no cover - regression detail
            failures.append(f"{operation}: wrong exception {type(exc).__name__}")
        else:
            failures.append(f"{operation}: did not raise LiveAdapterBlockedError")
    ok = not failures and live_adapter.build_live_adapter_readback().get("side_effects_performed") == []
    return PassiveContractCheck(
        name="module_level_operations_blocked",
        ok=ok,
        status=_status(ok),
        details={"failures": failures},
    )


def _check_skeleton_methods_blocked() -> PassiveContractCheck:
    skeleton = live_adapter.create_live_adapter_skeleton()
    failures: list[str] = []
    for operation in REQUIRED_BLOCKED_OPERATIONS:
        method = getattr(skeleton, operation, None)
        if not callable(method):
            failures.append(f"{operation}: missing skeleton method")
            continue
        result = method()
        payload = result.to_dict()
        if payload.get("ok") is not False:
            failures.append(f"{operation}: ok was not false")
        if payload.get("side_effects_performed") != []:
            failures.append(f"{operation}: side_effects_performed was not []")
        if operation == "send_or_submit":
            if payload.get("status") != "UNSUPPORTED":
                failures.append(f"{operation}: status was not UNSUPPORTED")
        elif payload.get("status") != "BLOCKED":
            failures.append(f"{operation}: status was not BLOCKED")
    ok = not failures
    return PassiveContractCheck(
        name="skeleton_methods_blocked",
        ok=ok,
        status=_status(ok),
        details={"failures": failures},
    )


def _check_no_browser_optional_modules_loaded_by_gate(before_modules: set[str]) -> PassiveContractCheck:
    after_modules = set(sys.modules)
    newly_loaded_forbidden = sorted(
        root for root in FORBIDDEN_IMPORT_ROOTS
        if root not in before_modules and root in after_modules
    )
    ok = not newly_loaded_forbidden
    return PassiveContractCheck(
        name="gate_did_not_load_browser_optional_modules",
        ok=ok,
        status=_status(ok),
        details={"newly_loaded_forbidden_modules": newly_loaded_forbidden},
    )


def evaluate_live_adapter_passive_contract() -> dict[str, object]:
    """Evaluate the L1.3 passive contract without live browser side effects."""

    before_modules = set(sys.modules)
    payload = live_adapter.build_live_adapter_readback()
    checks = [
        _check_readback_payload(payload),
        _check_capability_consistency(payload),
        _check_no_optional_browser_dependency_imports(),
        _check_module_level_operations_blocked(),
        _check_skeleton_methods_blocked(),
        _check_no_browser_optional_modules_loaded_by_gate(before_modules),
    ]
    ok = all(check.ok for check in checks)
    return {
        "name": GATE_NAME,
        "phase": GATE_PHASE,
        "patch": GATE_PATCH,
        "status": GATE_STATUS_PASS if ok else GATE_STATUS_FAIL,
        "ok": ok,
        "browser_started": False,
        "browser_session_created": False,
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "required_blocked_operations": list(REQUIRED_BLOCKED_OPERATIONS),
        "checks": [check.to_payload() for check in checks],
        "next_patch": NEXT_PATCH,
    }


def contract_gate_json(*, indent: int | None = 2) -> str:
    return json.dumps(evaluate_live_adapter_passive_contract(), indent=indent, sort_keys=True)


def _render_text(payload: Mapping[str, object]) -> str:
    lines = [
        "PatchOps LLM browser live adapter passive contract gate",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        "Browser    : not started",
        f"SideEffects: {payload.get('side_effects_performed')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m patchops.llm_browser.live_adapter_contract_gate",
        description="Evaluate the passive L1 live-adapter contract without browser side effects.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON gate payload.")
    parser.add_argument("--compact", action="store_true", help="Use compact JSON when --json is supplied.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    args = build_arg_parser().parse_args(raw)
    payload = evaluate_live_adapter_passive_contract()
    if args.json:
        print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    else:
        print(_render_text(payload), end="")
    return 0 if payload.get("ok") is True else 1


__all__ = [
    "GATE_NAME",
    "GATE_PHASE",
    "GATE_PATCH",
    "NEXT_PATCH",
    "PassiveContractCheck",
    "REQUIRED_BLOCKED_OPERATIONS",
    "contract_gate_json",
    "evaluate_live_adapter_passive_contract",
    "main",
]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
