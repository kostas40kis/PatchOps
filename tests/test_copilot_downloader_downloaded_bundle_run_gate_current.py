from __future__ import annotations

import json
import zipfile
from pathlib import Path

from patchops.copilot_downloader.download_stable_validator import check_and_write_ledger, sha256_file, stage_downloaded_artifact
from patchops.copilot_downloader.downloaded_bundle_run_gate import (
    BLOCKED_RUN_NOT_AUTHORIZED,
    FAIL_PATCHOPS_RUN,
    PASS_PATCHOPS_RUN_COMPLETED,
    build_bundle_run_command,
    extract_patchops_report_signal,
    ledger_contains_sha,
    run_downloaded_bundle_gate_and_runner,
    validate_downloaded_bundle_run_gate,
)
from patchops.copilot_downloader.script_payload_contract import REQUIRED_CONFIRMATION


def _make_bundle(path: Path, marker: str = "ok") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("manifest.json", json.dumps({"marker": marker}))
        archive.writestr("content/payload.txt", marker)
    return path


def _stage_validated_bundle(repo_root: Path, marker: str = "ok", *, ledger: bool = True, validation_ok: bool = True) -> Path:
    repo_root.mkdir(parents=True, exist_ok=True)
    artifact = _make_bundle(repo_root / "bundle.zip", marker)
    digest = sha256_file(artifact)
    if ledger:
        check_and_write_ledger(repo_root=repo_root, artifact_path=artifact, artifact_sha256=digest, artifact_kind="patchops_bundle_zip")
    staged = stage_downloaded_artifact(
        repo_root=repo_root,
        artifact_path=artifact,
        artifact_sha256=digest,
        classification={"kind": "patchops_bundle_zip", "suffix": ".zip"},
    )
    metadata_path = Path(staged["metadata_path"])
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata.update(
        {
            "bundle_validation_performed": True,
            "bundle_validation_ok": validation_ok,
            "bundle_validation_result_label": "PASS_BUNDLE_VALIDATED_RUN_BLOCKED" if validation_ok else "BLOCKED_INVALID_BUNDLE",
            "bundle_validation_surfaces": ["check-bundle", "inspect-bundle", "plan-bundle"],
            "run_authorized": False,
            "artifact_executed": False,
        }
    )
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metadata_path


def test_downloaded_bundle_run_gate_blocks_without_staged_metadata(tmp_path: Path):
    result = run_downloaded_bundle_gate_and_runner(repo_root=tmp_path, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert result["run_result"] is None
    assert result["checks"]["run_not_started_without_authorization"] is True
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()
    assert Path(result["desktop_report_path"]).is_file()


def test_downloaded_bundle_run_gate_requires_ledger_shape_validation_and_surfaces(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    no_ledger_metadata = _stage_validated_bundle(repo_root, ledger=False)
    gate = validate_downloaded_bundle_run_gate(
        repo_root=repo_root,
        staged_metadata_path=no_ledger_metadata,
        allow_run=True,
        confirm_run_text=REQUIRED_CONFIRMATION,
    )
    assert gate["authorized"] is False
    assert any("ledger" in issue for issue in gate["issues"])

    bad_validation_root = repo_root / "repo2"
    bad_validation_metadata = _stage_validated_bundle(bad_validation_root, validation_ok=False)
    gate2 = validate_downloaded_bundle_run_gate(
        repo_root=bad_validation_root,
        staged_metadata_path=bad_validation_metadata,
        allow_run=True,
        confirm_run_text=REQUIRED_CONFIRMATION,
    )
    assert gate2["authorized"] is False
    assert any("validation ok" in issue for issue in gate2["issues"])


def test_downloaded_bundle_run_gate_requires_allow_run_and_confirmation(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    metadata_path = _stage_validated_bundle(repo_root)
    without_allow = run_downloaded_bundle_gate_and_runner(repo_root=repo_root, evidence_root=repo_root / "e1", staged_metadata_path=metadata_path)
    assert without_allow["ok"] is True
    assert without_allow["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert without_allow["safety"]["patchops_invoked"] is False
    wrong_confirm = run_downloaded_bundle_gate_and_runner(
        repo_root=repo_root,
        evidence_root=repo_root / "e2",
        staged_metadata_path=metadata_path,
        allow_run=True,
        confirm_run_text="WRONG",
    )
    assert wrong_confirm["ok"] is True
    assert wrong_confirm["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert wrong_confirm["safety"]["artifact_executed"] is False


def test_downloaded_bundle_run_gate_executes_fake_apply_bundle_and_captures_report_signal(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    metadata_path = _stage_validated_bundle(repo_root)
    calls: list[str] = []

    def fake_runner(command, *, cwd, timeout_seconds):
        calls.append(command[3])
        return {
            "command": " ".join(command),
            "exit_code": 0,
            "timed_out": False,
            "elapsed_seconds": 0.01,
            "stdout": "PATCHOPS RUN SUMMARY\nReport Path        : C:\\tmp\\patchops_report.txt\nExitCode           : 0\nResult             : PASS\n",
            "stderr": "",
            "stdout_size_chars": 110,
            "stderr_size_chars": 0,
        }

    result = run_downloaded_bundle_gate_and_runner(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        desktop_report_dir=repo_root / "desktop",
        staged_metadata_path=metadata_path,
        allow_run=True,
        confirm_run_text=REQUIRED_CONFIRMATION,
        run_surface="apply-bundle",
        command_runner=fake_runner,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_PATCHOPS_RUN_COMPLETED
    assert calls == ["apply-bundle"]
    assert result["run_result"]["exit_code"] == 0
    assert result["patchops_report_signal"]["report_signal_found"] is True
    assert result["checks"]["stdout_captured"] is True
    assert result["checks"]["exit_code_captured"] is True
    assert result["safety"]["artifact_executed"] is True
    assert result["safety"]["patchops_invoked"] is True
    updated = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert updated["run_authorized"] is True
    assert updated["artifact_executed"] is True
    assert updated["bundle_run_result_label"] == PASS_PATCHOPS_RUN_COMPLETED
    assert Path(result["desktop_report_path"]).is_file()


def test_downloaded_bundle_run_gate_supports_run_package_surface_with_fake_runner(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    metadata_path = _stage_validated_bundle(repo_root)

    def fake_runner(command, *, cwd, timeout_seconds):
        return {"command": " ".join(command), "exit_code": 0, "timed_out": False, "elapsed_seconds": 0.01, "stdout": "Result : PASS\nExitCode : 0\n", "stderr": "", "stdout_size_chars": 25, "stderr_size_chars": 0}

    result = run_downloaded_bundle_gate_and_runner(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_metadata_path=metadata_path,
        allow_run=True,
        confirm_run_text=REQUIRED_CONFIRMATION,
        run_surface="run-package",
        command_runner=fake_runner,
    )
    assert result["ok"] is True
    assert result["run_surface"] == "run-package"
    assert result["run_result"]["command"].split()[3] == "run-package"


def test_downloaded_bundle_run_gate_returns_fail_label_on_nonzero_exit(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    metadata_path = _stage_validated_bundle(repo_root)

    def fake_runner(command, *, cwd, timeout_seconds):
        return {"command": " ".join(command), "exit_code": 7, "timed_out": False, "elapsed_seconds": 0.01, "stdout": "Result : FAIL\nExitCode : 7\n", "stderr": "failed", "stdout_size_chars": 25, "stderr_size_chars": 6}

    result = run_downloaded_bundle_gate_and_runner(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_metadata_path=metadata_path,
        allow_run=True,
        confirm_run_text=REQUIRED_CONFIRMATION,
        command_runner=fake_runner,
    )
    assert result["ok"] is False
    assert result["result_label"] == FAIL_PATCHOPS_RUN
    assert result["run_result"]["exit_code"] == 7
    assert result["safety"]["artifact_executed"] is True


def test_build_bundle_run_command_allows_only_run_surfaces(tmp_path: Path):
    command = build_bundle_run_command(tmp_path / "bundle.zip", run_surface="apply-bundle")
    assert command[3] == "apply-bundle"
    command2 = build_bundle_run_command(tmp_path / "bundle.zip", run_surface="run-package")
    assert command2[3] == "run-package"
    try:
        build_bundle_run_command(tmp_path / "bundle.zip", run_surface="check-bundle")
    except ValueError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("check-bundle must not be accepted as run surface")


def test_ledger_contains_sha_reads_d3_2_ledger(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    artifact = _make_bundle(repo_root / "bundle.zip")
    digest = sha256_file(artifact)
    check_and_write_ledger(repo_root=repo_root, artifact_path=artifact, artifact_sha256=digest, artifact_kind="patchops_bundle_zip")
    result = ledger_contains_sha(repo_root, digest)
    assert result["ledger_exists"] is True
    assert result["sha_found"] is True


def test_extract_patchops_report_signal():
    signal = extract_patchops_report_signal("Report Path : C:/tmp/r.txt\nExitCode : 0\nResult : PASS\n", "")
    assert signal["report_path"] == "C:/tmp/r.txt"
    assert signal["exit_code_text"] == "0"
    assert signal["result_text"] == "PASS"


def test_repository_downloaded_bundle_run_gate_doctor_is_controlled_and_safe():
    result = run_downloaded_bundle_gate_and_runner(
        repo_root=Path.cwd(),
        evidence_root="data/runtime/copilot_downloader/d3_04_downloaded_bundle_run_gate_test",
        desktop_report_dir="data/runtime/copilot_downloader/d3_04_downloaded_bundle_run_gate_test_desktop",
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert result["checks"]["run_not_started_without_authorization"] is True
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["safety"]["artifact_executed"] is False
    assert result["safety"]["patchops_invoked"] is False