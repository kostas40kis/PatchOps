from __future__ import annotations

from patchops.llm_browser.chat_page_contract import snapshot_from_html


def test_artifact_candidates_dedupe_href_and_visible_anchor_text() -> None:
    html = """
    <article data-message-author-role="assistant">
      <a href="/downloads/patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip?download=1">
        patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip
      </a>
    </article>
    <textarea></textarea>
    """

    snapshot = snapshot_from_html(html)

    assert len(snapshot.artifact_candidates) == 1
    candidate = snapshot.artifact_candidates[0]
    assert candidate.filename == "patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip"
    assert candidate.href == "/downloads/patch_d0_09_chatgpt_page_readiness_patchops_bundle.zip?download=1"
    assert candidate.source == "href"


def test_artifact_candidates_keep_distinct_zip_filenames() -> None:
    html = """
    <article data-message-author-role="assistant">
      <a href="/downloads/first_bundle.zip">first_bundle.zip</a>
      <span>second_bundle.zip</span>
    </article>
    <textarea></textarea>
    """

    snapshot = snapshot_from_html(html)

    assert [candidate.filename for candidate in snapshot.artifact_candidates] == [
        "first_bundle.zip",
        "second_bundle.zip",
    ]
