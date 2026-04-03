from dataclasses import dataclass
from typing import Any, Mapping


CLEANUP_REPORT_SECTIONS = (
    "TARGET FILES",
    "BACKUP",
    "CLEANUP COMMANDS",
    "CLEANUP OUTPUT",
    "SUMMARY",
)


@dataclass(frozen=True)
class CleanupWorkflowState:
    mode: str
    cleanup_command_count: int
    validation_command_count: int
    report_sections: tuple[str, ...]
    deterministic_reporting: bool
    destructive: bool


def resolve_cleanup_commands(manifest: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    commands = manifest.get("cleanup_commands") or []
    normalized = []
    for item in commands:
        if isinstance(item, Mapping):
            normalized.append(item)
    return tuple(normalized)


def build_cleanup_workflow_state(manifest: Mapping[str, Any]) -> CleanupWorkflowState:
    cleanup_commands = resolve_cleanup_commands(manifest)
    validation_commands = manifest.get("validation_commands") or []
    destructive = bool(manifest.get("destructive_cleanup", False))
    return CleanupWorkflowState(
        mode="cleanup",
        cleanup_command_count=len(cleanup_commands),
        validation_command_count=len(validation_commands),
        report_sections=CLEANUP_REPORT_SECTIONS,
        deterministic_reporting=True,
        destructive=destructive,
    )


def render_cleanup_scope_lines(state: CleanupWorkflowState) -> tuple[str, ...]:
    return (
        "Scope    : cleanup workflow",
        f"Mode     : {state.mode}",
        f"Cleanup  : {state.cleanup_command_count}",
        f"Validate : {state.validation_command_count}",
        "Evidence : explicit and deterministic cleanup sections",
        f"Danger   : {'destructive' if state.destructive else 'non-destructive'}",
    )


def cleanup_has_work(state: CleanupWorkflowState) -> bool:
    return state.cleanup_command_count > 0
