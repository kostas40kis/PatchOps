from __future__ import annotations

import json
import sys
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"
    inner_report_root = working_root / "inner_reports"
    content_root.mkdir(parents=True, exist_ok=True)
    inner_report_root.mkdir(parents=True, exist_ok=True)

    rerun_path = wrapper_root / "patchops" / "rerun_decisions.py"
    current_test_path = wrapper_root / "tests" / "test_wrapper_retry_decision_helper_current.py"

    if not rerun_path.exists():
        raise SystemExit("MP37 prerequisite missing: patchops/rerun_decisions.py not found.")

    source = rerun_path.read_text(encoding="utf-8")

    helper_name = "should_recommend_wrapper_only_repair"
    helper_exists = helper_name in source
    verify_helper_present = "should_recommend_verify_only" in source
    current_test_exists = current_test_path.exists()

    required_fragments = [
        helper_name,
        "WRAPPER_ONLY_REPAIR",
        "writes_applied_by_wrapper",
        "target_content_already_present",
    ]
    required_fragments_present = all(fragment in source for fragment in required_fragments) and current_test_exists

    if required_fragments_present:
        decision = "stop_mp38_already_present"
        decision_reason = "Wrapper-retry helper and current-state test already exist."
    else:
        decision = "author_mp38"
        decision_reason = "Create a pure helper that decides wrapper-only retry eligibility."

    if decision == "author_mp38":
        if not verify_helper_present:
            raise SystemExit("MP37 prerequisite shape missing from patchops/rerun_decisions.py.")

        if "WRAPPER_ONLY_REPAIR = 'wrapper_only_repair'" not in source:
            source = source.replace(
                "VERIFY_ONLY = 'verify_only'\n",
                "VERIFY_ONLY = 'verify_only'\nWRAPPER_ONLY_REPAIR = 'wrapper_only_repair'\n",
                1,
            )

        new_function = '''

def should_recommend_wrapper_only_repair(*, failure_class: str | None, target_content_already_present: bool, writes_applied_by_wrapper: bool) -> bool:
    """Return True when wrapper-only repair is the narrow truthful next mode."""
    if failure_class != 'wrapper_failure':
        return False
    if not target_content_already_present:
        return False
    if writes_applied_by_wrapper:
        return False
    return True
'''
        if helper_name not in source:
            source = source.rstrip() + new_function

        output_rerun_path = content_root / "patchops" / "rerun_decisions.py"
        ensure_parent(output_rerun_path)
        output_rerun_path.write_text(source.rstrip() + "\n", encoding="utf-8")

        current_test = '''from patchops.failure_categories import PATCH_AUTHORING_FAILURE, TARGET_PROJECT_FAILURE, WRAPPER_FAILURE
from patchops.rerun_decisions import (
    WRAPPER_ONLY_REPAIR,
    should_recommend_verify_only,
    should_recommend_wrapper_only_repair,
)


def test_wrapper_retry_constant_is_stable():
    assert WRAPPER_ONLY_REPAIR == 'wrapper_only_repair'


def test_wrapper_retry_helper_accepts_wrapper_failure_when_target_already_present_and_no_writes():
    assert should_recommend_wrapper_only_repair(
        failure_class=WRAPPER_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is True


def test_wrapper_retry_helper_rejects_when_writes_were_applied_by_wrapper():
    assert should_recommend_wrapper_only_repair(
        failure_class=WRAPPER_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=True,
    ) is False


def test_wrapper_retry_helper_rejects_when_target_content_is_not_already_present():
    assert should_recommend_wrapper_only_repair(
        failure_class=WRAPPER_FAILURE,
        target_content_already_present=False,
        writes_applied_by_wrapper=False,
    ) is False


def test_wrapper_retry_helper_rejects_target_failure():
    assert should_recommend_wrapper_only_repair(
        failure_class=TARGET_PROJECT_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is False


def test_wrapper_retry_helper_rejects_patch_authoring_failure():
    assert should_recommend_wrapper_only_repair(
        failure_class=PATCH_AUTHORING_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is False


def test_wrapper_retry_and_verify_only_helpers_remain_separate():
    assert should_recommend_verify_only(
        failure_class=TARGET_PROJECT_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is True
    assert should_recommend_wrapper_only_repair(
        failure_class=WRAPPER_FAILURE,
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    ) is True
'''
        current_test_output = content_root / "tests" / "test_wrapper_retry_decision_helper_current.py"
        ensure_parent(current_test_output)
        current_test_output.write_text(current_test, encoding="utf-8")

        manifest = {
            "manifest_version": "1",
            "patch_name": "mp38_wrapper_retry_decision_helper",
            "active_profile": "generic_python",
            "target_project_root": str(wrapper_root),
            "files_to_write": [
                {
                    "path": "patchops/rerun_decisions.py",
                    "content_path": str(output_rerun_path),
                    "encoding": "utf-8",
                },
                {
                    "path": "tests/test_wrapper_retry_decision_helper_current.py",
                    "content_path": str(current_test_output),
                    "encoding": "utf-8",
                },
            ],
            "validation_commands": [
                {
                    "name": "mp38 wrapper-retry decision helper tests",
                    "program": "py",
                    "args": [
                        "-3",
                        "-m",
                        "pytest",
                        "-q",
                        "tests/test_wrapper_retry_decision_helper_current.py",
                        "tests/test_verify_only_decision_helper_current.py",
                        "tests/test_failure_classification_rules_current.py",
                        "tests/test_failure_category_model_current.py",
                    ],
                    "working_directory": ".",
                    "use_profile_runtime": False,
                    "allowed_exit_codes": [0],
                }
            ],
            "report_preferences": {
                "report_dir": str(inner_report_root),
                "report_name_prefix": "mp38",
                "write_to_desktop": False,
            },
            "tags": ["maintenance", "pythonization", "phase_f", "mp38", "self_hosted"],
            "notes": "MP38 wrapper-retry decision helper after confirmed MP37 completion.",
        }
        manifest_path = working_root / "patch_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    else:
        manifest_path = None

    payload = {
        "decision": decision,
        "decision_reason": decision_reason,
        "helper_exists": helper_exists,
        "current_test_exists": current_test_exists,
        "required_fragments_present": required_fragments_present,
        "manifest_path": str(manifest_path) if manifest_path else "",
        "inner_report_root": str(inner_report_root),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())