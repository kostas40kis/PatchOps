from patchops.edge_rpa.edge_l26_12z_short_live_root_canonical_report import ShortLiveRootCanonicalReportResult, assert_acceptance

def test_acceptance_passes_short_live_canonical_report() -> None:
    r = ShortLiveRootCanonicalReportResult(short_live_root_used=True, short_live_root_path="C:/dev/patchops/data/runtime/edge_live_short/z_1", short_live_root_path_length=50, canonical_report_created=True, canonical_report_path="C:/tmp/canonical.txt", canonical_report_size_bytes=100, canonical_contains_patchops_apply_evidence=True, canonical_contains_browser_live_evidence=True, canonical_contains_upload_submit_probe_evidence=True, canonical_uploaded_this_run=False, uploaded_report_role_this_run="inner_patchops_apply_report_short_safe_copy", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, upload_submit_idle_result="PASS", chatgpt_submit_performed=True, ready_for_next_probe=True, post_scan_completed=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_long_live_root() -> None:
    r = ShortLiveRootCanonicalReportResult(short_live_root_used=True, short_live_root_path="C:/" + "x" * 200, short_live_root_path_length=203, canonical_report_created=True, canonical_report_path="C:/tmp/canonical.txt", canonical_report_size_bytes=100, canonical_contains_patchops_apply_evidence=True, canonical_contains_browser_live_evidence=True, canonical_contains_upload_submit_probe_evidence=True, canonical_uploaded_this_run=False, uploaded_report_role_this_run="inner_patchops_apply_report_short_safe_copy", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, post_scan_completed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "short_live_root_path_length_under_120" in str(exc)
    else:
        raise AssertionError("Long live root must fail L26.12Z acceptance")

def test_acceptance_rejects_content_logging() -> None:
    r = ShortLiveRootCanonicalReportResult(short_live_root_used=True, short_live_root_path="C:/short", short_live_root_path_length=8, canonical_report_created=True, canonical_report_path="C:/tmp/canonical.txt", canonical_report_size_bytes=100, canonical_contains_patchops_apply_evidence=True, canonical_contains_browser_live_evidence=True, canonical_contains_upload_submit_probe_evidence=True, canonical_uploaded_this_run=False, uploaded_report_role_this_run="inner_patchops_apply_report_short_safe_copy", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, post_scan_completed=True, conversation_text_logged=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "conversation_text_logged" in str(exc)
    else:
        raise AssertionError("Content logging must fail L26.12Z acceptance")
