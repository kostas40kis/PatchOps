from __future__ import annotations

from pathlib import Path

import pytest

from patchops.llm_browser.browser_paths import (
    browser_candidate_paths,
    edge_candidate_paths,
    find_browser_path,
    normalize_browser,
    opera_candidate_paths,
    require_browser_path,
)


def test_edge_explicit_override_path_is_checked_first(tmp_path: Path) -> None:
    override = tmp_path / "edge" / "msedge.exe"
    override.parent.mkdir()
    override.write_text("", encoding="utf-8")

    result = find_browser_path(
        "edge",
        explicit_path=override,
        exists=lambda path: path == override,
    )

    assert result.found is True
    assert result.executable_path == override
    assert result.source == "override"
    assert result.candidates[0] == override


def test_opera_explicit_override_path_is_checked_first(tmp_path: Path) -> None:
    override = tmp_path / "opera" / "opera.exe"
    override.parent.mkdir()
    override.write_text("", encoding="utf-8")

    result = find_browser_path(
        "opera",
        explicit_path=str(override),
        exists=lambda path: path == override,
    )

    assert result.found is True
    assert result.executable_path == override
    assert result.source == "override"
    assert result.candidates[0] == override


def test_edge_candidate_path_can_be_found_from_environment_override(tmp_path: Path) -> None:
    edge = tmp_path / "custom_edge.exe"
    edge.write_text("", encoding="utf-8")
    env = {"PATCHOPS_EDGE_PATH": str(edge)}

    result = find_browser_path("edge", environ=env, exists=lambda path: path == edge)

    assert result.found is True
    assert result.executable_path == edge
    assert result.source == "override"


def test_opera_candidate_paths_include_localappdata_without_crashing(tmp_path: Path) -> None:
    env = {"LOCALAPPDATA": str(tmp_path)}
    candidates = opera_candidate_paths(env)

    assert tmp_path / "Programs" / "Opera" / "opera.exe" in candidates
    assert tmp_path / "Programs" / "Opera GX" / "opera.exe" in candidates


def test_missing_browser_result_is_clear_and_non_crashing_without_environment() -> None:
    result = find_browser_path("opera", environ={}, exists=lambda _path: False)

    assert result.found is False
    assert result.executable_path is None
    assert result.source == "not_found"
    assert "not found" in result.message.lower()
    assert result.candidates


def test_required_browser_path_raises_clear_file_not_found() -> None:
    with pytest.raises(FileNotFoundError, match="edge executable was not found"):
        require_browser_path("edge", environ={}, exists=lambda _path: False)


def test_invalid_browser_name_is_rejected() -> None:
    with pytest.raises(ValueError, match="browser must be one of"):
        normalize_browser("firefox")

    with pytest.raises(ValueError, match="browser must be one of"):
        browser_candidate_paths("chrome")


def test_standard_edge_candidates_are_present() -> None:
    candidates = edge_candidate_paths({})

    assert Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe") in candidates
    assert Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe") in candidates


def test_standard_opera_candidates_are_present() -> None:
    candidates = opera_candidate_paths({})

    assert Path(r"C:\Program Files\Opera\opera.exe") in candidates
    assert Path(r"C:\Program Files\Opera GX\opera.exe") in candidates
