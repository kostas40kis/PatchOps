from __future__ import annotations

import builtins
import json
from pathlib import Path

import pytest

from patchops.chatgpt_uploader.target_readiness import probe_target_readiness


GOOD_TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f9e01d-f588-838f-b2c8-3e3f0f0153cf"


def test_target_readiness_accepts_requested_chatgpt_conversation_url(tmp_path: Path) -> None:
    result = probe_target_readiness(target_url=GOOD_TARGET_URL, output_dir=tmp_path)

    assert result.result == "PASS"
    assert result.safe_target_url is True
    assert result.target_url_is_chatgpt is True
    assert result.target_url_has_conversation_id is True
    assert result.network_request_performed is False
    assert result.webdriver_used is False
    assert result.selenium_used is False
    assert result.browser_dom_automation_used is False
    assert result.file_upload_attempted is False
    assert result.chatgpt_submit_performed is False
    assert result.conversation_text_logged is False
    assert result.random_page_click_performed is False

    payload = json.loads((tmp_path / "chatgpt_uploader_target_readiness_probe.json").read_text(encoding="utf-8"))
    assert payload["result"] == "PASS"
    assert payload["safe_target_url"] is True


def test_target_readiness_blocks_non_chatgpt_url() -> None:
    result = probe_target_readiness(target_url="https://example.com/c/69f9e01d-f588-838f-b2c8-3e3f0f0153cf")

    assert result.result == "BLOCKED"
    assert result.safe_target_url is False
    assert result.failure_layer == "target_readiness_probe"
    assert result.error == "target_url_not_chatgpt"
    assert result.file_upload_attempted is False
    assert result.chatgpt_submit_performed is False


def test_target_readiness_blocks_missing_conversation_id() -> None:
    result = probe_target_readiness(target_url="https://chatgpt.com/")

    assert result.result == "BLOCKED"
    assert result.target_url_is_chatgpt is True
    assert result.target_url_has_conversation_id is False
    assert result.error == "target_url_missing_conversation_id"


def test_target_readiness_does_not_import_pywinauto_without_explicit_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def guarded_import(name: str, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "pywinauto" or name.startswith("pywinauto."):
            raise AssertionError("pywinauto should not be imported without --allow-pywinauto-probe")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    result = probe_target_readiness(target_url=GOOD_TARGET_URL, allow_pywinauto_probe=False)

    assert result.result == "PASS"
    assert result.pywinauto_probe_requested is False
    assert result.pywinauto_imported is False
    assert result.edge_window_probe_attempted is False


def test_target_readiness_artifacts_redact_conversation_identifier(tmp_path: Path) -> None:
    result = probe_target_readiness(target_url=GOOD_TARGET_URL, output_dir=tmp_path)

    text_report = (tmp_path / "chatgpt_uploader_target_readiness_probe.txt").read_text(encoding="utf-8")
    assert result.target_url_hash
    assert "<conversation_id>" in result.target_url_redacted
    assert "69f9e01d-f588-838f-b2c8-3e3f0f0153cf" not in text_report
    assert "Network Request Performed      : False" in text_report
    assert "file_upload_attempted          : False" in text_report
    assert "chatgpt_submit_performed       : False" in text_report
