from __future__ import annotations

import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1])
working_root = Path(sys.argv[2])
content_root = working_root / "content"
inner_report_root = working_root / "inner_reports"
prep_state_path = working_root / "prep_state.txt"

docs_path = project_root / "docs" / "failure_repair_guide.md"
test_path = project_root / "tests" / "test_classification_docs_stop_current.py"
manifest_path = working_root / "patch_manifest.json"

required_fragments = [
    "classification-guided repair choice",
    "verify-only",
    "wrapper-only repair",
    "repair target content",
    "suspicious",
    "target_project_failure",
    "wrapper_failure",
    "patch_authoring_failure",
    "ambiguous_or_suspicious_run",
]

doc_text = docs_path.read_text(encoding="utf-8")
doc_lower = doc_text.lower()

current_test_exists = test_path.exists()
required_fragments_present = all(fragment in doc_lower for fragment in required_fragments)

decision = "stop_mp36_already_present" if (current_test_exists and required_fragments_present) else "author_mp36"
decision_reason = (
    "classification docs stop already present."
    if decision == "stop_mp36_already_present"
    else "Refresh failure-repair guidance so maintained docs match classifier behavior."
)

state_lines = [
    f"decision={decision}",
    f"decision_reason={decision_reason}",
    f"manifest_path={manifest_path}",
    f"inner_report_root={inner_report_root}",
    f"docs_path={docs_path}",
    f"test_path={test_path}",
    f"current_test_exists={'yes' if current_test_exists else 'no'}",
    f"required_fragments_present={'yes' if required_fragments_present else 'no'}",
    "required_fragments=" + " | ".join(required_fragments),
]
prep_state_path.write_text("\n".join(state_lines) + "\n", encoding="utf-8")

if decision != "author_mp36":
    print("decision=stop_mp36_already_present")
    sys.exit(0)

section_header = "## Classification-guided repair choice"
section_body = """## Classification-guided repair choice

Use the maintained failure classification to choose the narrowest truthful next action.

- `target_project_failure` means required validation proved the target content is wrong. Repair target content first.
- `wrapper_failure` means launcher, reporting, or wrapper mechanics failed while target content may already be correct. Prefer a wrapper-only repair path instead of claiming a target-content regression first.
- `patch_authoring_failure` means the patch authoring layer or generated patch content is malformed before the real repo truth is exercised. Repair the authoring layer first.
- `ambiguous_or_suspicious_run` means the evidence is contradictory or incomplete. Stop, inspect the canonical report and supporting evidence, and narrow the problem before continuing blindly.

Mode guidance:

- Use `verify-only` when the patch content is already correct and the goal is only to rerun validation and evidence without rewriting files.
- Use `wrapper-only repair` when target content already appears correct but wrapper mechanics or report generation failed.
- Repair target content when required validation proves the shipped content is wrong.
- Stop because the run is suspicious when the evidence does not support a safe automatic next step.
"""

if section_header.lower() not in doc_lower:
    updated_doc = doc_text.rstrip() + "\n\n" + section_body.strip() + "\n"
else:
    updated_doc = doc_text
    start = updated_doc.lower().find(section_header.lower())
    if start >= 0:
        updated_doc = updated_doc[:start].rstrip() + "\n\n" + section_body.strip() + "\n"

doc_content_path = content_root / "docs" / "failure_repair_guide.md"
doc_content_path.parent.mkdir(parents=True, exist_ok=True)
doc_content_path.write_text(updated_doc, encoding="utf-8")

current_test = """from pathlib import Path


def test_failure_repair_guide_mentions_classification_guided_repair_choice():
    text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8").lower()

    assert "classification-guided repair choice" in text
    assert "verify-only" in text
    assert "wrapper-only repair" in text
    assert "repair target content" in text
    assert "suspicious" in text


def test_failure_repair_guide_mentions_maintained_failure_classes():
    text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8").lower()

    assert "target_project_failure" in text
    assert "wrapper_failure" in text
    assert "patch_authoring_failure" in text
    assert "ambiguous_or_suspicious_run" in text
"""
test_content_path = content_root / "tests" / "test_classification_docs_stop_current.py"
test_content_path.parent.mkdir(parents=True, exist_ok=True)
test_content_path.write_text(current_test, encoding="utf-8")

manifest = {
    "manifest_version": "1",
    "patch_name": "mp36_classification_docs_stop",
    "active_profile": "generic_python",
    "target_project_root": str(project_root),
    "files_to_write": [
        {
            "path": "docs/failure_repair_guide.md",
            "content_path": str(doc_content_path),
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_classification_docs_stop_current.py",
            "content_path": str(test_content_path),
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "mp36 classification docs stop tests",
            "program": "py",
            "args": [
                "-3",
                "-m",
                "pytest",
                "-q",
                "tests/test_classification_docs_stop_current.py",
                "tests/test_handoff_failure_class_current.py",
                "tests/test_report_failure_section_current.py",
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
        "report_name_prefix": "mp36",
        "write_to_desktop": False,
    },
    "tags": ["maintenance", "pythonization", "phase_e", "mp36", "self_hosted"],
    "notes": "MP36 classification docs stop after confirmed MP35A green repair.",
}
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("decision=author_mp36")