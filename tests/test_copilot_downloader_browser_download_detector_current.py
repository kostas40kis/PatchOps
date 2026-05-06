from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.browser_download_detector import (
    BLOCKED_AMBIGUOUS_ARTIFACTS,
    BLOCKED_NO_ARTIFACT,
    PASS_ARTIFACT_DETECTED,
    run_browser_download_detector,
    scan_download_folder_once,
)


def test_download_detector_empty_folder_is_controlled_no_artifact(tmp_path: Path):
    download_dir = tmp_path / "downloads"
    result = run_browser_download_detector(repo_root=tmp_path, download_dir=download_dir, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_NO_ARTIFACT
    assert result["candidate_count"] == 0
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["safety"]["file_download_observed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_download_detector_detects_single_zip_without_reading_content(tmp_path: Path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    sentinel = "RAW_DOWNLOAD_CONTENT_SENTINEL_D3_01"
    (download_dir / "patchops_bundle.zip").write_text(sentinel, encoding="utf-8")
    result = run_browser_download_detector(repo_root=tmp_path, download_dir=download_dir, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == PASS_ARTIFACT_DETECTED
    assert result["candidate_count"] == 1
    candidate = result["candidates"][0]
    assert candidate["name"] == "patchops_bundle.zip"
    assert candidate["suffix"] == ".zip"
    assert candidate["content_read"] is False
    assert candidate["hash_computed"] is False
    assert candidate["staged"] is False
    assert result["safety"]["file_download_observed"] is True
    serialized = json.dumps(result)
    evidence_json = Path(result["evidence_files"]["json"]).read_text(encoding="utf-8")
    assert sentinel not in serialized
    assert sentinel not in evidence_json


def test_download_detector_detects_json_and_ps1_and_blocks_ambiguous(tmp_path: Path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    (download_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (download_dir / "script.ps1").write_text("& { Set-StrictMode -Version Latest }", encoding="utf-8")
    result = run_browser_download_detector(repo_root=tmp_path, download_dir=download_dir, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_AMBIGUOUS_ARTIFACTS
    assert result["candidate_count"] == 2
    assert {item["suffix"] for item in result["candidates"]} == {".json", ".ps1"}


def test_download_detector_ignores_partial_unsupported_hidden_empty_and_directories(tmp_path: Path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    (download_dir / "partial.zip.crdownload").write_text("partial", encoding="utf-8")
    (download_dir / "notes.txt").write_text("unsupported", encoding="utf-8")
    (download_dir / ".hidden.zip").write_text("hidden", encoding="utf-8")
    (download_dir / "empty.zip").write_bytes(b"")
    (download_dir / "subdir").mkdir()
    scan = scan_download_folder_once(repo_root=tmp_path, download_dir=download_dir)
    assert scan["candidates"] == []
    reasons = {item["reason"] for item in scan["ignored"]}
    assert "partial_download_extension" in reasons
    assert "unsupported_extension" in reasons
    assert "hidden" in reasons
    assert "empty_file" in reasons
    assert "directory" in reasons


def test_download_detector_uses_configured_download_dir(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    download_dir = repo_root / "configured_downloads"
    download_dir.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(json.dumps({"paths": {"browser_downloads_dir": str(download_dir)}}), encoding="utf-8")
    (download_dir / "configured.zip").write_text("zip", encoding="utf-8")
    result = run_browser_download_detector(repo_root=repo_root, config_path=config_path, evidence_root=repo_root / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == PASS_ARTIFACT_DETECTED
    assert Path(result["download_dir"]) == download_dir.resolve(strict=False)


def test_download_detector_bounded_poll_can_observe_late_file(tmp_path: Path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    (download_dir / "late.json").write_text("{}", encoding="utf-8")
    result = run_browser_download_detector(
        repo_root=tmp_path,
        download_dir=download_dir,
        evidence_root=tmp_path / "evidence",
        timeout_seconds=0.01,
        poll_interval_seconds=0.01,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_ARTIFACT_DETECTED
    assert result["checks"]["bounded_timeout_used"] is True


def test_repository_browser_download_detector_doctor_is_controlled_and_safe():
    result = run_browser_download_detector(
        repo_root=Path.cwd(),
        config_path="data/config/copilot_downloader_config.json",
        evidence_root="data/runtime/copilot_downloader/d3_01_browser_download_detector_test",
    )
    assert result["ok"] is True
    assert result["result_label"] in {PASS_ARTIFACT_DETECTED, BLOCKED_NO_ARTIFACT, BLOCKED_AMBIGUOUS_ARTIFACTS}
    assert result["checks"]["artifact_not_executed"] is True
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["file_content_not_read"] is True