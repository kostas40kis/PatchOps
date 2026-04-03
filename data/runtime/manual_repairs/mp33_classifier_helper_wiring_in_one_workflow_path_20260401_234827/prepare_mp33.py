from __future__ import annotations

import json
import sys
from pathlib import Path

PATCH_NAME = "mp33_classifier_helper_wiring_in_one_workflow_path"

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_state(path: Path, mapping: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in mapping.items()]
    write_text(path, "\n".join(lines) + "\n")

def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_mp33.py <repo_root> <working_root>")

    repo_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"
    inner_report_root = working_root / "inner_reports"
    prep_state_path = working_root / "prep_state.txt"
    manifest_path = working_root / "patch_manifest.json"

    apply_path = repo_root / "patchops" / "workflows" / "apply_patch.py"
    categories_path = repo_root / "patchops" / "failure_categories.py"
    rules_test_path = repo_root / "tests" / "test_failure_classification_rules_current.py"
    current_test_path = repo_root / "tests" / "test_classifier_helper_wiring_current.py"
    legacy_test_path = repo_root / "tests" / "test_failure_classifier.py"

    apply_exists = apply_path.exists()
    categories_exists = categories_path.exists()
    rules_test_exists = rules_test_path.exists()
    legacy_test_exists = legacy_test_path.exists()
    current_test_exists = current_test_path.exists()

    source = apply_path.read_text(encoding="utf-8") if apply_exists else ""

    helper_import_present = "from patchops.failure_categories import normalize_failure_category" in source
    helper_def_present = "def _normalize_failure_info(" in source
    helper_call_present = "failure=_normalize_failure_info(failure)" in source
    existing_classifier_import = "from patchops.execution.failure_classifier import classify_command_failure, classify_exception" in source

    if not apply_exists or not categories_exists or not rules_test_exists:
        write_state(
            prep_state_path,
            {
                "decision": "stop_missing_prerequisite",
                "decision_reason": "A required MP31/MP32 or workflow prerequisite surface is missing.",
                "apply_path_exists": "yes" if apply_exists else "no",
                "categories_exists": "yes" if categories_exists else "no",
                "rules_test_exists": "yes" if rules_test_exists else "no",
                "legacy_test_exists": "yes" if legacy_test_exists else "no",
                "current_test_exists": "yes" if current_test_exists else "no",
                "inner_report_root": str(inner_report_root),
                "manifest_path": str(manifest_path),
            },
        )
        return 0

    if helper_import_present and helper_def_present and helper_call_present and current_test_exists:
        write_state(
            prep_state_path,
            {
                "decision": "stop_mp33_already_present",
                "decision_reason": "apply workflow path already wires the classifier helper and the current test exists.",
                "apply_path_exists": "yes",
                "categories_exists": "yes",
                "rules_test_exists": "yes",
                "legacy_test_exists": "yes" if legacy_test_exists else "no",
                "current_test_exists": "yes",
                "helper_import_present": "yes",
                "helper_def_present": "yes",
                "helper_call_present": "yes",
                "inner_report_root": str(inner_report_root),
                "manifest_path": str(manifest_path),
            },
        )
        return 0

    if not existing_classifier_import:
        write_state(
            prep_state_path,
            {
                "decision": "stop_unexpected_apply_shape",
                "decision_reason": "apply_patch.py no longer contains the expected failure-classifier import shape.",
                "apply_path_exists": "yes",
                "categories_exists": "yes",
                "rules_test_exists": "yes",
                "legacy_test_exists": "yes" if legacy_test_exists else "no",
                "current_test_exists": "yes" if current_test_exists else "no",
                "helper_import_present": "yes" if helper_import_present else "no",
                "helper_def_present": "yes" if helper_def_present else "no",
                "helper_call_present": "yes" if helper_call_present else "no",
                "inner_report_root": str(inner_report_root),
                "manifest_path": str(manifest_path),
            },
        )
        return 0

    patched_source = source
    import_line = "from patchops.execution.failure_classifier import classify_command_failure, classify_exception\n"
    normalize_import = "from patchops.failure_categories import normalize_failure_category\n"
    if normalize_import not in patched_source:
        patched_source = patched_source.replace(import_line, import_line + normalize_import, 1)

    helper_block = '''
def _normalize_failure_info(failure):
    if failure is None:
        return None
    category = getattr(failure, "category", None)
    if category is None:
        return failure
    normalized_category = normalize_failure_category(category)
    try:
        if normalized_category != category:
            failure.category = normalized_category
    except Exception:
        return failure
    return failure


'''
    if "def _normalize_failure_info(" not in patched_source:
        patched_source = patched_source.replace("def apply_patch(", helper_block + "def apply_patch(", 1)

    if "failure=_normalize_failure_info(failure)," not in patched_source:
        patched_source = patched_source.replace("            failure=failure,\n", "            failure=_normalize_failure_info(failure),\n", 1)

    test_content = '''from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest


def test_apply_workflow_source_mentions_classifier_helper_wiring():
    source = Path("patchops/workflows/apply_patch.py").read_text(encoding="utf-8")
    assert "from patchops.failure_categories import normalize_failure_category" in source
    assert "def _normalize_failure_info(" in source
    assert "failure=_normalize_failure_info(failure)" in source


def test_apply_workflow_normalize_helper_delegates_to_normalizer(monkeypatch: pytest.MonkeyPatch):
    from patchops.workflows import apply_patch as module

    failure = SimpleNamespace(category="legacy_category_value", message="x")
    seen: dict[str, str] = {}

    def fake_normalize(value: str) -> str:
        seen["value"] = value
        return "normalized_by_fake"

    monkeypatch.setattr(module, "normalize_failure_category", fake_normalize)
    result = module._normalize_failure_info(failure)

    assert result is failure
    assert seen["value"] == "legacy_category_value"
    assert result.category == "normalized_by_fake"


def test_apply_workflow_normalize_helper_passes_through_missing_category():
    from patchops.workflows import apply_patch as module

    failure = SimpleNamespace(message="x")
    result = module._normalize_failure_info(failure)

    assert result is failure
    assert not hasattr(result, "category")
'''

    target_apply_content = content_root / "patchops" / "workflows" / "apply_patch.py"
    target_test_content = content_root / "tests" / "test_classifier_helper_wiring_current.py"
    write_text(target_apply_content, patched_source)
    write_text(target_test_content, test_content)

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(repo_root),
        "files_to_write": [
            {
                "path": "patchops/workflows/apply_patch.py",
                "content_path": str(target_apply_content.relative_to(repo_root)),
                "encoding": "utf-8",
            },
            {
                "path": "tests/test_classifier_helper_wiring_current.py",
                "content_path": str(target_test_content.relative_to(repo_root)),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "mp33 classifier helper wiring tests",
                "program": "py",
                "args": [
                    "-3",
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_classifier_helper_wiring_current.py",
                    "tests/test_failure_classification_rules_current.py",
                    "tests/test_failure_category_model_current.py",
                    "tests/test_failure_classifier.py",
                ],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "report_preferences": {
            "report_dir": str(inner_report_root),
            "report_name_prefix": "mp33",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "phase_e", "mp33", "self_hosted"],
        "notes": "MP33 classifier helper wiring in one workflow path after confirmed MP32 completion.",
    }
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")

    write_state(
        prep_state_path,
        {
            "decision": "author_mp33",
            "decision_reason": "Wire the reusable classifier helper through one stable workflow path.",
            "apply_path_exists": "yes",
            "categories_exists": "yes",
            "rules_test_exists": "yes",
            "legacy_test_exists": "yes" if legacy_test_exists else "no",
            "current_test_exists": "yes" if current_test_exists else "no",
            "helper_import_present": "yes" if helper_import_present else "no",
            "helper_def_present": "yes" if helper_def_present else "no",
            "helper_call_present": "yes" if helper_call_present else "no",
            "manifest_path": str(manifest_path),
            "inner_report_root": str(inner_report_root),
            "workflow_path": "patchops/workflows/apply_patch.py",
            "required_fragments": "from patchops.failure_categories import normalize_failure_category | def _normalize_failure_info( | failure=_normalize_failure_info(failure)",
        },
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())