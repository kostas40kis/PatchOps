from __future__ import annotations

from pathlib import Path

from patchops.execution.failure_classifier import classify_command_failure, classify_exception
from patchops.execution.process_runner import run_command
from patchops.manifest_loader import load_manifest
from patchops.models import FailureInfo, WorkflowResult
from patchops.profiles.base import resolve_profile
from patchops.reporting.renderer import render_workflow_report
from patchops.workflows.common import build_report_path, default_report_directory, infer_workspace_root


def verify_only(manifest_path: str | Path, wrapper_project_root: str | Path | None = None) -> WorkflowResult:
    manifest_path = Path(manifest_path).resolve()
    wrapper_root = Path(wrapper_project_root).resolve() if wrapper_project_root else Path(__file__).resolve().parents[2]
    manifest = load_manifest(manifest_path)
    resolved_profile = resolve_profile(manifest, wrapper_root)
    target_root = Path(manifest.target_project_root) if manifest.target_project_root else resolved_profile.default_target_root
    if target_root is None:
        raise ValueError("No target project root could be resolved from the manifest/profile.")
    runtime_path = resolved_profile.runtime_path if resolved_profile.runtime_path is not None else None
    workspace_root = infer_workspace_root(target_root)

    report_dir = (
        Path(manifest.report_preferences.report_dir)
        if manifest.report_preferences.report_dir
        else default_report_directory()
    )
    report_path = build_report_path(
        manifest.report_preferences.report_name_prefix or f"{resolved_profile.report_prefix}_verify",
        manifest.patch_name,
        report_dir,
    )

    backup_records = []
    write_records = []
    validation_results = []
    smoke_results = []
    audit_results = []
    cleanup_results = []
    archive_results = []
    failure: FailureInfo | None = None
    exit_code = 0
    result_label = "PASS"

    try:
        missing_files = []
        for spec in manifest.files_to_write:
            target_path = target_root / spec.path
            if not target_path.exists():
                missing_files.append(target_path)
        if missing_files:
            names = ", ".join(str(path) for path in missing_files)
            raise RuntimeError(f"Verify-only run found missing expected file(s): {names}")

        for phase_name, commands, sink in [
            ("validation", manifest.validation_commands, validation_results),
            ("smoke", manifest.smoke_commands, smoke_results),
            ("audit", manifest.audit_commands, audit_results),
        ]:
            for command in commands:
                result = run_command(command, runtime_path=runtime_path, working_directory_root=target_root, phase=phase_name)
                sink.append(result)
                command_failure = classify_command_failure(result, command.allowed_exit_codes)
                if command_failure is not None:
                    failure = command_failure
                    exit_code = result.exit_code
                    result_label = "FAIL"
                    raise RuntimeError(command_failure.message)
    except Exception as exc:  # noqa: BLE001
        if failure is None:
            failure = classify_exception(exc)
            if exit_code == 0:
                exit_code = 1
        result_label = "FAIL"
    finally:
        workflow_result = WorkflowResult(
            mode="verify_only",
            manifest_path=manifest_path,
            manifest=manifest,
            resolved_profile=resolved_profile,
            workspace_root=workspace_root,
            wrapper_project_root=wrapper_root,
            target_project_root=target_root,
            runtime_path=runtime_path,
            backup_root=None,
            report_path=report_path,
            backup_records=backup_records,
            write_records=write_records,
            validation_results=validation_results,
            smoke_results=smoke_results,
            audit_results=audit_results,
            cleanup_results=cleanup_results,
            archive_results=archive_results,
            failure=failure,
            exit_code=exit_code,
            result_label=result_label,
        )
        report_path.write_text(render_workflow_report(workflow_result), encoding="utf-8")
    return workflow_result

# PATCHOPS_PATCH32_VERIFY_ONLY_HELPERS_START
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class VerifyOnlyFlowState:
    mode: str
    writes_skipped: bool
    expected_target_files: tuple[str, ...]
    existing_target_files: tuple[str, ...]
    missing_target_files: tuple[str, ...]
    validation_command_count: int
    smoke_command_count: int
    audit_command_count: int



def _verify_only_iter_manifest_paths(manifest: Mapping[str, Any]) -> list[str]:
    values: list[str] = []

    explicit_targets = manifest.get("target_files") or []
    for value in explicit_targets:
        if isinstance(value, str) and value.strip():
            values.append(value.strip())

    files_to_write = manifest.get("files_to_write") or []
    for item in files_to_write:
        if isinstance(item, Mapping):
            path_value = item.get("path")
            if isinstance(path_value, str) and path_value.strip():
                values.append(path_value.strip())

    return values



def resolve_verify_only_expected_target_files(
    manifest: Mapping[str, Any],
    target_project_root: str | Path,
) -> list[str]:
    target_root = Path(str(target_project_root))
    resolved: list[str] = []
    seen: set[str] = set()

    for raw in _verify_only_iter_manifest_paths(manifest):
        path = Path(raw)
        candidate = path if path.is_absolute() else target_root / path
        normalized = str(candidate)
        if normalized not in seen:
            seen.add(normalized)
            resolved.append(normalized)

    return resolved



def build_verify_only_flow_state(
    manifest: Mapping[str, Any],
    target_project_root: str | Path,
) -> VerifyOnlyFlowState:
    expected = tuple(resolve_verify_only_expected_target_files(manifest, target_project_root))
    existing = tuple(path for path in expected if Path(path).exists())
    missing = tuple(path for path in expected if not Path(path).exists())

    validation_commands = manifest.get("validation_commands") or []
    smoke_commands = manifest.get("smoke_commands") or []
    audit_commands = manifest.get("audit_commands") or []

    return VerifyOnlyFlowState(
        mode="verify",
        writes_skipped=True,
        expected_target_files=expected,
        existing_target_files=existing,
        missing_target_files=missing,
        validation_command_count=len(validation_commands),
        smoke_command_count=len(smoke_commands),
        audit_command_count=len(audit_commands),
    )



def render_verify_only_scope_lines(state: VerifyOnlyFlowState) -> tuple[str, ...]:
    return (
        "Scope    : verification-only rerun",
        f"Mode     : {state.mode}",
        "Writes   : skipped",
        "Intent   : re-check files already on disk and rerun validation commands",
        f"Expected : {len(state.expected_target_files)}",
        f"Existing : {len(state.existing_target_files)}",
        f"Missing  : {len(state.missing_target_files)}",
        f"Validate : {state.validation_command_count}",
        f"Smoke    : {state.smoke_command_count}",
        f"Audit    : {state.audit_command_count}",
    )



def verify_only_flow_needs_attention(state: VerifyOnlyFlowState) -> bool:
    return bool(state.missing_target_files)
# PATCHOPS_PATCH32_VERIFY_ONLY_HELPERS_END
