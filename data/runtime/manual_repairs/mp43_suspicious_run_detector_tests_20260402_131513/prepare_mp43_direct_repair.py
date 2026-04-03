from __future__ import annotations

import json
import shutil
import sys
import textwrap
from pathlib import Path


CURRENT_TEST = textwrap.dedent(
    """
    from patchops.suspicious_runs import SuspiciousRunFinding, detect_suspicious_run


    def _codes(findings):
        return [finding.code for finding in findings]


    def test_detector_keeps_tolerated_non_required_failure_out_of_summary_contradiction_bucket():
        findings = detect_suspicious_run(
            report_text="SUMMARY\n-------\nExitCode : 0\nResult   : PASS\n",
            summary_result="PASS",
            required_command_results=[
                {"name": "tolerated audit", "required": False, "exit_code": 7},
            ],
        )
        assert findings == []


    def test_detector_keeps_required_success_with_fail_summary_non_suspicious():
        findings = detect_suspicious_run(
            report_text="SUMMARY\n-------\nExitCode : 1\nResult   : FAIL\n",
            summary_result="FAIL",
            required_command_results=[
                {"name": "validation", "required": True, "exit_code": 0},
            ],
        )
        assert findings == []


    def test_detector_can_accumulate_multiple_small_intended_findings():
        findings = detect_suspicious_run(
            report_text="PATCHOPS PARTIAL REPORT\n",
            summary_result="PASS",
            required_command_results=[
                {"name": "validation", "required": True, "exit_code": 3},
            ],
            wrapper_executed=True,
            provenance={"workflow_mode": "apply"},
            latest_report_copy_expected=True,
            latest_report_copy_exists=False,
            workflow_mode="export_handoff",
        )
        assert _codes(findings) == [
            "required_command_summary_contradiction",
            "missing_required_report_fields",
            "missing_critical_provenance",
            "missing_latest_report_copy",
        ]


    def test_detector_returns_structured_findings_with_wrapper_failure_default():
        findings = detect_suspicious_run(
            report_text="PATCHOPS PARTIAL REPORT\n",
            summary_result="FAIL",
        )
        assert findings
        assert all(isinstance(finding, SuspiciousRunFinding) for finding in findings)
        assert all(finding.failure_class == "wrapper_failure" for finding in findings)


    def test_detector_requires_wrapper_execution_before_flagging_missing_provenance():
        findings = detect_suspicious_run(
            report_text="SUMMARY\n-------\nExitCode : 0\nResult   : FAIL\n",
            summary_result="FAIL",
            wrapper_executed=False,
            provenance={},
        )
        assert _codes(findings) == []


    def test_detector_only_flags_missing_latest_report_copy_when_explicitly_expected_and_missing():
        findings = detect_suspicious_run(
            report_text="SUMMARY\n-------\nExitCode : 0\nResult   : FAIL\n",
            summary_result="FAIL",
            latest_report_copy_expected=True,
            latest_report_copy_exists=None,
            workflow_mode="export_handoff",
        )
        assert _codes(findings) == []


    def test_detector_normal_case_with_complete_metadata_remains_non_suspicious():
        findings = detect_suspicious_run(
            report_text="SUMMARY\n-------\nExitCode : 0\nResult   : PASS\n",
            summary_result="PASS",
            required_command_results=[
                {"name": "validation", "required": True, "exit_code": 0},
                {"name": "audit", "required": False, "exit_code": 5},
            ],
            wrapper_executed=True,
            provenance={
                "wrapper_project_root": "C:/dev/patchops",
                "report_path": "C:/Users/kostas/Desktop/example.txt",
                "workflow_mode": "apply",
            },
            latest_report_copy_expected=False,
            latest_report_copy_exists=None,
            workflow_mode="apply",
        )
        assert findings == []
    """
).strip() + "\n"


REQUIRED_FRAGMENTS = [
    'test_detector_can_accumulate_multiple_small_intended_findings',
    'test_detector_normal_case_with_complete_metadata_remains_non_suspicious',
    'required_command_summary_contradiction',
    'missing_latest_report_copy',
]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_file(src: Path, backup_root: Path, repo_root: Path) -> None:
    if not src.exists():
        return
    relative = src.relative_to(repo_root)
    dest = backup_root / relative
    ensure_parent(dest)
    shutil.copy2(src, dest)


def write_file(path: Path, content: str) -> None:
    ensure_parent(path)
    path.write_text(content, encoding='utf-8')


def print_kv(key: str, value: object) -> None:
    print(f"{key}={value}")


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    backup_root = Path(sys.argv[2]).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)

    rule_path = repo_root / 'patchops' / 'suspicious_runs.py'
    if not rule_path.exists():
        raise SystemExit('patchops/suspicious_runs.py not found. MP42 must be green before MP43.')

    rule_text = rule_path.read_text(encoding='utf-8')
    required_rule_fragments = [
        'class SuspiciousRunFinding',
        'def detect_suspicious_run(',
        'missing_required_report_fields',
        'missing_critical_provenance',
        'missing_latest_report_copy',
    ]
    if not all(fragment in rule_text for fragment in required_rule_fragments):
        raise SystemExit('patchops/suspicious_runs.py does not match the expected MP42 rule-set surface.')

    test_path = repo_root / 'tests' / 'test_suspicious_run_detector_current.py'
    existing_test_text = test_path.read_text(encoding='utf-8') if test_path.exists() else ''
    already_present = all(fragment in existing_test_text for fragment in REQUIRED_FRAGMENTS)

    if not already_present:
        backup_file(test_path, backup_root, repo_root)
        write_file(test_path, CURRENT_TEST)

    print(json.dumps(
        {
            'patched_files': [str(test_path.relative_to(repo_root))] if not already_present else [],
            'backup_root': str(backup_root),
            'already_present': already_present,
        },
        indent=2,
    ))
    print_kv('test_path', str(test_path))
    print_kv('already_present', already_present)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())