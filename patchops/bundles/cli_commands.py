from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .applier import apply_bundle_zip
from .checker import check_bundle_zip
from .cli_payloads import (
    bundle_apply_result_as_dict,
    bundle_check_result_as_dict,
    bundle_inspect_result_as_dict,
    bundle_plan_result_as_dict,
    bundle_verify_result_as_dict,
)
from .inspector import inspect_bundle_zip
from .planner import plan_bundle_zip
from .verifier import verify_bundle_zip


def run_check_bundle_command(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> dict[str, Any]:
    return bundle_check_result_as_dict(
        check_bundle_zip(
            bundle_zip_path,
            wrapper_project_root,
            timestamp_token=timestamp_token,
        )
    )


def run_inspect_bundle_command(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> dict[str, Any]:
    return bundle_inspect_result_as_dict(
        inspect_bundle_zip(
            bundle_zip_path,
            wrapper_project_root,
            timestamp_token=timestamp_token,
        )
    )


def run_plan_bundle_command(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> dict[str, Any]:
    return bundle_plan_result_as_dict(
        plan_bundle_zip(
            bundle_zip_path,
            wrapper_project_root,
            timestamp_token=timestamp_token,
        )
    )


def run_apply_bundle_command(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> dict[str, Any]:
    return bundle_apply_result_as_dict(
        apply_bundle_zip(
            bundle_zip_path,
            wrapper_project_root,
            timestamp_token=timestamp_token,
        )
    )


def run_verify_bundle_command(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> dict[str, Any]:
    return bundle_verify_result_as_dict(
        verify_bundle_zip(
            bundle_zip_path,
            wrapper_project_root,
            timestamp_token=timestamp_token,
        )
    )


_BUNDLE_COMMAND_HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "check-bundle": run_check_bundle_command,
    "inspect-bundle": run_inspect_bundle_command,
    "plan-bundle": run_plan_bundle_command,
    "apply-bundle": run_apply_bundle_command,
    "verify-bundle": run_verify_bundle_command,
}


def run_bundle_command(
    command_name: str,
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> dict[str, Any]:
    try:
        handler = _BUNDLE_COMMAND_HANDLERS[command_name]
    except KeyError as exc:
        supported = ", ".join(sorted(_BUNDLE_COMMAND_HANDLERS))
        raise ValueError(
            f"Unsupported bundle command: {command_name!r}. Supported commands: {supported}"
        ) from exc

    return handler(
        bundle_zip_path,
        wrapper_project_root,
        timestamp_token=timestamp_token,
    )
