from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from patchops.chatgpt_uploader import canonical_upload_path_stage as stage
from patchops.chatgpt_uploader.canonical_upload_path_stage import upload_path_stage_safety_flags

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_upload_path_stage_safety_flags_allow_path_but_not_open_send() -> None:
    flags = upload_path_stage_safety_flags(open_attempted=True, path_written=True)
    assert flags["canonical_picker_trigger_attempted"] is True
    assert flags["slash_sent"] is True
    assert flags["file_path_written"] is True
    assert flags["tab_sent"] is False
    assert flags["second_enter_attempted"] is False
    assert flags["plus_control_search_attempted"] is False
    assert flags["menu_control_search_attempted"] is False
    assert flags["ctrl_u_attempted"] is False
    assert flags["file_selected"] is False
    assert flags["open_button_pressed"] is False
    assert flags["attachment_confirmed"] is False
    assert flags["file_upload_attempted"] is False
    assert flags["chatgpt_submit_performed"] is False


def test_stage_success_composes_trigger_then_path_writer(monkeypatch, tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("hello\n", encoding="utf-8")
    fake_run = SimpleNamespace(status="PASS", attempts_requested=1, attempts_completed=1, pass_count=1)

    def fake_trigger(**kwargs):
        assert kwargs["close_picker_on_detect"] is False
        assert kwargs["allow_open_picker"] is True
        return fake_run, tmp_path / "trigger.json", tmp_path / "trigger.txt"

    fake_writer = SimpleNamespace(
        status="PASS_PATH_WRITTEN_NO_OPEN",
        reason="unit",
        report_path=str(report),
        wrote_path=True,
    )
    monkeypatch.setattr(stage, "run_canonical_picker_trigger", fake_trigger)
    monkeypatch.setattr(stage, "write_report_path_to_detected_picker", lambda **kwargs: fake_writer)
    monkeypatch.setattr(stage, "cleanup_open_picker", lambda: True)
    result = stage.run_canonical_open_write_path_no_open(
        target_config_path=tmp_path / "target.json",
        report_path=report,
        evidence_dir=tmp_path,
        allow_open_picker=True,
    )
    assert result.status == "PASS_PATH_WRITTEN_NO_OPEN"
    assert result.path_written is True
    assert result.picker_cleanup_closed is True
    assert result.safety_flags["file_path_written"] is True
    assert result.safety_flags["open_button_pressed"] is False
    assert result.safety_flags["chatgpt_submit_performed"] is False


def test_stage_blocks_if_trigger_does_not_pass(monkeypatch, tmp_path) -> None:
    fake_run = SimpleNamespace(status="FAIL_OR_BLOCKED", attempts_requested=1, attempts_completed=1, pass_count=0)
    monkeypatch.setattr(stage, "run_canonical_picker_trigger", lambda **kwargs: (fake_run, tmp_path / "trigger.json", tmp_path / "trigger.txt"))
    monkeypatch.setattr(stage, "cleanup_open_picker", lambda: False)
    result = stage.run_canonical_open_write_path_no_open(
        target_config_path=tmp_path / "target.json",
        report_path=tmp_path / "report.txt",
        evidence_dir=tmp_path,
        allow_open_picker=True,
    )
    assert result.status == "BLOCKED_TRIGGER_NOT_PASS"
    assert result.path_written is False
    assert result.safety_flags["file_path_written"] is False
    assert result.safety_flags["open_button_pressed"] is False


def test_open_write_path_script_dry_run_does_not_touch_picker(tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_open_picker_write_path_no_open.py"),
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
    assert "PATCHOPS_UPLOADER_OPEN_WRITE_PATH_STATUS: PASS_DRY_RUN_NO_PICKER_OPEN" in result.stdout
    assert "CANONICAL_TRIGGER_ATTEMPTED: false" in result.stdout
    assert "FILE_PATH_WRITTEN: false" in result.stdout
    assert "OPEN_BUTTON_PRESSED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
