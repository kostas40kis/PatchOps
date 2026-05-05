from pathlib import Path
from patchops.edge_rpa.edge_l26_14j_upload_primitive_diagnostic_freeze import UploadPrimitiveDiagnosticFreezeResult, assert_acceptance

def base(**kw):
    d = dict(latest_restored_or_already_good=True, restored_source_path="C:/good.txt", probe_file_created=True, probe_file_path="C:/probe.txt", probe_file_hash="h", picker_confirmed_upload_accepted=True, edge_window_found_after_picker=True, attachment_visible_after_picker=True, attachment_signal_count_after_picker=1, upload_primitive_reliable=True, recommended_next_patch="L26.14K strict upload-submit rerun from reliable primitive", result="PASS")
    d.update(kw)
    return UploadPrimitiveDiagnosticFreezeResult(**d)

def test_acceptance_passes_reliable_upload_primitive() -> None:
    assert_acceptance(base())

def test_acceptance_rejects_picker_false_positive() -> None:
    r = base(attachment_visible_after_picker=False, attachment_signal_count_after_picker=0, upload_primitive_reliable=False, result="FAIL")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "attachment_visible_after_picker" in str(exc) or "result_PASS" in str(exc)
    else:
        raise AssertionError("Visible attachment proof is required for upload primitive reliability")

def test_acceptance_rejects_any_submit() -> None:
    r = base(chatgpt_submit_performed=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "chatgpt_submit_performed" in str(exc)
    else:
        raise AssertionError("L26.14J must not submit")

def test_acceptance_rejects_candidate_click() -> None:
    r = base(candidate_click_performed=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "candidate_click_performed" in str(exc)
    else:
        raise AssertionError("L26.14J must not click candidates")
