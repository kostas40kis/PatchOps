from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.picker_path_writer import PickerPathWriteResult, default_path_write_safety_flags, write_path_writer_evidence

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_default_path_write_safety_flags_before_write() -> None:
    flags = default_path_write_safety_flags(wrote_path=False)
    assert flags["file_picker_open_attempted"] is False
    assert flags["file_path_written"] is False
    assert flags["file_selected"] is False
    assert flags["open_button_pressed"] is False
    assert flags["file_upload_attempted"] is False
    assert flags["chatgpt_submit_performed"] is False
    assert flags["clipboard_written"] is False
    assert flags["paste_attempted"] is False


def test_default_path_write_safety_flags_after_path_write_only() -> None:
    flags = default_path_write_safety_flags(wrote_path=True)
    assert flags["file_path_written"] is True
    assert flags["file_selected"] is False
    assert flags["open_button_pressed"] is False
    assert flags["file_upload_attempted"] is False
    assert flags["attachment_confirmed"] is False
    assert flags["chatgpt_submit_performed"] is False


def test_write_path_writer_evidence(tmp_path) -> None:
    result = PickerPathWriteResult(
        status="PASS_NO_PICKER_NO_WRITE",
        reason="unit",
        report_path=str(tmp_path / "report.txt"),
        report_name="report.txt",
        report_sha256="abc",
        picker_detected=False,
        picker_count=0,
        error_modal_detected=False,
        ambiguous=False,
        picker_handle=None,
        target_control_handle=None,
        target_control_class=None,
        wrote_path=False,
        verified_control_text_hash=None,
        safety_flags=default_path_write_safety_flags(wrote_path=False),
        created_at="2026-01-01T00:00:00Z",
    )
    json_path, txt_path = write_path_writer_evidence(result, tmp_path / "evidence")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_NO_PICKER_NO_WRITE"
    assert payload["safety_flags"]["file_path_written"] is False
    assert payload["safety_flags"]["open_button_pressed"] is False
    text = txt_path.read_text(encoding="utf-8")
    assert "PATCHOPS CHATGPT UPLOADER PICKER PATH WRITER" in text
    assert "OpenButtonPressed      : false" in text


def test_writer_script_no_picker_passes_without_writing_path(tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("report body\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_write_report_path_to_picker.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--report-path",
            str(report),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--wait-seconds",
            "0",
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode in {0, 2}
    assert "PATCHOPS_UPLOADER_PICKER_PATH_WRITE_STATUS:" in result.stdout
    assert "OPEN_BUTTON_PRESSED: false" in result.stdout
    assert "FILE_SELECTED: false" in result.stdout
    assert "FILE_UPLOAD_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
    if result.returncode == 0:
        assert "PATH_WRITTEN: false" in result.stdout or "PATH_WRITTEN: true" in result.stdout
