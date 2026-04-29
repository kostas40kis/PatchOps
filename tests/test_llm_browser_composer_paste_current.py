from __future__ import annotations

import pytest

from patchops.llm_browser.composer_paste import (
    DEFAULT_COMPOSER_SELECTORS,
    find_composer_element,
    paste_summary_into_composer,
    paste_text_into_composer,
    summarize_composer_element,
)


class FakeElement:
    def __init__(
        self,
        *,
        tag_name: str = "textarea",
        text: str = "",
        value: str | None = "",
        attrs: dict[str, str | None] | None = None,
        enabled: bool = True,
        send_keys_raises: bool = False,
    ) -> None:
        self.tag_name = tag_name
        self.text = text
        self.value = value
        self.attrs = dict(attrs or {})
        self.enabled = enabled
        self.send_keys_raises = send_keys_raises
        self.click_calls = 0
        self.clear_calls = 0
        self.sent_keys: list[str] = []

    def get_attribute(self, name: str):
        if name == "value":
            return self.value
        return self.attrs.get(name)

    def is_enabled(self) -> bool:
        return self.enabled

    def click(self) -> None:
        self.click_calls += 1

    def clear(self) -> None:
        self.clear_calls += 1
        self.value = ""

    def send_keys(self, text: str) -> None:
        if self.send_keys_raises:
            raise RuntimeError("send_keys failed")
        self.sent_keys.append(text)
        self.value = (self.value or "") + text


class FakeDriver:
    def __init__(self, elements_by_selector: dict[str, list[object]] | None = None, *, js_result: bool | None = None) -> None:
        self.elements_by_selector = dict(elements_by_selector or {})
        self.calls: list[tuple[str, str]] = []
        self.js_result = js_result
        self.js_calls: list[tuple[str, object, str]] = []

    def find_elements(self, by: str, selector: str):
        self.calls.append((by, selector))
        return self.elements_by_selector.get(selector, [])

    def execute_script(self, script: str, element: object, text: str):
        self.js_calls.append((script, element, text))
        if self.js_result is None:
            return False
        if self.js_result and isinstance(element, FakeElement):
            if element.tag_name.lower() == "textarea":
                element.value = text
            else:
                element.text = text
        return self.js_result


class SummaryLike:
    text = "PatchOps browser-runner summary: PASS"


def test_summarize_composer_element_is_compact() -> None:
    element = FakeElement(
        tag_name="textarea",
        text="",
        value="hello",
        attrs={"contenteditable": None, "aria-label": "Message ChatGPT"},
        enabled=True,
    )

    summary = summarize_composer_element(element, selector="textarea#prompt-textarea")
    payload = summary.to_payload()

    assert payload["tag_name"] == "textarea"
    assert payload["text_length"] == 0
    assert payload["value_length"] == 5
    assert payload["aria_label"] == "Message ChatGPT"
    assert payload["selector"] == "textarea#prompt-textarea"
    assert payload["enabled"] is True


def test_find_composer_element_finds_enabled_textarea() -> None:
    nonmatch = FakeElement(tag_name="button")
    match = FakeElement(tag_name="textarea")
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[0]: [nonmatch, match]})

    element, summary = find_composer_element(driver)

    assert element is match
    assert summary is not None
    assert summary.selector == DEFAULT_COMPOSER_SELECTORS[0]


def test_find_composer_element_finds_contenteditable_div() -> None:
    element = FakeElement(tag_name="div", attrs={"contenteditable": "true", "aria-label": "Message ChatGPT"})
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[-1]: [element]})

    found, summary = find_composer_element(driver)

    assert found is element
    assert summary is not None
    assert summary.contenteditable == "true"


def test_find_composer_element_ignores_disabled_element() -> None:
    element = FakeElement(tag_name="textarea", enabled=False)
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[0]: [element]})

    found, summary = find_composer_element(driver)

    assert found is None
    assert summary is None


def test_find_composer_element_handles_driver_without_finder() -> None:
    found, summary = find_composer_element(object())

    assert found is None
    assert summary is None


def test_paste_text_uses_javascript_when_available() -> None:
    element = FakeElement(tag_name="textarea")
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[0]: [element]}, js_result=True)

    result = paste_text_into_composer(driver, "hello world")

    assert result.pasted is True
    assert result.reason == "pasted_without_submit"
    assert result.used_javascript is True
    assert result.submitted is False
    assert element.value == "hello world"
    assert element.click_calls == 1
    assert element.clear_calls == 0
    assert element.sent_keys == []


def test_paste_text_falls_back_to_send_keys_when_javascript_unavailable() -> None:
    element = FakeElement(tag_name="textarea", value="old")
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[0]: [element]}, js_result=False)

    result = paste_text_into_composer(driver, "new text")

    assert result.pasted is True
    assert result.used_javascript is False
    assert element.clear_calls == 1
    assert element.sent_keys == ["new text"]
    assert element.value == "new text"


def test_paste_text_can_skip_clear_first() -> None:
    element = FakeElement(tag_name="textarea", value="old ")
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[0]: [element]}, js_result=False)

    result = paste_text_into_composer(driver, "new", clear_first=False)

    assert result.pasted is True
    assert element.clear_calls == 0
    assert element.value == "old new"


def test_paste_text_reports_empty_text_without_lookup() -> None:
    driver = FakeDriver()

    result = paste_text_into_composer(driver, "")

    assert result.pasted is False
    assert result.reason == "empty_text"
    assert driver.calls == []


def test_paste_text_reports_composer_not_found() -> None:
    result = paste_text_into_composer(FakeDriver(), "hello")

    assert result.pasted is False
    assert result.reason == "composer_not_found"
    assert result.submitted is False


def test_paste_text_reports_send_keys_failure() -> None:
    element = FakeElement(tag_name="textarea", send_keys_raises=True)
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[0]: [element]}, js_result=False)

    result = paste_text_into_composer(driver, "hello")

    assert result.pasted is False
    assert result.reason == "composer_text_set_failed"
    assert result.submitted is False


def test_paste_text_rejects_none() -> None:
    with pytest.raises(ValueError, match="text"):
        paste_text_into_composer(FakeDriver(), None)  # type: ignore[arg-type]


def test_paste_summary_uses_text_attribute() -> None:
    element = FakeElement(tag_name="textarea")
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[0]: [element]}, js_result=False)

    result = paste_summary_into_composer(driver, SummaryLike())

    assert result.pasted is True
    assert element.value == "PatchOps browser-runner summary: PASS"


def test_paste_result_payload_is_compact() -> None:
    element = FakeElement(tag_name="textarea")
    driver = FakeDriver({DEFAULT_COMPOSER_SELECTORS[0]: [element]}, js_result=True)

    result = paste_text_into_composer(driver, "PatchOps browser-runner summary: PASS")
    payload = result.to_payload()

    assert payload["pasted"] is True
    assert payload["submitted"] is False
    assert payload["text_length"] == len("PatchOps browser-runner summary: PASS")
    assert payload["element"]["tag_name"] == "textarea"
    assert "text" not in payload["element"]
