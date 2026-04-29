from __future__ import annotations

from pathlib import Path

import pytest

from patchops.llm_browser.chat_page_contract import (
    snapshot_from_file,
    snapshot_from_html,
    stable_hash,
)
from patchops.llm_browser.reply_stability import ReplyStabilityTracker


FIXTURES = Path(__file__).parent / "fixtures" / "llm_browser"


def test_snapshot_detects_latest_assistant_artifact_only() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_with_zip.html")

    assert snapshot.assistant_message_count == 2
    assert snapshot.has_latest_assistant_reply is True
    assert snapshot.streaming is False
    assert snapshot.composer_enabled is True
    assert snapshot.ready_for_artifact_scan is True

    filenames = [candidate.filename for candidate in snapshot.artifact_candidates]
    assert filenames == ["patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip"]
    assert "patch_d0_08_old_patchops_bundle.zip" not in filenames


def test_snapshot_without_zip_has_no_artifact_candidates() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_without_zip.html")

    assert snapshot.ready_for_artifact_scan is True
    assert snapshot.artifact_candidates == ()


def test_snapshot_streaming_is_not_ready_even_with_latest_reply() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_streaming.html")

    assert snapshot.has_latest_assistant_reply is True
    assert snapshot.streaming is True
    assert snapshot.composer_enabled is False
    assert snapshot.ready_for_artifact_scan is False


def test_snapshot_composer_disabled_is_not_ready() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_composer_disabled.html")

    assert snapshot.streaming is False
    assert snapshot.composer_enabled is False
    assert snapshot.ready_for_artifact_scan is False


def test_snapshot_payload_does_not_include_full_message_text() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_with_zip.html")

    payload = snapshot.to_payload()

    assert "latest_assistant_text" not in payload
    assert payload["latest_assistant_text_length"] == len(snapshot.latest_assistant_text)
    assert payload["assistant_message_count"] == 2
    assert payload["artifact_candidates"]


def test_stable_hash_is_deterministic() -> None:
    assert stable_hash("same text") == stable_hash("same text")
    assert stable_hash("same text") != stable_hash("different text")


def test_reply_stability_requires_two_matching_observations_and_elapsed_time() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_with_zip.html")
    tracker = ReplyStabilityTracker(stability_seconds=15)

    first = tracker.observe(snapshot, now=100.0)
    second = tracker.observe(snapshot, now=110.0)
    third = tracker.observe(snapshot, now=115.0)

    assert first.ready is False
    assert first.reason == "hash_changed"
    assert second.ready is False
    assert second.reason == "warming_up"
    assert third.ready is True
    assert third.reason == "stable"
    assert third.stable_seconds == 15.0


def test_reply_stability_resets_when_hash_changes() -> None:
    snapshot_one = snapshot_from_html(
        '<article data-message-author-role="assistant">first</article><textarea></textarea>'
    )
    snapshot_two = snapshot_from_html(
        '<article data-message-author-role="assistant">second</article><textarea></textarea>'
    )
    tracker = ReplyStabilityTracker(stability_seconds=5)

    assert tracker.observe(snapshot_one, now=0).ready is False
    assert tracker.observe(snapshot_one, now=5).ready is True

    changed = tracker.observe(snapshot_two, now=6)
    assert changed.ready is False
    assert changed.reason == "hash_changed"

    stable = tracker.observe(snapshot_two, now=11)
    assert stable.ready is True


def test_reply_stability_blocks_streaming_and_composer_disabled() -> None:
    streaming = snapshot_from_file(FIXTURES / "chatgpt_reply_streaming.html")
    disabled = snapshot_from_file(FIXTURES / "chatgpt_reply_composer_disabled.html")
    tracker = ReplyStabilityTracker(stability_seconds=1)

    streaming_result = tracker.observe(streaming, now=0)
    disabled_result = tracker.observe(disabled, now=10)

    assert streaming_result.ready is False
    assert streaming_result.reason == "streaming"
    assert disabled_result.ready is False
    assert disabled_result.reason == "composer_disabled"


def test_reply_stability_requires_latest_assistant_reply() -> None:
    snapshot = snapshot_from_html("<html><body><textarea></textarea></body></html>")
    tracker = ReplyStabilityTracker(stability_seconds=1)

    result = tracker.observe(snapshot, now=0)

    assert result.ready is False
    assert result.reason == "missing_latest_assistant_reply"


def test_reply_stability_rejects_nonpositive_stability_seconds() -> None:
    with pytest.raises(ValueError, match="stability_seconds"):
        ReplyStabilityTracker(stability_seconds=0)
