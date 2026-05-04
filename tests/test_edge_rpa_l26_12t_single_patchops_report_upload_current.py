from patchops.edge_rpa.edge_l26_12t_single_patchops_report_upload import SinglePatchOpsReportUploadResult, assert_acceptance

def test_acceptance_passes_single_inner_report_upload() -> None:
    r = SinglePatchOpsReportUploadResult(uploaded_report_role="inner_patchops_apply_report", uploaded_report_count=1, uploaded_report_path_matches_inner_patchops_report=True, operator_report_uploaded=False, inner_patchops_report_exists=True, inner_patchops_report_hash="abc", submit_result="PASS", picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_operator_report_upload() -> None:
    r = SinglePatchOpsReportUploadResult(uploaded_report_role="inner_patchops_apply_report", uploaded_report_count=1, uploaded_report_path_matches_inner_patchops_report=True, operator_report_uploaded=True, inner_patchops_report_exists=True, inner_patchops_report_hash="abc", submit_result="PASS", picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "operator_report_uploaded" in str(exc)
    else:
        raise AssertionError("Uploading the outer operator report must fail L26.12T acceptance")

def test_acceptance_rejects_multiple_uploads() -> None:
    r = SinglePatchOpsReportUploadResult(uploaded_report_role="inner_patchops_apply_report", uploaded_report_count=2, uploaded_report_path_matches_inner_patchops_report=True, operator_report_uploaded=False, inner_patchops_report_exists=True, inner_patchops_report_hash="abc", submit_result="PASS", picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "uploaded_report_count_1" in str(exc)
    else:
        raise AssertionError("Multiple uploads must fail L26.12T acceptance")
