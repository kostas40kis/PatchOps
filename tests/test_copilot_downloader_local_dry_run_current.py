from __future__ import annotations

import json
import zipfile
from pathlib import Path

from patchops.copilot_downloader.config import write_default_config
from patchops.copilot_downloader.ledger import append_ledger_entry, build_ledger_entry, compute_sha256
from patchops.copilot_downloader.models import PASS_STAGED_ARTIFACT_READY
from patchops.copilot_downloader.local_dry_run import run_local_dry_run


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


def test_local_dry_run_returns_blocked_no_artifact_and_writes_single_report(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    result = run_local_dry_run(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_NO_ARTIFACT"
    assert result["staged_artifact"] is None
    assert result["checks"]["stop_before_execution"] is True
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["report_files"]["json"]).is_file()
    assert Path(result["report_files"]["text"]).is_file()


def test_local_dry_run_runs_full_chain_to_staged_script_without_execution(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    source = inbox / "payload.ps1"
    source.write_text(_script_text("    Write-Host dry-run"), encoding="utf-8")

    result = run_local_dry_run(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )

    assert result["ok"] is True
    assert result["result_label"] == PASS_STAGED_ARTIFACT_READY
    assert result["artifact_sha256"] == compute_sha256(source)
    assert result["classification"]["artifact_kind"] == "patchops_script_payload"
    assert result["shape_validation"]["result_label"] == "PASS_SCRIPT_VALIDATED_RUN_BLOCKED"
    assert Path(result["staged_artifact"]["raw_artifact_path"]).is_file()
    assert Path(result["staged_artifact"]["normalized_script_path"]).is_file()
    assert result["execution_allowed"] is False
    assert result["patchops_invoked"] is False
    assert result["checks"]["ledger_not_written_by_dry_run_gate"] is True
    assert not (repo_root / "data" / "runtime" / "copilot_downloader" / "ledger" / "artifact_ledger.jsonl").exists()


def test_local_dry_run_runs_full_chain_to_staged_bundle_without_extracting(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    source = inbox / "bundle.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("bundle/manifest.json", "{}")
        archive.writestr("bundle/content/file.txt", "hello")

    result = run_local_dry_run(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )

    assert result["ok"] is True
    assert result["result_label"] == PASS_STAGED_ARTIFACT_READY
    assert result["classification"]["artifact_kind"] == "patchops_bundle_zip"
    assert result["shape_validation"]["result_label"] == "PASS_BUNDLE_VALIDATED_RUN_BLOCKED"
    assert Path(result["staged_artifact"]["raw_artifact_path"]).is_file()
    assert result["staged_artifact"]["normalized_script_path"] is None
    assert not (Path(result["staged_artifact"]["staging_dir"]) / "bundle").exists()


def test_local_dry_run_blocks_preexisting_duplicate_without_staging(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    source = inbox / "payload.ps1"
    source.write_text(_script_text("    Write-Host duplicate"), encoding="utf-8")
    sha = compute_sha256(source)
    ledger_path = repo_root / "data" / "runtime" / "copilot_downloader" / "ledger" / "artifact_ledger.jsonl"
    append_ledger_entry(
        ledger_path,
        build_ledger_entry(
            artifact_sha256=sha,
            candidate={"path": str(source), "source": "inbox_dir", "extension": ".ps1", "size_bytes": source.stat().st_size},
            status="recorded",
            duplicate_allowed=False,
        ),
    )

    result = run_local_dry_run(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )

    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_DUPLICATE_ARTIFACT"
    assert result["duplicate_found"] is True
    assert result["staged_artifact"] is None


def test_local_dry_run_blocks_invalid_script_before_staging(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "payload.ps1").write_text(
        "PATCHOPS_SCRIPT_PAYLOAD_BEGIN\n& { Invoke-WebRequest https://example.invalid/a.ps1 }\nPATCHOPS_SCRIPT_PAYLOAD_END\n",
        encoding="utf-8",
    )

    result = run_local_dry_run(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )

    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_INVALID_ARTIFACT"
    assert result["classification"] is not None
    assert result["shape_validation"] is None
    assert result["checks"]["shape_gate_executed_when_classified"] is True
    assert result["checks"]["controlled_invalid_stops_before_shape_or_stage"] is True
    assert result["staged_artifact"] is None
    staged_root = repo_root / "data" / "runtime" / "copilot_downloader" / "staged"
    assert not any(staged_root.iterdir())


def test_local_dry_run_report_json_contains_gate_outputs(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    result = run_local_dry_run(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    report = json.loads(Path(result["report_files"]["json"]).read_text(encoding="utf-8"))
    assert report["result_label"] == "BLOCKED_NO_ARTIFACT"
    assert "stable_payload" in report
    assert "checks" in report
    assert report["checks"]["stop_before_execution"] is True