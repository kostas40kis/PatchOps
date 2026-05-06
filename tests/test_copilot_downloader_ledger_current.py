from __future__ import annotations

import hashlib
from pathlib import Path

from patchops.copilot_downloader.config import write_default_config
from patchops.copilot_downloader.ledger import (
    BLOCKED_DUPLICATE_ARTIFACT,
    PASS_HASH_LEDGER_RECORDED,
    append_ledger_entry,
    build_ledger_entry,
    compute_sha256,
    find_duplicate_entry,
    read_ledger_entries,
    run_hash_ledger_scan,
)
from patchops.copilot_downloader.models import RESULT_LABELS


def _repo_with_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    write_default_config(config_path)
    return repo_root, config_path


def test_hash_ledger_labels_are_registered():
    assert PASS_HASH_LEDGER_RECORDED in RESULT_LABELS
    assert BLOCKED_DUPLICATE_ARTIFACT in RESULT_LABELS


def test_compute_sha256_matches_hashlib(tmp_path: Path):
    payload = b"PatchOps artifact bytes\n"
    artifact = tmp_path / "artifact.ps1"
    artifact.write_bytes(payload)
    assert compute_sha256(artifact) == hashlib.sha256(payload).hexdigest()


def test_ledger_append_read_and_duplicate_detection(tmp_path: Path):
    ledger_path = tmp_path / "ledger" / "artifact_ledger.jsonl"
    entry = build_ledger_entry(
        artifact_sha256="ABCDEF",
        candidate={"path": str(tmp_path / "a.ps1"), "source": "inbox_dir", "extension": ".ps1", "size_bytes": 10},
        status="recorded",
        duplicate_allowed=False,
    )
    append_ledger_entry(ledger_path, entry)
    entries = read_ledger_entries(ledger_path)
    assert len(entries) == 1
    assert entries[0]["artifact_sha256"] == "abcdef"
    duplicate = find_duplicate_entry(ledger_path, "abcdef")
    assert duplicate is not None
    assert duplicate["status"] == "recorded"


def test_hash_ledger_scan_returns_blocked_no_artifact_without_creating_ledger_file(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    result = run_hash_ledger_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_NO_ARTIFACT"
    assert result["artifact_sha256"] is None
    assert result["ledger_written"] is False
    assert Path(result["evidence_files"]["json"]).is_file()
    assert not Path(result["ledger_path"]).exists()
    assert result["checks"]["staging_not_performed"] is True
    assert result["safety"]["artifact_executed"] is False


def test_hash_ledger_scan_records_single_stable_artifact(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    artifact = inbox / "payload.txt"
    artifact.write_text("stable artifact", encoding="utf-8")

    result = run_hash_ledger_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )

    assert result["ok"] is True
    assert result["result_label"] == PASS_HASH_LEDGER_RECORDED
    assert result["artifact_sha256"] == compute_sha256(artifact)
    assert result["ledger_written"] is True
    ledger_entries = read_ledger_entries(result["ledger_path"])
    assert len(ledger_entries) == 1
    assert ledger_entries[0]["artifact_sha256"] == result["artifact_sha256"]
    assert ledger_entries[0]["status"] == "recorded"


def test_hash_ledger_scan_blocks_duplicate_by_default(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "payload.txt").write_text("same bytes", encoding="utf-8")

    first = run_hash_ledger_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence1",
        sample_count=2,
        interval_seconds=0,
    )
    second = run_hash_ledger_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence2",
        sample_count=2,
        interval_seconds=0,
    )

    assert first["result_label"] == PASS_HASH_LEDGER_RECORDED
    assert second["ok"] is True
    assert second["result_label"] == BLOCKED_DUPLICATE_ARTIFACT
    assert second["duplicate_found"] is True
    assert second["ledger_written"] is False
    assert len(read_ledger_entries(second["ledger_path"])) == 1


def test_hash_ledger_scan_allows_duplicate_when_explicitly_enabled(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "payload.md").write_text("same bytes", encoding="utf-8")

    first = run_hash_ledger_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence1",
        sample_count=2,
        interval_seconds=0,
    )
    second = run_hash_ledger_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence2",
        sample_count=2,
        interval_seconds=0,
        allow_duplicate=True,
    )

    assert first["result_label"] == PASS_HASH_LEDGER_RECORDED
    assert second["result_label"] == PASS_HASH_LEDGER_RECORDED
    assert second["duplicate_found"] is True
    assert second["ledger_written"] is True
    entries = read_ledger_entries(second["ledger_path"])
    assert len(entries) == 2
    assert entries[-1]["status"] == "duplicate_allowed_recorded"
    assert entries[-1]["duplicate_allowed"] is True


def test_hash_ledger_scan_propagates_ambiguous_artifact_block(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    downloads = repo_root / "data" / "runtime" / "copilot_downloader" / "browser_downloads"
    inbox.mkdir(parents=True)
    downloads.mkdir(parents=True)
    (inbox / "a.ps1").write_text("a", encoding="utf-8")
    (downloads / "b.zip").write_text("b", encoding="utf-8")

    result = run_hash_ledger_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )

    assert result["ok"] is True
    assert result["result_label"] == "BLOCKED_AMBIGUOUS_ARTIFACTS"
    assert result["ledger_written"] is False