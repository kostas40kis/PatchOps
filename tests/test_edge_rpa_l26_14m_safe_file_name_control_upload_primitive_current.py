from patchops.edge_rpa.edge_l26_14m_safe_file_name_control_upload_primitive import SafeFileNameControlUploadPrimitiveResult, assert_acceptance

def base(**kw):
    d = dict(latest_pointer_good_before_probe=True, probe_file_created=True, probe_file_path="C:/dev/patchops/data/runtime/edge_upload_short/m/probe.txt", probe_file_hash="h", probe_parent_is_desktop=False, stale_dialog_closed_before_start=True, edge_window_found_before_open=True, upload_trigger_attempted=True, file_dialog_found=True, file_name_control_found=True, file_name_control_strategy="uia_Edit", global_ctrl_a_sent=False, desktop_file_list_selection_detected=False, file_name_value_set=True, file_name_value_verified=True, open_button_invoked=True, enter_pressed_after_value_verified=False, file_dialog_remaining_after_open=False, edge_window_found_after_open=True, attachment_visible_after_open=True, attachment_signal_count_after_open=1, upload_primitive_reliable=True, recommended_next_patch="L26.14N strict upload-submit using safe File name control primitive", result="PASS")
    d.update(kw)
    return SafeFileNameControlUploadPrimitiveResult(**d)

def test_acceptance_passes_safe_control_upload() -> None:
    assert_acceptance(base())

def test_acceptance_rejects_global_ctrl_a() -> None:
    r = base(global_ctrl_a_sent=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "global_ctrl_a_sent" in str(exc)
    else:
        raise AssertionError("Global Ctrl+A must be forbidden")

def test_acceptance_rejects_desktop_parent() -> None:
    r = base(probe_parent_is_desktop=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "probe_parent_is_desktop" in str(exc)
    else:
        raise AssertionError("Probe should not be placed on Desktop")

def test_acceptance_rejects_unverified_value() -> None:
    r = base(file_name_value_verified=False, upload_primitive_reliable=False, result="FAIL")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "file_name_value_verified" in str(exc)
    else:
        raise AssertionError("File name value must be verified before Open/Enter")

def test_acceptance_rejects_submit() -> None:
    r = base(chatgpt_submit_performed=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "chatgpt_submit_performed" in str(exc)
    else:
        raise AssertionError("L26.14M must not submit")
