from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.edge_focus_guard import (
    EdgeWindowSnapshot,
    FakeEdgeAdapter,
    guard_target,
    run_guard,
    score_window,
    target_host_from_url,
)


TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f9e01d-f588-838f-b2c8-3e3f0f0153cf"
ROOT_TARGET_URL = "https://chatgpt.com/"


def test_target_host_accepts_only_https_chatgpt() -> None:
    assert target_host_from_url(TARGET_URL) == "chatgpt.com"
    assert target_host_from_url("http://chatgpt.com/") is None
    assert target_host_from_url("https://example.com/") is None


def test_guard_finds_exact_target_without_focus() -> None:
    adapter = FakeEdgeAdapter([
        EdgeWindowSnapshot(handle="1", title="ChatGPT - Microsoft Edge", url=TARGET_URL),
    ])
    result = guard_target(TARGET_URL, adapter, allow_focus=False)
    payload = result.to_payload()
    assert result.ok is True
    assert payload["status"] == "PASS_TARGET_READY"
    assert payload["focus_attempted"] is False
    assert payload["focus_confirmed"] is False
    assert payload["matching_candidate_count"] == 1
    assert payload["candidates"]
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["selenium_used"] is False


def test_guard_focus_is_explicitly_gated() -> None:
    adapter = FakeEdgeAdapter([
        EdgeWindowSnapshot(handle="1", title="ChatGPT - Microsoft Edge", url=TARGET_URL),
    ])
    result = guard_target(TARGET_URL, adapter, allow_focus=True)
    assert result.status == "PASS_TARGET_FOCUSED"
    assert result.focus_attempted is True
    assert result.focus_confirmed is True
    assert adapter.focused_handles == ["1"]


def test_guard_blocks_missing_target() -> None:
    adapter = FakeEdgeAdapter([
        EdgeWindowSnapshot(handle="1", title="Example - Microsoft Edge", url="https://example.com/"),
    ])
    result = guard_target(TARGET_URL, adapter)
    assert result.ok is False
    assert result.status == "BLOCKED_TARGET_NOT_FOUND"
    assert result.to_payload()["candidates"]


def test_guard_blocks_ambiguous_exact_targets() -> None:
    adapter = FakeEdgeAdapter([
        EdgeWindowSnapshot(handle="1", title="ChatGPT - Microsoft Edge", url=TARGET_URL),
        EdgeWindowSnapshot(handle="2", title="ChatGPT - Microsoft Edge", url=TARGET_URL),
    ])
    result = guard_target(TARGET_URL, adapter)
    assert result.status == "BLOCKED_AMBIGUOUS_TARGET"
    assert result.matching_candidate_count == 2


def test_title_only_root_chatgpt_target_matches_normal_edge() -> None:
    adapter = FakeEdgeAdapter([
        EdgeWindowSnapshot(
            handle="edge-1",
            title="ChatGPT - Personal - Microsoft\u200b Edge",
            url=None,
            process_name="msedge.exe",
            class_name="Chrome_WidgetWin_1",
            process_id=16972,
        )
    ])
    result = guard_target(ROOT_TARGET_URL, adapter)
    assert result.status == "PASS_TARGET_READY"
    assert result.matching_candidate_count == 1
    payload = result.to_payload()
    assert payload["selected"]["window"]["title"] == "ChatGPT - Personal - Microsoft\u200b Edge"
    assert "chatgpt_title" in payload["selected"]["reasons"]
    assert "normal_edge_window" in payload["selected"]["reasons"]


def test_title_only_match_chooses_edge_over_other_chromium_chatgpt_windows() -> None:
    adapter = FakeEdgeAdapter([
        EdgeWindowSnapshot(
            handle="opera-1",
            title="ChatGPT - wrapper - Opera",
            url=None,
            process_name="opera.exe",
            class_name="Chrome_WidgetWin_1",
            process_id=1668,
        ),
        EdgeWindowSnapshot(
            handle="edge-1",
            title="ChatGPT - Personal - Microsoft\u200b Edge",
            url=None,
            process_name="msedge.exe",
            class_name="Chrome_WidgetWin_1",
            process_id=16972,
        ),
        EdgeWindowSnapshot(
            handle="brave-1",
            title="New Private Tab - Brave",
            url=None,
            process_name="brave.exe",
            class_name="Chrome_WidgetWin_1",
            process_id=14828,
        ),
    ])
    result = guard_target(ROOT_TARGET_URL, adapter)
    payload = result.to_payload()
    assert result.status == "PASS_TARGET_READY"
    assert payload["candidate_count"] == 3
    assert payload["matching_candidate_count"] == 1
    assert payload["selected"]["window"]["handle"] == "edge-1"


def test_title_only_multiple_normal_edge_chatgpt_windows_blocks_ambiguous() -> None:
    adapter = FakeEdgeAdapter([
        EdgeWindowSnapshot(handle="edge-1", title="ChatGPT - Microsoft Edge", process_name="msedge.exe"),
        EdgeWindowSnapshot(handle="edge-2", title="ChatGPT - Personal - Microsoft Edge", process_name="msedge.exe"),
    ])
    result = guard_target(ROOT_TARGET_URL, adapter)
    assert result.status == "BLOCKED_AMBIGUOUS_TARGET"
    assert result.matching_candidate_count == 2


def test_score_penalizes_non_edge_chromium_chatgpt_title() -> None:
    candidate = score_window(
        EdgeWindowSnapshot(
            handle="opera-1",
            title="ChatGPT - wrapper - Opera",
            process_name="opera.exe",
            class_name="Chrome_WidgetWin_1",
        ),
        ROOT_TARGET_URL,
        "chatgpt.com",
    )
    assert candidate.score < 60
    assert "non_edge_process:opera.exe" in candidate.reasons


def test_real_edge_provider_is_blocked_without_explicit_gate() -> None:
    result = run_guard(target_url=TARGET_URL, provider="pywinauto", allow_real_edge=False)
    assert result.status == "BLOCKED_REAL_EDGE_NOT_ALLOWED"
    assert result.focus_attempted is False
    assert result.to_payload()["safety_flags"]["browser_dom_automation_used"] is False


def test_text_output_contains_required_safety_markers_and_candidates() -> None:
    result = run_guard(target_url=TARGET_URL, provider="fake")
    text = result.to_text()
    assert "PATCHOPS_CHATGPT_UPLOADER_EDGE_FOCUS_GUARD" in text
    assert "CANDIDATES" in text
    assert "ChatGPT - Microsoft Edge" in text
    assert "webdriver_used:false" in text
    assert "file_upload_attempted:false" in text
    assert "chatgpt_submit_performed:false" in text
    assert "END_PATCHOPS_CHATGPT_UPLOADER_EDGE_FOCUS_GUARD" in text


def test_direct_script_path_smoke_writes_evidence(tmp_path: Path) -> None:
    script = Path("scripts/run_u0_07_chatgpt_uploader_edge_focus_guard.py")
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target-url",
            TARGET_URL,
            "--provider",
            "fake",
            "--output-dir",
            str(tmp_path),
            "--json",
        ],
        cwd=Path.cwd(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "PASS_TARGET_READY"
    assert payload["candidates"]
    assert (tmp_path / "edge_focus_guard_result.json").exists()
    assert (tmp_path / "edge_focus_guard_result.txt").exists()
