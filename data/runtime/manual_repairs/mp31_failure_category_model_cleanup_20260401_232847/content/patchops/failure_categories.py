from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


TARGET_PROJECT_FAILURE = "target_project_failure"
WRAPPER_FAILURE = "wrapper_failure"
PATCH_AUTHORING_FAILURE = "patch_authoring_failure"
AMBIGUOUS_OR_SUSPICIOUS_RUN = "ambiguous_or_suspicious_run"

MAINTAINED_FAILURE_CATEGORIES: Tuple[str, ...] = (
    TARGET_PROJECT_FAILURE,
    WRAPPER_FAILURE,
    PATCH_AUTHORING_FAILURE,
    AMBIGUOUS_OR_SUSPICIOUS_RUN,
)


@dataclass(frozen=True)
class FailureCategoryModel:
    target_project_failure: str = TARGET_PROJECT_FAILURE
    wrapper_failure: str = WRAPPER_FAILURE
    patch_authoring_failure: str = PATCH_AUTHORING_FAILURE
    ambiguous_or_suspicious_run: str = AMBIGUOUS_OR_SUSPICIOUS_RUN

    def as_tuple(self) -> Tuple[str, ...]:
        return (
            self.target_project_failure,
            self.wrapper_failure,
            self.patch_authoring_failure,
            self.ambiguous_or_suspicious_run,
        )


def known_failure_categories() -> Tuple[str, ...]:
    return MAINTAINED_FAILURE_CATEGORIES


def is_known_failure_category(value: str) -> bool:
    return value in MAINTAINED_FAILURE_CATEGORIES


def normalize_failure_category(value: str | None) -> str:
    if value is None:
        return AMBIGUOUS_OR_SUSPICIOUS_RUN
    normalized = value.strip()
    if normalized in MAINTAINED_FAILURE_CATEGORIES:
        return normalized
    return AMBIGUOUS_OR_SUSPICIOUS_RUN


def unique_failure_categories(values: Iterable[str | None]) -> Tuple[str, ...]:
    ordered = []
    for value in values:
        normalized = normalize_failure_category(value)
        if normalized not in ordered:
            ordered.append(normalized)
    return tuple(ordered)
