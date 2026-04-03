from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

from patchops.models import WorkflowResult


HANDOFF_DIRNAME = "handoff"
CURRENT_HANDOFF_FILENAME = "current_handoff.md"

DEFAULT_CURRENT_STAGE = "Stage 2 in progress"
DEFAULT_MUST_READ_FILES = (
    "docs/llm_usage.md",
    "docs/project_status.md",
    "docs/patch_ledger.md",
    "docs/manifest_schema.md",
    "docs/failure_repair_guide.md",
)
DEFAULT_DO_NOT_REDESIGN_NOTE = (
    "Keep PowerShell thin and reusable logic in Python unless the evidence forces deeper change."
)

_PATCH_TOKEN_RE = re.compile(r"patch[_\-\s]*(\d+(?:_\d+)?[a-zA-Z]?)", re.IGNORECASE)
_FIRST_INTEGER_RE = re.compile(r"(\d+)")


def _line(label: str, value: str) -> str:
    return f"{label:<22}: {value}"


def _stringify(value: Any) -> str:
    if value is None:
        return "(none)"
    return str(value)


def _failure_category_label(result: WorkflowResult) -> str:
    if result.failure is None:
        return "none"
    category = result.failure.category
    return getattr(category, "value", str(category))


def _patch_token_from_name(patch_name: str) -> str | None:
    match = _PATCH_TOKEN_RE.search(patch_name)
    if match is None:
        return None
    return match.group(1)


def _patch_label_from_name(patch_name: str) -> str:
    token = _patch_token_from_name(patch_name)
    if token is None:
        return patch_name
    return f"Patch {token.upper()}"


def _next_patch_label_from_name(patch_name: str) -> str:
    match = _FIRST_INTEGER_RE.search(patch_name)
    if match is None:
        return "the next planned patch"
    return f"Patch {int(match.group(1)) + 1}"


def current_status_label(result: WorkflowResult) -> str:
    return "pass" if result.result_label.upper() == "PASS" else "fail"


def latest_attempted_patch_label(result: WorkflowResult) -> str:
    return _patch_label_from_name(result.manifest.patch_name)


def latest_passed_patch_label(result: WorkflowResult) -> str:
    if result.result_label.upper() == "PASS":
        return latest_attempted_patch_label(result)
    return "unknown from this run"


def recommended_mode(result: WorkflowResult) -> str:
    if result.result_label.upper() == "PASS":
        return "new_patch"

    failure_class = _failure_category_label(result)
    if failure_class == "wrapper_failure":
        return "wrapper_only_retry"
    if failure_class == "target_project_failure":
        return "repair_patch"
    return "manual_review"


def recommended_next_action(result: WorkflowResult) -> str:
    if result.result_label.upper() == "PASS":
        return f"Continue with {_next_patch_label_from_name(result.manifest.patch_name)}."

    failure_class = _failure_category_label(result)
    if failure_class == "wrapper_failure":
        return "Keep the repair narrow. Prefer wrapper-only retry or wrapper-only repair."
    if failure_class == "target_project_failure":
        return "Keep the repair narrow. Write a repair patch for the failed target surface."
    return "Stop and inspect the latest report before widening scope."


def render_current_handoff_lines(
    result: WorkflowResult,
    *,
    current_stage: str = DEFAULT_CURRENT_STAGE,
    must_read_files: Iterable[str] = DEFAULT_MUST_READ_FILES,
    do_not_redesign_note: str = DEFAULT_DO_NOT_REDESIGN_NOTE,
) -> tuple[str, ...]:
    lines: list[str] = [
        "# PatchOps current handoff",
        "",
        "This file is the current human-readable resume point for a future LLM or operator.",
        "",
        "## Resume snapshot",
        "",
        _line("Project", "PatchOps"),
        _line("Wrapper Project Root", _stringify(result.wrapper_project_root)),
        _line("Target Project Root", _stringify(result.target_project_root)),
        _line("Current Stage", current_stage),
        _line("Latest Run Mode", result.mode),
        _line("Current Status", current_status_label(result)),
        _line("Latest Attempted Patch", latest_attempted_patch_label(result)),
        _line("Latest Passed Patch", latest_passed_patch_label(result)),
        _line("Latest Report Path", _stringify(result.report_path)),
        _line("Failure Class", _failure_category_label(result)),
        _line("Next Action", recommended_next_action(result)),
        _line("Next Recommended Mode", recommended_mode(result)),
        _line("Do Not Redesign", do_not_redesign_note),
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
    current_stage: str = DEFAULT_CURRENT_STAGE,
    must_read_files: Iterable[str] = DEFAULT_MUST_READ_FILES,
    do_not_redesign_note: str = DEFAULT_DO_NOT_REDESIGN_NOTE,
    handoff_path: str | Path | None = None,
) -> str:
    if handoff_path is None:
        path = result.wrapper_project_root / HANDOFF_DIRNAME / CURRENT_HANDOFF_FILENAME
    else:
        path = Path(handoff_path)

    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        render_current_handoff_lines(
            result,
            current_stage=current_stage,
            must_read_files=must_read_files,
            do_not_redesign_note=do_not_redesign_note,
        )
    ) + "\n"
    path.write_text(text, encoding="utf-8")
    return str(path)