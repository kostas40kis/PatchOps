from __future__ import annotations

from pathlib import Path
from typing import Any

from .report_chain import bundle_report_chain_as_dict


def _stringify_path(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _tuple_strings(values: Any) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, (str, bytes)):
        return (str(values),)
    return tuple(str(value) for value in values)


def _validation_command_payloads(values: Any) -> tuple[dict[str, Any], ...]:
    if not values:
        return ()
    payloads: list[dict[str, Any]] = []
    for value in values:
        if isinstance(value, (str, bytes)):
            payloads.append(
                {
                    "name": str(value),
                    "command": None,
                    "program": None,
                    "args": [],
                    "cwd": None,
                    "exit_code": None,
                }
            )
            continue
        payloads.append(
            {
                "name": getattr(value, "name", None),
                "command": getattr(value, "command", None),
                "program": getattr(value, "program", None),
                "args": list(getattr(value, "args", ()) or ()),
                "cwd": _stringify_path(getattr(value, "cwd", None)),
                "exit_code": getattr(value, "exit_code", None),
            }
        )
    return tuple(payloads)


def _nested_attr(obj: Any, *names: str) -> Any:
    current = obj
    for name in names:
        if current is None:
            return None
        current = getattr(current, name, None)
    return current


def _bundle_metadata(result: Any) -> Any:
    for path in (
        ("metadata",),
        ("check", "metadata"),
        ("inspect", "metadata"),
        ("plan", "metadata"),
        ("inspect", "check", "metadata"),
        ("plan", "inspect", "metadata"),
        ("plan", "inspect", "check", "metadata"),
    ):
        candidate = _nested_attr(result, *path)
        if candidate is not None:
            return candidate
    return None


def _bundle_extraction(result: Any) -> Any:
    for path in (
        ("extraction",),
        ("check", "extraction"),
        ("inspect", "check", "extraction"),
        ("plan", "inspect", "check", "extraction"),
    ):
        candidate = _nested_attr(result, *path)
        if candidate is not None:
            return candidate
    return None


def _bundle_resolved_layout(result: Any) -> Any:
    for path in (
        ("resolved_layout",),
        ("inspect", "resolved_layout"),
        ("plan", "inspect", "resolved_layout"),
    ):
        candidate = _nested_attr(result, *path)
        if candidate is not None:
            return candidate
    return None


def _issues_from_result(result: Any) -> tuple[str, ...]:
    direct = getattr(result, "issues", None)
    if direct is not None:
        return _tuple_strings(direct)

    validation = getattr(result, "validation", None)
    if validation is None:
        check = getattr(result, "check", None)
        validation = getattr(check, "validation", None) if check is not None else None
    if validation is None:
        return ()

    messages: list[str] = []
    for group_name in ("errors", "warnings"):
        for entry in getattr(validation, group_name, ()) or ():
            message = getattr(entry, "message", None)
            messages.append(str(message if message is not None else entry))
    return tuple(messages)


def bundle_check_result_as_dict(result: Any) -> dict[str, Any]:
    metadata = _bundle_metadata(result)
    extraction = _bundle_extraction(result)
    issues = _issues_from_result(result)
    payload = {
        "ok": bool(getattr(result, "ok", getattr(result, "is_valid", False))),
        "patch_name": getattr(result, "patch_name", getattr(metadata, "patch_name", None)),
        "recommended_profile": getattr(
            result,
            "recommended_profile",
            getattr(metadata, "recommended_profile", None),
        ),
        "bundle_zip_path": _stringify_path(
            getattr(result, "bundle_zip_path", getattr(extraction, "bundle_zip_path", None))
        ),
        "workspace_root": _stringify_path(
            getattr(result, "workspace_root", getattr(extraction, "run_root", None))
        ),
        "extracted_bundle_root": _stringify_path(
            getattr(result, "extracted_bundle_root", getattr(extraction, "bundle_root", None))
        ),
        "issue_count": len(issues),
        "issues": list(issues),
    }
    payload["report_chain"] = bundle_report_chain_as_dict(result)
    return payload


def bundle_inspect_result_as_dict(result: Any) -> dict[str, Any]:
    metadata = _bundle_metadata(result)
    extraction = _bundle_extraction(result)
    resolved_layout = _bundle_resolved_layout(result)
    write_targets = _tuple_strings(
        getattr(result, "write_targets", getattr(result, "target_paths", ()) or ())
    )
    validation_commands = _tuple_strings(
        getattr(result, "validation_commands", getattr(result, "validation_command_names", ()) or ())
    )
    payload = {
        "patch_name": getattr(result, "patch_name", getattr(metadata, "patch_name", None)),
        "recommended_profile": getattr(
            result,
            "recommended_profile",
            getattr(metadata, "recommended_profile", None),
        ),
        "bundle_zip_path": _stringify_path(
            getattr(result, "bundle_zip_path", getattr(extraction, "bundle_zip_path", None))
        ),
        "workspace_root": _stringify_path(
            getattr(result, "workspace_root", getattr(extraction, "run_root", None))
        ),
        "extracted_bundle_root": _stringify_path(
            getattr(result, "extracted_bundle_root", getattr(extraction, "bundle_root", None))
        ),
        "manifest_path": _stringify_path(
            getattr(result, "manifest_path", getattr(resolved_layout, "manifest_path", None))
        ),
        "content_root": _stringify_path(
            getattr(result, "content_root", getattr(resolved_layout, "content_root_path", None))
        ),
        "write_target_count": len(write_targets),
        "write_targets": list(write_targets),
        "validation_command_count": len(validation_commands),
        "validation_commands": list(validation_commands),
    }
    payload["report_chain"] = bundle_report_chain_as_dict(result)
    return payload


def bundle_plan_result_as_dict(result: Any) -> dict[str, Any]:
    metadata = _bundle_metadata(result)
    extraction = _bundle_extraction(result)
    resolved_layout = _bundle_resolved_layout(result)
    write_targets = _tuple_strings(getattr(result, "write_targets", ()) or ())
    validation_values = getattr(result, "validation_commands", None)
    if validation_values is None:
        validation_values = getattr(result, "validation_command_names", ()) or ()
    validation_commands = _validation_command_payloads(validation_values)
    payload = {
        "patch_name": getattr(result, "patch_name", getattr(metadata, "patch_name", None)),
        "recommended_profile": getattr(
            result,
            "recommended_profile",
            getattr(result, "resolved_profile", getattr(metadata, "recommended_profile", None)),
        ),
        "bundle_zip_path": _stringify_path(
            getattr(result, "bundle_zip_path", getattr(extraction, "bundle_zip_path", None))
        ),
        "workspace_root": _stringify_path(
            getattr(result, "workspace_root", getattr(extraction, "run_root", None))
        ),
        "extracted_bundle_root": _stringify_path(
            getattr(result, "extracted_bundle_root", getattr(extraction, "bundle_root", None))
        ),
        "manifest_path": _stringify_path(
            getattr(result, "manifest_path", getattr(resolved_layout, "manifest_path", None))
        ),
        "content_root": _stringify_path(
            getattr(result, "content_root", getattr(resolved_layout, "content_root_path", None))
        ),
        "prepared_manifest_path": _stringify_path(getattr(result, "prepared_manifest_path", None)),
        "write_target_count": len(write_targets),
        "write_targets": list(write_targets),
        "validation_commands": list(validation_commands),
        "target_project_root": _stringify_path(getattr(result, "target_project_root", None)),
        "report_path_preview": _stringify_path(getattr(result, "report_path_preview", None)),
    }
    payload["report_chain"] = bundle_report_chain_as_dict(result)
    return payload


def bundle_apply_result_as_dict(result: Any) -> dict[str, Any]:
    metadata = _bundle_metadata(result)
    extraction = _bundle_extraction(result)
    workflow_result = getattr(result, "workflow_result", None)
    payload = {
        "patch_name": getattr(result, "patch_name", getattr(metadata, "patch_name", None)),
        "bundle_zip_path": _stringify_path(
            getattr(result, "bundle_zip_path", getattr(extraction, "bundle_zip_path", None))
        ),
        "workspace_root": _stringify_path(
            getattr(result, "workspace_root", getattr(extraction, "run_root", None))
        ),
        "extracted_bundle_root": _stringify_path(
            getattr(result, "extracted_bundle_root", getattr(extraction, "bundle_root", None))
        ),
        "prepared_manifest_path": _stringify_path(getattr(result, "prepared_manifest_path", None)),
        "report_path": _stringify_path(
            getattr(result, "report_path", getattr(workflow_result, "report_path", None))
        ),
        "result_label": getattr(result, "result_label", getattr(workflow_result, "result_label", None)),
        "exit_code": getattr(result, "exit_code", getattr(workflow_result, "exit_code", None)),
    }
    payload["report_chain"] = bundle_report_chain_as_dict(result)
    return payload


def bundle_verify_result_as_dict(result: Any) -> dict[str, Any]:
    metadata = _bundle_metadata(result)
    extraction = _bundle_extraction(result)
    workflow_result = getattr(result, "workflow_result", None)
    payload = {
        "patch_name": getattr(result, "patch_name", getattr(metadata, "patch_name", None)),
        "bundle_zip_path": _stringify_path(
            getattr(result, "bundle_zip_path", getattr(extraction, "bundle_zip_path", None))
        ),
        "workspace_root": _stringify_path(
            getattr(result, "workspace_root", getattr(extraction, "run_root", None))
        ),
        "extracted_bundle_root": _stringify_path(
            getattr(result, "extracted_bundle_root", getattr(extraction, "bundle_root", None))
        ),
        "prepared_manifest_path": _stringify_path(getattr(result, "prepared_manifest_path", None)),
        "report_path": _stringify_path(
            getattr(result, "report_path", getattr(workflow_result, "report_path", None))
        ),
        "result_label": getattr(result, "result_label", getattr(workflow_result, "result_label", None)),
        "exit_code": getattr(result, "exit_code", getattr(workflow_result, "exit_code", None)),
    }
    payload["report_chain"] = bundle_report_chain_as_dict(result)
    return payload
