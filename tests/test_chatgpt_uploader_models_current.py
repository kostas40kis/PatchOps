from __future__ import annotations

from patchops.chatgpt_uploader.models import DependencyStatus, TargetUrlInfo, UploaderSafetyFlags
from patchops.chatgpt_uploader.safety_policy import UploaderSafetyError, assert_safe_no_side_effects


def test_uploader_safety_flags_default_to_no_side_effects() -> None:
    flags = UploaderSafetyFlags()
    payload = flags.to_payload()

    assert payload["browser_opened"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["webdriver_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False

    assert_safe_no_side_effects(flags)


def test_uploader_safety_detects_live_side_effects() -> None:
    flags = UploaderSafetyFlags(browser_opened=True)

    try:
        assert_safe_no_side_effects(flags)
    except UploaderSafetyError as exc:
        assert "browser_opened" in str(exc)
    else:
        raise AssertionError("expected UploaderSafetyError")


def test_dependency_status_payload_is_json_safe() -> None:
    dep = DependencyStatus(name="playwright", import_ok=False, error="missing", required_for=("file_input_probe",))
    payload = dep.to_payload()

    assert payload["name"] == "playwright"
    assert payload["import_ok"] is False
    assert payload["required_for"] == ("file_input_probe",)


def test_target_url_info_payload_is_json_safe() -> None:
    info = TargetUrlInfo(
        raw_url="https://chatgpt.com/g/example/c/example",
        scheme="https",
        netloc="chatgpt.com",
        path="/g/example/c/example",
        is_chatgpt=True,
        has_gpt_project_path=True,
        has_conversation_path=True,
        safe_to_use_as_config=True,
        reason="chatgpt_conversation_url",
    )

    assert info.to_payload()["safe_to_use_as_config"] is True
