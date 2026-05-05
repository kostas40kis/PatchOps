from patchops.edge_rpa.edge_l26_14n_probe_specific_upload_trigger_repair import ProbeSpecificUploadTriggerRepairResult, assert_acceptance

def base(**kw):
    d = dict(latest_pointer_good_before_probe=True, probe_file_created=True, probe_file_path="C:/dev/patchops/data/runtime/edge_upload_short/n/probe.txt", probe_file_hash="h", probe_baseline_signal_count=0, probe_baseline_zero=True, stale_dialog_closed_before_start=True, edge_window_found_before_open=True, upload_trigger_attempted=True, upload_trigger_method="uia_attach_control_plus_ctrl_u", file_dialog_found=True, file_name_control_found=True, file_name_control_strategy="uia_Edit", global_ctrl_a_sent=False, desktop_file_list_selection_detected=False, file_name_value_set=True, file_name_value_verified=True, open_button_invoked=True, enter_pressed_after_value_verified=False, file_dialog_remaining_after_open=False, edge_window_found_after_open=True, probe_specific_attachment_visible_after_open=True, probe_specific_attachment_signal_count_after_open=1, generic_attachment_signal_count_after_open=1, upload_primitive_reliable=True, recommended_next_patch="L26.14O strict upload-submit using probe-specific primitive", result="PASS")
    d.update(kw)
    return ProbeSpecificUploadTriggerRepairResult(**d)

def test_acceptance_passes_probe_specific_upload() -> None:
    assert_acceptance(base())

def test_acceptance_rejects_stale_generic_attachment() -> None:
    r = base(probe_baseline_signal_count=1, probe_baseline_zero=False, probe_specific_attachment_signal_count_after_open=1, probe_specific_attachment_visible_after_open=False, upload_primitive_reliable=False, result="FAIL")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "probe_baseline_zero" in str(exc) or "probe_specific_attachment_signal_count_increased" in str(exc)
    else:
        raise AssertionError("Stale/generic attachment evidence must not pass")

def test_acceptance_rejects_no_real_dialog() -> None:
    r = base(upload_trigger_attempted=False, file_dialog_found=False, upload_primitive_reliable=False, result="FAIL")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "upload_trigger_attempted" in str(exc) or "file_dialog_found" in str(exc)
    else:
        raise AssertionError("Upload picker dialog must open")

def test_acceptance_rejects_global_ctrl_a() -> None:
    r = base(global_ctrl_a_sent=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "global_ctrl_a_sent" in str(exc)
    else:
        raise AssertionError("Global Ctrl+A must remain forbidden")

def test_acceptance_rejects_submit() -> None:
    r = base(chatgpt_submit_performed=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "chatgpt_submit_performed" in str(exc)
    else:
        raise AssertionError("L26.14N must not submit")
