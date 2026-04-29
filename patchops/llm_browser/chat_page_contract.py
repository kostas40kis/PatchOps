"""Local ChatGPT page contract helpers for the LLM browser runner.

This module is fixture-first and passive:
- it imports no Selenium modules,
- it starts no browser driver,
- it does not touch a live provider page,
- it does not log full conversation text.

The contract extracts only the minimal state needed by later runner patches:
latest assistant reply metadata, streaming/composer readiness, and visible
downloadable artifact candidates from the latest assistant reply.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlparse


_ZIP_RE = re.compile(r"(?P<name>[A-Za-z0-9][A-Za-z0-9_.-]*\.zip)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ArtifactCandidate:
    filename: str
    href: str | None
    source: str
    text: str

    def to_payload(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "href": self.href,
            "source": self.source,
            "text": self.text,
        }


@dataclass(frozen=True)
class ChatPageSnapshot:
    latest_assistant_text: str
    latest_assistant_html_hash: str
    streaming: bool
    composer_enabled: bool
    artifact_candidates: tuple[ArtifactCandidate, ...]
    assistant_message_count: int

    @property
    def has_latest_assistant_reply(self) -> bool:
        return bool(self.latest_assistant_text)

    @property
    def ready_for_artifact_scan(self) -> bool:
        return self.has_latest_assistant_reply and not self.streaming and self.composer_enabled

    def to_payload(self) -> dict[str, object]:
        return {
            "latest_assistant_html_hash": self.latest_assistant_html_hash,
            "streaming": self.streaming,
            "composer_enabled": self.composer_enabled,
            "artifact_candidates": [candidate.to_payload() for candidate in self.artifact_candidates],
            "assistant_message_count": self.assistant_message_count,
            # Deliberately no full message text in the payload.
            "latest_assistant_text_length": len(self.latest_assistant_text),
        }


@dataclass
class _AssistantMessage:
    text_parts: list[str]
    hrefs: list[str]

    @property
    def text(self) -> str:
        return normalize_text(" ".join(self.text_parts))


class _ChatPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.assistant_messages: list[_AssistantMessage] = []
        self._current: _AssistantMessage | None = None
        self._assistant_depth = 0
        self.streaming = False
        self.composer_enabled = False

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key.lower(): "" if value is None else value for key, value in attrs_list}
        lowered_values = " ".join(attrs.values()).lower()

        if self._is_streaming_signal(tag, attrs, lowered_values):
            self.streaming = True

        if self._is_enabled_composer(tag, attrs):
            self.composer_enabled = True

        if self._is_assistant_message_start(attrs):
            self._current = _AssistantMessage(text_parts=[], hrefs=[])
            self._assistant_depth = 1
            href = attrs.get("href")
            if href:
                self._current.hrefs.append(href)
            return

        if self._current is not None:
            self._assistant_depth += 1
            href = attrs.get("href")
            if href:
                self._current.hrefs.append(href)

    def handle_startendtag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key.lower(): "" if value is None else value for key, value in attrs_list}
        lowered_values = " ".join(attrs.values()).lower()
        if self._is_streaming_signal(tag, attrs, lowered_values):
            self.streaming = True
        if self._current is not None and attrs.get("href"):
            self._current.hrefs.append(attrs["href"])

    def handle_endtag(self, tag: str) -> None:
        if self._current is None:
            return
        self._assistant_depth -= 1
        if self._assistant_depth <= 0:
            self.assistant_messages.append(self._current)
            self._current = None
            self._assistant_depth = 0

    def handle_data(self, data: str) -> None:
        if "stop generating" in data.lower() or "regenerate response" in data.lower():
            self.streaming = True
        if self._current is not None:
            self._current.text_parts.append(data)

    @staticmethod
    def _is_assistant_message_start(attrs: dict[str, str]) -> bool:
        role = attrs.get("data-message-author-role", "").strip().lower()
        if role == "assistant":
            return True

        aria = attrs.get("aria-label", "").strip().lower()
        data_role = attrs.get("data-role", "").strip().lower()
        return "assistant" in aria and data_role in {"message", "conversation-turn", "assistant"}

    @staticmethod
    def _is_streaming_signal(tag: str, attrs: dict[str, str], lowered_values: str) -> bool:
        if attrs.get("data-streaming", "").lower() == "true":
            return True
        if "stop-generating" in lowered_values or "stop generating" in lowered_values:
            return True
        if "result-streaming" in lowered_values or "streaming" in lowered_values:
            return True
        return False

    @staticmethod
    def _is_enabled_composer(tag: str, attrs: dict[str, str]) -> bool:
        if tag == "textarea":
            return "disabled" not in attrs and attrs.get("aria-disabled", "false").lower() != "true"
        if attrs.get("contenteditable", "").lower() == "true":
            return attrs.get("aria-disabled", "false").lower() != "true"
        return False


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _filename_from_href(href: str) -> str | None:
    parsed = urlparse(href)
    candidate = unquote(Path(parsed.path).name)
    match = _ZIP_RE.search(candidate)
    return match.group("name") if match else None


def _artifact_candidates_from_latest_message(message: _AssistantMessage) -> tuple[ArtifactCandidate, ...]:
    # Prefer real href-backed download candidates. A common DOM shape repeats
    # the same .zip filename both in the href and as visible anchor text; that
    # must produce one candidate, not two.
    seen_filenames: set[str] = set()
    candidates: list[ArtifactCandidate] = []

    for href in message.hrefs:
        filename = _filename_from_href(href)
        if filename is None:
            continue
        filename_key = filename.lower()
        if filename_key in seen_filenames:
            continue
        seen_filenames.add(filename_key)
        candidates.append(ArtifactCandidate(filename=filename, href=href, source="href", text=filename))

    for match in _ZIP_RE.finditer(message.text):
        filename = match.group("name")
        filename_key = filename.lower()
        if filename_key in seen_filenames:
            continue
        seen_filenames.add(filename_key)
        candidates.append(ArtifactCandidate(filename=filename, href=None, source="text", text=filename))

    return tuple(candidates)


def snapshot_from_html(html: str) -> ChatPageSnapshot:
    parser = _ChatPageParser()
    parser.feed(html)
    parser.close()

    latest = parser.assistant_messages[-1] if parser.assistant_messages else _AssistantMessage(text_parts=[], hrefs=[])
    latest_text = latest.text
    latest_hash = stable_hash(latest_text)

    return ChatPageSnapshot(
        latest_assistant_text=latest_text,
        latest_assistant_html_hash=latest_hash,
        streaming=parser.streaming,
        composer_enabled=parser.composer_enabled,
        artifact_candidates=_artifact_candidates_from_latest_message(latest),
        assistant_message_count=len(parser.assistant_messages),
    )


def snapshot_from_file(path: str | Path) -> ChatPageSnapshot:
    return snapshot_from_html(Path(path).read_text(encoding="utf-8"))
