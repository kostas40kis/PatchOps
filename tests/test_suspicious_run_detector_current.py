from patchops.suspicious_runs import detect_suspicious_run


def _codes(findings):
    return [finding.code for finding in findings]


def test_detector_proves_contradictory_required_command_case():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 1\nResult   : PASS\n",
        summary_result="PASS",
        required_command_results=[
            {"name": "required smoke", "required": True, "exit_code": 1},
        ],
        wrapper_executed=True,
        provenance={
            "workflow_mode": "apply",
            "wrapper_project_root": "C:/dev/patchops",
            "report_path": "C:/Users/kostas/Desktop/report.txt",
        },
    )
    assert _codes(findings) == ["required_command_summary_contradiction"]


def test_detector_proves_missing_metadata_case_after_wrapper_execution():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 0\nResult   : FAIL\n",
        summary_result="FAIL",
        wrapper_executed=True,
        provenance={"workflow_mode": "apply"},
    )
    assert _codes(findings) == ["missing_critical_provenance"]


def test_detector_proves_missing_latest_report_copy_case():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 0\nResult   : FAIL\n",
        summary_result="FAIL",
        latest_report_copy_expected=True,
        latest_report_copy_exists=False,
        workflow_mode="export_handoff",
    )
    assert _codes(findings) == ["missing_latest_report_copy"]


def test_detector_proves_non_suspicious_normal_case_stays_quiet():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 0\nResult   : PASS\n",
        summary_result="PASS",
        required_command_results=[
            {"name": "validation", "required": True, "exit_code": 0},
        ],
        wrapper_executed=True,
        provenance={
            "workflow_mode": "apply",
            "wrapper_project_root": "C:/dev/patchops",
            "report_path": "C:/Users/kostas/Desktop/report.txt",
        },
        latest_report_copy_expected=False,
        latest_report_copy_exists=None,
        workflow_mode="apply",
    )
    assert findings == []


def test_detector_does_not_overclaim_when_wrapper_did_not_execute():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 0\nResult   : FAIL\n",
        summary_result="FAIL",
        wrapper_executed=False,
        provenance={},
    )
    assert findings == []


def test_detector_can_return_multiple_findings_for_one_bad_run():
    findings = detect_suspicious_run(
        report_text="PATCHOPS REPORT WITHOUT SUMMARY\n",
        summary_result="PASS",
        required_command_results=[
            {"name": "required smoke", "required": True, "exit_code": 1},
        ],
        wrapper_executed=True,
        provenance={"workflow_mode": "apply"},
    )
    assert _codes(findings) == [
        "required_command_summary_contradiction",
        "missing_critical_provenance",
        "missing_required_report_fields",
    ]
