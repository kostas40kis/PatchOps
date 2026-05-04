from patchops.edge_rpa.edge_l26_12u_short_safe_inner_patchops_report_upload import ShortSafeInnerReportUploadResult, assert_acceptance

def test_acceptance_passes_short_safe_inner_report_upload() -> None:
    r = ShortSafeInnerReportUploadResult(uploaded_report_role="inner_patchops_apply_report_short_safe_copy", uploaded_report_count=1, uploaded_safe_copy_path="C:/dev/patchops/data/runtime/edge_upload_short/u/patchops_apply_report.txt", uploaded_safe_copy_path_length=80, uploaded_safe_copy_short_path=True, uploaded_safe_copy_hash_matches_inner_report=True, inner_patchops_report_exists=True, inner_patchops_report_hash="abc", short_safe_copy_created=True, short_safe_copy_hash="abc", safe_copy_drive_valid=True, composer_candidate_found=True, slash_typed=True, ctrl_u_sent=True, foreground_picker_handoff_used=True, full_quoted_path_used=True, picker_confirmed=True, picker_enter_sent=True, picker_confirmed_upload_accepted=True, allow_chatgpt_submit=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_long_nested_safe_path() -> None:
    r = ShortSafeInnerReportUploadResult(uploaded_report_role="inner_patchops_apply_report_short_safe_copy", uploaded_report_count=1, uploaded_safe_copy_path="C:/" + "x" * 260, uploaded_safe_copy_path_length=263, uploaded_safe_copy_short_path=False, uploaded_safe_copy_hash_matches_inner_report=True, inner_patchops_report_exists=True, inner_patchops_report_hash="abc", short_safe_copy_created=True, short_safe_copy_hash="abc", safe_copy_drive_valid=True, composer_candidate_found=True, slash_typed=True, ctrl_u_sent=True, foreground_picker_handoff_used=True, full_quoted_path_used=True, picker_confirmed=True, picker_enter_sent=True, picker_confirmed_upload_accepted=True, allow_chatgpt_submit=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "uploaded_safe_copy_short_path" in str(exc)
    else:
        raise AssertionError("Long nested safe path must fail L26.12U acceptance")

def test_acceptance_rejects_operator_report_upload() -> None:
    r = ShortSafeInnerReportUploadResult(uploaded_report_role="inner_patchops_apply_report_short_safe_copy", uploaded_report_count=1, uploaded_safe_copy_path="C:/short/patchops_apply_report.txt", uploaded_safe_copy_path_length=32, uploaded_safe_copy_short_path=True, uploaded_safe_copy_hash_matches_inner_report=True, operator_report_uploaded=True, inner_patchops_report_exists=True, inner_patchops_report_hash="abc", short_safe_copy_created=True, short_safe_copy_hash="abc", safe_copy_drive_valid=True, composer_candidate_found=True, slash_typed=True, ctrl_u_sent=True, foreground_picker_handoff_used=True, full_quoted_path_used=True, picker_confirmed=True, picker_enter_sent=True, picker_confirmed_upload_accepted=True, allow_chatgpt_submit=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "operator_report_uploaded" in str(exc)
    else:
        raise AssertionError("Operator report upload must fail L26.12U acceptance")
