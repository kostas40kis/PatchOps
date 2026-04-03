from __future__ import annotations

import json
import re
import sys
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
working_root = Path(sys.argv[2]).resolve()
py_command = sys.argv[3]
py_prefix = sys.argv[4:]

sections_path = project_root / 'patchops' / 'reporting' / 'sections.py'
current_test_path = project_root / 'tests' / 'test_report_failure_section_current.py'
legacy_reporting_test_path = project_root / 'tests' / 'test_reporting.py'

if not sections_path.exists():
    payload = {
        'decision': 'stop_missing_sections',
        'decision_reason': 'patchops/reporting/sections.py is missing.',
        'sections_exists': False,
        'current_test_exists': current_test_path.exists(),
        'legacy_reporting_test_exists': legacy_reporting_test_path.exists(),
    }
    print(json.dumps(payload, indent=2))
    raise SystemExit(0)

sections_text = sections_path.read_text(encoding='utf-8')
required_fragments = [
    'Failure Class',
    'Failure Reason',
    'Category :',
    'Message  :',
]

already_present = all(fragment in sections_text for fragment in required_fragments)
if already_present and current_test_path.exists():
    payload = {
        'decision': 'stop_mp34_already_present',
        'decision_reason': 'Dedicated failure class/reason report fields already exist.',
        'sections_exists': True,
        'current_test_exists': True,
        'legacy_reporting_test_exists': legacy_reporting_test_path.exists(),
        'required_fragments_present': True,
        'required_fragments': required_fragments,
    }
    print(json.dumps(payload, indent=2))
    raise SystemExit(0)

anchor = 'def failure_section(result: WorkflowResult) -> str:\n'
if anchor not in sections_text:
    payload = {
        'decision': 'stop_unexpected_sections_shape',
        'decision_reason': 'sections.py no longer contains the expected failure_section anchor.',
        'sections_exists': True,
        'current_test_exists': current_test_path.exists(),
        'legacy_reporting_test_exists': legacy_reporting_test_path.exists(),
        'required_fragments_present': False,
        'required_fragments': required_fragments,
    }
    print(json.dumps(payload, indent=2))
    raise SystemExit(0)

if 'from patchops.failure_categories import normalize_failure_category\n' not in sections_text:
    future_import_idx = sections_text.find('from __future__ import annotations\n')
    if future_import_idx != -1:
        insert_at = future_import_idx + len('from __future__ import annotations\n')
        sections_text = sections_text[:insert_at] + '\nfrom patchops.failure_categories import normalize_failure_category\n' + sections_text[insert_at:]
    else:
        match = re.search(r'^(from .+\n|import .+\n)+', sections_text, re.MULTILINE)
        if match:
            insert_at = match.end()
            sections_text = sections_text[:insert_at] + 'from patchops.failure_categories import normalize_failure_category\n' + sections_text[insert_at:]
        else:
            sections_text = 'from patchops.failure_categories import normalize_failure_category\n' + sections_text

helper_code = '''

def _failure_category_label(result: WorkflowResult) -> str:
    if result.failure is None:
        return "none"
    category = getattr(result.failure, "category", None)
    if category is None:
        return "none"
    raw = getattr(category, "value", category)
    return normalize_failure_category(raw)
'''
if '_failure_category_label(result: WorkflowResult)' not in sections_text:
    sections_text = sections_text.replace(anchor, helper_code + '\n' + anchor, 1)

old_block = '''def failure_section(result: WorkflowResult) -> str:\n    lines = [_rule("FAILURE DETAILS")]\n    if result.failure is None:\n        lines.append("(none)")\n        return "\\n".join(lines)\n    lines.append(f"Category : {result.failure.category}")\n    lines.append(f"Message  : {result.failure.message}")\n    if result.failure.details:\n        lines.append(f"Details  : {result.failure.details}")\n    return "\\n".join(lines)\n'''
new_block = '''def failure_section(result: WorkflowResult) -> str:\n    lines = [_rule("FAILURE DETAILS")]\n    if result.failure is None:\n        lines.append("(none)")\n        return "\\n".join(lines)\n    lines.append(f"Failure Class : {_failure_category_label(result)}")\n    lines.append(f"Failure Reason: {result.failure.message}")\n    lines.append(f"Category : {result.failure.category}")\n    lines.append(f"Message  : {result.failure.message}")\n    if result.failure.details:\n        lines.append(f"Details  : {result.failure.details}")\n    return "\\n".join(lines)\n'''
if old_block in sections_text:
    sections_text = sections_text.replace(old_block, new_block, 1)
else:
    pattern = re.compile(
        r'def failure_section\(result: WorkflowResult\) -> str:\n(?:    .*\n)+?    return "\\n"\.join\(lines\)\n',
        re.MULTILINE,
    )
    if not pattern.search(sections_text):
        payload = {
            'decision': 'stop_unexpected_failure_section_shape',
            'decision_reason': 'Could not locate a stable failure_section block for narrow replacement.',
            'sections_exists': True,
            'current_test_exists': current_test_path.exists(),
            'legacy_reporting_test_exists': legacy_reporting_test_path.exists(),
            'required_fragments_present': False,
            'required_fragments': required_fragments,
        }
        print(json.dumps(payload, indent=2))
        raise SystemExit(0)
    sections_text = pattern.sub(new_block, sections_text, count=1)

content_root = working_root / 'content'
(content_root / 'patchops' / 'reporting').mkdir(parents=True, exist_ok=True)
(content_root / 'tests').mkdir(parents=True, exist_ok=True)

(content_root / 'patchops' / 'reporting' / 'sections.py').write_text(sections_text, encoding='utf-8')

current_test_text = '''from __future__ import annotations

from types import SimpleNamespace

from patchops.reporting.sections import failure_section


class _Category:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


def test_failure_section_includes_failure_class_and_reason() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("wrapper_failure"),
            message="wrapper layer failed after authoring",
            details="report capture mismatch",
        )
    )

    rendered = failure_section(result)

    assert "FAILURE DETAILS" in rendered
    assert "Failure Class : wrapper_failure" in rendered
    assert "Failure Reason: wrapper layer failed after authoring" in rendered
    assert "Category : wrapper_failure" in rendered
    assert "Message  : wrapper layer failed after authoring" in rendered
    assert "Details  : report capture mismatch" in rendered


def test_failure_section_none_shape_stays_compact() -> None:
    result = SimpleNamespace(failure=None)
    rendered = failure_section(result)
    assert "FAILURE DETAILS" in rendered
    assert "(none)" in rendered
'''
(current_test_path := content_root / 'tests' / 'test_report_failure_section_current.py').write_text(current_test_text, encoding='utf-8')

manifest = {
    'manifest_version': '1',
    'patch_name': 'mp34_report_failure_section_cleanup',
    'active_profile': 'generic_python',
    'target_project_root': str(project_root),
    'backup_files': [],
    'files_to_write': [
        {
            'path': 'patchops/reporting/sections.py',
            'content_path': str((content_root / 'patchops' / 'reporting' / 'sections.py').resolve()),
            'encoding': 'utf-8',
        },
        {
            'path': 'tests/test_report_failure_section_current.py',
            'content_path': str(current_test_path.resolve()),
            'encoding': 'utf-8',
        },
    ],
    'validation_commands': [
        {
            'name': 'mp34 report failure section tests',
            'program': py_command,
            'args': py_prefix + [
                '-m',
                'pytest',
                '-q',
                'tests/test_report_failure_section_current.py',
                'tests/test_reporting.py',
                'tests/test_failure_category_model_current.py',
                'tests/test_failure_classification_rules_current.py',
                'tests/test_classifier_helper_wiring_current.py',
            ],
            'working_directory': '.',
            'use_profile_runtime': False,
            'allowed_exit_codes': [0],
        }
    ],
    'smoke_commands': [],
    'audit_commands': [],
    'cleanup_commands': [],
    'archive_commands': [],
    'failure_policy': {},
    'report_preferences': {
        'report_dir': str((working_root / 'inner_reports').resolve()),
        'report_name_prefix': 'mp34',
        'write_to_desktop': False,
    },
    'tags': ['maintenance', 'pythonization', 'phase_e', 'mp34', 'self_hosted'],
    'notes': 'MP34 report failure section cleanup after confirmed MP33A green repair.',
}

manifest_path = working_root / 'patch_manifest.json'
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

payload = {
    'decision': 'author_mp34',
    'decision_reason': 'Render classification in a clearer dedicated report section.',
    'sections_exists': True,
    'current_test_exists': current_test_path.exists(),
    'legacy_reporting_test_exists': legacy_reporting_test_path.exists(),
    'required_fragments_present': False,
    'required_fragments': required_fragments,
    'manifest_path': str(manifest_path.resolve()),
    'inner_report_root': str((working_root / 'inner_reports').resolve()),
}
print(json.dumps(payload, indent=2))