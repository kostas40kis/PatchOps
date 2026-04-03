from __future__ import annotations

from typing import Any

from patchops.models import CommandResult, CommandSpec, WorkflowResult


FAIL_LABEL = "FAIL"


def _phase_specs(result: WorkflowResult, phase: str) -> list[CommandSpec]:
    if phase == "validation":
        return list(result.manifest.validation_commands)
    if phase == "smoke":
        return list(result.manifest.smoke_commands)
    if phase == "audit":
        return list(result.manifest.audit_commands)
    if phase == "cleanup":
        return list(result.manifest.cleanup_commands)
    if phase == "archive":
        return list(result.manifest.archive_commands)
    return []


def _pair_results_with_specs(result: WorkflowResult, phase: str, command_results: list[CommandResult]) -> list[tuple[CommandResult, CommandSpec | None]]:
    specs = _phase_specs(result, phase)
    if not command_results:
        return []
    if len(specs) == len(command_results):
        return list(zip(command_results, specs))

    by_name: dict[str, list[CommandSpec]] = {}
    for spec in specs:
        by_name.setdefault(spec.name, []).append(spec)

    consumed: dict[str, int] = {}
    pairs: list[tuple[CommandResult, CommandSpec | None]] = []
    for index, command_result in enumerate(command_results):
        spec: CommandSpec | None = None
        named_specs = by_name.get(command_result.name, [])
        used = consumed.get(command_result.name, 0)
        if used < len(named_specs):
            spec = named_specs[used]
            consumed[command_result.name] = used + 1
        elif index < len(specs):
            spec = specs[index]
        pairs.append((command_result, spec))
    return pairs


def _first_required_failure_exit_code(result: WorkflowResult) -> int | None:
    for phase, command_results in (
        ("validation", result.validation_results),
        ("smoke", result.smoke_results),
    ):
        for command_result, spec in _pair_results_with_specs(result, phase, command_results):
            allowed_exit_codes = spec.allowed_exit_codes if spec is not None else [0]
            if command_result.exit_code not in allowed_exit_codes:
                return command_result.exit_code
    return None


def derive_effective_summary_fields(result: WorkflowResult) -> dict[str, Any]:
    required_failure_exit_code = _first_required_failure_exit_code(result)
    if required_failure_exit_code is not None:
        return {
            "exit_code": required_failure_exit_code,
            "result_label": FAIL_LABEL,
            "source": "required_command_failure",
        }

    if result.failure is not None:
        return {
            "exit_code": result.exit_code if result.exit_code != 0 else 1,
            "result_label": FAIL_LABEL,
            "source": "workflow_failure",
        }

    if str(result.result_label).upper() == FAIL_LABEL:
        return {
            "exit_code": result.exit_code if result.exit_code != 0 else 1,
            "result_label": FAIL_LABEL,
            "source": "workflow_result",
        }

    return {
        "exit_code": result.exit_code,
        "result_label": result.result_label,
        "source": "workflow_result",
    }
