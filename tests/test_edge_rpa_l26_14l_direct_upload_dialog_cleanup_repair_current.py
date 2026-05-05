from patchops.edge_rpa.edge_l26_14l_direct_upload_dialog_cleanup_repair import DirectUploadDialogCleanupRepairResult, assert_acceptance

def base(**kw):
    d = dict(latest_pointer_good_before_probe=True, probe_file_created=True, probe_file_path="C:/probe.txt", probe_file_hash="h", edge_window_found_before_open=True, upload_trigger_attempted=True, file_dialog_found=True, file_dialog_path_entered=True, file_dialog_open_invoked=True, attachment_visible_after_direct_open=True, attachment_signal_count_after_direct_open=6, file_dialog_seen_after_open=True, dialog_cleanup_attempted=True, dialog_cleanup_method="esc+edge_escape", file_dialog_seen_after_cleanup=False, edge_window_found_after_cleanup=True, attachment_visible_after_cleanup=True, attachment_signal_count_after_cleanup=6, upload_primitive_reliable=True, recommended_next_patch="L26.14M strict upload-submit using direct path entry cleanup primitive", result="PASS")
    d.update(kw)
    return DirectUploadDialogCleanupRepairResult(**d)

def test_acceptance_passes_cleanup_repair() -> None:
    assert_acceptance(base())

def test_acceptance_rejects_dialog_still_open() -> None:
    r = base(file_dialog_seen_after_cleanup=True, upload_primitive_reliable=False, result="FAIL")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "file_dialog_seen_after_cleanup" in str(exc)
    else:
        raise AssertionError("Dialog must be closed after cleanup")

def test_acceptance_rejects_no_attachment_after_cleanup() -> None:
    r = base(attachment_visible_after_direct_open=False, attachment_visible_after_cleanup=False, attachment_signal_count_after_cleanup=0, upload_primitive_reliable=False, result="FAIL")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "attachment_visible_after_cleanup" in str(exc) or "attachment_visible_after_direct_open_or_cleanup" in str(exc)
    else:
        raise AssertionError("Attachment must remain visible after cleanup")

def test_acceptance_rejects_submit() -> None:
    r = base(chatgpt_submit_performed=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "chatgpt_submit_performed" in str(exc)
    else:
        raise AssertionError("L26.14L must not submit")
