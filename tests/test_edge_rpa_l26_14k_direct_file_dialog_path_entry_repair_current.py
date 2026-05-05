from patchops.edge_rpa.edge_l26_14k_direct_file_dialog_path_entry_repair import DirectFileDialogPathEntryRepairResult, assert_acceptance

def base(**kw):
    d = dict(latest_pointer_good_before_probe=True, probe_file_created=True, probe_file_path="C:/probe.txt", probe_file_hash="h", edge_window_found_before_open=True, upload_trigger_attempted=True, file_dialog_found=True, file_dialog_path_entered=True, file_dialog_open_invoked=True, file_dialog_closed_after_open=True, edge_window_found_after_open=True, attachment_visible_after_direct_open=True, attachment_signal_count_after_direct_open=1, upload_primitive_reliable=True, recommended_next_patch="L26.14L strict upload-submit rerun using direct file-dialog path entry", result="PASS")
    d.update(kw)
    return DirectFileDialogPathEntryRepairResult(**d)

def test_acceptance_passes_direct_file_dialog_repair() -> None:
    assert_acceptance(base())

def test_acceptance_rejects_dialog_left_open() -> None:
    r = base(file_dialog_closed_after_open=False, upload_primitive_reliable=False, result="FAIL")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "file_dialog_closed_after_open" in str(exc)
    else:
        raise AssertionError("Dialog must close after Open")

def test_acceptance_rejects_no_visible_attachment() -> None:
    r = base(attachment_visible_after_direct_open=False, attachment_signal_count_after_direct_open=0, upload_primitive_reliable=False, result="FAIL")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "attachment_visible_after_direct_open" in str(exc)
    else:
        raise AssertionError("Visible attachment proof is required")

def test_acceptance_rejects_any_submit() -> None:
    r = base(chatgpt_submit_performed=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "chatgpt_submit_performed" in str(exc)
    else:
        raise AssertionError("L26.14K must not submit")
