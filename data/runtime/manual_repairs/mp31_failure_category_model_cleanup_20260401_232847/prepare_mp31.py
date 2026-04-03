from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

repo_root = Path(sys.argv[1]).resolve()
working_root = Path(sys.argv[2]).resolve()

content_root = working_root / "content"
inner_reports = working_root / "inner_reports"
content_root.mkdir(parents=True, exist_ok=True)
inner_reports.mkdir(parents=True, exist_ok=True)

module_path = repo_root / "patchops" / "failure_categories.py"
test_path = repo_root / "tests" / "test_failure_category_model_current.py"
legacy_test_path = repo_root / "tests" / "test_failure_classifier.py"

required_categories = [
    "target_project_failure",
    "wrapper_failure",
    "patch_authoring_failure",
    "ambiguous_or_suspicious_run",
]

module_exists = module_path.exists()
test_exists = test_path.exists()
module_text = module_path.read_text(encoding="utf-8") if module_exists else ""
module_has_all = all(token in module_text for token in required_categories)

decision = "author_mp31"
decision_reason = "formalize the maintained failure category model."
if module_exists and test_exists and module_has_all:
    decision = "stop_mp31_already_present"
    decision_reason = "patchops/failure_categories.py and the current-state test already exist."

state = {
    "decision": decision,
    "decision_reason": decision_reason,
    "module_exists": "yes" if module_exists else "no",
    "test_exists": "yes" if test_exists else "no",
    "legacy_test_exists": "yes" if legacy_test_path.exists() else "no",
    "required_categories_present": "yes" if module_has_all else "no",
    "required_categories": " | ".join(required_categories),
    "inner_report_root": str(inner_reports),
}

if decision == "author_mp31":
    module_content = """from __future__ import annotations

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
"""
    test_content = """from patchops.failure_categories import (
    AMBIGUOUS_OR_SUSPICIOUS_RUN,
    PATCH_AUTHORING_FAILURE,
    TARGET_PROJECT_FAILURE,
    WRAPPER_FAILURE,
    FailureCategoryModel,
    is_known_failure_category,
    known_failure_categories,
    normalize_failure_category,
    unique_failure_categories,
)


def test_failure_category_model_exposes_maintained_vocabulary() -> None:
    assert known_failure_categories() == (
        TARGET_PROJECT_FAILURE,
        WRAPPER_FAILURE,
        PATCH_AUTHORING_FAILURE,
        AMBIGUOUS_OR_SUSPICIOUS_RUN,
    )


def test_failure_category_model_dataclass_matches_tuple_order() -> None:
    model = FailureCategoryModel()
    assert model.as_tuple() == known_failure_categories()


def test_failure_category_normalization_falls_back_to_ambiguous() -> None:
    assert normalize_failure_category(None) == AMBIGUOUS_OR_SUSPICIOUS_RUN
    assert normalize_failure_category("not_a_real_class") == AMBIGUOUS_OR_SUSPICIOUS_RUN
    assert normalize_failure_category(" wrapper_failure ") == WRAPPER_FAILURE


def test_failure_category_recognition_and_uniqueness() -> None:
    assert is_known_failure_category(TARGET_PROJECT_FAILURE) is True
    assert is_known_failure_category("made_up") is False
    assert unique_failure_categories(
        [
            TARGET_PROJECT_FAILURE,
            " wrapper_failure ",
            None,
            "made_up",
            TARGET_PROJECT_FAILURE,
        ]
    ) == (
        TARGET_PROJECT_FAILURE,
        WRAPPER_FAILURE,
        AMBIGUOUS_OR_SUSPICIOUS_RUN,
    )
"""
    module_content_path = content_root / "patchops" / "failure_categories.py"
    module_content_path.parent.mkdir(parents=True, exist_ok=True)
    module_content_path.write_text(module_content, encoding="utf-8")

    test_content_path = content_root / "tests" / "test_failure_category_model_current.py"
    test_content_path.parent.mkdir(parents=True, exist_ok=True)
    test_content_path.write_text(test_content, encoding="utf-8")

    validation_args: List[str] = [
        "-3",
        "-m",
        "pytest",
        "-q",
        "tests/test_failure_category_model_current.py",
    ]
    if legacy_test_path.exists():
        validation_args.append("tests/test_failure_classifier.py")

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp31_failure_category_model_cleanup",
        "active_profile": "generic_python",
        "target_project_root": str(repo_root),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "patchops/failure_categories.py",
                "content_path": str(module_content_path.relative_to(repo_root)).replace("/", "\\"),
                "encoding": "utf-8",
            },
            {
                "path": "tests/test_failure_category_model_current.py",
                "content_path": str(test_content_path.relative_to(repo_root)).replace("/", "\\"),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "mp31 failure category model tests",
                "program": "py",
                "args": validation_args,
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(inner_reports),
            "report_name_prefix": "mp31",
            "write_to_desktop": False,
        },
        "tags": [
            "maintenance",
            "pythonization",
            "phase_e",
            "mp31",
            "self_hosted",
        ],
        "notes": "MP31 failure category model cleanup after confirmed MP30 completion.",
    }
    manifest_path = working_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    state["manifest_path"] = str(manifest_path)

state_path = working_root / "prepare_state.json"
state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")