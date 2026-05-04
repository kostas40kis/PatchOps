from __future__ import annotations

import json

from patchops.edge_rpa import pywinauto_edge_doctor as doctor
from patchops.edge_rpa.pywinauto_edge_doctor import EdgeLiveProbeResult, UiControlSummary, assert_l26_01_acceptance


def test_redact_text_bounds_long_values_without_leaking_body() -> None:
    original = "secret conversation text " * 20
    redacted = doctor._redact_text(original, max_chars=24)
    assert redacted.startswith("<redacted length=")
    assert "secret conversation text" not in redacted


def test_write_json_sets_json_written_marker(tmp_path) -> None:
    path = tmp_path / "probe.json"
    written = doctor._write_json(path, EdgeLiveProbeResult(error="example"))
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert written.json_written is True
    assert payload["json_written"] is True
    assert payload["error"] == "example"


def test_acceptance_policy_allows_attach_or_start_and_forbidden_flags_false() -> None:
    result = EdgeLiveProbeResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_process_count=1,
        edge_window_title="ChatGPT - Microsoft Edge",
        edge_window_title_read=True,
        edge_focused=True,
        uia_control_tree_dumped=True,
        control_count_reported=True,
        uia_control_count=1,
        json_written=True,
        top_level_control_summary=(UiControlSummary(0, "Window", "Chrome_WidgetWin_1", "Microsoft Edge", ""),),
        result="PASS",
    )
    assert_l26_01_acceptance(result)


def test_acceptance_policy_rejects_webdriver_or_selenium_truth_leakage() -> None:
    result = EdgeLiveProbeResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_window_title_read=True,
        edge_focused=True,
        uia_control_tree_dumped=True,
        control_count_reported=True,
        json_written=True,
        webdriver_used=True,
        result="PASS",
    )
    try:
        assert_l26_01_acceptance(result)
    except AssertionError as exc:
        assert "webdriver_used" in str(exc)
    else:
        raise AssertionError("webdriver_used:true must fail L26.1 acceptance")


def test_payload_is_json_safe_and_conversation_logging_false() -> None:
    result = EdgeLiveProbeResult(top_level_control_summary=(UiControlSummary(0, "Window", "Chrome_WidgetWin_1", "Edge", ""),))
    payload = result.to_payload()
    encoded = json.dumps(payload, sort_keys=True)
    assert "conversation_text_logged" in encoded
    assert payload["conversation_text_logged"] is False
