from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.browser_target_config import write_default_browser_target_config
from patchops.copilot_downloader.clipboard_probe import CLIPBOARD_CONFIRM_TEXT, SCRIPT_BEGIN, SCRIPT_END
from patchops.copilot_downloader.edge_window_preflight import LIVE_CONFIRM_TEXT, WindowSnapshot
from patchops.copilot_downloader.live_browser_evidence import (
    BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY,
    PASS_LIVE_BROWSER_EVIDENCE_RECORDED,
    run_live_browser_evidence_harness,
)


def _repo_with_browser_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)
    return repo_root, config_path


def test_live_browser_evidence_non_live_doctor_is_controlled_and_writes_reports(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    result = run_live_browser_evidence_harness(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        desktop_report_dir=repo_root / "desktop",
        live_browser=False,
        live_clipboard=False,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY
    assert result["browser_preflight"]["result_label"] == "BLOCKED_BROWSER_NOT_READY"
    assert result["clipboard_probe"]["result_label"] == "BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED"
    assert result["checks"]["sub_payloads_controlled"] is True
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["raw_clipboard_text_not_logged"] is True
    assert result["safety"]["clipboard_read"] is False
    assert Path(result["evidence_files"]["json"]).is_file()
    assert Path(result["evidence_files"]["text"]).is_file()
    assert Path(result["desktop_report_path"]).is_file()


def test_live_browser_evidence_can_pass_browser_ready_without_clipboard_read(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    result = run_live_browser_evidence_harness(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        desktop_report_dir=repo_root / "desktop",
        live_browser=True,
        confirm_live_browser_text=LIVE_CONFIRM_TEXT,
        live_clipboard=False,
        window_provider=lambda: (WindowSnapshot(title="Secret project - ChatGPT - Microsoft Edge", process_name="msedge.exe"),),
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_LIVE_BROWSER_EVIDENCE_RECORDED
    assert result["browser_preflight"]["result_label"] == "PASS_BROWSER_READY"
    assert result["clipboard_probe"]["result_label"] == "BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED"
    assert result["safety"]["clipboard_read"] is False
    serialized = json.dumps(result)
    assert "Secret project" not in serialized
    assert "ChatGPT - Microsoft Edge" in serialized


def test_live_browser_evidence_can_pass_with_clipboard_marker_summary_without_raw_payload(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    raw_prefix = "RAW_LIVE_EVIDENCE_PREFIX_SENTINEL"
    raw_suffix = "RAW_LIVE_EVIDENCE_SUFFIX_SENTINEL"
    clipboard_text = f"{raw_prefix}\n{SCRIPT_BEGIN}\n& {{ Set-StrictMode -Version Latest }}\n{SCRIPT_END}\n{raw_suffix}"
    result = run_live_browser_evidence_harness(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        desktop_report_dir=repo_root / "desktop",
        live_browser=True,
        confirm_live_browser_text=LIVE_CONFIRM_TEXT,
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        window_provider=lambda: (WindowSnapshot(title="Another secret - ChatGPT - Microsoft Edge", process_name="msedge.exe"),),
        clipboard_provider=lambda: clipboard_text,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_LIVE_BROWSER_EVIDENCE_RECORDED
    assert result["clipboard_probe"]["result_label"] == "PASS_CLIPBOARD_MARKER_DETECTED"
    assert result["clipboard_probe"]["clipboard_summary"]["has_complete_patchops_script_payload_markers"] is True
    assert result["safety"]["clipboard_read"] is True
    serialized = json.dumps(result)
    assert raw_prefix not in serialized
    assert raw_suffix not in serialized
    assert "Set-StrictMode" not in serialized
    assert "Another secret" not in serialized


def test_live_browser_evidence_blocks_when_live_browser_confirmation_wrong(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    called = {"window": False}

    def provider():
        called["window"] = True
        return (WindowSnapshot(title="ChatGPT - Microsoft Edge", process_name="msedge.exe"),)

    result = run_live_browser_evidence_harness(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        desktop_report_dir=repo_root / "desktop",
        live_browser=True,
        confirm_live_browser_text="wrong",
        window_provider=provider,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY
    assert result["browser_preflight"]["analysis"]["issue"] == "live_browser_confirmation_required"
    assert called["window"] is False


def test_live_browser_evidence_blocks_when_clipboard_requested_but_not_confirmed(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    called = {"clipboard": False}

    def clipboard_provider():
        called["clipboard"] = True
        return "RAW_SHOULD_NOT_BE_READ"

    result = run_live_browser_evidence_harness(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        desktop_report_dir=repo_root / "desktop",
        live_browser=True,
        confirm_live_browser_text=LIVE_CONFIRM_TEXT,
        live_clipboard=True,
        confirm_clipboard_text="wrong",
        window_provider=lambda: (WindowSnapshot(title="ChatGPT - Microsoft Edge", process_name="msedge.exe"),),
        clipboard_provider=clipboard_provider,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY
    assert result["clipboard_probe"]["issue"] == "clipboard_confirmation_required"
    assert called["clipboard"] is False
    serialized = json.dumps(result)
    assert "RAW_SHOULD_NOT_BE_READ" not in serialized


def test_repository_live_browser_evidence_non_live_doctor_is_controlled():
    result = run_live_browser_evidence_harness(
        repo_root=Path.cwd(),
        browser_config_path="data/config/copilot_downloader_browser_target.json",
        evidence_root="data/runtime/copilot_downloader/d1_04_live_browser_evidence_test",
        desktop_report_dir="data/runtime/copilot_downloader/d1_04_live_browser_evidence_test_desktop",
        live_browser=False,
        live_clipboard=False,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["selenium_not_used"] is True
    assert result["checks"]["webdriver_not_used"] is True
    assert result["checks"]["submit_not_performed"] is True
    assert Path(result["desktop_report_path"]).is_file()