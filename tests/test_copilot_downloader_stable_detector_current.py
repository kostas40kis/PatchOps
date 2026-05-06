from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.copilot_downloader.config import write_default_config
from patchops.copilot_downloader.models import ArtifactCandidate
from patchops.copilot_downloader.stable_detector import (
    AMBIGUOUS_LABEL,
    NO_ARTIFACT_LABEL,
    STABLE_PASS_LABEL,
    UNSTABLE_LABEL,
    run_stable_artifact_scan,
    validate_candidate_stable_size,
)


def _candidate(path: Path) -> ArtifactCandidate:
    stat = path.stat()
    return ArtifactCandidate(
        path=path.resolve(strict=False),
        source="inbox_dir",
        extension=path.suffix.lower(),
        size_bytes=stat.st_size,
        modified_timestamp=stat.st_mtime,
    )


def _repo_with_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    write_default_config(config_path)
    return repo_root, config_path


def test_stable_candidate_passes_when_size_and_modified_time_are_constant(tmp_path: Path):
    artifact = tmp_path / "payload.ps1"
    artifact.write_text("& { Set-StrictMode -Version Latest }\n", encoding="utf-8")
    result = validate_candidate_stable_size(
        _candidate(artifact),
        sample_count=3,
        interval_seconds=0,
        sleep_fn=lambda _seconds: None,
    )
    assert result.result_label == STABLE_PASS_LABEL
    assert len(result.samples) == 3
    assert result.stable_after_seconds is not None
    assert {sample.size_bytes for sample in result.samples} == {artifact.stat().st_size}


def test_growing_candidate_is_blocked_as_unstable(tmp_path: Path):
    artifact = tmp_path / "payload.zip"
    artifact.write_text("x", encoding="utf-8")
    sizes = iter([1, 2, 3])

    def fake_stat(_path: Path):
        return SimpleNamespace(st_size=next(sizes), st_mtime=100.0)

    result = validate_candidate_stable_size(
        _candidate(artifact),
        sample_count=3,
        interval_seconds=0,
        sleep_fn=lambda _seconds: None,
        stat_fn=fake_stat,
        clock_fn=lambda: 200.0,
    )
    assert result.result_label == UNSTABLE_LABEL
    assert result.issue == "size_changed_across_samples"


def test_modified_timestamp_change_is_blocked_even_when_size_matches(tmp_path: Path):
    artifact = tmp_path / "payload.md"
    artifact.write_text("stable size", encoding="utf-8")
    mtimes = iter([100.0, 101.0, 102.0])

    def fake_stat(_path: Path):
        return SimpleNamespace(st_size=11, st_mtime=next(mtimes))

    result = validate_candidate_stable_size(
        _candidate(artifact),
        sample_count=3,
        interval_seconds=0,
        sleep_fn=lambda _seconds: None,
        stat_fn=fake_stat,
    )
    assert result.result_label == UNSTABLE_LABEL
    assert result.issue == "modified_timestamp_changed_across_samples"


def test_partial_download_candidate_is_blocked_without_sampling(tmp_path: Path):
    artifact = tmp_path / "payload.zip.crdownload"
    artifact.write_text("not ready", encoding="utf-8")
    candidate = ArtifactCandidate(
        path=artifact.resolve(strict=False),
        source="browser_downloads_dir",
        extension=".crdownload",
        size_bytes=artifact.stat().st_size,
        modified_timestamp=artifact.stat().st_mtime,
    )
    result = validate_candidate_stable_size(candidate, sample_count=3, interval_seconds=0)
    assert result.result_label == UNSTABLE_LABEL
    assert result.issue == "partial_or_temporary_extension"
    assert result.samples == ()


def test_run_stable_scan_returns_blocked_no_artifact_for_empty_configured_folders(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    result = run_stable_artifact_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == NO_ARTIFACT_LABEL
    assert result["candidate_count"] == 0
    assert result["checks"]["hash_not_computed"] is True
    assert result["checks"]["staging_not_performed"] is True
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_run_stable_scan_passes_single_stable_artifact(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "payload.txt").write_text("stable artifact", encoding="utf-8")
    result = run_stable_artifact_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == STABLE_PASS_LABEL
    assert result["candidate_count"] == 1
    assert result["stable_validation"]["stable_after_seconds"] is not None


def test_run_stable_scan_blocks_ambiguous_artifacts_before_sampling(tmp_path: Path):
    repo_root, config_path = _repo_with_config(tmp_path)
    inbox = repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    downloads = repo_root / "data" / "runtime" / "copilot_downloader" / "browser_downloads"
    inbox.mkdir(parents=True)
    downloads.mkdir(parents=True)
    (inbox / "a.ps1").write_text("a", encoding="utf-8")
    (downloads / "b.zip").write_text("b", encoding="utf-8")
    result = run_stable_artifact_scan(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=repo_root / "evidence",
        sample_count=2,
        interval_seconds=0,
    )
    assert result["ok"] is True
    assert result["result_label"] == AMBIGUOUS_LABEL
    assert result["candidate_count"] == 2
    assert result["stable_validation"]["issue"] == "ambiguous_artifacts"


def test_sample_count_must_be_at_least_two(tmp_path: Path):
    artifact = tmp_path / "payload.json"
    artifact.write_text("{}", encoding="utf-8")
    try:
        validate_candidate_stable_size(_candidate(artifact), sample_count=1, interval_seconds=0)
    except ValueError as exc:
        assert "sample_count" in str(exc)
    else:
        raise AssertionError("expected ValueError for sample_count < 2")