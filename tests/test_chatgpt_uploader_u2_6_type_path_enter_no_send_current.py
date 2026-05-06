from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from patchops.chatgpt_uploader import canonical_upload_enter_stage as stage
from patchops.chatgpt_uploader.canonical_upload_enter_stage import upload_enter_stage_safety_flags

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_upload_enter_stage_flags_allow_enter_upload_attempt_but_not_send() -> None:
    flags = upload_enter_stage_safety_flags(open_attempted=True, path_typed=True, picker_enter_pressed=True)
    assert flags["canonical_picker_trigger_attempted"] is True
    assert flags["slash_sent"] is True
    assert flags["file_path_written"] is True
    assert flags["picker_enter_pressed"] is True
    assert flags["file_upload_attempted"] is True
    assert flags["file_selected_or_confirmed_by_picker_enter"] is True
    assert flags["tab_sent"] is False
    assert flags["second_enter_attempted"] is False
    assert flags["plus_control_search_attempted"] is False
    assert flags["menu_control_search_attempted"] is False
    assert flags["ctrl_u_attempted"] is False
    assert flags["open_button_clicked"] is False
    assert flags["attachment_confirmed"] is False
    assert flags["chatgpt_submit_performed"] is False


def test_stage_success_types_path_enters_and_observes_picker_closed(monkeypatch, tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("hello\n", encoding="utf-8")
    fake_run = SimpleNamespace(status="PASS", attempts_requested=1, attempts_completed=1, pass_count=1)

    def fake_trigger(**kwargs):
        assert kwargs["close_picker_on_detect"] is False
        assert kwargs["allow_open_picker"] is True
        return fake_run, tmp_path / "trigger.json", tmp_path / "trigger.txt"

    monkeypatch.setattr(stage, "run_canonical_picker_trigger", fake_trigger)
    monkeypatch.setattr(stage, "type_path_and_press_enter", lambda report_path: (True, True, "typed_entered"))
    monkeypatch.setattr(stage, "wait_for_picker_closed", lambda **kwargs: True)
    result = stage.run_canonical_type_path_enter_no_send(
        target_config_path=tmp_path / "target.json",
        report_path=report,
        evidence_dir=tmp_path,
        allow_open_picker=True,
    )
    assert result.status == "PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND"
    assert result.path_typed is True
    assert result.picker_enter_pressed is True
    assert result.picker_closed_after_enter is True
    assert result.safety_flags["file_upload_attempted"] is True
    assert result.safety_flags["chatgpt_submit_performed"] is False


def test_stage_blocks_if_picker_stays_open_after_enter(monkeypatch, tmp_path) -> None:
    fake_run = SimpleNamespace(status="PASS", attempts_requested=1, attempts_completed=1, pass_count=1)
    monkeypatch.setattr(stage, "run_canonical_picker_trigger", lambda **kwargs: (fake_run, tmp_path / "trigger.json", tmp_path / "trigger.txt"))
    monkeypatch.setattr(stage, "type_path_and_press_enter", lambda report_path: (True, True, "typed_entered"))
    monkeypatch.setattr(stage, "wait_for_picker_closed", lambda **kwargs: False)
    monkeypatch.setattr(stage, "cleanup_open_picker", lambda: True)
    result = stage.run_canonical_type_path_enter_no_send(
        target_config_path=tmp_path / "target.json",
        report_path=tmp_path / "report.txt",
        evidence_dir=tmp_path,
        allow_open_picker=True,
    )
    assert result.status == "FAIL_PICKER_STILL_OPEN_AFTER_ENTER"
    assert result.path_typed is True
    assert result.picker_enter_pressed is True
    assert result.picker_closed_after_enter is False
    assert result.picker_cleanup_closed is True
    assert result.safety_flags["chatgpt_submit_performed"] is False


def test_type_path_enter_script_dry_run_does_not_touch_picker(tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_type_path_enter_no_send.py"),
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
    assert "PATCHOPS_UPLOADER_TYPE_PATH_ENTER_STATUS: PASS_DRY_RUN_NO_PICKER_OPEN" in result.stdout
    assert "CANONICAL_TRIGGER_ATTEMPTED: false" in result.stdout
    assert "FILE_PATH_WRITTEN: false" in result.stdout
    assert "PICKER_ENTER_PRESSED: false" in result.stdout
    assert "FILE_UPLOAD_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
