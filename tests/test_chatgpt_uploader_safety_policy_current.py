from __future__ import annotations

from patchops.chatgpt_uploader.models import UploaderSafetyFlags
from patchops.chatgpt_uploader.safety_policy import (
    UploaderSafetyError,
    assert_safe_no_side_effects,
    default_foundation_safety_flags,
)


def test_default_foundation_safety_flags_are_safe() -> None:
    flags = default_foundation_safety_flags()

    assert flags.browser_opened is False
    assert flags.file_upload_attempted is False
    assert flags.chatgpt_submit_performed is False
    assert flags.webdriver_used is False
    assert flags.cloudflare_bypass_attempted is False

    assert_safe_no_side_effects(flags)


def test_safety_policy_reports_all_unsafe_flags() -> None:
    flags = UploaderSafetyFlags(
        browser_opened=True,
        file_upload_attempted=True,
        chatgpt_submit_performed=True,
    )

    try:
        assert_safe_no_side_effects(flags)
    except UploaderSafetyError as exc:
        message = str(exc)
        assert "browser_opened" in message
        assert "file_upload_attempted" in message
        assert "chatgpt_submit_performed" in message
    else:
        raise AssertionError("expected UploaderSafetyError")
