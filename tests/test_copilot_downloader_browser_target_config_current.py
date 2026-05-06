from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.browser_target_config import (
    ALLOWED_HOSTS,
    redacted_target_display,
    run_browser_target_config_doctor,
    target_url_sha256,
    validate_browser_target_config_file,
    write_default_browser_target_config,
)
from patchops.copilot_downloader.models import (
    BLOCKED_BROWSER_TARGET_CONFIG_INVALID,
    BLOCKED_BROWSER_TARGET_CONFIG_MISSING,
    PASS_BROWSER_TARGET_CONFIGURED,
    RESULT_LABELS,
)


def test_browser_target_labels_are_registered():
    assert PASS_BROWSER_TARGET_CONFIGURED in RESULT_LABELS
    assert BLOCKED_BROWSER_TARGET_CONFIG_MISSING in RESULT_LABELS
    assert BLOCKED_BROWSER_TARGET_CONFIG_INVALID in RESULT_LABELS


def test_target_hash_and_redaction_do_not_emit_raw_path_or_query():
    url = "https://chatgpt.com/c/example-secret?model=gpt-5.5"
    assert len(target_url_sha256(url)) == 64
    assert target_url_sha256(url) == target_url_sha256(url)
    display = redacted_target_display(url)
    assert display == "https://chatgpt.com/<redacted-path>"
    assert "example-secret" not in display
    assert "model" not in display


def test_default_browser_target_config_loads_and_evidence_hides_raw_url(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)

    label, issues, config = validate_browser_target_config_file(config_path, repo_root=repo_root, create_dirs=True)

    assert label == PASS_BROWSER_TARGET_CONFIGURED
    assert issues == []
    assert config is not None
    assert config.target_url == "https://chatgpt.com/"
    evidence = config.to_evidence_dict()
    assert "target_url" not in evidence
    assert evidence["target_url_sha256"] == target_url_sha256("https://chatgpt.com/")
    assert evidence["redacted_target_display"] == "https://chatgpt.com/"
    assert config.evidence_dir.is_dir()


def test_missing_browser_target_config_returns_blocked_missing(tmp_path: Path):
    label, issues, config = validate_browser_target_config_file(tmp_path / "missing.json", repo_root=tmp_path)
    assert label == BLOCKED_BROWSER_TARGET_CONFIG_MISSING
    assert config is None
    assert issues and "missing" in issues[0].lower()


def test_invalid_browser_target_rejects_non_https_or_wrong_host(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["target"]["target_url"] = "http://example.com/conversation"
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    label, issues, config = validate_browser_target_config_file(config_path, repo_root=repo_root)

    assert label == BLOCKED_BROWSER_TARGET_CONFIG_INVALID
    assert config is None
    assert any("https" in issue for issue in issues)
    assert any("host" in issue for issue in issues)


def test_invalid_browser_target_rejects_enabled_live_policy(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["policy"]["allow_browser_start"] = True
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    label, issues, config = validate_browser_target_config_file(config_path, repo_root=repo_root)

    assert label == BLOCKED_BROWSER_TARGET_CONFIG_INVALID
    assert config is None
    assert any("allow_browser_start" in issue for issue in issues)


def test_browser_target_config_rejects_evidence_dir_outside_repo(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["paths"]["evidence_dir"] = "../outside"
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    label, issues, config = validate_browser_target_config_file(config_path, repo_root=repo_root)

    assert label == BLOCKED_BROWSER_TARGET_CONFIG_INVALID
    assert config is None
    assert any("under repo root" in issue for issue in issues)


def test_browser_target_doctor_writes_redacted_evidence_without_raw_url(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)
    evidence_root = repo_root / "evidence"

    result = run_browser_target_config_doctor(
        repo_root=repo_root,
        config_path=config_path,
        evidence_root=evidence_root,
        create_dirs=True,
    )

    assert result["ok"] is True
    assert result["result_label"] == PASS_BROWSER_TARGET_CONFIGURED
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["window_scan_not_performed"] is True
    assert result["checks"]["dom_automation_disabled"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["conversation_text_not_logged"] is True
    assert result["safety"]["browser_used"] is False
    assert result["safety"]["clipboard_read"] is False
    assert result["safety"]["conversation_text_logged"] is False
    assert result["target"]["redacted_target_display"] == "https://chatgpt.com/"
    assert "target_url" not in result["target"]
    evidence_json = Path(result["evidence_files"]["json"])
    evidence_text = Path(result["evidence_files"]["text"])
    assert evidence_json.is_file()
    assert evidence_text.is_file()
    evidence_payload = json.loads(evidence_json.read_text(encoding="utf-8"))
    serialized = json.dumps(evidence_payload)
    assert "target_url\"" not in serialized
    assert "https://chatgpt.com/" in serialized


def test_repository_browser_target_config_doctor_accepts_checked_in_config():
    result = run_browser_target_config_doctor(
        repo_root=Path.cwd(),
        config_path="data/config/copilot_downloader_browser_target.json",
        evidence_root="data/runtime/copilot_downloader/d1_01_browser_target_config_test",
        create_dirs=True,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_BROWSER_TARGET_CONFIGURED
    assert result["target"]["redacted_target_display"].startswith("https://")
    assert result["target"]["redacted_target_display"].split("/")[2] in ALLOWED_HOSTS
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["conversation_text_not_logged"] is True