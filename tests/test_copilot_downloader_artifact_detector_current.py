from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.artifact_detector import (
    SUPPORTED_EXTENSIONS,
    run_artifact_scan,
    scan_local_artifacts,
)
from patchops.copilot_downloader.config import default_config_payload, write_default_config


def _make_repo_with_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    write_default_config(config_path)
    return repo_root, config_path


def test_supported_extensions_are_downloader_intake_shapes():
    assert {".ps1", ".zip", ".json", ".txt", ".md"}.issubset(SUPPORTED_EXTENSIONS)


def test_scan_returns_blocked_no_artifact_for_empty_configured_folders(tmp_path: Path):
    repo_root, config_path = _make_repo_with_config(tmp_path)
    result = run_artifact_scan(repo_root=repo_root, config_path=config_path, evidence_root=repo_root / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_NO_ARTIFACT"
    assert result["candidate_count"] == 0
    assert result["safety"]["browser_used"] is False
    assert result["safety"]["clipboard_read"] is False
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()
    assert Path(result["evidence_files"]["text"]).is_file()


def test_scan_detects_single_local_ps1_without_reading_or_running_it(tmp_path: Path):
    inbox = tmp_path / "inbox"
    downloads = tmp_path / "downloads"
    inbox.mkdir()
    downloads.mkdir()
    artifact = inbox / "example.ps1"
    artifact.write_text("& { Set-StrictMode -Version Latest }\n", encoding="utf-8")

    result = scan_local_artifacts(inbox_dir=inbox, browser_downloads_dir=downloads)

    assert result.result_label == "PASS_ARTIFACT_DETECTED"
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.path == artifact.resolve(strict=False)
    assert candidate.source == "inbox_dir"
    assert candidate.extension == ".ps1"
    assert candidate.size_bytes > 0


def test_scan_blocks_ambiguous_artifacts_when_more_than_one_candidate_exists(tmp_path: Path):
    inbox = tmp_path / "inbox"
    downloads = tmp_path / "downloads"
    inbox.mkdir()
    downloads.mkdir()
    (inbox / "a.ps1").write_text("a", encoding="utf-8")
    (downloads / "b.zip").write_text("b", encoding="utf-8")

    result = scan_local_artifacts(inbox_dir=inbox, browser_downloads_dir=downloads)

    assert result.result_label == "BLOCKED_AMBIGUOUS_ARTIFACTS"
    assert len(result.candidates) == 2


def test_scan_ignores_partial_temp_empty_unsupported_and_runtime_internal_files(tmp_path: Path):
    inbox = tmp_path / "inbox"
    downloads = tmp_path / "downloads"
    inbox.mkdir()
    downloads.mkdir()
    (inbox / "empty.ps1").write_text("", encoding="utf-8")
    (inbox / "partial.zip.crdownload").write_text("not ready", encoding="utf-8")
    (inbox / "temp.tmp").write_text("temp", encoding="utf-8")
    (inbox / "unsupported.exe").write_text("no", encoding="utf-8")
    hidden_dir = inbox / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "hidden.ps1").write_text("hidden", encoding="utf-8")
    staged_dir = inbox / "staged"
    staged_dir.mkdir()
    (staged_dir / "already.ps1").write_text("already", encoding="utf-8")

    result = scan_local_artifacts(inbox_dir=inbox, browser_downloads_dir=downloads)

    assert result.result_label == "BLOCKED_NO_ARTIFACT"
    assert len(result.candidates) == 0
    reasons = {item["reason"] for item in result.ignored}
    assert "empty_file" in reasons
    assert "partial_or_temporary_extension" in reasons
    assert "unsupported_extension" in reasons
    assert "hidden_or_runtime_internal" in reasons


def test_run_artifact_scan_respects_config_detection_gate(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    payload = default_config_payload()
    payload["policy"]["allow_artifact_detection"] = False
    config_path.parent.mkdir(parents=True)
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    result = run_artifact_scan(repo_root=repo_root, config_path=config_path, evidence_root=repo_root / "evidence")

    assert result["ok"] is False
    assert result["result_label"] == "BLOCKED_INVALID_ARTIFACT"
    assert result["ignored"][0]["reason"] == "local_artifact_detection_disabled_by_config"


def test_run_artifact_scan_detects_checked_config_fixture(tmp_path: Path):
    repo_root, config_path = _make_repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "payload.md").write_text("PATCHOPS_SCRIPT_PAYLOAD_BEGIN\n", encoding="utf-8")

    result = run_artifact_scan(repo_root=repo_root, config_path=config_path, evidence_root=repo_root / "evidence")

    assert result["ok"] is True
    assert result["result_label"] == "PASS_ARTIFACT_DETECTED"
    assert result["candidate_count"] == 1
    assert result["candidates"][0]["extension"] == ".md"