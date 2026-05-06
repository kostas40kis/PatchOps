from __future__ import annotations

import json
import zipfile
from pathlib import Path

from patchops.copilot_downloader.download_stable_validator import (
    BLOCKED_AMBIGUOUS_ARTIFACTS,
    BLOCKED_DUPLICATE_ARTIFACT,
    BLOCKED_NO_ARTIFACT,
    BLOCKED_UNSTABLE_FILE,
    PASS_STABLE_ARTIFACT_VALIDATED,
    check_and_write_ledger,
    classify_downloaded_artifact,
    run_download_stable_validator,
    sample_stability,
    sha256_file,
)


def _make_patchops_zip(path: Path, marker: str = "marker") -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("manifest.json", json.dumps({"marker": marker}))
        archive.writestr("content/file.txt", marker)
    return path


def test_download_stable_validator_empty_folder_is_controlled_no_artifact(tmp_path: Path):
    result = run_download_stable_validator(repo_root=tmp_path, download_dir=tmp_path / "downloads", evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_NO_ARTIFACT
    assert result["artifact_sha256"] is None
    assert result["staging"] is None
    assert result["checks"]["artifact_not_executed"] is True
    assert Path(result["evidence_files"]["json"]).is_file()


def test_download_stable_validator_blocks_ambiguous_artifacts(tmp_path: Path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    _make_patchops_zip(download_dir / "one.zip", "one")
    (download_dir / "two.json").write_text("{}", encoding="utf-8")
    result = run_download_stable_validator(repo_root=tmp_path, download_dir=download_dir, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_AMBIGUOUS_ARTIFACTS
    assert result["staging"] is None
    assert result["ledger"] is None


def test_sample_stability_rejects_partial_and_growing_file(tmp_path: Path):
    partial = tmp_path / "bundle.zip.crdownload"
    partial.write_text("partial", encoding="utf-8")
    assert sample_stability(partial)["result_label"] == BLOCKED_UNSTABLE_FILE

    growing = tmp_path / "bundle.zip"
    growing.write_text("a", encoding="utf-8")

    def hook(index: int, path: Path) -> None:
        if index == 1:
            path.write_text("aa", encoding="utf-8")

    result = sample_stability(growing, sample_count=2, interval_seconds=0, sample_hook=hook)
    assert result["result_label"] == BLOCKED_UNSTABLE_FILE
    assert result["issue"] == "file_size_or_mtime_changed"


def test_download_stable_validator_hashes_classifies_ledgers_and_stages_stable_zip(tmp_path: Path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    sentinel = "RAW_STABLE_DOWNLOAD_SENTINEL_D3_02"
    artifact = _make_patchops_zip(download_dir / "bundle.zip", sentinel)
    result = run_download_stable_validator(repo_root=tmp_path, download_dir=download_dir, evidence_root=tmp_path / "evidence", sample_count=2, interval_seconds=0)
    assert result["ok"] is True
    assert result["result_label"] == PASS_STABLE_ARTIFACT_VALIDATED
    assert result["artifact_sha256"] == sha256_file(artifact)
    assert result["classification"]["kind"] == "patchops_bundle_zip"
    assert result["ledger"]["ledger_written"] is True
    assert result["ledger"]["duplicate_found"] is False
    assert Path(result["staging"]["raw_artifact_path"]).is_file()
    assert Path(result["staging"]["metadata_path"]).is_file()
    assert result["staging"]["run_authorized"] is False
    assert result["staging"]["bundle_validation_performed"] is False
    serialized = json.dumps(result)
    evidence_json = Path(result["evidence_files"]["json"]).read_text(encoding="utf-8")
    assert sentinel not in serialized
    assert sentinel not in evidence_json


def test_download_stable_validator_blocks_duplicate_unless_allowed(tmp_path: Path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    _make_patchops_zip(download_dir / "bundle.zip", "dupe")
    first = run_download_stable_validator(repo_root=tmp_path, download_dir=download_dir, evidence_root=tmp_path / "evidence1")
    assert first["result_label"] == PASS_STABLE_ARTIFACT_VALIDATED
    second = run_download_stable_validator(repo_root=tmp_path, download_dir=download_dir, evidence_root=tmp_path / "evidence2")
    assert second["ok"] is True
    assert second["result_label"] == BLOCKED_DUPLICATE_ARTIFACT
    assert second["ledger"]["duplicate_found"] is True
    assert second["staging"] is None
    third = run_download_stable_validator(repo_root=tmp_path, download_dir=download_dir, evidence_root=tmp_path / "evidence3", allow_duplicate=True)
    assert third["ok"] is True
    assert third["result_label"] == PASS_STABLE_ARTIFACT_VALIDATED
    assert third["ledger"]["duplicate_found"] is True
    assert third["ledger"]["ledger_written"] is True


def test_classify_downloaded_artifact_json_ps1_and_unknown_zip(tmp_path: Path):
    json_path = tmp_path / "manifest.json"
    json_path.write_text("{}", encoding="utf-8")
    ps1_path = tmp_path / "script.ps1"
    ps1_path.write_text("& { Set-StrictMode -Version Latest }", encoding="utf-8")
    zip_path = tmp_path / "unknown.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("readme.txt", "hello")
    assert classify_downloaded_artifact(json_path)["kind"] == "patchops_manifest_json"
    assert classify_downloaded_artifact(ps1_path)["kind"] == "patchops_script_or_powershell"
    assert classify_downloaded_artifact(zip_path)["kind"] == "unknown_zip"


def test_ledger_duplicate_detection_without_staging(tmp_path: Path):
    artifact = tmp_path / "bundle.zip"
    _make_patchops_zip(artifact, "ledger")
    digest = sha256_file(artifact)
    first = check_and_write_ledger(repo_root=tmp_path, artifact_path=artifact, artifact_sha256=digest, artifact_kind="patchops_bundle_zip")
    second = check_and_write_ledger(repo_root=tmp_path, artifact_path=artifact, artifact_sha256=digest, artifact_kind="patchops_bundle_zip")
    assert first["ledger_written"] is True
    assert second["duplicate_found"] is True
    assert second["duplicate_blocked"] is True


def test_repository_download_stable_validator_doctor_is_controlled_and_safe():
    result = run_download_stable_validator(
        repo_root=Path.cwd(),
        config_path="data/config/copilot_downloader_config.json",
        evidence_root="data/runtime/copilot_downloader/d3_02_download_stable_validator_test",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] in {
        PASS_STABLE_ARTIFACT_VALIDATED,
        BLOCKED_NO_ARTIFACT,
        BLOCKED_AMBIGUOUS_ARTIFACTS,
        BLOCKED_UNSTABLE_FILE,
        BLOCKED_DUPLICATE_ARTIFACT,
    }
    assert result["checks"]["artifact_not_executed"] is True
    assert result["checks"]["patchops_not_invoked_by_downloader_runtime"] is True
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["clipboard_not_read"] is True