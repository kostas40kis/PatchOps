from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_only_architecture.md"
UPLOADER_ROOT = PROJECT_ROOT / "patchops" / "chatgpt_uploader"


def _doc_text() -> str:
    assert DOC_PATH.exists(), f"missing architecture doc: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_chrome_lane_contract_required_phrases() -> None:
    text = _doc_text()

    required_phrases = [
        "Chrome is the only active browser lane.",
        "No all-browser abstraction.",
        "No browser registry.",
        "No auto-detect-everything behavior.",
        "A second browser may be added later only by explicit decision.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_chrome_lane_contract_keeps_patchops_as_truth() -> None:
    text = _doc_text()

    required_truth_lines = [
        "PatchOps remains truth. Chrome is only the delivery bridge.",
        "Downloader creates truth.",
        "PatchOps validates/runs truth.",
        "Canonical report records truth.",
        "Uploader transports truth.",
        "Chrome does not become truth.",
    ]

    for line in required_truth_lines:
        assert line in text


def test_chrome_lane_contract_records_forbidden_automation_and_side_effects() -> None:
    text = _doc_text()

    forbidden_terms = [
        "ChromeDriver",
        "Selenium",
        "WebDriver",
        "browser DOM automation",
        "CAPTCHA bypass",
        "Cloudflare bypass",
        "hidden browser automation",
        "random clicking",
        "unbounded upload loops",
        "unbounded send loops",
    ]

    for term in forbidden_terms:
        assert term in text

    patch_one_boundary = [
        "live_browser_used:false",
        "file_upload_attempted:false",
        "chatgpt_submit_performed:false",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "conversation_text_logged:false",
        "random_page_click_performed:false",
    ]

    for flag in patch_one_boundary:
        assert flag in text


def test_chrome_lane_does_not_create_generic_browser_adapter_files() -> None:
    forbidden_files = [
        "browser_factory.py",
        "browser_adapter.py",
        "browser_registry.py",
        "all_browsers.py",
        "generic_browser.py",
    ]

    for filename in forbidden_files:
        assert not (UPLOADER_ROOT / filename).exists(), filename


def test_chrome_lane_contract_names_parallel_second_browser_not_registry() -> None:
    text = _doc_text()

    assert "separate explicit lane" in text
    assert "parallel browser-specific lane" in text
    assert "shared browser registry" in text