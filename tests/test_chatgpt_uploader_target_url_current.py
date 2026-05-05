from __future__ import annotations

from patchops.chatgpt_uploader.target_url import parse_target_url


TARGET = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f9e01d-f588-838f-b2c8-3e3f0f0153cf"


def test_parse_target_chatgpt_conversation_url() -> None:
    info = parse_target_url(TARGET)

    assert info.safe_to_use_as_config is True
    assert info.is_chatgpt is True
    assert info.has_gpt_project_path is True
    assert info.has_conversation_path is True
    assert info.reason == "chatgpt_conversation_url"


def test_parse_rejects_non_chatgpt_url() -> None:
    info = parse_target_url("https://example.com/c/not-chatgpt")

    assert info.safe_to_use_as_config is False
    assert info.reason == "not_chatgpt"


def test_parse_rejects_missing_conversation_path() -> None:
    info = parse_target_url("https://chatgpt.com/")

    assert info.safe_to_use_as_config is False
    assert info.reason == "missing_conversation_path"


def test_parse_rejects_empty_url() -> None:
    info = parse_target_url("")

    assert info.safe_to_use_as_config is False
    assert info.reason == "empty_url"
