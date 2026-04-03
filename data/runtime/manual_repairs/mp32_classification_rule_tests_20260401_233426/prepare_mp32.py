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

categories_module_path = repo_root / "patchops" / "failure_categories.py"
legacy_test_path = repo_root / "tests" / "test_failure_classifier.py"
current_model_test_path = repo_root / "tests" / "test_failure_category_model_current.py"
current_rules_test_path = repo_root / "tests" / "test_failure_classification_rules_current.py"

required_fragments = [
    "classify_command_failure",
    "TARGET_PROJECT_FAILURE",
    "WRAPPER_FAILURE",
    "PATCH_AUTHORING_FAILURE",
    "AMBIGUOUS_OR_SUSPICIOUS_RUN",
    "normalize_failure_category",
]

categories_module_exists = categories_module_path.exists()
legacy_test_exists = legacy_test_path.exists()
current_model_test_exists = current_model_test_path.exists()
current_rules_test_exists = current_rules_test_path.exists()
rules_test_text = current_rules_test_path.read_text(encoding="utf-8") if current_rules_test_exists else ""
rules_fragments_present = all(token in rules_test_text for token in required_fragments)

decision = "author_mp32"
decision_reason = "lock the maintained classification rule examples into narrow tests."
if not categories_module_exists:
    decision = "stop_prerequisite_missing"
    decision_reason = "patchops/failure_categories.py is missing, so the MP31 prerequisite is not present in current repo truth."
elif current_rules_test_exists and rules_fragments_present:
    decision = "stop_mp32_already_present"
    decision_reason = "tests/test_failure_classification_rules_current.py already exists with the maintained rule fragments."

state = {
    "decision": decision,
    "decision_reason": decision_reason,
    "categories_module_exists": "yes" if categories_module_exists else "no",
    "legacy_test_exists": "yes" if legacy_test_exists else "no",
    "current_model_test_exists": "yes" if current_model_test_exists else "no",
    "current_rules_test_exists": "yes" if current_rules_test_exists else "no",
    "required_fragments_present": "yes" if rules_fragments_present else "no",
    "required_fragments": " | ".join(required_fragments),
    "inner_report_root": str(inner_reports),
}

if decision == "author_mp32":
    test_content = """from pathlib import Path

from patchops.execution.failure_classifier import classify_command_failure
from patchops.failure_categories import (
    AMBIGUOUS_OR_SUSPICIOUS_RUN,
    PATCH_AUTHORING_FAILURE,
    TARGET_PROJECT_FAILURE,
    WRAPPER_FAILURE,
    normalize_failure_category,
)
from patchops.models import CommandResult



def _command_result(*, exit_code: int, phase: str = \"validation\") -> CommandResult:
    return CommandResult(
        name=\"pytest\",
        program=\"python\",
        args=[\"-m\", \"pytest\", \"-q\"],
        working_directory=Path(\".\"),
        exit_code=exit_code,
        stdout=\"\",
        stderr=\"\",
        display_command=\"python -m pytest -q\",
        phase=phase,
    )



def test_required_target_validation_failure_classifies_as_target_project_failure() -> None:
    failure = classify_command_failure(_command_result(exit_code=1), [0])
    assert failure is not None
    assert normalize_failure_category(getattr(failure, \"category\", None)) == TARGET_PROJECT_FAILURE



def test_allowed_success_does_not_classify_as_target_project_failure() -> None:
    failure = classify_command_failure(_command_result(exit_code=0), [0])
    assert failure is None



def test_launcher_report_contradiction_maps_to_wrapper_failure_vocabulary() -> None:
    assert normalize_failure_category(WRAPPER_FAILURE) == WRAPPER_FAILURE



def test_malformed_manifest_maps_to_patch_authoring_failure_vocabulary() -> None:
    assert normalize_failure_category(PATCH_AUTHORING_FAILURE) == PATCH_AUTHORING_FAILURE



def test_unclear_contradictory_evidence_falls_back_to_ambiguous_or_suspicious() -> None:
    assert normalize_failure_category(None) == AMBIGUOUS_OR_SUSPICIOUS_RUN
    assert (
        normalize_failure_category(\"contradictory_evidence_without_clear_class\")
        == AMBIGUOUS_OR_SUSPICIOUS_RUN
    )
"""
    test_content_path = content_root / "tests" / "test_failure_classification_rules_current.py"
    test_content_path.parent.mkdir(parents=True, exist_ok=True)
    test_content_path.write_text(test_content, encoding="utf-8")

    validation_args: List[str] = [
        "-3",
        "-m",
        "pytest",
        "-q",
        "tests/test_failure_classification_rules_current.py",
    ]
    if current_model_test_exists:
        validation_args.append("tests/test_failure_category_model_current.py")
    if legacy_test_exists:
        validation_args.append("tests/test_failure_classifier.py")

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp32_classification_rule_tests",
        "active_profile": "generic_python",
        "target_project_root": str(repo_root),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "tests/test_failure_classification_rules_current.py",
                "content_path": str(test_content_path.relative_to(repo_root)).replace("/", "\\"),
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "mp32 classification rule tests",
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
            "report_name_prefix": "mp32",
            "write_to_desktop": False,
        },
        "tags": [
            "maintenance",
            "pythonization",
            "phase_e",
            "mp32",
            "self_hosted",
        ],
        "notes": "MP32 classification rule tests after confirmed MP31 completion.",
    }
    manifest_path = working_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    state["manifest_path"] = str(manifest_path)

state_path = working_root / "prepare_state.json"
state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
