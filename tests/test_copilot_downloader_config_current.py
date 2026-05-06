from __future__ import annotations

import json
import sys
from pathlib import Path

from patchops.copilot_downloader.config import (
    CONFIG_INVALID_LABEL,
    CONFIG_MISSING_LABEL,
    CONFIG_VALIDATED_LABEL,
    default_config_payload,
    load_downloader_config,
    run_config_doctor,
    validate_config_file,
    write_default_config,
)
from patchops.copilot_downloader.models import RESULT_LABELS


def test_config_labels_are_declared_in_model_ladder():
    assert CONFIG_VALIDATED_LABEL in RESULT_LABELS
    assert CONFIG_MISSING_LABEL in RESULT_LABELS
    assert CONFIG_INVALID_LABEL in RESULT_LABELS


def test_default_config_payload_allows_only_local_detection_runtime_actions():
    payload = default_config_payload()
    assert payload["producer"] == "patchops.copilot_downloader"
    assert payload["schema_version"] == 1
    policy = payload["policy"]
    assert policy["allow_artifact_detection"] is True
    assert policy["allow_browser_observation"] is False
    assert policy["allow_clipboard_read"] is False
    assert policy["allow_artifact_execution"] is False


def test_write_and_load_default_config_creates_expected_runtime_dirs(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    write_default_config(config_path)
    config = load_downloader_config(config_path, repo_root=repo_root, create_dirs=True)

    assert config.allow_artifact_detection is True
    assert config.inbox_dir == repo_root / "data" / "runtime" / "copilot_downloader" / "inbox"
    assert config.browser_downloads_dir == repo_root / "data" / "runtime" / "copilot_downloader" / "browser_downloads"
    assert config.staging_dir == repo_root / "data" / "runtime" / "copilot_downloader" / "staged"
    assert config.evidence_dir == repo_root / "data" / "runtime" / "copilot_downloader" / "evidence"
    assert config.duplicate_ledger_path == repo_root / "data" / "runtime" / "copilot_downloader" / "ledger" / "artifact_ledger.jsonl"
    assert config.inbox_dir.is_dir()
    assert config.browser_downloads_dir.is_dir()
    assert config.staging_dir.is_dir()
    assert config.evidence_dir.is_dir()
    assert config.duplicate_ledger_path.parent.is_dir()
    assert not config.duplicate_ledger_path.exists()


def test_missing_config_returns_blocked_missing(tmp_path: Path):
    label, issues, config = validate_config_file(tmp_path / "missing.json", repo_root=tmp_path)
    assert label == CONFIG_MISSING_LABEL
    assert config is None
    assert issues and "missing" in issues[0].lower()


def test_invalid_config_returns_blocked_invalid(tmp_path: Path):
    config_path = tmp_path / "bad.json"
    config_path.write_text("{not json", encoding="utf-8")
    label, issues, config = validate_config_file(config_path, repo_root=tmp_path)
    assert label == CONFIG_INVALID_LABEL
    assert config is None
    assert issues


def test_config_rejects_paths_outside_repo(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    payload = default_config_payload()
    payload["paths"]["inbox_dir"] = "../outside"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    label, issues, config = validate_config_file(config_path, repo_root=repo_root)
    assert label == CONFIG_INVALID_LABEL
    assert config is None
    assert any("under repo root" in issue for issue in issues)


def test_config_rejects_browser_clipboard_or_execution_policy_enablement(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    payload = default_config_payload()
    payload["policy"]["allow_clipboard_read"] = True
    config_path.parent.mkdir(parents=True)
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    label, issues, config = validate_config_file(config_path, repo_root=repo_root)
    assert label == CONFIG_INVALID_LABEL
    assert config is None
    assert any("allow_clipboard_read" in issue for issue in issues)


def test_config_doctor_writes_evidence_and_never_imports_uploader(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_config.json"
    write_default_config(config_path)
    evidence_root = repo_root / "data" / "runtime" / "copilot_downloader" / "d0_03_config"

    result = run_config_doctor(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=evidence_root,
        create_dirs=True,
    )

    assert result["ok"] is True
    assert result["result_label"] == CONFIG_VALIDATED_LABEL
    assert result["safety"]["browser_used"] is False
    assert result["safety"]["clipboard_read"] is False
    assert result["safety"]["artifact_executed"] is False
    assert result["checks"]["local_artifact_detection_enabled"] is True
    assert result["checks"]["uploader_module_not_imported"] is True
    assert "patchops.chatgpt_uploader" not in sys.modules
    assert Path(result["evidence_files"]["json"]).is_file()
    assert Path(result["evidence_files"]["text"]).is_file()


def test_repository_config_doctor_accepts_checked_in_config():
    result = run_config_doctor(
        repo_root=Path.cwd(),
        config_path="data/config/copilot_downloader_config.json",
        evidence_root="data/runtime/copilot_downloader/d0_03_config_test",
        create_dirs=True,
    )
    assert result["ok"] is True
    assert result["result_label"] == CONFIG_VALIDATED_LABEL
    assert result["checks"]["config_validated"] is True
    assert result["checks"]["browser_observation_disabled"] is True
    assert result["checks"]["local_artifact_detection_enabled"] is True
    assert result["checks"]["artifact_execution_disabled"] is True