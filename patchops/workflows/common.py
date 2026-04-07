from __future__ import annotations

from datetime import datetime
from hashlib import sha1
from pathlib import Path

from patchops.files.paths import ensure_directory
from patchops.execution.failure_classifier import classify_command_failure
from patchops.execution.process_runner import run_command_result
from patchops.execution.result_model import ExecutionResult, normalize_execution_result
from patchops.models import CommandResult


MAX_REPORT_PATH_LENGTH = 220
FALLBACK_REPORT_DIR_NAME = "patchops_reports"


def infer_workspace_root(target_project_root: Path) -> Path | None:
    return target_project_root.parent if target_project_root.parent != target_project_root else None


def default_report_directory() -> Path:
    return Path.home() / "Desktop"


def fallback_report_directory() -> Path:
    fallback_dir = default_report_directory() / FALLBACK_REPORT_DIR_NAME
    ensure_directory(fallback_dir)
    return fallback_dir


def build_report_path(prefix: str, patch_name: str, report_dir: Path) -> Path:
    safe_prefix = prefix.lower().replace(" ", "_")
    safe_patch = patch_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    name_token = safe_prefix if safe_prefix == safe_patch else f"{safe_prefix}_{safe_patch}"
    preferred = report_dir / f"{name_token}_{timestamp}.txt"
    if len(str(preferred)) <= MAX_REPORT_PATH_LENGTH:
        ensure_directory(report_dir)
        return preferred

    digest_source = f"{safe_prefix}|{safe_patch}|{report_dir}"
    digest = sha1(digest_source.encode("utf-8")).hexdigest()[:12]

    compact_base = safe_patch[:40] if safe_patch else "report"
    compact = report_dir / f"{compact_base}_{digest}_{timestamp}.txt"
    if len(str(compact)) <= MAX_REPORT_PATH_LENGTH:
        ensure_directory(report_dir)
        return compact

    minimal = report_dir / f"r_{digest}_{timestamp}.txt"
    if len(str(minimal)) <= MAX_REPORT_PATH_LENGTH:
        ensure_directory(report_dir)
        return minimal

    fallback_dir = fallback_report_directory()
    return fallback_dir / f"r_{digest}_{timestamp}.txt"


def execute_command_adapter(command, *, runtime_path, working_directory_root, phase: str) -> tuple[ExecutionResult, CommandResult, object | None]:
    execution_result = normalize_execution_result(
        run_command_result(
            command,
            runtime_path=runtime_path,
            working_directory_root=working_directory_root,
            phase=phase,
        )
    )
    command_result = execution_result.to_command_result()
    command_failure = classify_command_failure(command_result, command.allowed_exit_codes)
    return execution_result, command_result, command_failure


def execute_command_group(commands, *, runtime_path, working_directory_root, phase: str):
    results = []
    for command in commands:
        _execution_result, command_result, command_failure = execute_command_adapter(
            command,
            runtime_path=runtime_path,
            working_directory_root=working_directory_root,
            phase=phase,
        )
        results.append(command_result)
        if command_failure is not None:
            return results, command_failure
    return results, None
