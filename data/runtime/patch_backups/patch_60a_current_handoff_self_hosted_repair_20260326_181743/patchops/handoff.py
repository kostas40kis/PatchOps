from __future__ import annotations

import re
from pathlib import Path

from patchops.models import WorkflowResult


HANDOFF_DIRNAME = "handoff"
HANDOFF_FILENAME = "current_handoff.md"
DEFAULT_STAGE_LABEL = "Stage 2 in progress"
DEFAULT_MUST_READ_FILES = (
    "docs/llm_usage.md",
    "docs/project_status.md",
    "docs/patch_ledger.md",
    "docs/manifest_schema.md",
    "docs/failure_repair_guide.md",
)

_PATCH_NUMBER_RE = re.compile(r"patch[_\-\s]*(\d+(?:_[0-9]+)?[a-zA-Z]?)", re.IGNORECASE)
_FIRST_INTEGER_RE = re.compile(r"(\d+)")


def _line(label: str, value: str) -> str:
    return f"{label:<22}: {value}"


def _extract_patch_token(patch_name: str) -> str | None:
    match = _PATCH_NUMBER_RE.search(patch_name)
    if match is None:
        return None
    return match.group(1)


def _patch_label_from_name(patch_name: str) -> str:
    token = _extract_patch_token(patch_name)
    if token is None:
        return patch_name
    return f"Patch {token.upper()}"


def _next_patch_label_from_name(patch_name: str) -> str:
    match = _FIRST_INTEGER_RE.search(patch_name)
    if match is None:
        return "the next planned patch"
    value = int(match.group(1)) + 1
    return f"Patch {value}"


def _latest_status(result: WorkflowResult) -> str:
    return "pass" if result.result_label.upper() == "PASS" else "fail"


def _latest_passed_patch(result: WorkflowResult) -> str:
    if result.result_label.upper() == "PASS":
        return _patch_label_from_name(result.manifest.patch_name)
    return "unknown from this run"


def _failure_class(result: WorkflowResult) -> str:
    if result.failure is None:
        return "none"
    return str(result.failure.category)


def _next_recommended_mode(result: WorkflowResult) -> str:
    if result.result_label.upper() == "PASS":
        return "new_patch"
    if result.failure is None:
        return "manual_review"
    if str(result.failure.category) == "wrapper_failure":
        return "wrapper_only_retry"
    if str(result.failure.category) == "target_project_failure":
        return "repair_patch"
    return "manual_review"


def _next_action(result: WorkflowResult) -> str:
    if result.result_label.upper() == "PASS":
        return f"Continue with {_next_patch_label_from_name(result.manifest.patch_name)}."
    if result.failure is None:
        return "Stop and inspect the latest report before widening scope."
    if str(result.failure.category) == "wrapper_failure":
        return "Keep the repair narrow. Prefer wrapper-only retry or a wrapper-only repair."
    if str(result.failure.category) == "target_project_failure":
        return "Keep the repair narrow. Write a repair patch for the failed target surface."
    return "Stop for manual review before changing architecture."


def render_current_handoff_lines(
    result: WorkflowResult,
    *,
    current_stage: str = DEFAULT_STAGE_LABEL,
    must_read_files: tuple[str, ...] = DEFAULT_MUST_READ_FILES,
) -> tuple[str, ...]:
    latest_attempted_patch = _patch_label_from_name(result.manifest.patch_name)
    latest_passed_patch = _latest_passed_patch(result)
    latest_status = _latest_status(result)
    failure_class = _failure_class(result)
    next_action = _next_action(result)
    next_mode = _next_recommended_mode(result)

    lines: list[str] = [
        "# PatchOps current handoff",
        "",
        "This file is the current human-readable resume point for a future LLM or operator.",
        "",
        "## Resume snapshot",
        "",
        _line("Project", "PatchOps"),
        _line("Wrapper Project Root", str(result.wrapper_project_root)),
        _line("Target Project Root", str(result.target_project_root)),
        _line("Current Stage", current_stage),
        _line("Latest Run Mode", result.mode),
        _line("Current Status", latest_status),
        _line("Latest Attempted Patch", latest_attempted_patch),
        _line("Latest Passed Patch", latest_passed_patch),
        _line("Latest Report Path", str(result.report_path)),
        _line("Failure Class", failure_class),
        _line("Next Action", next_action),
        _line("Next Recommended Mode", next_mode),
        _line(
            "Do Not Redesign",
            "Keep PowerShell thin and reusable logic in Python unless the evidence forces deeper change.",
        ),
        "",
        "## Must-read files before acting",
        "",
    ]

    for item in must_read_files:
        lines.append(f"- `{item}`")

    lines.extend(
        [
            "",
            "## Resume rules",
            "",
            "- PatchOps owns patch application, validation, evidence, retry, and handoff mechanics.",
            "- Target repos own their own business logic.",
            "- Prefer narrow repair over broad rewrite.",
            "- Preserve the one-report evidence contract.",
        ]
    )

    return tuple(lines)


def write_current_handoff(
    result: WorkflowResult,
    *,
    current_stage: str = DEFAULT_STAGE_LABEL,
    must_read_files: tuple[str, ...] = DEFAULT_MUST_READ_FILES,
    handoff_path: str | Path | None = None,
) -> str:
    if handoff_path is None:
        path = result.wrapper_project_root / HANDOFF_DIRNAME / HANDOFF_FILENAME
    else:
        path = Path(handoff_path)

    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        render_current_handoff_lines(
            result,
            current_stage=current_stage,
            must_read_files=must_read_files,
        )
    ) + "\n"
    path.write_text(text, encoding="utf-8")
    return str(path)