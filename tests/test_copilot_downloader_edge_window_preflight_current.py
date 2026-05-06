from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.browser_target_config import write_default_browser_target_config
from patchops.copilot_downloader.edge_window_preflight import (
    BLOCKED_AMBIGUOUS_BROWSER_TARGET,
    BLOCKED_BROWSER_NOT_READY,
    BLOCKED_LOGIN_OR_CHALLENGE,
    LIVE_CONFIRM_TEXT,
    PASS_BROWSER_READY,
    WindowSnapshot,
    analyze_edge_windows,
    redact_window_title,
    run_edge_window_preflight,
    sha256_text,
    window_evidence,
)
from patchops.copilot_downloader.models import RESULT_LABELS


def _repo_with_browser_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)
    return repo_root, config_path


def test_edge_window_preflight_labels_are_registered():
    assert PASS_BROWSER_READY in RESULT_LABELS
    assert BLOCKED_BROWSER_NOT_READY in RESULT_LABELS
    assert BLOCKED_AMBIGUOUS_BROWSER_TARGET in RESULT_LABELS
    assert BLOCKED_LOGIN_OR_CHALLENGE in RESULT_LABELS


def test_window_title_redaction_hides_conversation_title_and_query():
    title = "Very secret project plan - ChatGPT - Microsoft Edge"
    redacted = redact_window_title(title)
    assert redacted == "ChatGPT - Microsoft Edge"
    assert "secret" not in redacted.lower()
    assert sha256_text(title) == sha256_text(title)


def test_window_evidence_does_not_emit_raw_title():
    snapshot = WindowSnapshot(title="Private ChatGPT conversation - Microsoft Edge", process_name="msedge.exe", handle=100)
    evidence = window_evidence(snapshot)
    serialized = json.dumps(evidence)
    assert "Private" not in serialized
    assert "ChatGPT - Microsoft Edge" in serialized
    assert evidence["title_sha256"] == sha256_text(snapshot.title)
    assert evidence["handle_present"] is True


def test_analyze_blocks_when_no_edge_windows_exist():
    result = analyze_edge_windows([])
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_BROWSER_NOT_READY
    assert result["issue"] == "no_visible_edge_windows"


def test_analyze_blocks_when_no_chatgpt_edge_window_exists():
    result = analyze_edge_windows([WindowSnapshot(title="Docs - Microsoft Edge", process_name="msedge.exe")])
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_BROWSER_NOT_READY
    assert result["issue"] == "no_visible_chatgpt_edge_window"


def test_analyze_passes_single_visible_chatgpt_edge_window():
    result = analyze_edge_windows([WindowSnapshot(title="ChatGPT - Microsoft Edge", process_name="msedge.exe")])
    assert result["ok"] is True
    assert result["result_label"] == PASS_BROWSER_READY
    assert result["target_window_count"] == 1
    assert result["selected_window"]["title_redacted"] == "ChatGPT - Microsoft Edge"


def test_analyze_blocks_ambiguous_chatgpt_windows():
    result = analyze_edge_windows([
        WindowSnapshot(title="ChatGPT - Microsoft Edge", process_name="msedge.exe"),
        WindowSnapshot(title="Another ChatGPT - Microsoft Edge", process_name="msedge.exe"),
    ])
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_AMBIGUOUS_BROWSER_TARGET
    assert result["issue"] == "multiple_visible_chatgpt_edge_windows"


def test_analyze_blocks_login_or_challenge_window():
    result = analyze_edge_windows([WindowSnapshot(title="Sign in - ChatGPT - Microsoft Edge", process_name="msedge.exe")])
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_LOGIN_OR_CHALLENGE
    assert result["issue"] == "login_or_challenge_indicator_detected"


def test_run_preflight_without_live_flag_blocks_controlled_and_writes_evidence(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    result = run_edge_window_preflight(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_browser=False,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_BROWSER_NOT_READY
    assert result["analysis"]["issue"] == "live_browser_flag_required"
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["dom_automation_not_used"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["live_confirmation_gate_enforced"] is True
    assert result["safety"]["webdriver_used"] is False
    assert Path(result["evidence_files"]["json"]).is_file()
    assert Path(result["evidence_files"]["text"]).is_file()


def test_run_preflight_with_live_flag_requires_confirmation_but_remains_controlled(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    result = run_edge_window_preflight(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_browser=True,
        confirm_live_browser_text="wrong",
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_BROWSER_NOT_READY
    assert result["analysis"]["issue"] == "live_browser_confirmation_required"
    assert result["analysis"]["observed_window_count"] == 0
    assert result["checks"]["live_confirmation_gate_enforced"] is True
    assert result["checks"]["window_scan_not_attempted_without_confirmation"] is True


def test_run_preflight_live_provider_can_pass_without_raw_title_in_evidence(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    result = run_edge_window_preflight(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_browser=True,
        confirm_live_browser_text=LIVE_CONFIRM_TEXT,
        window_provider=lambda: (WindowSnapshot(title="Secret Topic - ChatGPT - Microsoft Edge", process_name="msedge.exe"),),
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_BROWSER_READY
    serialized = json.dumps(result)
    assert "Secret Topic" not in serialized
    assert "ChatGPT - Microsoft Edge" in serialized


def test_run_preflight_provider_failure_is_controlled_not_crash(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)

    def fail_provider():
        raise RuntimeError("pywinauto_unavailable:test")

    result = run_edge_window_preflight(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_browser=True,
        confirm_live_browser_text=LIVE_CONFIRM_TEXT,
        window_provider=fail_provider,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_BROWSER_NOT_READY
    assert result["analysis"]["issue"] == "window_provider_failed"
    assert result["issues"]


def test_repository_edge_window_preflight_non_live_doctor_is_controlled():
    result = run_edge_window_preflight(
        repo_root=Path.cwd(),
        browser_config_path="data/config/copilot_downloader_browser_target.json",
        evidence_root="data/runtime/copilot_downloader/d1_02_edge_window_preflight_test",
        live_browser=False,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_BROWSER_NOT_READY
    assert result["checks"]["selenium_not_used"] is True
    assert result["checks"]["webdriver_not_used"] is True
    assert result["checks"]["copy_not_performed"] is True
    assert result["checks"]["submit_not_performed"] is True