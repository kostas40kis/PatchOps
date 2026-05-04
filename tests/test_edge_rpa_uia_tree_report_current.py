from __future__ import annotations

import json

from patchops.edge_rpa import edge_uia_tree_report as report
from patchops.edge_rpa.edge_uia_tree_report import SafeUiaControlRecord, UiaTreeReportResult, assert_l26_03_acceptance


def test_safe_text_redacts_document_like_content() -> None:
    redacted, digest, length = report.safe_text("secret conversation text", control_type="Document", max_chars=200)
    assert redacted.startswith("<name redacted by policy")
    assert "secret conversation" not in redacted
    assert digest
    assert length == len("secret conversation text")


def test_safe_text_allows_short_ui_labels_for_known_control_types() -> None:
    value, digest, length = report.safe_text("Settings and more", control_type="Button", max_chars=60)
    assert value == "Settings and more"
    assert digest
    assert length == len("Settings and more")


def test_candidate_classifier_finds_address_bar_hint() -> None:
    kind, score = report.classify_candidate("Edit", "OmniboxViewViews", "Search or enter web address", "", 2)
    assert kind == "address_bar_candidate"
    assert score >= 80


def test_result_payload_json_safe() -> None:
    result = UiaTreeReportResult(
        controls=(SafeUiaControlRecord(0, None, 0, "Window", "Chrome_WidgetWin_1", "Microsoft Edge", "abc", 14, "", "L0 T0 R10 B10", "none", 0),),
        control_type_counts={"Window": 1},
    )
    payload = result.to_payload()
    encoded = json.dumps(payload, sort_keys=True)
    assert "controls" in encoded
    assert "control_type_counts" in encoded


def test_acceptance_policy_passes_without_address_bar_requirement() -> None:
    result = UiaTreeReportResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_window_title_read=True,
        edge_focused=True,
        uia_control_tree_dumped=True,
        control_count_reported=True,
        control_count=1,
        max_depth_observed=0,
        tree_report_written=True,
        control_type_summary_written=True,
        address_bar_candidate_found=False,
        input_candidate_count=0,
        controls=(SafeUiaControlRecord(0, None, 0, "Window", "Chrome_WidgetWin_1", "Microsoft Edge", "abc", 14, "", "L0 T0 R10 B10", "none", 0),),
        control_type_counts={"Window": 1},
        result="PASS",
    )
    assert_l26_03_acceptance(result)


def test_acceptance_policy_rejects_conversation_logging_or_clicks() -> None:
    result = UiaTreeReportResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_window_title_read=True,
        edge_focused=True,
        uia_control_tree_dumped=True,
        control_count_reported=True,
        control_count=1,
        tree_report_written=True,
        control_type_summary_written=True,
        controls=(SafeUiaControlRecord(0, None, 0, "Window", "Chrome_WidgetWin_1", "Microsoft Edge", "abc", 14, "", "L0 T0 R10 B10", "none", 0),),
        control_type_counts={"Window": 1},
        conversation_text_logged=True,
        result="PASS",
    )
    try:
        assert_l26_03_acceptance(result)
    except AssertionError as exc:
        assert "conversation_text_logged" in str(exc)
    else:
        raise AssertionError("conversation logging must fail L26.3 acceptance")
