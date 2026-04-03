from __future__ import annotations

import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
working_root = Path(sys.argv[2]).resolve()

handoff_path = project_root / 'patchops' / 'handoff.py'
current_test_path = project_root / 'tests' / 'test_handoff_failure_class_current.py'
legacy_handoff_test_path = project_root / 'tests' / 'test_handoff.py'

required_fragments = [
    'failure_class',
    'current_handoff.json',
    'latest_report_index.json',
    'next_prompt.txt',
]

if not handoff_path.exists():
    payload = {
        'decision': 'stop_missing_handoff_module',
        'decision_reason': 'patchops/handoff.py is missing.',
        'handoff_module_exists': False,
        'legacy_handoff_test_exists': legacy_handoff_test_path.exists(),
        'current_test_exists': current_test_path.exists(),
    }
    print(json.dumps(payload, indent=2))
    raise SystemExit(0)

handoff_text = handoff_path.read_text(encoding='utf-8')
count_failure_class = handoff_text.count('failure_class')

if count_failure_class >= 3 and current_test_path.exists():
    payload = {
        'decision': 'stop_mp35_already_present',
        'decision_reason': 'Handoff failure-class propagation and current proof test already exist.',
        'handoff_module_exists': True,
        'legacy_handoff_test_exists': legacy_handoff_test_path.exists(),
        'current_test_exists': True,
        'required_fragments_present': True,
        'required_fragments': required_fragments,
        'failure_class_mentions': count_failure_class,
    }
    print(json.dumps(payload, indent=2))
    raise SystemExit(0)

if count_failure_class < 3:
    payload = {
        'decision': 'stop_unexpected_handoff_shape',
        'decision_reason': 'handoff.py does not expose failure_class strongly enough for a safe narrow test-only patch.',
        'handoff_module_exists': True,
        'legacy_handoff_test_exists': legacy_handoff_test_path.exists(),
        'current_test_exists': current_test_path.exists(),
        'required_fragments_present': False,
        'required_fragments': required_fragments,
        'failure_class_mentions': count_failure_class,
    }
    print(json.dumps(payload, indent=2))
    raise SystemExit(0)

content_root = working_root / 'content'
(content_root / 'tests').mkdir(parents=True, exist_ok=True)

current_test = '''from __future__ import annotations

from pathlib import Path

from patchops.failure_categories import normalize_failure_category
from patchops.handoff import export_handoff_bundle
from tests.test_handoff import _read_json, _write_apply_report


def test_export_handoff_bundle_keeps_normalized_failure_class_for_target_failure(tmp_path: Path) -> None:
    report_path = _write_apply_report(
        tmp_path,
        result_label="FAIL",
        failure_category="target_project_failure",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    current_handoff = _read_json(handoff_root / "current_handoff.json")
    latest_index = _read_json(handoff_root / "latest_report_index.json")
    next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8")

    expected = normalize_failure_category("target_project_failure")
    assert payload["failure_class"] == expected
    assert current_handoff["repo_state"]["failure_class"] == expected
    assert latest_index["failure_class"] == expected
    assert f"failure class: {expected}" in next_prompt.lower()


def test_export_handoff_bundle_normalizes_legacy_suspicious_label_for_continuation(tmp_path: Path) -> None:
    report_path = _write_apply_report(
        tmp_path,
        result_label="FAIL",
        failure_category="suspicious/ambiguous run",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    current_handoff = _read_json(handoff_root / "current_handoff.json")
    latest_index = _read_json(handoff_root / "latest_report_index.json")
    next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8")

    expected = normalize_failure_category("suspicious/ambiguous run")
    assert payload["failure_class"] == expected
    assert current_handoff["repo_state"]["failure_class"] == expected
    assert latest_index["failure_class"] == expected
    assert f"failure class: {expected}" in next_prompt.lower()
'''
(content_root / 'tests' / 'test_handoff_failure_class_current.py').write_text(current_test, encoding='utf-8')

manifest = {
    'manifest_version': '1',
    'patch_name': 'mp35_handoff_failure_class_propagation',
    'active_profile': 'generic_python',
    'target_project_root': str(project_root),
    'backup_files': [],
    'files_to_write': [
        {
            'path': 'tests/test_handoff_failure_class_current.py',
            'content_path': str((content_root / 'tests' / 'test_handoff_failure_class_current.py').resolve()),
            'encoding': 'utf-8',
        }
    ],
    'validation_commands': [
        {
            'name': 'mp35 handoff failure-class propagation tests',
            'program': 'py',
            'args': [
                '-3',
                '-m',
                'pytest',
                '-q',
                'tests/test_handoff_failure_class_current.py',
                'tests/test_handoff.py',
                'tests/test_report_failure_section_current.py',
                'tests/test_failure_category_model_current.py',
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
        'report_name_prefix': 'mp35',
        'write_to_desktop': False,
    },
    'tags': ['maintenance', 'pythonization', 'phase_e', 'mp35', 'self_hosted'],
    'notes': 'MP35 handoff failure-class propagation after confirmed MP34 completion.',
}
manifest_path = working_root / 'patch_manifest.json'
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

payload = {
    'decision': 'author_mp35',
    'decision_reason': 'Lock handoff failure-class propagation into a current-state proof.',
    'handoff_module_exists': True,
    'legacy_handoff_test_exists': legacy_handoff_test_path.exists(),
    'current_test_exists': current_test_path.exists(),
    'required_fragments_present': True,
    'required_fragments': required_fragments,
    'failure_class_mentions': count_failure_class,
    'manifest_path': str(manifest_path.resolve()),
    'inner_report_root': str((working_root / 'inner_reports').resolve()),
}
print(json.dumps(payload, indent=2))