from __future__ import annotations

from pathlib import Path
import os

from patchops.llm_browser.artifact_detector import detect_downloadable_patchops_artifact
from patchops.llm_browser.chat_page_contract import ArtifactCandidate, snapshot_from_html
from patchops.llm_browser.download_bridge import (
    click_download_candidate,
    click_download_from_detection,
    element_matches_candidate,
    find_download_element,
    summarize_download_element,
)


class FakeElement:
    def __init__(
        self,
        *,
        text: str = "",
        href: str | None = None,
        download: str | None = None,
        aria_label: str | None = None,
        tag_name: str = "a",
        on_click=None,
    ) -> None:
        self.text = text
        self.tag_name = tag_name
        self._attrs = {
            "href": href,
            "download": download,
            "aria-label": aria_label,
        }
        self.on_click = on_click
        self.click_calls = 0

    def get_attribute(self, name: str):
        return self._attrs.get(name)

    def click(self) -> None:
        self.click_calls += 1
        if self.on_click is not None:
            self.on_click()


class NotClickableElement:
    text = "patch_d0_12_browser_click_to_download_bridge_patchops_bundle.zip"
    tag_name = "span"

    def get_attribute(self, name: str):
        return None


class FakeDriver:
    def __init__(self, elements_by_selector: dict[str, list[object]]) -> None:
        self.elements_by_selector = elements_by_selector
        self.calls: list[tuple[str, str]] = []

    def find_elements(self, by: str, selector: str):
        self.calls.append((by, selector))
        return self.elements_by_selector.get(selector, [])


def _candidate(filename: str = "patch_d0_12_browser_click_to_download_bridge_patchops_bundle.zip") -> ArtifactCandidate:
    return ArtifactCandidate(
        filename=filename,
        href=f"/downloads/{filename}?download=1",
        source="href",
        text=filename,
    )


def test_element_matches_candidate_by_href_text_download_or_aria() -> None:
    candidate = _candidate()

    assert element_matches_candidate(FakeElement(href="https://example.test/downloads/" + candidate.filename), candidate) is True
    assert element_matches_candidate(FakeElement(text=candidate.filename), candidate) is True
    assert element_matches_candidate(FakeElement(download=candidate.filename), candidate) is True
    assert element_matches_candidate(FakeElement(aria_label="Download " + candidate.filename), candidate) is True
    assert element_matches_candidate(FakeElement(text="other.zip", href="/downloads/other.zip"), candidate) is False


def test_summarize_download_element_is_compact() -> None:
    element = FakeElement(
        text="Download bundle",
        href="/downloads/patch_d0_12_browser_click_to_download_bridge_patchops_bundle.zip",
        download="patch_d0_12_browser_click_to_download_bridge_patchops_bundle.zip",
    )

    summary = summarize_download_element(element, selector='a[href*=".zip"]')
    payload = summary.to_payload()

    assert payload["tag_name"] == "a"
    assert payload["text"] == "Download bundle"
    assert payload["href"] == "/downloads/patch_d0_12_browser_click_to_download_bridge_patchops_bundle.zip"
    assert payload["download"] == "patch_d0_12_browser_click_to_download_bridge_patchops_bundle.zip"
    assert payload["selector"] == 'a[href*=".zip"]'


def test_find_download_element_returns_first_matching_candidate() -> None:
    candidate = _candidate()
    nonmatch = FakeElement(text="random_notes.zip", href="/downloads/random_notes.zip")
    match = FakeElement(text=candidate.filename, href=candidate.href)
    driver = FakeDriver({'a[href*=".zip"]': [nonmatch, match]})

    element, summary = find_download_element(driver, candidate)

    assert element is match
    assert summary is not None
    assert summary.href == candidate.href
    assert driver.calls == [("css selector", 'a[href*=".zip"]')]


def test_click_download_candidate_clicks_and_waits_for_ready_file(tmp_path: Path) -> None:
    candidate = _candidate()
    download_dir = tmp_path / "Downloads"
    download_dir.mkdir()
    expected_file = download_dir / candidate.filename

    def create_download() -> None:
        expected_file.write_text("zip bytes", encoding="utf-8")
        os.utime(expected_file, (100.0, 100.0))

    element = FakeElement(text=candidate.filename, href=candidate.href, on_click=create_download)
    driver = FakeDriver({'a[href*=".zip"]': [element]})

    result = click_download_candidate(
        driver,
        candidate,
        download_dir=download_dir,
        min_stable_age_seconds=0,
        timeout_seconds=1,
        poll_seconds=0.1,
    )

    assert result.clicked is True
    assert result.ready is True
    assert result.reason == "download_ready"
    assert result.expected_path == expected_file
    assert element.click_calls == 1


def test_click_download_candidate_can_prepare_artifact_copy(tmp_path: Path) -> None:
    candidate = _candidate()
    download_dir = tmp_path / "Downloads"
    prepared_dir = tmp_path / "prepared"
    download_dir.mkdir()
    expected_file = download_dir / candidate.filename

    def create_download() -> None:
        expected_file.write_text("zip bytes", encoding="utf-8")
        os.utime(expected_file, (100.0, 100.0))

    driver = FakeDriver({'a[href*=".zip"]': [FakeElement(text=candidate.filename, href=candidate.href, on_click=create_download)]})

    result = click_download_candidate(
        driver,
        candidate,
        download_dir=download_dir,
        prepared_dir=prepared_dir,
        min_stable_age_seconds=0,
        timeout_seconds=1,
        poll_seconds=0.1,
    )

    assert result.ready is True
    assert result.prepared_artifact is not None
    assert result.prepared_artifact.prepared_path == prepared_dir / candidate.filename
    assert result.prepared_artifact.prepared_path.read_text(encoding="utf-8") == "zip bytes"


def test_click_download_candidate_reports_missing_element(tmp_path: Path) -> None:
    candidate = _candidate()
    download_dir = tmp_path / "Downloads"
    download_dir.mkdir()
    driver = FakeDriver({'a[href*=".zip"]': []})

    result = click_download_candidate(
        driver,
        candidate,
        download_dir=download_dir,
        timeout_seconds=0,
        min_stable_age_seconds=0,
    )

    assert result.clicked is False
    assert result.reason == "download_element_not_found"
    assert result.wait_result is None


def test_click_download_candidate_reports_not_clickable(tmp_path: Path) -> None:
    candidate = _candidate()
    download_dir = tmp_path / "Downloads"
    download_dir.mkdir()
    driver = FakeDriver({'a[href*=".zip"]': [NotClickableElement()]})

    result = click_download_candidate(
        driver,
        candidate,
        download_dir=download_dir,
        timeout_seconds=0,
        min_stable_age_seconds=0,
    )

    assert result.clicked is False
    assert result.reason == "download_element_not_clickable"
    assert result.element is not None


def test_click_download_candidate_reports_download_not_ready(tmp_path: Path) -> None:
    candidate = _candidate()
    download_dir = tmp_path / "Downloads"
    download_dir.mkdir()
    element = FakeElement(text=candidate.filename, href=candidate.href)
    driver = FakeDriver({'a[href*=".zip"]': [element]})

    result = click_download_candidate(
        driver,
        candidate,
        download_dir=download_dir,
        timeout_seconds=0,
        min_stable_age_seconds=0,
    )

    assert result.clicked is True
    assert result.ready is False
    assert result.reason == "download_not_ready"
    assert result.wait_result is not None
    assert result.wait_result.timed_out is True


def test_click_download_from_detection_handles_missing_detection(tmp_path: Path) -> None:
    snapshot = snapshot_from_html(
        '<article data-message-author-role="assistant">no zip here</article><textarea></textarea>'
    )
    detection = detect_downloadable_patchops_artifact(snapshot)
    download_dir = tmp_path / "Downloads"
    download_dir.mkdir()

    result = click_download_from_detection(FakeDriver({}), detection, download_dir=download_dir)

    assert result.clicked is False
    assert result.reason == "artifact_not_detected:no_patchops_bundle_candidates"
    assert result.candidate is None


def test_click_download_from_detection_clicks_detected_candidate(tmp_path: Path) -> None:
    filename = "patch_d0_12_browser_click_to_download_bridge_patchops_bundle.zip"
    html = f"""
    <article data-message-author-role="assistant">
      <a href="/downloads/{filename}?download=1">{filename}</a>
    </article>
    <textarea></textarea>
    """
    snapshot = snapshot_from_html(html)
    detection = detect_downloadable_patchops_artifact(snapshot)
    download_dir = tmp_path / "Downloads"
    download_dir.mkdir()
    expected_file = download_dir / filename

    def create_download() -> None:
        expected_file.write_text("zip bytes", encoding="utf-8")
        os.utime(expected_file, (100.0, 100.0))

    driver = FakeDriver({'a[href*=".zip"]': [FakeElement(text=filename, href=f"/downloads/{filename}?download=1", on_click=create_download)]})

    result = click_download_from_detection(
        driver,
        detection,
        download_dir=download_dir,
        min_stable_age_seconds=0,
        timeout_seconds=1,
        poll_seconds=0.1,
    )

    assert result.clicked is True
    assert result.ready is True
    assert result.candidate is not None
    assert result.candidate.filename == filename


def test_download_click_result_payload_is_stable(tmp_path: Path) -> None:
    candidate = _candidate()
    download_dir = tmp_path / "Downloads"
    download_dir.mkdir()
    expected_file = download_dir / candidate.filename

    def create_download() -> None:
        expected_file.write_text("zip bytes", encoding="utf-8")
        os.utime(expected_file, (100.0, 100.0))

    result = click_download_candidate(
        FakeDriver({'a[href*=".zip"]': [FakeElement(text=candidate.filename, href=candidate.href, on_click=create_download)]}),
        candidate,
        download_dir=download_dir,
        min_stable_age_seconds=0,
        timeout_seconds=1,
        poll_seconds=0.1,
    )

    payload = result.to_payload()

    assert payload["clicked"] is True
    assert payload["ready"] is True
    assert payload["candidate"]["filename"] == candidate.filename
    assert payload["expected_path"] == str(expected_file)
    assert payload["wait_result"]["ready"] is True
