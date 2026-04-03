from __future__ import annotations

from pathlib import Path

from patchops.execution.failure_classifier import classify_command_failure, classify_exception
from patchops.execution.process_runner import run_command
from patchops.files.backups import backup_file, generate_backup_root
from patchops.files.writers import load_content, write_text_file
from patchops.manifest_loader import load_manifest
from patchops.models import FailureInfo, WorkflowResult
from patchops.profiles.base import resolve_profile
from patchops.reporting.renderer import render_workflow_report
from patchops.workflows.common import build_report_path, default_report_directory, infer_workspace_root


def apply_manifest(manifest_path: str | Path, wrapper_project_root: str | Path | None = None) -> WorkflowResult:
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
        manifest.report_preferences.report_name_prefix or resolved_profile.report_prefix,
        manifest.patch_name,
        report_dir,
    )
    backup_root = generate_backup_root(target_root, resolved_profile.backup_root_name, manifest.patch_name)

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
        file_paths_to_backup = set(manifest.backup_files)
        file_paths_to_backup.update(item.path for item in manifest.files_to_write)

        for relative_path in sorted(file_paths_to_backup):
            source = target_root / relative_path
            backup_records.append(backup_file(source, target_root, backup_root))

        for spec in manifest.files_to_write:
            destination = target_root / spec.path
            content = load_content(spec, manifest_path=manifest_path)
            write_records.append(write_text_file(destination, content, encoding=spec.encoding))

        for phase_name, commands, sink in [
            ("validation", manifest.validation_commands, validation_results),
            ("smoke", manifest.smoke_commands, smoke_results),
            ("audit", manifest.audit_commands, audit_results),
            ("cleanup", manifest.cleanup_commands, cleanup_results),
            ("archive", manifest.archive_commands, archive_results),
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
            mode="apply",
            manifest_path=manifest_path,
            manifest=manifest,
            resolved_profile=resolved_profile,
            workspace_root=workspace_root,
            wrapper_project_root=wrapper_root,
            target_project_root=target_root,
            runtime_path=runtime_path,
            backup_root=backup_root,
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