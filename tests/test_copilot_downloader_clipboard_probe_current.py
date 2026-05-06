from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.browser_target_config import write_default_browser_target_config
from patchops.copilot_downloader.clipboard_probe import (
    BLOCKED_CLIPBOARD_EMPTY,
    BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED,
    BLOCKED_CLIPBOARD_TOO_LARGE,
    BLOCKED_CLIPBOARD_UNAVAILABLE,
    CLIPBOARD_CONFIRM_TEXT,
    PASS_CLIPBOARD_MARKER_DETECTED,
    PASS_CLIPBOARD_PROBE_RECORDED,
    SCRIPT_BEGIN,
    SCRIPT_END,
    run_clipboard_probe,
    sha256_text,
    summarize_clipboard_text,
)


def _repo_with_browser_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)
    return repo_root, config_path


def test_clipboard_summary_records_hash_size_and_markers_without_content():
    text = "RAW_CLIPBOARD_SECRET_CONVERSATION\nnot an artifact"
    summary = summarize_clipboard_text(text)
    serialized = json.dumps(summary)
    assert summary["sha256"] == sha256_text(text)
    assert summary["size_chars"] == len(text)
    assert summary["line_count"] == 2
    assert summary["content_logged"] is False
    assert summary["content_preview_logged"] is False
    assert "RAW_CLIPBOARD_SECRET_CONVERSATION" not in serialized
    assert "not an artifact" not in serialized


def test_non_live_probe_blocks_controlled_and_does_not_read_clipboard(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    called = {"value": False}

    def provider():
        called["value"] = True
        return "should not be read"

    result = run_clipboard_probe(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=False,
        clipboard_provider=provider,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED
    assert result["issue"] == "live_clipboard_flag_required"
    assert called["value"] is False
    assert result["checks"]["clipboard_not_read_without_confirmation"] is True
    assert result["safety"]["clipboard_read"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_live_probe_wrong_confirmation_blocks_controlled_and_does_not_read_clipboard(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    called = {"value": False}

    def provider():
        called["value"] = True
        return "should not be read"

    result = run_clipboard_probe(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text="wrong",
        clipboard_provider=provider,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED
    assert result["issue"] == "clipboard_confirmation_required"
    assert called["value"] is False
    assert result["safety"]["clipboard_read"] is False


def test_live_probe_records_hash_only_for_plain_clipboard_text(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    text = "RAW_PRIVATE_COPIED_BROWSER_TEXT_SENTINEL"
    result = run_clipboard_probe(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: text,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_CLIPBOARD_PROBE_RECORDED
    assert result["clipboard_summary"]["sha256"] == sha256_text(text)
    assert result["clipboard_summary"]["size_chars"] == len(text)
    assert result["clipboard_summary"]["artifact_marker_detected"] is False
    assert result["safety"]["clipboard_read"] is True
    serialized = json.dumps(result)
    assert "RAW_PRIVATE_COPIED_BROWSER_TEXT_SENTINEL" not in serialized


def test_live_probe_detects_patchops_markers_without_logging_payload(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    raw_prefix = "RAW_CLIPBOARD_PREFIX_SENTINEL_7f1a"
    raw_suffix = "RAW_CLIPBOARD_SUFFIX_SENTINEL_9b2c"
    text = f"{raw_prefix}\n{SCRIPT_BEGIN}\n& {{ Set-StrictMode -Version Latest }}\n{SCRIPT_END}\n{raw_suffix}"
    result = run_clipboard_probe(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: text,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_CLIPBOARD_MARKER_DETECTED
    assert result["clipboard_summary"]["has_complete_patchops_script_payload_markers"] is True
    serialized = json.dumps(result)
    assert "Set-StrictMode" not in serialized
    assert raw_prefix not in serialized
    assert raw_suffix not in serialized


def test_live_probe_empty_clipboard_is_controlled_block(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    result = run_clipboard_probe(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: "",
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_CLIPBOARD_EMPTY
    assert result["issue"] == "clipboard_empty"


def test_live_probe_too_large_clipboard_is_controlled_block(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    text = "x" * 11
    result = run_clipboard_probe(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: text,
        max_chars=10,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_CLIPBOARD_TOO_LARGE
    assert result["issue"] == "clipboard_too_large"
    assert result["clipboard_summary"]["sha256"] == sha256_text(text)


def test_live_probe_provider_failure_is_controlled_block(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)

    def provider():
        raise RuntimeError("clipboard unavailable for test")

    result = run_clipboard_probe(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=provider,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_CLIPBOARD_UNAVAILABLE
    assert result["issue"].startswith("clipboard_read_failed")


def test_repository_clipboard_probe_non_live_doctor_is_controlled():
    result = run_clipboard_probe(
        repo_root=Path.cwd(),
        browser_config_path="data/config/copilot_downloader_browser_target.json",
        evidence_root="data/runtime/copilot_downloader/d1_03_clipboard_probe_test",
        live_clipboard=False,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED
    assert result["checks"]["raw_clipboard_text_not_logged"] is True
    assert result["checks"]["artifact_not_executed"] is True
    assert result["safety"]["clipboard_read"] is False