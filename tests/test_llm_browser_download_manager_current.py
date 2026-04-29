from __future__ import annotations

import os
from pathlib import Path

import pytest

from patchops.llm_browser.chat_page_contract import ArtifactCandidate
from patchops.llm_browser.download_manager import (
    expected_download_path,
    expected_download_path_for_candidate,
    inspect_download_state,
    partial_download_paths,
    prepare_downloaded_artifact,
    validate_download_filename,
    wait_for_candidate_download,
    wait_for_download_ready,
)


def test_validate_download_filename_accepts_patchops_bundle() -> None:
    assert validate_download_filename("patch_d0_11_download_manager_patchops_bundle.zip") == "patch_d0_11_download_manager_patchops_bundle.zip"


@pytest.mark.parametrize(
    "bad_name",
    [
        "",
        "random_notes.zip",
        "patch_d0_11_download_manager.zip",
        "../patch_d0_11_download_manager_patchops_bundle.zip",
        r"..\patch_d0_11_download_manager_patchops_bundle.zip",
        "nested/patch_d0_11_download_manager_patchops_bundle.zip",
        r"nested\patch_d0_11_download_manager_patchops_bundle.zip",
    ],
)
def test_validate_download_filename_rejects_unsafe_or_wrong_names(bad_name: str) -> None:
    with pytest.raises(ValueError):
        validate_download_filename(bad_name)


def test_expected_download_path_joins_safe_filename(tmp_path: Path) -> None:
    path = expected_download_path(tmp_path, "patch_d0_11_download_manager_patchops_bundle.zip")

    assert path == tmp_path / "patch_d0_11_download_manager_patchops_bundle.zip"


def test_expected_download_path_for_candidate(tmp_path: Path) -> None:
    candidate = ArtifactCandidate(
        filename="patch_d0_11_download_manager_patchops_bundle.zip",
        href="/downloads/patch_d0_11_download_manager_patchops_bundle.zip",
        source="href",
        text="patch_d0_11_download_manager_patchops_bundle.zip",
    )

    path = expected_download_path_for_candidate(tmp_path, candidate)

    assert path == tmp_path / "patch_d0_11_download_manager_patchops_bundle.zip"


def test_partial_download_paths_use_browser_temp_suffixes(tmp_path: Path) -> None:
    target = tmp_path / "patch_d0_11_download_manager_patchops_bundle.zip"

    partials = partial_download_paths(target)

    assert target.with_name(target.name + ".crdownload") in partials
    assert target.with_name(target.name + ".part") in partials
    assert target.with_name(target.name + ".tmp") in partials


def test_inspect_download_state_missing(tmp_path: Path) -> None:
    state = inspect_download_state(tmp_path / "patch_missing_patchops_bundle.zip")

    assert state.ready is False
    assert state.exists is False
    assert state.reason == "missing"


def test_inspect_download_state_blocks_partial_download(tmp_path: Path) -> None:
    target = tmp_path / "patch_d0_11_download_manager_patchops_bundle.zip"
    partial = target.with_name(target.name + ".crdownload")
    partial.write_text("partial", encoding="utf-8")

    state = inspect_download_state(target)

    assert state.ready is False
    assert state.complete is False
    assert state.reason == "partial_download_present"
    assert state.partial_paths == (partial,)


def test_inspect_download_state_requires_stable_age(tmp_path: Path) -> None:
    target = tmp_path / "patch_d0_11_download_manager_patchops_bundle.zip"
    target.write_text("zip bytes", encoding="utf-8")
    os.utime(target, (100.0, 100.0))

    young = inspect_download_state(target, min_stable_age_seconds=10.0, now=lambda: 105.0)
    ready = inspect_download_state(target, min_stable_age_seconds=10.0, now=lambda: 111.0)

    assert young.ready is False
    assert young.reason == "not_stable_yet"
    assert ready.ready is True
    assert ready.reason == "ready"
    assert ready.size_bytes == len("zip bytes")


def test_inspect_download_state_rejects_negative_stable_age(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="min_stable_age_seconds"):
        inspect_download_state(tmp_path / "patch_x_patchops_bundle.zip", min_stable_age_seconds=-1)


def test_wait_for_download_ready_returns_immediately_when_ready(tmp_path: Path) -> None:
    target = tmp_path / "patch_d0_11_download_manager_patchops_bundle.zip"
    target.write_text("zip bytes", encoding="utf-8")
    os.utime(target, (100.0, 100.0))

    result = wait_for_download_ready(
        target,
        timeout_seconds=30,
        poll_seconds=1,
        min_stable_age_seconds=5,
        now=lambda: 106.0,
        sleep=lambda _seconds: None,
    )

    assert result.ready is True
    assert result.timed_out is False
    assert result.attempts == 1


def test_wait_for_download_ready_times_out_when_missing(tmp_path: Path) -> None:
    times = iter([0.0, 0.0, 2.0, 2.0, 4.0, 4.0])

    result = wait_for_download_ready(
        tmp_path / "patch_missing_patchops_bundle.zip",
        timeout_seconds=4,
        poll_seconds=2,
        now=lambda: next(times),
        sleep=lambda _seconds: None,
    )

    assert result.ready is False
    assert result.timed_out is True
    assert result.state.reason == "missing"


def test_wait_for_download_ready_rejects_bad_timing_values(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="timeout_seconds"):
        wait_for_download_ready(tmp_path / "patch_missing_patchops_bundle.zip", timeout_seconds=-1)

    with pytest.raises(ValueError, match="poll_seconds"):
        wait_for_download_ready(tmp_path / "patch_missing_patchops_bundle.zip", poll_seconds=0)


def test_prepare_downloaded_artifact_copies_to_prepared_dir(tmp_path: Path) -> None:
    source = tmp_path / "Downloads" / "patch_d0_11_download_manager_patchops_bundle.zip"
    prepared = tmp_path / "prepared"
    source.parent.mkdir()
    source.write_text("zip bytes", encoding="utf-8")

    result = prepare_downloaded_artifact(source, prepared)

    assert result.source_path == source
    assert result.prepared_path == prepared / source.name
    assert result.prepared_path.read_text(encoding="utf-8") == "zip bytes"
    assert result.copied is True
    assert result.size_bytes == len("zip bytes")


def test_prepare_downloaded_artifact_can_reference_without_copy(tmp_path: Path) -> None:
    source = tmp_path / "patch_d0_11_download_manager_patchops_bundle.zip"
    source.write_text("zip bytes", encoding="utf-8")

    result = prepare_downloaded_artifact(source, tmp_path / "prepared", copy=False)

    assert result.prepared_path == source
    assert result.copied is False


def test_prepare_downloaded_artifact_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        prepare_downloaded_artifact(tmp_path / "patch_missing_patchops_bundle.zip", tmp_path / "prepared")


def test_wait_for_candidate_download_uses_candidate_filename(tmp_path: Path) -> None:
    filename = "patch_d0_11_download_manager_patchops_bundle.zip"
    target = tmp_path / filename
    target.write_text("zip bytes", encoding="utf-8")
    os.utime(target, (100.0, 100.0))
    candidate = ArtifactCandidate(filename=filename, href="/downloads/" + filename, source="href", text=filename)

    result = wait_for_candidate_download(
        candidate,
        download_dir=tmp_path,
        timeout_seconds=5,
        min_stable_age_seconds=1,
        now=lambda: 102.0,
        sleep=lambda _seconds: None,
    )

    assert result.ready is True
    assert result.state.path == target


def test_download_wait_result_payload_is_stable(tmp_path: Path) -> None:
    target = tmp_path / "patch_d0_11_download_manager_patchops_bundle.zip"
    target.write_text("zip bytes", encoding="utf-8")
    os.utime(target, (100.0, 100.0))

    result = wait_for_download_ready(
        target,
        timeout_seconds=5,
        min_stable_age_seconds=1,
        now=lambda: 102.0,
        sleep=lambda _seconds: None,
    )
    payload = result.to_payload()

    assert payload["ready"] is True
    assert payload["timed_out"] is False
    assert payload["state"]["ready"] is True
    assert payload["state"]["path"] == str(target)
