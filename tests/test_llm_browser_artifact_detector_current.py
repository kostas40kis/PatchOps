from __future__ import annotations

from pathlib import Path

from patchops.llm_browser.artifact_detector import (
    ArtifactDetectionResult,
    candidate_is_processed,
    detect_downloadable_patchops_artifact,
    filter_patchops_bundle_candidates,
    is_patchops_bundle_filename,
)
from patchops.llm_browser.chat_page_contract import ArtifactCandidate, snapshot_from_file, snapshot_from_html


FIXTURES = Path(__file__).parent / "fixtures" / "llm_browser"


def test_detects_patchops_zip_in_latest_reply_fixture() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_with_zip.html")

    result = detect_downloadable_patchops_artifact(snapshot)

    assert result.found is True
    assert result.reason == "found"
    assert result.filename == "patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip"
    assert result.href == "/downloads/patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip?download=1"


def test_ignores_old_assistant_message_artifacts() -> None:
    html = """
    <article data-message-author-role="assistant">
      <a href="/downloads/patch_old_patchops_bundle.zip">patch_old_patchops_bundle.zip</a>
    </article>
    <article data-message-author-role="assistant">
      <p>No artifact in the newest assistant reply.</p>
    </article>
    <textarea></textarea>
    """

    snapshot = snapshot_from_html(html)
    result = detect_downloadable_patchops_artifact(snapshot)

    assert result.found is False
    assert result.reason == "no_patchops_bundle_candidates"
    assert result.candidates_seen == ()


def test_ignores_non_zip_and_non_patchops_bundle_zip_candidates() -> None:
    html = """
    <article data-message-author-role="assistant">
      <a href="/downloads/random_notes.zip">random_notes.zip</a>
      <span>patch_missing_suffix.zip</span>
      <span>patch_good_example_patchops_bundle.zip</span>
    </article>
    <textarea></textarea>
    """

    snapshot = snapshot_from_html(html)
    result = detect_downloadable_patchops_artifact(snapshot)

    assert result.found is True
    assert result.filename == "patch_good_example_patchops_bundle.zip"
    assert "random_notes.zip" in result.ignored_filenames
    assert "patch_missing_suffix.zip" in result.ignored_filenames


def test_processed_filename_is_ignored() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_with_zip.html")

    result = detect_downloadable_patchops_artifact(
        snapshot,
        processed_artifacts={"patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip"},
    )

    assert result.found is False
    assert result.reason == "artifact_already_processed"
    assert result.ignored_filenames == ("patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip",)


def test_processed_href_is_ignored() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_with_zip.html")

    result = detect_downloadable_patchops_artifact(
        snapshot,
        processed_artifacts={"/downloads/patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip?download=1"},
    )

    assert result.found is False
    assert result.reason == "artifact_already_processed"


def test_streaming_snapshot_blocks_detection() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_streaming.html")

    result = detect_downloadable_patchops_artifact(snapshot)

    assert result.found is False
    assert result.reason == "reply_still_streaming"


def test_disabled_composer_blocks_detection_even_with_artifact() -> None:
    html = """
    <article data-message-author-role="assistant">
      <a href="/downloads/patch_ready_patchops_bundle.zip">patch_ready_patchops_bundle.zip</a>
    </article>
    <textarea disabled></textarea>
    """

    snapshot = snapshot_from_html(html)
    result = detect_downloadable_patchops_artifact(snapshot)

    assert result.found is False
    assert result.reason == "composer_not_ready"


def test_missing_latest_assistant_reply_blocks_detection() -> None:
    snapshot = snapshot_from_html("<html><body><textarea></textarea></body></html>")

    result = detect_downloadable_patchops_artifact(snapshot)

    assert result.found is False
    assert result.reason == "missing_latest_assistant_reply"


def test_patchops_bundle_filename_matching_is_strict() -> None:
    assert is_patchops_bundle_filename("patch_314_example_patchops_bundle.zip") is True
    assert is_patchops_bundle_filename("patch_d0_10_downloadable_artifact_detector_patchops_bundle.zip") is True
    assert is_patchops_bundle_filename("PATCH_D0_10_DOWNLOADABLE_ARTIFACT_DETECTOR_PATCHOPS_BUNDLE.ZIP") is True

    assert is_patchops_bundle_filename("random_notes.zip") is False
    assert is_patchops_bundle_filename("patch_314_example.zip") is False
    assert is_patchops_bundle_filename("patchops_bundle.zip") is False
    assert is_patchops_bundle_filename("patch__patchops_bundle.zip") is False


def test_filter_preserves_distinct_unprocessed_patchops_bundles() -> None:
    candidates = (
        ArtifactCandidate("patch_first_patchops_bundle.zip", "/downloads/first.zip", "href", "first"),
        ArtifactCandidate("random_notes.zip", "/downloads/random_notes.zip", "href", "random"),
        ArtifactCandidate("patch_second_patchops_bundle.zip", None, "text", "second"),
    )

    accepted, ignored = filter_patchops_bundle_candidates(
        candidates,
        processed_artifacts={"patch_first_patchops_bundle.zip"},
    )

    assert [candidate.filename for candidate in accepted] == ["patch_second_patchops_bundle.zip"]
    assert ignored == ("patch_first_patchops_bundle.zip", "random_notes.zip")


def test_candidate_is_processed_matches_filename_or_href_case_insensitively() -> None:
    candidate = ArtifactCandidate(
        "Patch_D0_10_Downloadable_Artifact_Detector_PatchOps_Bundle.zip",
        "/downloads/patch_d0_10_downloadable_artifact_detector_patchops_bundle.zip?download=1",
        "href",
        "Patch_D0_10_Downloadable_Artifact_Detector_PatchOps_Bundle.zip",
    )

    assert candidate_is_processed(candidate, {"patch_d0_10_downloadable_artifact_detector_patchops_bundle.zip"}) is True
    assert candidate_is_processed(candidate, {"/DOWNLOADS/PATCH_D0_10_DOWNLOADABLE_ARTIFACT_DETECTOR_PATCHOPS_BUNDLE.ZIP?DOWNLOAD=1"}) is True
    assert candidate_is_processed(candidate, {"other.zip"}) is False


def test_detection_result_payload_is_compact_and_stable() -> None:
    snapshot = snapshot_from_file(FIXTURES / "chatgpt_reply_with_zip.html")
    result = detect_downloadable_patchops_artifact(snapshot)

    payload = result.to_payload()

    assert payload["found"] is True
    assert payload["reason"] == "found"
    assert payload["filename"] == "patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip"
    assert payload["href"] == "/downloads/patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip?download=1"
    assert "latest_assistant_text" not in payload


def test_detection_result_filename_and_href_are_none_when_missing() -> None:
    result = ArtifactDetectionResult(
        found=False,
        candidate=None,
        reason="missing",
        candidates_seen=(),
        ignored_filenames=(),
    )

    assert result.filename is None
    assert result.href is None
