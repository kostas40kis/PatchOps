"""Composer paste helper for the optional LLM browser runner.

This module can place a prepared summary into a ChatGPT-like composer field.
It deliberately does not submit/send the message.

Safety:
- imports no Selenium modules,
- starts no browser driver,
- does not click download links,
- does not run PatchOps,
- does not press Enter or click Send,
- validation uses fake drivers/elements only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


DEFAULT_COMPOSER_SELECTORS: tuple[str, ...] = (
    'textarea[data-testid="prompt-textarea"]',
    'textarea#prompt-textarea',
    'textarea[placeholder*="Message"]',
    'div[contenteditable="true"][data-testid="prompt-textarea"]',
    'div[contenteditable="true"][aria-label*="Message"]',
    '[contenteditable="true"]',
)


@dataclass(frozen=True)
class ComposerElementSummary:
    tag_name: str | None
    text_length: int
    value_length: int | None
    contenteditable: str | None
    aria_label: str | None
    selector: str | None
    enabled: bool

    def to_payload(self) -> dict[str, object]:
        return {
            "tag_name": self.tag_name,
            "text_length": self.text_length,
            "value_length": self.value_length,
            "contenteditable": self.contenteditable,
            "aria_label": self.aria_label,
            "selector": self.selector,
            "enabled": self.enabled,
        }


@dataclass(frozen=True)
class ComposerPasteResult:
    pasted: bool
    reason: str
    text_length: int
    selector: str | None
    element: ComposerElementSummary | None
    used_javascript: bool
    submitted: bool = False

    def to_payload(self) -> dict[str, object]:
        return {
            "pasted": self.pasted,
            "reason": self.reason,
            "text_length": self.text_length,
            "selector": self.selector,
            "element": None if self.element is None else self.element.to_payload(),
            "used_javascript": self.used_javascript,
            "submitted": self.submitted,
        }


def _safe_get_attribute(element: Any, name: str) -> str | None:
    getter = getattr(element, "get_attribute", None)
    if not callable(getter):
        return None
    try:
        value = getter(name)
    except Exception:
        return None
    return None if value is None else str(value)


def _safe_text(element: Any) -> str:
    value = getattr(element, "text", "")
    return "" if value is None else str(value)


def _safe_tag_name(element: Any) -> str | None:
    value = getattr(element, "tag_name", None)
    return None if value is None else str(value)


def _safe_is_enabled(element: Any) -> bool:
    method = getattr(element, "is_enabled", None)
    if callable(method):
        try:
            return bool(method())
        except Exception:
            return False

    disabled = _safe_get_attribute(element, "disabled")
    aria_disabled = (_safe_get_attribute(element, "aria-disabled") or "").strip().lower()
    return disabled is None and aria_disabled != "true"


def summarize_composer_element(element: Any, *, selector: str | None = None) -> ComposerElementSummary:
    value = _safe_get_attribute(element, "value")
    return ComposerElementSummary(
        tag_name=_safe_tag_name(element),
        text_length=len(_safe_text(element)),
        value_length=None if value is None else len(value),
        contenteditable=_safe_get_attribute(element, "contenteditable"),
        aria_label=_safe_get_attribute(element, "aria-label"),
        selector=selector,
        enabled=_safe_is_enabled(element),
    )


def _looks_like_composer(element: Any) -> bool:
    if not _safe_is_enabled(element):
        return False

    tag_name = (_safe_tag_name(element) or "").strip().lower()
    if tag_name == "textarea":
        return True

    contenteditable = (_safe_get_attribute(element, "contenteditable") or "").strip().lower()
    if contenteditable == "true":
        return True

    role = (_safe_get_attribute(element, "role") or "").strip().lower()
    aria = (_safe_get_attribute(element, "aria-label") or "").strip().lower()
    return role == "textbox" and "message" in aria


def find_composer_element(
    driver: Any,
    *,
    selectors: Sequence[str] = DEFAULT_COMPOSER_SELECTORS,
) -> tuple[Any | None, ComposerElementSummary | None]:
    finder = getattr(driver, "find_elements", None)
    if not callable(finder):
        return None, None

    for selector in selectors:
        try:
            elements = list(finder("css selector", selector))
        except Exception:
            continue

        for element in elements:
            if _looks_like_composer(element):
                return element, summarize_composer_element(element, selector=selector)

    return None, None


def _set_text_with_javascript(driver: Any, element: Any, text: str) -> bool:
    execute_script = getattr(driver, "execute_script", None)
    if not callable(execute_script):
        return False

    script = """
const element = arguments[0];
const value = arguments[1];
if (!element) {
  return false;
}
if (element.tagName && element.tagName.toLowerCase() === 'textarea') {
  element.value = value;
} else {
  element.textContent = value;
}
element.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: value }));
element.dispatchEvent(new Event('change', { bubbles: true }));
return true;
"""
    try:
        return bool(execute_script(script, element, text))
    except Exception:
        return False


def _clear_element(element: Any) -> None:
    clear = getattr(element, "clear", None)
    if callable(clear):
        clear()


def _click_element(element: Any) -> None:
    click = getattr(element, "click", None)
    if callable(click):
        click()


def _send_keys(element: Any, text: str) -> bool:
    send_keys = getattr(element, "send_keys", None)
    if not callable(send_keys):
        return False
    try:
        send_keys(text)
        return True
    except Exception:
        return False


def paste_text_into_composer(
    driver: Any,
    text: str,
    *,
    selectors: Sequence[str] = DEFAULT_COMPOSER_SELECTORS,
    clear_first: bool = True,
    prefer_javascript: bool = True,
) -> ComposerPasteResult:
    """Paste text into the composer without sending it."""

    if text is None:
        raise ValueError("text must not be None")
    if not str(text):
        return ComposerPasteResult(
            pasted=False,
            reason="empty_text",
            text_length=0,
            selector=None,
            element=None,
            used_javascript=False,
            submitted=False,
        )

    element, summary = find_composer_element(driver, selectors=selectors)
    if element is None or summary is None:
        return ComposerPasteResult(
            pasted=False,
            reason="composer_not_found",
            text_length=len(text),
            selector=None,
            element=None,
            used_javascript=False,
            submitted=False,
        )

    if not summary.enabled:
        return ComposerPasteResult(
            pasted=False,
            reason="composer_disabled",
            text_length=len(text),
            selector=summary.selector,
            element=summary,
            used_javascript=False,
            submitted=False,
        )

    _click_element(element)

    used_javascript = False
    if prefer_javascript:
        used_javascript = _set_text_with_javascript(driver, element, text)

    if not used_javascript:
        if clear_first:
            _clear_element(element)
        if not _send_keys(element, text):
            return ComposerPasteResult(
                pasted=False,
                reason="composer_text_set_failed",
                text_length=len(text),
                selector=summary.selector,
                element=summary,
                used_javascript=False,
                submitted=False,
            )

    return ComposerPasteResult(
        pasted=True,
        reason="pasted_without_submit",
        text_length=len(text),
        selector=summary.selector,
        element=summarize_composer_element(element, selector=summary.selector),
        used_javascript=used_javascript,
        submitted=False,
    )


def paste_summary_into_composer(
    driver: Any,
    summary: Any,
    *,
    selectors: Sequence[str] = DEFAULT_COMPOSER_SELECTORS,
    clear_first: bool = True,
    prefer_javascript: bool = True,
) -> ComposerPasteResult:
    """Paste a PastebackSummary-like object or raw string into the composer."""

    text = getattr(summary, "text", summary)
    return paste_text_into_composer(
        driver,
        str(text),
        selectors=selectors,
        clear_first=clear_first,
        prefer_javascript=prefer_javascript,
    )
