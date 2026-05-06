from __future__ import annotations

import json
import zipfile
from pathlib import Path

from patchops.copilot_downloader.download_stable_validator import sha256_file, stage_downloaded_artifact
from patchops.copilot_downloader.patchops_bundle_validator import (
    BLOCKED_BUNDLE_SURFACE_FAILED,
    BLOCKED_INVALID_BUNDLE,
    BLOCKED_NO_STAGED_ARTIFACT,
    PASS_BUNDLE_VALIDATED_RUN_BLOCKED,
    build_bundle_surface_commands,
    find_latest_staged_downloaded_artifact,
    run_patchops_bundle_validator,
    validate_staged_bundle_shape,
)


def _make_bundle(path: Path, marker: str = "ok") -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("manifest.json", json.dumps({"marker": marker}))
        archive.writestr("content/payload.txt", marker)
    return path


def _stage_bundle(repo_root: Path, artifact: Path) -> Path:
    digest = sha256_file(artifact)
    staged = stage_downloaded_artifact(
        repo_root=repo_root,
        artifact_path=artifact,
        artifact_sha256=digest,
        classification={"kind": "patchops_bundle_zip", "suffix": ".zip"},
    )
    return Path(staged["metadata_path"])


def test_bundle_validator_blocks_without_staged_artifact(tmp_path: Path):
    result = run_patchops_bundle_validator(repo_root=tmp_path, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_NO_STAGED_ARTIFACT
    assert result["issue"] == "staged_bundle_metadata_required"
    assert result["checks"]["artifact_not_executed"] is True
    assert Path(result["evidence_files"]["json"]).is_file()


def test_bundle_validator_validates_shape_and_metadata_without_running_surfaces_by_default(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    artifact = _make_bundle(repo_root / "bundle.zip")
    metadata_path = _stage_bundle(repo_root, artifact)
    result = run_patchops_bundle_validator(repo_root=repo_root, evidence_root=repo_root / "evidence", staged_metadata_path=metadata_path)
    assert result["ok"] is True
    assert result["result_label"] == PASS_BUNDLE_VALIDATED_RUN_BLOCKED
    assert result["issue"] == "surface_execution_not_requested"
    assert result["shape"]["has_manifest_like_member"] is True
    assert result["shape"]["archive_extracted"] is False
    assert result["shape"]["manifest_bytes_read"] is False
    assert result["surface_validation"]["dry_surface_plan_only"] is True
    updated = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert updated["bundle_validation_performed"] is True
    assert updated["bundle_validation_ok"] is True
    assert updated["run_authorized"] is False


def test_bundle_validator_rejects_non_zip_and_bad_zip(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    artifact = repo_root / "manifest.json"
    artifact.write_text("{}", encoding="utf-8")
    digest = sha256_file(artifact)
    staged = stage_downloaded_artifact(
        repo_root=repo_root,
        artifact_path=artifact,
        artifact_sha256=digest,
        classification={"kind": "patchops_manifest_json", "suffix": ".json"},
    )
    result = run_patchops_bundle_validator(repo_root=repo_root, evidence_root=repo_root / "evidence", staged_metadata_path=staged["metadata_path"])
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_INVALID_BUNDLE
    assert any(".zip" in issue for issue in result["shape"]["issues"])

    bad_zip = repo_root / "bad.zip"
    bad_zip.write_text("not a zip", encoding="utf-8")
    bad_digest = sha256_file(bad_zip)
    bad_staged = stage_downloaded_artifact(repo_root=repo_root, artifact_path=bad_zip, artifact_sha256=bad_digest, classification={"kind": "patchops_bundle_zip", "suffix": ".zip"})
    bad_result = run_patchops_bundle_validator(repo_root=repo_root, evidence_root=repo_root / "evidence2", staged_metadata_path=bad_staged["metadata_path"])
    assert bad_result["ok"] is True
    assert bad_result["result_label"] == BLOCKED_INVALID_BUNDLE
    assert bad_result["shape"]["zip_issue"] == "bad_zip_file"


def test_bundle_validator_surface_commands_are_non_executing():
    commands = build_bundle_surface_commands("C:/tmp/bundle.zip")
    surfaces = [command[3] for command in commands]
    assert surfaces == ["check-bundle", "inspect-bundle", "plan-bundle"]
    assert "apply-bundle" not in surfaces
    assert "run-package" not in surfaces


def test_bundle_validator_runs_non_executing_surfaces_with_fake_runner(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    artifact = _make_bundle(repo_root / "bundle.zip")
    metadata_path = _stage_bundle(repo_root, artifact)
    calls: list[str] = []

    def fake_runner(command, *, cwd, timeout_seconds):
        calls.append(command[3])
        return {"command": " ".join(command), "exit_code": 0, "timed_out": False, "stdout": "ok", "stderr": "", "stdout_size_chars": 2, "stderr_size_chars": 0}

    result = run_patchops_bundle_validator(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_metadata_path=metadata_path,
        command_runner=fake_runner,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_BUNDLE_VALIDATED_RUN_BLOCKED
    assert calls == ["check-bundle", "inspect-bundle", "plan-bundle"]
    assert result["surface_validation"]["apply_or_run_invoked"] is False
    assert result["checks"]["no_apply_bundle_or_run_package"] is True
    assert result["checks"]["run_not_authorized"] is True


def test_bundle_validator_runs_bundle_doctor_when_surface_fails(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    artifact = _make_bundle(repo_root / "bundle.zip")
    metadata_path = _stage_bundle(repo_root, artifact)
    calls: list[str] = []

    def fake_runner(command, *, cwd, timeout_seconds):
        surface = command[3]
        calls.append(surface)
        exit_code = 1 if surface == "inspect-bundle" else 0
        return {"command": " ".join(command), "exit_code": exit_code, "timed_out": False, "stdout": "", "stderr": "failed" if exit_code else "", "stdout_size_chars": 0, "stderr_size_chars": 6 if exit_code else 0}

    result = run_patchops_bundle_validator(repo_root=repo_root, evidence_root=repo_root / "evidence", staged_metadata_path=metadata_path, command_runner=fake_runner)
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_BUNDLE_SURFACE_FAILED
    assert result["issue"] == "non_executing_bundle_surface_failed"
    assert calls == ["check-bundle", "inspect-bundle", "plan-bundle", "bundle-doctor"]
    assert result["surface_validation"]["bundle_doctor_result"]["surface"] == "bundle-doctor"
    assert result["checks"]["no_apply_bundle_or_run_package"] is True


def test_bundle_validator_detects_staged_raw_sha_mismatch(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    artifact = _make_bundle(repo_root / "bundle.zip")
    metadata_path = _stage_bundle(repo_root, artifact)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    staged_raw_path = Path(metadata["raw_artifact_path"])
    with zipfile.ZipFile(staged_raw_path, "a") as archive:
        archive.writestr("changed.txt", "changed")
    shape = validate_staged_bundle_shape(json.loads(metadata_path.read_text(encoding="utf-8")))
    assert shape["ok"] is False
    assert any("sha256" in issue for issue in shape["issues"])


def test_find_latest_staged_downloaded_artifact(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    artifact = _make_bundle(repo_root / "bundle.zip")
    metadata_path = _stage_bundle(repo_root, artifact)
    assert find_latest_staged_downloaded_artifact(repo_root) == metadata_path.resolve(strict=False)


def test_repository_bundle_validator_doctor_is_controlled_and_safe():
    result = run_patchops_bundle_validator(
        repo_root=Path.cwd(),
        evidence_root="data/runtime/copilot_downloader/d3_03_bundle_validator_test",
    )
    assert result["ok"] is True
    assert result["result_label"] in {PASS_BUNDLE_VALIDATED_RUN_BLOCKED, BLOCKED_NO_STAGED_ARTIFACT, BLOCKED_INVALID_BUNDLE, BLOCKED_BUNDLE_SURFACE_FAILED}
    assert result["checks"]["artifact_not_executed"] is True
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["no_apply_bundle_or_run_package"] is True