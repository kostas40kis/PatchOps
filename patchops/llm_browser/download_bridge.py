"""Browser click-to-download bridge for the optional LLM browser runner.

This module bridges the passive artifact detector to the passive download
manager by clicking a detected download element and then waiting for the local
download file to become stable.

It is deliberately narrow:
- importing this module does not import Selenium,
- tests use fake drivers/elements,
- it does not run PatchOps,
- it does not auto-send prompts,
- it does not create a localhost service.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from .artifact_detector import ArtifactDetectionResult
from .chat_page_contract import ArtifactCandidate
from .download_manager import (
    DownloadWaitResult,
    PreparedDownloadArtifact,
    expected_download_path_for_candidate,
    prepare_downloaded_artifact,
    wait_for_candidate_download,
)


DEFAULT_DOWNLOAD_SELECTORS: tuple[str, ...] = (
    'a[href*=".zip"]',
    'a[download]',
    '[data-testid*="download"]',
    '[aria-label*="Download"]',
)


@dataclass(frozen=True)
class DownloadElementSummary:
    tag_name: str | None
    text: str
    href: str | None
    download: str | None
    selector: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "tag_name": self.tag_name,
            "text": self.text,
            "href": self.href,
            "download": self.download,
            "selector": self.selector,
        }


@dataclass(frozen=True)
class DownloadClickResult:
    clicked: bool
    reason: str
    candidate: ArtifactCandidate | None
    element: DownloadElementSummary | None
    expected_path: Path | None
    wait_result: DownloadWaitResult | None
    prepared_artifact: PreparedDownloadArtifact | None

    @property
    def ready(self) -> bool:
        return self.wait_result.ready if self.wait_result is not None else False

    def to_payload(self) -> dict[str, object]:
        return {
            "clicked": self.clicked,
            "reason": self.reason,
            "candidate": None if self.candidate is None else self.candidate.to_payload(),
            "element": None if self.element is None else self.element.to_payload(),
            "expected_path": None if self.expected_path is None else str(self.expected_path),
            "wait_result": None if self.wait_result is None else self.wait_result.to_payload(),
            "prepared_artifact": None if self.prepared_artifact is None else self.prepared_artifact.to_payload(),
            "ready": self.ready,
        }


def _safe_text(element: Any) -> str:
    value = getattr(element, "text", "")
    return "" if value is None else str(value)


def _safe_tag_name(element: Any) -> str | None:
    value = getattr(element, "tag_name", None)
    return None if value is None else str(value)


def _safe_get_attribute(element: Any, name: str) -> str | None:
    getter = getattr(element, "get_attribute", None)
    if not callable(getter):
        return None
    try:
        value = getter(name)
    except Exception:
        return None
    return None if value is None else str(value)


def summarize_download_element(element: Any, *, selector: str | None = None) -> DownloadElementSummary:
    return DownloadElementSummary(
        tag_name=_safe_tag_name(element),
        text=_safe_text(element),
        href=_safe_get_attribute(element, "href"),
        download=_safe_get_attribute(element, "download"),
        selector=selector,
    )


def _normalized(value: str | None) -> str:
    return "" if value is None else value.strip().lower()


def element_matches_candidate(element: Any, candidate: ArtifactCandidate) -> bool:
    filename = _normalized(candidate.filename)
    candidate_href = _normalized(candidate.href)

    text = _normalized(_safe_text(element))
    href = _normalized(_safe_get_attribute(element, "href"))
    download = _normalized(_safe_get_attribute(element, "download"))
    aria = _normalized(_safe_get_attribute(element, "aria-label"))

    if filename and filename in {download, text}:
        return True
    if filename and (filename in href or filename in aria or filename in text):
        return True
    if candidate_href and (candidate_href == href or href.endswith(candidate_href)):
        return True
    return False


def find_download_element(
    driver: Any,
    candidate: ArtifactCandidate,
    *,
    selectors: Sequence[str] = DEFAULT_DOWNLOAD_SELECTORS,
) -> tuple[Any | None, DownloadElementSummary | None]:
    """Find the first DOM element that appears to represent candidate.

    Uses Selenium-compatible string locator names, but does not import Selenium.
    """

    finder = getattr(driver, "find_elements", None)
    if not callable(finder):
        return None, None

    for selector in selectors:
        try:
            elements = list(finder("css selector", selector))
        except Exception:
            continue

        for element in elements:
            if element_matches_candidate(element, candidate):
                return element, summarize_download_element(element, selector=selector)

    return None, None


def click_download_candidate(
    driver: Any,
    candidate: ArtifactCandidate,
    *,
    download_dir: str | Path,
    prepared_dir: str | Path | None = None,
    timeout_seconds: float = 60.0,
    poll_seconds: float = 1.0,
    min_stable_age_seconds: float = 1.0,
    selectors: Sequence[str] = DEFAULT_DOWNLOAD_SELECTORS,
) -> DownloadClickResult:
    expected_path = expected_download_path_for_candidate(download_dir, candidate)
    element, summary = find_download_element(driver, candidate, selectors=selectors)

    if element is None:
        return DownloadClickResult(
            clicked=False,
            reason="download_element_not_found",
            candidate=candidate,
            element=None,
            expected_path=expected_path,
            wait_result=None,
            prepared_artifact=None,
        )

    click = getattr(element, "click", None)
    if not callable(click):
        return DownloadClickResult(
            clicked=False,
            reason="download_element_not_clickable",
            candidate=candidate,
            element=summary,
            expected_path=expected_path,
            wait_result=None,
            prepared_artifact=None,
        )

    click()

    wait_result = wait_for_candidate_download(
        candidate,
        download_dir=download_dir,
        timeout_seconds=timeout_seconds,
        poll_seconds=poll_seconds,
        min_stable_age_seconds=min_stable_age_seconds,
    )

    if not wait_result.ready:
        return DownloadClickResult(
            clicked=True,
            reason="download_not_ready",
            candidate=candidate,
            element=summary,
            expected_path=expected_path,
            wait_result=wait_result,
            prepared_artifact=None,
        )

    prepared = None
    if prepared_dir is not None:
        prepared = prepare_downloaded_artifact(wait_result.state.path, prepared_dir)

    return DownloadClickResult(
        clicked=True,
        reason="download_ready",
        candidate=candidate,
        element=summary,
        expected_path=expected_path,
        wait_result=wait_result,
        prepared_artifact=prepared,
    )


def click_download_from_detection(
    driver: Any,
    detection: ArtifactDetectionResult,
    *,
    download_dir: str | Path,
    prepared_dir: str | Path | None = None,
    timeout_seconds: float = 60.0,
    poll_seconds: float = 1.0,
    min_stable_age_seconds: float = 1.0,
    selectors: Sequence[str] = DEFAULT_DOWNLOAD_SELECTORS,
) -> DownloadClickResult:
    if not detection.found or detection.candidate is None:
        return DownloadClickResult(
            clicked=False,
            reason=f"artifact_not_detected:{detection.reason}",
            candidate=None,
            element=None,
            expected_path=None,
            wait_result=None,
            prepared_artifact=None,
        )

    return click_download_candidate(
        driver,
        detection.candidate,
        download_dir=download_dir,
        prepared_dir=prepared_dir,
        timeout_seconds=timeout_seconds,
        poll_seconds=poll_seconds,
        min_stable_age_seconds=min_stable_age_seconds,
        selectors=selectors,
    )
