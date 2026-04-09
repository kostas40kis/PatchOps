from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from patchops.failure_categories import normalize_failure_category
from patchops.rerun_decisions import (
    VERIFY_ONLY,
    WRAPPER_ONLY_REPAIR,
    should_recommend_verify_only,
    should_recommend_wrapper_only_repair,
)


@dataclass(frozen=True)
class FailureContinuationMetadata:
    failure_class: str
    failure_reason: str
    recommended_next_mode: str | None
    category_display: str
    message_display: str
    details_display: str | None


def failure_category_label(result: Any) -> str:
    failure = getattr(result, "failure", None)
    if failure is None:
        return "none"
    category = getattr(failure, "category", None)
    if category is None:
        return "none"
    raw = getattr(category, "value", category)
    return normalize_failure_category(raw)


def recommended_next_mode_label(result: Any) -> str | None:
    failure = getattr(result, "failure", None)
    if failure is None:
        return None

    failure_class = failure_category_label(result)
    target_content_already_present = bool(getattr(result, "target_content_already_present", False))
    writes_applied_by_wrapper = bool(getattr(result, "writes_applied_by_wrapper", False))

    if should_recommend_verify_only(
        failure_class=failure_class,
        target_content_already_present=target_content_already_present,
        writes_applied_by_wrapper=writes_applied_by_wrapper,
    ):
        return VERIFY_ONLY
    if should_recommend_wrapper_only_repair(
        failure_class=failure_class,
        target_content_already_present=target_content_already_present,
        writes_applied_by_wrapper=writes_applied_by_wrapper,
    ):
        return WRAPPER_ONLY_REPAIR
    if failure_class == "target_project_failure":
        return "content_repair"
    return None


def build_failure_continuation_metadata(result: Any) -> FailureContinuationMetadata | None:
    failure = getattr(result, "failure", None)
    if failure is None:
        return None

    failure_class = failure_category_label(result)
    category_display = str(getattr(failure, "category", failure_class))
    message_display = str(getattr(failure, "message", "") or "")
    details = getattr(failure, "details", None)

    return FailureContinuationMetadata(
        failure_class=failure_class,
        failure_reason=message_display,
        recommended_next_mode=recommended_next_mode_label(result),
        category_display=category_display,
        message_display=message_display,
        details_display=str(details) if details else None,
    )
