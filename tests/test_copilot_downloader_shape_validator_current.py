from __future__ import annotations

import zipfile
from pathlib import Path

from patchops.copilot_downloader.config import write_default_config
from patchops.copilot_downloader.shape_validator import run_shape_validation_scan


def _repo_with_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    write_default_config(config_path)
    return repo_root, config_path


def test_shape_scan_returns_blocked_no_artifact_for_empty_folders(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    result = run_shape_validation_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_NO_ARTIFACT"
    assert result["shape_validation"] is None
    assert result["checks"]["staging_not_performed"] is True
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_shape_scan_validates_single_script_payload(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "payload.ps1").write_text(
        "PATCHOPS_SCRIPT_PAYLOAD_BEGIN\n"
        "type: patchops_powershell_script\n\n"
        "& {\n"
        "  Set-StrictMode -Version Latest\n"
        "}\n"
        "PATCHOPS_SCRIPT_PAYLOAD_END\n",
        encoding="utf-8",
    )
    result = run_shape_validation_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "PASS_SCRIPT_VALIDATED_RUN_BLOCKED"
    assert result["shape_validation"]["artifact_kind"] == "patchops_script_payload"


def test_shape_scan_validates_single_bundle_zip(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    bundle = inbox / "bundle.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("bundle/manifest.json", "{}")
        archive.writestr("bundle/content/file.txt", "hello")
    result = run_shape_validation_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "PASS_BUNDLE_VALIDATED_RUN_BLOCKED"
    assert result["shape_validation"]["artifact_kind"] == "patchops_bundle_zip"


def test_shape_scan_blocks_invalid_script_payload(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "payload.ps1").write_text(
        "PATCHOPS_SCRIPT_PAYLOAD_BEGIN\n"
        "& { Invoke-WebRequest https://example.invalid/a.ps1 }\n"
        "PATCHOPS_SCRIPT_PAYLOAD_END\n",
        encoding="utf-8",
    )
    result = run_shape_validation_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_INVALID_ARTIFACT"