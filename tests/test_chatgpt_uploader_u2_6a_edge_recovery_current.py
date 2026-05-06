from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from patchops.chatgpt_uploader import edge_session_recovery as recovery
from patchops.chatgpt_uploader.edge_session_recovery import edge_recovery_safety_flags

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_edge_recovery_flags_preserve_no_send_and_no_dom() -> None:
    upload = SimpleNamespace(
        safety_flags={
            "canonical_picker_trigger_attempted": True,
            "file_picker_open_attempted": True,
            "safe_click_attempted": True,
            "slash_sent": True,
            "file_path_written": True,
            "picker_enter_pressed": True,
            "file_upload_attempted": True,
        }
    )
    flags = edge_recovery_safety_flags(launch_attempted=True, upload_result=upload)
    assert flags["normal_edge_launch_attempted"] is True
    assert flags["configured_target_open_attempted"] is True
    assert flags["target_config_overwritten"] is False
    assert flags["hardcoded_target_url_used"] is False
    assert flags["slash_sent"] is True
    assert flags["file_path_written"] is True
    assert flags["picker_enter_pressed"] is True
    assert flags["tab_sent"] is False
    assert flags["second_enter_attempted"] is False
    assert flags["plus_control_search_attempted"] is False
    assert flags["menu_control_search_attempted"] is False
    assert flags["ctrl_u_attempted"] is False
    assert flags["chatgpt_submit_performed"] is False
    assert flags["selenium_used"] is False
    assert flags["webdriver_used"] is False
    assert flags["browser_dom_automation_used"] is False


def test_launch_skipped_without_explicit_gate(tmp_path) -> None:
    config = tmp_path / "target.json"
    config.write_text('{"target_url":"https://chatgpt.com/","browser":"msedge","mode":"operator_set"}', encoding="utf-8")
    result = recovery.launch_configured_edge_target(target_config_path=config, allow_launch_edge=False)
    assert result.status == "PASS_LAUNCH_SKIPPED"
    assert result.launch_attempted is False
    assert result.target_url_present is True


def test_recovery_blocks_if_launch_config_missing(monkeypatch, tmp_path) -> None:
    result = recovery.run_edge_recovery_then_type_path_enter_no_send(
        target_config_path=tmp_path / "missing.json",
        report_path=tmp_path / "report.txt",
        evidence_dir=tmp_path,
        allow_launch_edge=True,
        allow_open_picker=True,
    )
    assert result.status == "BLOCKED_CONFIG_LOAD_FAILED"
    assert result.upload_result is None
    assert result.safety_flags["chatgpt_submit_performed"] is False


def test_recovery_success_composes_launch_and_upload(monkeypatch, tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")
    fake_launch = recovery.EdgeLaunchRecoveryResult(
        status="PASS_EDGE_LAUNCH_REQUESTED",
        reason="unit",
        target_url_present=True,
        launch_attempted=True,
        process_started=True,
        executable="msedge.exe",
        wait_seconds=0.0,
        safety_flags=edge_recovery_safety_flags(launch_attempted=True),
        created_at="2026-01-01T00:00:00Z",
    )
    fake_upload = SimpleNamespace(
        status="PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND",
        reason="uploaded no send",
        report_path=str(report),
        safety_flags={
            "canonical_picker_trigger_attempted": True,
            "file_picker_open_attempted": True,
            "safe_click_attempted": True,
            "slash_sent": True,
            "file_path_written": True,
            "picker_enter_pressed": True,
            "file_upload_attempted": True,
            "chatgpt_submit_performed": False,
        },
        to_payload=lambda: {"status": "PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND"},
    )
    monkeypatch.setattr(recovery, "launch_configured_edge_target", lambda **kwargs: fake_launch)
    monkeypatch.setattr(recovery, "run_canonical_type_path_enter_no_send", lambda **kwargs: fake_upload)
    result = recovery.run_edge_recovery_then_type_path_enter_no_send(
        target_config_path=tmp_path / "target.json",
        report_path=report,
        evidence_dir=tmp_path,
        allow_launch_edge=True,
        allow_open_picker=True,
    )
    assert result.status == "PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND"
    assert result.safety_flags["normal_edge_launch_attempted"] is True
    assert result.safety_flags["file_upload_attempted"] is True
    assert result.safety_flags["chatgpt_submit_performed"] is False


def test_recovery_script_dry_run_no_launch_no_picker(tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_recover_edge_then_type_path_enter_no_send.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--report-path",
            str(report),
            "--evidence-dir",
            str(tmp_path / "evidence"),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_UPLOADER_EDGE_RECOVERY_UPLOAD_STATUS: PASS_DRY_RUN_NO_PICKER_OPEN" in result.stdout
    assert "LAUNCH_STATUS: PASS_LAUNCH_SKIPPED" in result.stdout
    assert "NORMAL_EDGE_LAUNCH_ATTEMPTED: false" in result.stdout
    assert "CONFIGURED_TARGET_OPEN_ATTEMPTED: false" in result.stdout
    assert "TARGET_CONFIG_OVERWRITTEN: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
