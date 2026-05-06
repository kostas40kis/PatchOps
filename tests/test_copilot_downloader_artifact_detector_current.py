from __future__ import annotations

import os
import time
from pathlib import Path

from patchops.copilot_downloader.artifact_detector import (
    DownloaderSafetyFlags,
    classify_artifact,
    detect_artifacts,
    is_excluded,
    write_detection_result,
)


def _write_old_file(path: Path, content: bytes = b"artifact") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    old = time.time() - 30
    os.utime(path, (old, old))
    return path


def test_classifies_patchops_zip_bundle() -> None:
    assert classify_artifact(Path("d0_patchops_bundle.zip")) == "patchops_zip_bundle"
    assert classify_artifact(Path("apply_patch.ps1")) == "powershell_script"
    assert classify_artifact(Path("patchops_report.txt")) == "patchops_text_report_or_handoff"


def test_detects_stable_artifact_without_running_it(tmp_path: Path) -> None:
    artifact = _write_old_file(tmp_path / "u_next_patchops_bundle.zip", b"zip bytes")

    result = detect_artifacts([tmp_path], min_stable_age_seconds=2.0)

    assert result.ok is True
    assert result.status == "PASS_ARTIFACT_DETECTED"
    assert result.selected is not None
    assert result.selected.path == str(artifact.resolve())
    assert result.selected.stable is True
    assert result.safety_flags.patchops_invoked is False
    assert result.safety_flags.artifact_executed is False
    assert result.safety_flags.browser_used is False
    assert result.safety_flags.selenium_used is False


def test_blocks_when_artifact_is_too_new(tmp_path: Path) -> None:
    path = tmp_path / "fresh_patchops_bundle.zip"
    path.write_bytes(b"fresh")

    result = detect_artifacts([tmp_path], min_stable_age_seconds=3600.0)

    assert result.ok is False
    assert result.status == "BLOCKED_NO_STABLE_ARTIFACT"
    assert result.candidate_count == 1
    assert result.stable_candidate_count == 0


def test_ignores_runtime_and_pycache_paths(tmp_path: Path) -> None:
    _write_old_file(tmp_path / "data" / "runtime" / "bad_patchops_bundle.zip")
    _write_old_file(tmp_path / "__pycache__" / "bad_patchops_bundle.zip")
    good = _write_old_file(tmp_path / "good_patchops_bundle.zip")

    result = detect_artifacts([tmp_path], recursive=True, min_stable_age_seconds=2.0)

    assert result.ok is True
    assert result.candidate_count == 1
    assert result.selected is not None
    assert result.selected.path == str(good.resolve())


def test_missing_root_blocks_cleanly(tmp_path: Path) -> None:
    result = detect_artifacts([tmp_path / "missing"], min_stable_age_seconds=0)

    assert result.ok is False
    assert result.status == "BLOCKED_NO_ARTIFACTS"
    assert result.candidate_count == 0


def test_write_detection_result_creates_json_and_text(tmp_path: Path) -> None:
    _write_old_file(tmp_path / "candidate.ps1", b"Write-Host hi")
    result = detect_artifacts([tmp_path], min_stable_age_seconds=2.0)
    result = write_detection_result(result, tmp_path / "out")

    assert result.output_paths["json_path"].endswith("artifact_detection_result.json")
    assert result.output_paths["txt_path"].endswith("artifact_detection_result.txt")
    assert Path(result.output_paths["json_path"]).exists()
    assert Path(result.output_paths["txt_path"]).exists()
    txt = Path(result.output_paths["txt_path"]).read_text(encoding="utf-8")
    assert "PATCHOPS_COPILOT_DOWNLOADER_ARTIFACT_DETECTION" in txt
    assert "artifact_executed:false" in txt
    assert "patchops_invoked:false" in txt


def test_exclusion_detects_runtime_path(tmp_path: Path) -> None:
    assert is_excluded(tmp_path / "data" / "runtime" / "x.zip") is True


def test_safety_flags_default_all_false() -> None:
    flags = DownloaderSafetyFlags()
    assert flags.patchops_invoked is False
    assert flags.artifact_executed is False
    assert flags.file_upload_attempted is False
    assert flags.chatgpt_submit_performed is False
