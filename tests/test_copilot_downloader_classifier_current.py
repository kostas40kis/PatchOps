from __future__ import annotations

import json
import zipfile
from pathlib import Path

from patchops.copilot_downloader.classifier import (
    PATCHOPS_BUNDLE_KIND,
    PATCHOPS_MANIFEST_KIND,
    PATCHOPS_SCRIPT_KIND,
    UNKNOWN_ZIP_KIND,
    UNSUPPORTED_KIND,
    classify_artifact_file,
    run_classifier_scan,
)
from patchops.copilot_downloader.config import write_default_config
from patchops.copilot_downloader.models import ARTIFACT_KINDS, PASS_ARTIFACT_CLASSIFIED, RESULT_LABELS


def _repo_with_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    write_default_config(config_path)
    return repo_root, config_path


def test_classifier_label_and_kinds_are_registered():
    assert PASS_ARTIFACT_CLASSIFIED in RESULT_LABELS
    assert PATCHOPS_SCRIPT_KIND in ARTIFACT_KINDS
    assert PATCHOPS_MANIFEST_KIND in ARTIFACT_KINDS
    assert PATCHOPS_BUNDLE_KIND in ARTIFACT_KINDS
    assert UNKNOWN_ZIP_KIND in ARTIFACT_KINDS
    assert UNSUPPORTED_KIND in ARTIFACT_KINDS


def test_classifies_marked_patchops_script_payload(tmp_path: Path):
    script = tmp_path / "payload.ps1"
    script.write_text(
        "PATCHOPS_SCRIPT_PAYLOAD_BEGIN\n"
        "name: d_example\n"
        "type: patchops_powershell_script\n\n"
        "& {\n"
        "    Set-StrictMode -Version Latest\n"
        "}\n"
        "PATCHOPS_SCRIPT_PAYLOAD_END\n",
        encoding="utf-8",
    )
    result = classify_artifact_file(script)
    assert result.result_label == PASS_ARTIFACT_CLASSIFIED
    assert result.artifact_kind == PATCHOPS_SCRIPT_KIND
    assert "marked_patchops_script_payload" in result.reasons


def test_unmarked_script_is_unsupported_until_marker_contract_patch(tmp_path: Path):
    script = tmp_path / "payload.ps1"
    script.write_text("& { Set-StrictMode -Version Latest }\n", encoding="utf-8")
    result = classify_artifact_file(script)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert result.artifact_kind == UNSUPPORTED_KIND
    assert "missing_payload_begin_marker" in result.reasons
    assert "missing_payload_end_marker" in result.reasons


def test_classifies_patchops_manifest_json(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({
            "manifest_version": "1",
            "patch_name": "d_example",
            "target_project_root": "C:/dev/patchops",
            "files_to_write": [],
        }),
        encoding="utf-8",
    )
    result = classify_artifact_file(manifest)
    assert result.result_label == PASS_ARTIFACT_CLASSIFIED
    assert result.artifact_kind == PATCHOPS_MANIFEST_KIND
    assert result.metadata["patch_name"] == "d_example"


def test_non_manifest_json_is_blocked_invalid(tmp_path: Path):
    payload = tmp_path / "not_manifest.json"
    payload.write_text(json.dumps({"hello": "world"}), encoding="utf-8")
    result = classify_artifact_file(payload)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert result.artifact_kind == UNSUPPORTED_KIND
    assert "json_not_patchops_manifest_shape" in result.reasons


def test_classifies_patchops_bundle_zip_by_index_without_extracting(tmp_path: Path):
    bundle = tmp_path / "bundle.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("bundle/manifest.json", "{}")
        archive.writestr("bundle/content/file.txt", "hello")
    result = classify_artifact_file(bundle)
    assert result.result_label == PASS_ARTIFACT_CLASSIFIED
    assert result.artifact_kind == PATCHOPS_BUNDLE_KIND
    assert result.metadata["has_manifest"] is True
    assert not (tmp_path / "bundle").exists()


def test_classifies_unknown_zip_when_no_patchops_markers_exist(tmp_path: Path):
    bundle = tmp_path / "unknown.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("readme.txt", "hello")
    result = classify_artifact_file(bundle)
    assert result.result_label == PASS_ARTIFACT_CLASSIFIED
    assert result.artifact_kind == UNKNOWN_ZIP_KIND
    assert "zip_opened_without_patchops_markers" in result.reasons


def test_unsupported_extension_is_blocked_invalid(tmp_path: Path):
    payload = tmp_path / "payload.exe"
    payload.write_text("no", encoding="utf-8")
    result = classify_artifact_file(payload)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert result.artifact_kind == UNSUPPORTED_KIND
    assert result.reasons[0].startswith("unsupported_extension")


def test_classifier_scan_returns_blocked_no_artifact_for_empty_folders(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    result = run_classifier_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_NO_ARTIFACT"
    assert result["classification"] is None
    assert result["checks"]["staging_not_performed"] is True
    assert result["checks"]["hash_not_computed_by_classifier"] is True
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_classifier_scan_classifies_single_stable_manifest(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "manifest.json").write_text(
        json.dumps({"manifest_version": "1", "patch_name": "d_example", "files_to_write": []}),
        encoding="utf-8",
    )
    result = run_classifier_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_ARTIFACT_CLASSIFIED
    assert result["artifact_kind"] == PATCHOPS_MANIFEST_KIND


def test_classifier_scan_propagates_ambiguous_artifact_block(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    downloads = repo_root / "data" / "runtime" / "copilot_downloader" / "browser_downloads"
    inbox.mkdir(parents=True)
    downloads.mkdir(parents=True)
    (inbox / "a.json").write_text("{}", encoding="utf-8")
    (downloads / "b.txt").write_text("b", encoding="utf-8")
    result = run_classifier_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_AMBIGUOUS_ARTIFACTS"
    assert result["classification"] is None