from __future__ import annotations

import json
import zipfile
from pathlib import Path

from patchops.copilot_downloader.config import write_default_config
from patchops.copilot_downloader.ledger import compute_sha256
from patchops.copilot_downloader.models import PASS_STAGED_ARTIFACT_READY, RESULT_LABELS
from patchops.copilot_downloader.staging import (
    normalized_script_from_marked_payload_file,
    run_staging_scan,
    stage_validated_artifact,
)


def _repo_with_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    write_default_config(config_path)
    return repo_root, config_path


def _script_text(extra: str = "") -> str:
    return (
        "PATCHOPS_SCRIPT_PAYLOAD_BEGIN\n"
        "type: patchops_powershell_script\n\n"
        "& {\n"
        "    Set-StrictMode -Version Latest\n"
        "    $ErrorActionPreference = \"Stop\"\n"
        f"{extra}\n"
        "}\n"
        "PATCHOPS_SCRIPT_PAYLOAD_END\n"
    )


def test_staging_label_is_registered():
    assert PASS_STAGED_ARTIFACT_READY in RESULT_LABELS
    assert "BLOCKED_STAGE_MISSING_SOURCE" in RESULT_LABELS
    assert "FAIL_STAGE_WRITE" in RESULT_LABELS


def test_normalized_script_extracts_only_invocation_block(tmp_path: Path):
    script = tmp_path / "payload.ps1"
    script.write_text(_script_text("    Write-Host staged"), encoding="utf-8")
    normalized = normalized_script_from_marked_payload_file(script)
    assert normalized.startswith("& {")
    assert "PATCHOPS_SCRIPT_PAYLOAD_BEGIN" not in normalized
    assert "Set-StrictMode -Version Latest" in normalized
    assert normalized.endswith("}\n")


def test_stage_validated_script_copies_raw_and_writes_normalized_script_and_metadata(tmp_path: Path):
    source = tmp_path / "payload.ps1"
    source.write_text(_script_text("    Write-Host staged"), encoding="utf-8")
    sha = compute_sha256(source)
    staged = stage_validated_artifact(
        source_path=source,
        artifact_kind="patchops_script_payload",
        staging_root=tmp_path / "staged",
        artifact_sha256=sha,
        shape_payload={"result_label": "PASS_SCRIPT_VALIDATED_RUN_BLOCKED"},
    )
    assert staged.artifact_sha256 == sha
    assert staged.staging_dir == tmp_path / "staged" / sha
    assert staged.raw_artifact_path.is_file()
    assert staged.normalized_script_path is not None and staged.normalized_script_path.is_file()
    metadata = json.loads(staged.metadata_path.read_text(encoding="utf-8"))
    assert metadata["artifact_sha256"] == sha
    assert metadata["artifact_kind"] == "patchops_script_payload"
    assert metadata["execution_allowed"] is False
    assert metadata["patchops_invoked"] is False


def test_stage_validated_bundle_copies_raw_zip_without_extracting(tmp_path: Path):
    source = tmp_path / "bundle.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("bundle/manifest.json", "{}")
        archive.writestr("bundle/content/file.txt", "hello")
    staged = stage_validated_artifact(
        source_path=source,
        artifact_kind="patchops_bundle_zip",
        staging_root=tmp_path / "staged",
        shape_payload={"result_label": "PASS_BUNDLE_VALIDATED_RUN_BLOCKED"},
    )
    assert staged.raw_artifact_path.is_file()
    assert staged.normalized_script_path is None
    assert not (staged.staging_dir / "bundle").exists()
    metadata = json.loads(staged.metadata_path.read_text(encoding="utf-8"))
    assert metadata["normalized_script_path"] is None
    assert metadata["artifact_kind"] == "patchops_bundle_zip"


def test_run_staging_scan_returns_blocked_no_artifact_for_empty_folders(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    result = run_staging_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_NO_ARTIFACT"
    assert result["staged_artifact"] is None
    assert result["checks"]["no_browser_or_clipboard_direct_execution"] is True
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_run_staging_scan_stages_single_valid_script_payload(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    source = inbox / "payload.ps1"
    source.write_text(_script_text("    Write-Host ok"), encoding="utf-8")
    result = run_staging_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_STAGED_ARTIFACT_READY
    staged = result["staged_artifact"]
    assert Path(staged["raw_artifact_path"]).is_file()
    assert Path(staged["normalized_script_path"]).is_file()
    assert Path(staged["metadata_path"]).is_file()
    assert result["artifact_sha256"] == compute_sha256(source)


def test_run_staging_scan_stages_single_valid_bundle_zip_without_extraction(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    source = inbox / "bundle.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("bundle/manifest.json", "{}")
        archive.writestr("bundle/content/file.txt", "hello")
    result = run_staging_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_STAGED_ARTIFACT_READY
    staged = result["staged_artifact"]
    assert Path(staged["raw_artifact_path"]).is_file()
    assert staged["normalized_script_path"] is None
    assert not (Path(staged["staging_dir"]) / "bundle").exists()


def test_run_staging_scan_blocks_invalid_script_without_staging(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "payload.ps1").write_text(
        "PATCHOPS_SCRIPT_PAYLOAD_BEGIN\n& { Invoke-WebRequest https://example.invalid/a.ps1 }\nPATCHOPS_SCRIPT_PAYLOAD_END\n",
        encoding="utf-8",
    )
    result = run_staging_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_INVALID_ARTIFACT"
    assert result["staged_artifact"] is None
    staged_root = repo_root / "data" / "runtime" / "copilot_downloader" / "staged"
    assert not any(staged_root.iterdir())