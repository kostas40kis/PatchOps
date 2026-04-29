"""Reply stability detector for ChatGPT page snapshots."""

from __future__ import annotations

from dataclasses import dataclass

from .chat_page_contract import ChatPageSnapshot


@dataclass(frozen=True)
class ReplyReadiness:
    ready: bool
    reason: str
    stable_seconds: float
    current_hash: str

    def to_payload(self) -> dict[str, object]:
        return {
            "ready": self.ready,
            "reason": self.reason,
            "stable_seconds": self.stable_seconds,
            "current_hash": self.current_hash,
        }


class ReplyStabilityTracker:
    """Track when the latest assistant reply is probably finished.

    The tracker only consumes compact ChatPageSnapshot values. It does not
    rescan the DOM itself, which keeps polling noise low and makes unit tests
    deterministic.
    """

    def __init__(self, *, stability_seconds: float = 15.0) -> None:
        if stability_seconds <= 0:
            raise ValueError("stability_seconds must be positive")
        self.stability_seconds = float(stability_seconds)
        self._last_hash: str | None = None
        self._last_changed_at: float | None = None

    def observe(self, snapshot: ChatPageSnapshot, *, now: float) -> ReplyReadiness:
        current_hash = snapshot.latest_assistant_html_hash

        if not snapshot.has_latest_assistant_reply:
            self._reset()
            return ReplyReadiness(False, "missing_latest_assistant_reply", 0.0, current_hash)

        if snapshot.streaming:
            self._last_hash = current_hash
            self._last_changed_at = now
            return ReplyReadiness(False, "streaming", 0.0, current_hash)

        if not snapshot.composer_enabled:
            self._last_hash = current_hash
            self._last_changed_at = now
            return ReplyReadiness(False, "composer_disabled", 0.0, current_hash)

        if self._last_hash != current_hash:
            self._last_hash = current_hash
            self._last_changed_at = now
            return ReplyReadiness(False, "hash_changed", 0.0, current_hash)

        changed_at = now if self._last_changed_at is None else self._last_changed_at
        stable_for = max(0.0, float(now) - float(changed_at))

        if stable_for < self.stability_seconds:
            return ReplyReadiness(False, "warming_up", stable_for, current_hash)

        return ReplyReadiness(True, "stable", stable_for, current_hash)

    def _reset(self) -> None:
        self._last_hash = None
        self._last_changed_at = None
