from dataclasses import dataclass
from typing import Any, Mapping


ARCHIVE_REPORT_SECTIONS = (
    "TARGET FILES",
    "BACKUP",
    "ARCHIVE COMMANDS",
    "ARCHIVE OUTPUT",
    "SUMMARY",
)


@dataclass(frozen=True)
class ArchiveWorkflowState:
    mode: str
    archive_command_count: int
    validation_command_count: int
    report_sections: tuple[str, ...]
    deterministic_reporting: bool
    destructive: bool
    traceable: bool


def resolve_archive_commands(manifest: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    commands = manifest.get("archive_commands") or []
    normalized = []
    for item in commands:
        if isinstance(item, Mapping):
            normalized.append(item)
    return tuple(normalized)


def build_archive_workflow_state(manifest: Mapping[str, Any]) -> ArchiveWorkflowState:
    archive_commands = resolve_archive_commands(manifest)
    validation_commands = manifest.get("validation_commands") or []
    destructive = bool(manifest.get("destructive_archive", False))
    return ArchiveWorkflowState(
        mode="archive",
        archive_command_count=len(archive_commands),
        validation_command_count=len(validation_commands),
        report_sections=ARCHIVE_REPORT_SECTIONS,
        deterministic_reporting=True,
        destructive=destructive,
        traceable=True,
    )


def render_archive_scope_lines(state: ArchiveWorkflowState) -> tuple[str, ...]:
    return (
        "Scope    : archive workflow",
        f"Mode     : {state.mode}",
        f"Archive  : {state.archive_command_count}",
        f"Validate : {state.validation_command_count}",
        "Evidence : explicit and traceable archive sections",
        f"Danger   : {'destructive' if state.destructive else 'non-destructive'}",
    )


def archive_has_work(state: ArchiveWorkflowState) -> bool:
    return state.archive_command_count > 0
