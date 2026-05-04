from __future__ import annotations

import json

from patchops.edge_rpa import edge_window_inventory as inv
from patchops.edge_rpa.edge_window_inventory import EdgeWindowCandidate, EdgeWindowInventoryResult, TopLevelControl, assert_l26_02_acceptance


def test_redaction_hashes_long_titles_without_full_title() -> None:
    title = "sensitive conversation title " * 10
    redacted = inv._redact_text(title, max_chars=20)
    assert redacted.startswith("<redacted length=")
    assert "sensitive conversation title" not in redacted


def test_result_payload_is_json_safe() -> None:
    result = EdgeWindowInventoryResult(
        candidates=(EdgeWindowCandidate(0, 123, 456, "Chrome_WidgetWin_1", "Microsoft Edge", "abc", 14, 80, ("pid_matches_msedge",)),),
        top_level_controls=(TopLevelControl(0, "Window", "Chrome_WidgetWin_1", "Microsoft Edge", ""),),
    )
    payload = result.to_payload()
    encoded = json.dumps(payload, sort_keys=True)
    assert "candidates" in encoded
    assert "top_level_controls" in encoded


def test_acceptance_policy_passes_with_live_inventory_markers() -> None:
    result = EdgeWindowInventoryResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        edge_process_count=2,
        edge_window_count=1,
        edge_window_inventory_written=True,
        selected_window_found=True,
        selected_window_index=0,
        selected_window_score=80,
        selected_window_title_redacted="Microsoft Edge",
        selected_window_title_hash="abc",
        selected_window_title_length=14,
        normal_edge_attached=True,
        edge_window_title_read=True,
        edge_focused=True,
        uia_top_level_tree_dumped=True,
        top_level_control_count=1,
        candidates=(EdgeWindowCandidate(0, 123, 456, "Chrome_WidgetWin_1", "Microsoft Edge", "abc", 14, 80, ("pid_matches_msedge",)),),
        top_level_controls=(TopLevelControl(0, "Window", "Chrome_WidgetWin_1", "Microsoft Edge", ""),),
        result="PASS",
    )
    assert_l26_02_acceptance(result)


def test_acceptance_policy_rejects_navigation_or_download() -> None:
    result = EdgeWindowInventoryResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        edge_process_count=2,
        edge_window_count=1,
        edge_window_inventory_written=True,
        selected_window_found=True,
        selected_window_score=80,
        selected_window_title_length=14,
        normal_edge_attached=True,
        edge_window_title_read=True,
        edge_focused=True,
        uia_top_level_tree_dumped=True,
        top_level_control_count=1,
        browser_navigation_performed=True,
        result="PASS",
    )
    try:
        assert_l26_02_acceptance(result)
    except AssertionError as exc:
        assert "browser_navigation_performed" in str(exc)
    else:
        raise AssertionError("navigation must remain forbidden in L26.2")
