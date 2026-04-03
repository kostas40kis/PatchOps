from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path
import sys


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    project_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / 'content'
    inner_reports = working_root / 'inner_reports'
    content_root.mkdir(parents=True, exist_ok=True)
    inner_reports.mkdir(parents=True, exist_ok=True)

    sections_path = project_root / 'patchops' / 'reporting' / 'sections.py'
    current_test_path = project_root / 'tests' / 'test_report_recommendation_note_current.py'

    if not sections_path.exists():
        raise SystemExit('patchops/reporting/sections.py not found.')

    sections_text = sections_path.read_text(encoding='utf-8')
    current_test_source = current_test_path.read_text(encoding='utf-8') if current_test_path.exists() else ''

    required_fragments = [
        'Recommended Next Mode :',
        '_recommended_next_mode_label(result: WorkflowResult)',
        'content_repair',
        'verify_only',
        'wrapper_only_repair',
    ]
    already_present = all(fragment in sections_text for fragment in required_fragments)

    if already_present and current_test_path.exists() and 'test_failure_section_includes_verify_only_recommendation' in current_test_source:
        payload = {
            'decision': 'stop_mp40_already_present',
            'decision_reason': 'Report recommendation note already exists and is covered by a current-state test.',
            'sections_exists': True,
            'current_test_exists': True,
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
            'required_fragments_present': False,
            'required_fragments': required_fragments,
        }
        print(json.dumps(payload, indent=2))
        raise SystemExit(0)

    rerun_import = textwrap.dedent('''
    from patchops.rerun_decisions import (
        VERIFY_ONLY,
        WRAPPER_ONLY_REPAIR,
        should_recommend_verify_only,
        should_recommend_wrapper_only_repair,
    )
    ''').strip() + '\n'
    if 'from patchops.rerun_decisions import (' not in sections_text:
        if 'from patchops.failure_categories import normalize_failure_category\n' in sections_text:
            sections_text = sections_text.replace(
                'from patchops.failure_categories import normalize_failure_category\n',
                'from patchops.failure_categories import normalize_failure_category\n' + rerun_import,
                1,
            )
        else:
            future_import_idx = sections_text.find('from __future__ import annotations\n')
            if future_import_idx != -1:
                insert_at = future_import_idx + len('from __future__ import annotations\n')
                sections_text = sections_text[:insert_at] + '\n' + rerun_import + sections_text[insert_at:]
            else:
                match = re.search(r'^(from .+\n|import .+\n)+', sections_text, re.MULTILINE)
                if match:
                    insert_at = match.end()
                    sections_text = sections_text[:insert_at] + rerun_import + sections_text[insert_at:]
                else:
                    sections_text = rerun_import + sections_text

    helper_code = '''

def _recommended_next_mode_label(result: WorkflowResult) -> str | None:
    if result.failure is None:
        return None
    failure_class = _failure_category_label(result)
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
'''
    if '_recommended_next_mode_label(result: WorkflowResult)' not in sections_text:
        sections_text = sections_text.replace(anchor, helper_code + '\n' + anchor, 1)

    old_block = '''def failure_section(result: WorkflowResult) -> str:\n    lines = [_rule("FAILURE DETAILS")]\n    if result.failure is None:\n        lines.append("(none)")\n        return "\\n".join(lines)\n    lines.append(f"Failure Class : {_failure_category_label(result)}")\n    lines.append(f"Failure Reason: {result.failure.message}")\n    lines.append(f"Category : {result.failure.category}")\n    lines.append(f"Message  : {result.failure.message}")\n    if result.failure.details:\n        lines.append(f"Details  : {result.failure.details}")\n    return "\\n".join(lines)\n'''
    new_block = '''def failure_section(result: WorkflowResult) -> str:\n    lines = [_rule("FAILURE DETAILS")]\n    if result.failure is None:\n        lines.append("(none)")\n        return "\\n".join(lines)\n    lines.append(f"Failure Class : {_failure_category_label(result)}")\n    lines.append(f"Failure Reason: {result.failure.message}")\n    recommended_next_mode = _recommended_next_mode_label(result)\n    if recommended_next_mode:\n        lines.append(f"Recommended Next Mode : {recommended_next_mode}")\n    lines.append(f"Category : {result.failure.category}")\n    lines.append(f"Message  : {result.failure.message}")\n    if result.failure.details:\n        lines.append(f"Details  : {result.failure.details}")\n    return "\\n".join(lines)\n'''
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
                'required_fragments_present': False,
                'required_fragments': required_fragments,
            }
            print(json.dumps(payload, indent=2))
            raise SystemExit(0)
        sections_text = pattern.sub(new_block, sections_text, count=1)

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


def test_failure_section_includes_verify_only_recommendation() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("target_project_failure"),
            message="validation failed after writes already landed",
            details=None,
        ),
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    )

    rendered = failure_section(result)

    assert "Recommended Next Mode : verify_only" in rendered


def test_failure_section_includes_wrapper_only_repair_recommendation() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("wrapper_failure"),
            message="report writer failed after target stayed correct",
            details=None,
        ),
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    )

    rendered = failure_section(result)

    assert "Recommended Next Mode : wrapper_only_repair" in rendered


def test_failure_section_includes_content_repair_recommendation_when_content_is_not_already_present() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("target_project_failure"),
            message="validation failed before content was proven landed",
            details=None,
        ),
        target_content_already_present=False,
        writes_applied_by_wrapper=False,
    )

    rendered = failure_section(result)

    assert "Recommended Next Mode : content_repair" in rendered
'''
    current_test_path = content_root / 'tests' / 'test_report_recommendation_note_current.py'
    current_test_path.write_text(current_test_text, encoding='utf-8')

    manifest = {
        'manifest_version': '1',
        'patch_name': 'mp40_report_recommendation_note',
        'active_profile': 'generic_python',
        'target_project_root': str(project_root),
        'files_to_write': [
            {
                'path': 'patchops/reporting/sections.py',
                'content_path': str((content_root / 'patchops' / 'reporting' / 'sections.py').resolve()),
                'encoding': 'utf-8',
            },
            {
                'path': 'tests/test_report_recommendation_note_current.py',
                'content_path': str(current_test_path.resolve()),
                'encoding': 'utf-8',
            },
        ],
        'validation_commands': [
            {
                'name': 'mp40 report recommendation note tests',
                'program': 'py',
                'args': ['-3','-m','pytest','-q','tests/test_report_recommendation_note_current.py','tests/test_rerun_decision_matrix_current.py','tests/test_wrapper_retry_decision_helper_current.py','tests/test_verify_only_decision_helper_current.py','tests/test_failure_classification_rules_current.py','tests/test_failure_category_model_current.py','tests/test_report_failure_section_current.py'],
                'working_directory': '.',
                'use_profile_runtime': False,
                'allowed_exit_codes': [0],
            }
        ],
        'report_preferences': {
            'report_dir': str(inner_reports.resolve()),
            'report_name_prefix': 'mp40',
            'write_to_desktop': False,
        },
        'tags': ['maintenance','pythonization','phase_f','mp40','self_hosted'],
        'notes': 'MP40 report recommendation note after confirmed MP39 completion.',
    }
        
        
    (working_root / 'patch_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    payload = {
        'decision': 'author_mp40',
        'decision_reason': 'Add a compact next-mode recommendation note to failed reports when the evidence is already sufficient.',
        'sections_exists': True,
        'current_test_exists': current_test_path.exists(),
        'required_fragments_present': False,
        'required_fragments': required_fragments,
        'manifest_path': str((working_root / 'patch_manifest.json').resolve()),
        'inner_report_root': str(inner_reports.resolve()),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())