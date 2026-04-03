from patchops.suspicious_runs import detect_suspicious_run


def test_detect_suspicious_run_flags_required_command_summary_contradiction():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 1\nResult   : PASS\n",
        summary_result="PASS",
        required_command_results=[
            {"name": "targeted validation", "required": True, "exit_code": 1},
        ],
    )
    assert [finding.code for finding in findings] == ["required_command_summary_contradiction"]


def test_detect_suspicious_run_flags_missing_provenance_after_wrapper_execution():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 0\nResult   : FAIL\n",
        summary_result="FAIL",
        wrapper_executed=True,
        provenance={"workflow_mode": "apply"},
    )
    assert [finding.code for finding in findings] == ["missing_critical_provenance"]


def test_detect_suspicious_run_flags_missing_latest_report_copy_when_expected():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 0\nResult   : FAIL\n",
        summary_result="FAIL",
        latest_report_copy_expected=True,
        latest_report_copy_exists=False,
        workflow_mode="export_handoff",
    )
    assert [finding.code for finding in findings] == ["missing_latest_report_copy"]


def test_detect_suspicious_run_flags_missing_required_report_fields():
    findings = detect_suspicious_run(
        report_text="PATCHOPS REPORT WITHOUT SUMMARY\n",
        summary_result="FAIL",
    )
    assert [finding.code for finding in findings] == ["missing_required_report_fields"]


def test_detect_suspicious_run_returns_empty_list_for_conservative_normal_case():
    findings = detect_suspicious_run(
        report_text="SUMMARY\n-------\nExitCode : 0\nResult   : PASS\n",
        summary_result="PASS",
        required_command_results=[
            {"name": "full validation", "required": True, "exit_code": 0},
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
