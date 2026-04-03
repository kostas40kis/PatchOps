from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from patchops.models import WorkflowResult
from patchops.result_integrity import derive_effective_summary_fields


HANDOFF_DIRNAME = "handoff"
CURRENT_HANDOFF_FILENAME = "current_handoff.md"
CURRENT_HANDOFF_JSON_FILENAME = "current_handoff.json"
LATEST_REPORT_COPY_FILENAME = "latest_report_copy.txt"
LATEST_REPORT_INDEX_FILENAME = "latest_report_index.json"
NEXT_PROMPT_FILENAME = "next_prompt.txt"
BUNDLE_DIRNAME = "bundle"

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
DEFAULT_RESUME_RULES = (
    "PatchOps owns patch application, validation, evidence, retry, and handoff mechanics.",
    "Target repos own their own business logic.",
    "Prefer narrow repair over broad rewrite.",
    "Preserve the one-report evidence contract.",
)

_PATCH_TOKEN_RE = re.compile(r"patch[_\-\s]*(\d+(?:_\d+)?[a-zA-Z]?)", re.IGNORECASE)
_FIRST_INTEGER_RE = re.compile(r"(\d+)")

PASS_LABEL = "PASS"
WRAPPER_FAILURE = "wrapper_failure"
TARGET_FAILURE = "target_project_failure"
NEW_PATCH_MODE = "new_patch"
REPAIR_PATCH_MODE = "repair_patch"
VERIFY_ONLY_MODE = "verify_only"
WRAPPER_ONLY_RETRY_MODE = "wrapper_only_retry"
MANUAL_REVIEW_MODE = "manual_review"


@dataclass(frozen=True)
class ExportedReportState:
    wrapper_project_root: Path
    target_project_root: Path
    latest_run_mode: str
    manifest_patch_name: str
    current_status: str
    failure_class: str
    report_path: Path


def _line(label: str, value: str) -> str:
    return f"{label:<22}: {value}"


def _stringify(value: Any) -> str:
    if value is None:
        return "(none)"
    return str(value)


def _failure_category_label(result: WorkflowResult) -> str:
    if result.failure is not None:
        category = result.failure.category
        return getattr(category, "value", str(category))

    effective = derive_effective_summary_fields(result)
    if effective["source"] == "required_command_failure":
        return TARGET_FAILURE
    return "none"


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
    effective = derive_effective_summary_fields(result)
    return "pass" if str(effective["result_label"]).upper() == PASS_LABEL else "fail"


def latest_attempted_patch_label(result: WorkflowResult) -> str:
    return _patch_label_from_name(result.manifest.patch_name)


def latest_passed_patch_label(result: WorkflowResult) -> str:
    effective = derive_effective_summary_fields(result)
    if str(effective["result_label"]).upper() == PASS_LABEL:
        return latest_attempted_patch_label(result)
    return "unknown from this run"


def _expected_target_paths(result: WorkflowResult) -> tuple[Path, ...]:
    return tuple(result.target_project_root / spec.path for spec in result.manifest.files_to_write)


def _existing_target_paths(result: WorkflowResult) -> tuple[Path, ...]:
    return tuple(path for path in _expected_target_paths(result) if path.exists())


def _missing_target_paths(result: WorkflowResult) -> tuple[Path, ...]:
    return tuple(path for path in _expected_target_paths(result) if not path.exists())


def build_next_action_recommendation(result: WorkflowResult) -> dict[str, Any]:
    effective = derive_effective_summary_fields(result)
    effective_label = str(effective["result_label"]).upper()
    failure_class = _failure_category_label(result)
    expected_paths = _expected_target_paths(result)
    existing_paths = _existing_target_paths(result)
    missing_paths = _missing_target_paths(result)
    expected_count = len(expected_paths)
    existing_count = len(existing_paths)
    missing_count = len(missing_paths)

    if effective_label == PASS_LABEL:
        return {
            "recommended_mode": NEW_PATCH_MODE,
            "next_action": f"Continue with {_next_patch_label_from_name(result.manifest.patch_name)}.",
            "rationale": "The latest run passed, so the trustworthy next step is the next planned patch.",
            "escalation_required": False,
            "next_recommended_patch": _next_patch_label_from_name(result.manifest.patch_name),
            "known_blockers": [],
            "expected_target_count": expected_count,
            "existing_target_count": existing_count,
            "missing_target_count": missing_count,
        }

    if failure_class == TARGET_FAILURE:
        if result.mode == VERIFY_ONLY_MODE:
            action = "Fix the target content, then rerun the normal patch flow or a deliberate verify-only rerun once the content issue is repaired."
            rationale = "Verify-only surfaced a real target-project failure, so the problem is content rather than wrapper evidence."
        else:
            action = "Keep the repair narrow. Write a repair patch for the failed target surface."
            rationale = "PatchOps executed and surfaced a real target-project failure, so the next step is a narrow content repair."
        return {
            "recommended_mode": REPAIR_PATCH_MODE,
            "next_action": action,
            "rationale": rationale,
            "escalation_required": False,
            "next_recommended_patch": None,
            "known_blockers": [],
            "expected_target_count": expected_count,
            "existing_target_count": existing_count,
            "missing_target_count": missing_count,
        }

    if failure_class == TARGET_FAILURE and effective["source"] == "required_command_failure" and result.failure is None:
        return {
            "recommended_mode": REPAIR_PATCH_MODE,
            "next_action": "Keep the repair narrow. Required command evidence failed, so treat this as a target repair until proven otherwise.",
            "rationale": "Required validation or smoke evidence failed outside allowed_exit_codes even though the workflow result looked successful, so the safe next step is a narrow repair path.",
            "escalation_required": False,
            "next_recommended_patch": None,
            "known_blockers": [],
            "expected_target_count": expected_count,
            "existing_target_count": existing_count,
            "missing_target_count": missing_count,
        }

    if failure_class == WRAPPER_FAILURE:
        if missing_count > 0:
            return {
                "recommended_mode": MANUAL_REVIEW_MODE,
                "next_action": "Stop for manual review. Expected target files are missing, so a narrow rerun is not yet trustworthy.",
                "rationale": "The wrapper failed and expected target files are missing, which means the repo state is too ambiguous for a safe narrow retry.",
                "escalation_required": True,
                "next_recommended_patch": None,
                "known_blockers": [str(path) for path in missing_paths],
                "expected_target_count": expected_count,
                "existing_target_count": existing_count,
                "missing_target_count": missing_count,
            }

        if result.mode == VERIFY_ONLY_MODE and existing_count > 0:
            return {
                "recommended_mode": VERIFY_ONLY_MODE,
                "next_action": "Use verify-only rerun to re-check and re-evidence the already-present target files.",
                "rationale": "The failure is in wrapper evidence and the target files already exist, so verify-only remains the narrowest trustworthy path.",
                "escalation_required": False,
                "next_recommended_patch": None,
                "known_blockers": [],
                "expected_target_count": expected_count,
                "existing_target_count": existing_count,
                "missing_target_count": missing_count,
            }

        if result.mode in ("apply", WRAPPER_ONLY_RETRY_MODE) and existing_count > 0:
            return {
                "recommended_mode": WRAPPER_ONLY_RETRY_MODE,
                "next_action": "Use wrapper-only retry to recover evidence and rerun narrowly without widening back into a full apply.",
                "rationale": "The wrapper failed after or around likely content success, and the expected target files already exist.",
                "escalation_required": False,
                "next_recommended_patch": None,
                "known_blockers": [],
                "expected_target_count": expected_count,
                "existing_target_count": existing_count,
                "missing_target_count": missing_count,
            }

        return {
            "recommended_mode": MANUAL_REVIEW_MODE,
            "next_action": "Stop for manual review before choosing a retry mode.",
            "rationale": "The wrapper failed, but the repo state does not make a safe narrow retry obvious yet.",
            "escalation_required": True,
            "next_recommended_patch": None,
            "known_blockers": [],
            "expected_target_count": expected_count,
            "existing_target_count": existing_count,
            "missing_target_count": missing_count,
        }

    return {
        "recommended_mode": MANUAL_REVIEW_MODE,
        "next_action": "Stop and inspect the latest report before widening scope.",
        "rationale": "The failure state is not explicit enough to choose a trustworthy narrower path automatically.",
        "escalation_required": True,
        "next_recommended_patch": None,
        "known_blockers": [],
        "expected_target_count": expected_count,
        "existing_target_count": existing_count,
        "missing_target_count": missing_count,
    }


def build_current_handoff_payload(
    result: WorkflowResult,
    *,
    current_stage: str = DEFAULT_CURRENT_STAGE,
    must_read_files: Iterable[str] = DEFAULT_MUST_READ_FILES,
    do_not_redesign_note: str = DEFAULT_DO_NOT_REDESIGN_NOTE,
    resume_rules: Iterable[str] = DEFAULT_RESUME_RULES,
) -> dict[str, Any]:
    must_read = [str(item) for item in must_read_files]
    rules = [str(item) for item in resume_rules]
    recommendation = build_next_action_recommendation(result)

    return {
        "schema_version": 1,
        "project": "PatchOps",
        "current_stage": current_stage,
        "repo_state": {
            "wrapper_project_root": _stringify(result.wrapper_project_root),
            "target_project_root": _stringify(result.target_project_root),
            "latest_run_mode": result.mode,
            "current_status": current_status_label(result),
            "failure_class": _failure_category_label(result),
            "latest_report_path": _stringify(result.report_path),
        },
        "latest_patch": {
            "manifest_patch_name": result.manifest.patch_name,
            "latest_attempted_patch": latest_attempted_patch_label(result),
            "latest_passed_patch": latest_passed_patch_label(result),
        },
        "resume": {
            "next_action": recommendation["next_action"],
            "next_recommended_mode": recommendation["recommended_mode"],
            "do_not_redesign_note": do_not_redesign_note,
        },
        "recommendation": recommendation,
        "required_reading": must_read,
        "resume_rules": rules,
    }


def build_latest_report_index_payload(
    result: WorkflowResult,
    *,
    latest_report_copy_path: str | Path | None = None,
) -> dict[str, Any]:
    report_path = Path(result.report_path)
    if latest_report_copy_path is None:
        copy_path = result.wrapper_project_root / HANDOFF_DIRNAME / LATEST_REPORT_COPY_FILENAME
    else:
        copy_path = Path(latest_report_copy_path)

    recommendation = build_next_action_recommendation(result)

    return {
        "schema_version": 1,
        "project": "PatchOps",
        "manifest_patch_name": result.manifest.patch_name,
        "latest_attempted_patch": latest_attempted_patch_label(result),
        "latest_passed_patch": latest_passed_patch_label(result),
        "latest_run_mode": result.mode,
        "current_status": current_status_label(result),
        "failure_class": _failure_category_label(result),
        "latest_report_path": str(report_path),
        "latest_report_exists": report_path.exists(),
        "latest_report_copy_path": str(copy_path),
        "latest_report_copy_filename": copy_path.name,
        "next_recommended_mode": recommendation["recommended_mode"],
        "next_action": recommendation["next_action"],
        "escalation_required": recommendation["escalation_required"],
    }


def render_current_handoff_lines(
    result: WorkflowResult,
    *,
    current_stage: str = DEFAULT_CURRENT_STAGE,
    must_read_files: Iterable[str] = DEFAULT_MUST_READ_FILES,
    do_not_redesign_note: str = DEFAULT_DO_NOT_REDESIGN_NOTE,
) -> tuple[str, ...]:
    recommendation = build_next_action_recommendation(result)

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
        _line("Next Action", recommendation["next_action"]),
        _line("Next Recommended Mode", recommendation["recommended_mode"]),
        _line("Recommendation Why", recommendation["rationale"]),
        _line("Escalation Required", "yes" if recommendation["escalation_required"] else "no"),
        _line("Known Blockers", str(len(recommendation["known_blockers"]))),
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
            "## Recommendation details",
            "",
            f"- expected target files: {recommendation['expected_target_count']}",
            f"- existing expected files: {recommendation['existing_target_count']}",
            f"- missing expected files: {recommendation['missing_target_count']}",
        ]
    )

    if recommendation["known_blockers"]:
        lines.append("- blockers:")
        lines.extend(f"  - `{item}`" for item in recommendation["known_blockers"])

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


def write_current_handoff_json(
    result: WorkflowResult,
    *,
    current_stage: str = DEFAULT_CURRENT_STAGE,
    must_read_files: Iterable[str] = DEFAULT_MUST_READ_FILES,
    do_not_redesign_note: str = DEFAULT_DO_NOT_REDESIGN_NOTE,
    resume_rules: Iterable[str] = DEFAULT_RESUME_RULES,
    handoff_json_path: str | Path | None = None,
) -> str:
    if handoff_json_path is None:
        path = result.wrapper_project_root / HANDOFF_DIRNAME / CURRENT_HANDOFF_JSON_FILENAME
    else:
        path = Path(handoff_json_path)

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_current_handoff_payload(
        result,
        current_stage=current_stage,
        must_read_files=must_read_files,
        do_not_redesign_note=do_not_redesign_note,
        resume_rules=resume_rules,
    )
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")
    return str(path)


def write_latest_report_copy(
    result: WorkflowResult,
    *,
    latest_report_copy_path: str | Path | None = None,
) -> str:
    source_path = Path(result.report_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Latest report path does not exist: {source_path}")

    if latest_report_copy_path is None:
        destination = result.wrapper_project_root / HANDOFF_DIRNAME / LATEST_REPORT_COPY_FILENAME
    else:
        destination = Path(latest_report_copy_path)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
    return str(destination)


def write_latest_report_index(
    result: WorkflowResult,
    *,
    latest_report_copy_path: str | Path | None = None,
    latest_report_index_path: str | Path | None = None,
) -> str:
    if latest_report_copy_path is None:
        copy_path = result.wrapper_project_root / HANDOFF_DIRNAME / LATEST_REPORT_COPY_FILENAME
    else:
        copy_path = Path(latest_report_copy_path)

    if latest_report_index_path is None:
        index_path = result.wrapper_project_root / HANDOFF_DIRNAME / LATEST_REPORT_INDEX_FILENAME
    else:
        index_path = Path(latest_report_index_path)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_latest_report_index_payload(
        result,
        latest_report_copy_path=copy_path,
    )
    index_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(index_path)


def _report_field(text: str, label: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(label)}\s*:\s*(.+)$", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(1).strip()


def _mode_from_report_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    first_line = lines[0].upper() if lines else ""
    if "WRAPPER" in first_line and "RETRY" in first_line:
        return WRAPPER_ONLY_RETRY_MODE
    if "VERIFY" in first_line:
        return VERIFY_ONLY_MODE
    return "apply"


def _build_exported_report_state(
    report_path: str | Path | None,
    *,
    wrapper_project_root: str | Path | None = None,
) -> ExportedReportState:
    resolved_wrapper_root = (
        Path(wrapper_project_root).resolve()
        if wrapper_project_root is not None
        else Path(__file__).resolve().parents[1]
    )
    handoff_root = resolved_wrapper_root / HANDOFF_DIRNAME

    if report_path is None:
        fallback_report = handoff_root / LATEST_REPORT_COPY_FILENAME
        if not fallback_report.exists():
            raise FileNotFoundError(
                "No report path was supplied and handoff/latest_report_copy.txt does not exist yet."
            )
        resolved_report_path = fallback_report.resolve()
    else:
        resolved_report_path = Path(report_path).resolve()

    if not resolved_report_path.exists():
        raise FileNotFoundError(f"Latest report path does not exist: {resolved_report_path}")

    text = resolved_report_path.read_text(encoding="utf-8")
    manifest_patch_name = _report_field(text, "Patch Name") or "unknown_patch"
    target_project_root_value = _report_field(text, "Target Project Root")
    target_project_root = (
        Path(target_project_root_value).resolve()
        if target_project_root_value and target_project_root_value != "(none)"
        else resolved_wrapper_root
    )
    result_label = (_report_field(text, "Result") or "FAIL").upper()
    current_status = "pass" if result_label == PASS_LABEL else "fail"
    failure_class = _report_field(text, "Category") or "none"

    return ExportedReportState(
        wrapper_project_root=resolved_wrapper_root,
        target_project_root=target_project_root,
        latest_run_mode=_mode_from_report_text(text),
        manifest_patch_name=manifest_patch_name,
        current_status=current_status,
        failure_class=failure_class,
        report_path=resolved_report_path,
    )


def _latest_attempted_patch_label_from_state(state: ExportedReportState) -> str:
    return _patch_label_from_name(state.manifest_patch_name)


def _latest_passed_patch_label_from_state(state: ExportedReportState) -> str:
    if state.current_status == "pass":
        return _latest_attempted_patch_label_from_state(state)
    return "unknown from this run"


def build_next_action_recommendation_from_report_state(state: ExportedReportState) -> dict[str, Any]:
    if state.current_status == "pass":
        return {
            "recommended_mode": NEW_PATCH_MODE,
            "next_action": f"Continue with {_next_patch_label_from_name(state.manifest_patch_name)}.",
            "rationale": "The latest exported report passed, so the trustworthy next step is the next planned patch.",
            "escalation_required": False,
            "next_recommended_patch": _next_patch_label_from_name(state.manifest_patch_name),
            "known_blockers": [],
        }

    if state.failure_class == TARGET_FAILURE:
        return {
            "recommended_mode": REPAIR_PATCH_MODE,
            "next_action": "Keep the repair narrow. Write a repair patch for the failed target surface.",
            "rationale": "The exported report shows a target-project failure, so the next step is a narrow target repair.",
            "escalation_required": False,
            "next_recommended_patch": None,
            "known_blockers": [],
        }

    if state.failure_class == WRAPPER_FAILURE:
        return {
            "recommended_mode": WRAPPER_ONLY_RETRY_MODE,
            "next_action": "Use wrapper-only retry or a narrow wrapper repair to recover the handoff and evidence surface.",
            "rationale": "The exported report shows a wrapper failure, so the next step should stay on the wrapper/evidence side.",
            "escalation_required": False,
            "next_recommended_patch": None,
            "known_blockers": [],
        }

    return {
        "recommended_mode": MANUAL_REVIEW_MODE,
        "next_action": "Stop and inspect the latest report before widening scope.",
        "rationale": "The exported report does not provide enough stable signal to choose a narrower path automatically.",
        "escalation_required": True,
        "next_recommended_patch": None,
        "known_blockers": [],
    }


def build_current_handoff_payload_from_report_state(
    state: ExportedReportState,
    *,
    current_stage: str = DEFAULT_CURRENT_STAGE,
    must_read_files: Iterable[str] = DEFAULT_MUST_READ_FILES,
    do_not_redesign_note: str = DEFAULT_DO_NOT_REDESIGN_NOTE,
    resume_rules: Iterable[str] = DEFAULT_RESUME_RULES,
) -> dict[str, Any]:
    recommendation = build_next_action_recommendation_from_report_state(state)

    return {
        "schema_version": 1,
        "project": "PatchOps",
        "current_stage": current_stage,
        "repo_state": {
            "wrapper_project_root": str(state.wrapper_project_root),
            "target_project_root": str(state.target_project_root),
            "latest_run_mode": state.latest_run_mode,
            "current_status": state.current_status,
            "failure_class": state.failure_class,
            "latest_report_path": str(state.report_path),
        },
        "latest_patch": {
            "manifest_patch_name": state.manifest_patch_name,
            "latest_attempted_patch": _latest_attempted_patch_label_from_state(state),
            "latest_passed_patch": _latest_passed_patch_label_from_state(state),
        },
        "resume": {
            "next_action": recommendation["next_action"],
            "next_recommended_mode": recommendation["recommended_mode"],
            "do_not_redesign_note": do_not_redesign_note,
        },
        "recommendation": recommendation,
        "required_reading": [str(item) for item in must_read_files],
        "resume_rules": [str(item) for item in resume_rules],
    }


def build_latest_report_index_payload_from_report_state(
    state: ExportedReportState,
    *,
    latest_report_copy_path: str | Path,
) -> dict[str, Any]:
    recommendation = build_next_action_recommendation_from_report_state(state)
    copy_path = Path(latest_report_copy_path)

    return {
        "schema_version": 1,
        "project": "PatchOps",
        "manifest_patch_name": state.manifest_patch_name,
        "latest_attempted_patch": _latest_attempted_patch_label_from_state(state),
        "latest_passed_patch": _latest_passed_patch_label_from_state(state),
        "latest_run_mode": state.latest_run_mode,
        "current_status": state.current_status,
        "failure_class": state.failure_class,
        "latest_report_path": str(state.report_path),
        "latest_report_exists": state.report_path.exists(),
        "latest_report_copy_path": str(copy_path),
        "latest_report_copy_filename": copy_path.name,
        "next_recommended_mode": recommendation["recommended_mode"],
        "next_action": recommendation["next_action"],
        "escalation_required": recommendation["escalation_required"],
    }


def render_current_handoff_lines_from_report_state(
    state: ExportedReportState,
    *,
    current_stage: str = DEFAULT_CURRENT_STAGE,
    must_read_files: Iterable[str] = DEFAULT_MUST_READ_FILES,
    do_not_redesign_note: str = DEFAULT_DO_NOT_REDESIGN_NOTE,
) -> tuple[str, ...]:
    recommendation = build_next_action_recommendation_from_report_state(state)

    lines: list[str] = [
        "# PatchOps current handoff",
        "",
        "This file is the current human-readable resume point for a future LLM or operator.",
        "",
        "## Resume snapshot",
        "",
        _line("Project", "PatchOps"),
        _line("Wrapper Project Root", str(state.wrapper_project_root)),
        _line("Target Project Root", str(state.target_project_root)),
        _line("Current Stage", current_stage),
        _line("Latest Run Mode", state.latest_run_mode),
        _line("Current Status", state.current_status),
        _line("Latest Attempted Patch", _latest_attempted_patch_label_from_state(state)),
        _line("Latest Passed Patch", _latest_passed_patch_label_from_state(state)),
        _line("Latest Report Path", str(state.report_path)),
        _line("Failure Class", state.failure_class),
        _line("Next Action", recommendation["next_action"]),
        _line("Next Recommended Mode", recommendation["recommended_mode"]),
        _line("Recommendation Why", recommendation["rationale"]),
        _line("Escalation Required", "yes" if recommendation["escalation_required"] else "no"),
        _line("Known Blockers", str(len(recommendation["known_blockers"]))),
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


def build_next_prompt_text_from_report_state(
    state: ExportedReportState,
    *,
    current_stage: str = DEFAULT_CURRENT_STAGE,
) -> str:
    recommendation = build_next_action_recommendation_from_report_state(state)
    lines = [
        f"You are taking over the PatchOps project at {state.wrapper_project_root}.",
        "",
        "Read these files in this order:",
        f"1. handoff/{CURRENT_HANDOFF_FILENAME}",
        f"2. handoff/{CURRENT_HANDOFF_JSON_FILENAME}",
        f"3. handoff/{LATEST_REPORT_COPY_FILENAME}",
        "",
        "Your task is to perform the exact next recommended action described in the handoff.",
        "",
        "Current exported state:",
        f"- current stage: {current_stage}",
        f"- latest attempted patch: {_latest_attempted_patch_label_from_state(state)}",
        f"- latest passed patch: {_latest_passed_patch_label_from_state(state)}",
        f"- failure class: {state.failure_class}",
        f"- next action: {recommendation['next_action']}",
        "",
        "Rules:",
        "- keep PowerShell thin",
        "- keep reusable logic in Python",
        "- preserve the one-report evidence contract",
        "- do not move target-repo business logic into PatchOps",
        "- do not redesign the architecture unless the handoff explicitly says architecture drift is the real problem",
        "",
        "After reading the handoff, briefly restate:",
        "- current state",
        "- latest attempted patch",
        "- failure class",
        "- next action",
        "",
        "Then produce only the next repair patch or next planned patch.",
    ]
    return "\n".join(lines) + "\n"


def export_handoff_bundle(
    *,
    report_path: str | Path | None = None,
    wrapper_project_root: str | Path | None = None,
    current_stage: str = DEFAULT_CURRENT_STAGE,
    bundle_name: str = "current",
) -> dict[str, Any]:
    state = _build_exported_report_state(
        report_path,
        wrapper_project_root=wrapper_project_root,
    )
    handoff_root = state.wrapper_project_root / HANDOFF_DIRNAME
    handoff_root.mkdir(parents=True, exist_ok=True)

    current_handoff_path = handoff_root / CURRENT_HANDOFF_FILENAME
    current_handoff_json_path = handoff_root / CURRENT_HANDOFF_JSON_FILENAME
    latest_report_copy_path = handoff_root / LATEST_REPORT_COPY_FILENAME
    latest_report_index_path = handoff_root / LATEST_REPORT_INDEX_FILENAME
    next_prompt_path = handoff_root / NEXT_PROMPT_FILENAME

    current_handoff_path.write_text(
        "\n".join(
            render_current_handoff_lines_from_report_state(
                state,
                current_stage=current_stage,
            )
        ) + "\n",
        encoding="utf-8",
    )

    current_handoff_json_path.write_text(
        json.dumps(
            build_current_handoff_payload_from_report_state(
                state,
                current_stage=current_stage,
            ),
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    latest_report_copy_path.write_text(
        state.report_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    latest_report_index_path.write_text(
        json.dumps(
            build_latest_report_index_payload_from_report_state(
                state,
                latest_report_copy_path=latest_report_copy_path,
            ),
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    next_prompt_path.write_text(
        build_next_prompt_text_from_report_state(
            state,
            current_stage=current_stage,
        ),
        encoding="utf-8",
    )

    bundle_root = handoff_root / BUNDLE_DIRNAME / bundle_name
    bundle_root.mkdir(parents=True, exist_ok=True)

    bundle_files = []
    for source in (
        current_handoff_path,
        current_handoff_json_path,
        latest_report_copy_path,
        latest_report_index_path,
        next_prompt_path,
    ):
        destination = bundle_root / source.name
        shutil.copyfile(source, destination)
        bundle_files.append(str(destination))

    recommendation = build_next_action_recommendation_from_report_state(state)

    return {
        "project": "PatchOps",
        "wrapper_project_root": str(state.wrapper_project_root),
        "target_project_root": str(state.target_project_root),
        "latest_run_mode": state.latest_run_mode,
        "current_status": state.current_status,
        "failure_class": state.failure_class,
        "latest_attempted_patch": _latest_attempted_patch_label_from_state(state),
        "latest_passed_patch": _latest_passed_patch_label_from_state(state),
        "next_action": recommendation["next_action"],
        "next_recommended_mode": recommendation["recommended_mode"],
        "report_path": str(state.report_path),
        "handoff_root": str(handoff_root),
        "bundle_root": str(bundle_root),
        "next_prompt_path": str(next_prompt_path),
        "written_files": [
            str(current_handoff_path),
            str(current_handoff_json_path),
            str(latest_report_copy_path),
            str(latest_report_index_path),
            str(next_prompt_path),
        ],
        "bundle_files": bundle_files,
    }

