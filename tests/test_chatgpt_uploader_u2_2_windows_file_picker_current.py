from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.windows_file_picker import WindowDescriptor, classify_descriptors, default_safety_flags, descriptor_is_known_error_modal, descriptor_is_picker, write_detection_evidence

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _descriptor(**overrides) -> WindowDescriptor:
    payload = {
        "handle": 100,
        "class_name": "#32770",
        "title_sha256": "hash",
        "title_length": 4,
        "title_has_open": True,
        "title_has_choose": False,
        "title_has_rename": False,
        "title_has_error": False,
        "visible": True,
        "enabled": True,
        "child_class_counts": {"edit": 1, "button": 2, "directuihwnd": 1},
        "child_text_keyword_hits": [],
        "rectangle": {"left": 0, "top": 0, "right": 500, "bottom": 400},
        "owner_handle": None,
    }
    payload.update(overrides)
    return WindowDescriptor(**payload)


def test_open_dialog_descriptor_is_picker() -> None:
    descriptor = _descriptor()
    assert descriptor_is_picker(descriptor) is True
    assert descriptor_is_known_error_modal(descriptor) is False


def test_choose_file_descriptor_is_picker() -> None:
    descriptor = _descriptor(title_has_open=False, title_has_choose=True, child_class_counts={"comboboxex32": 1, "button": 1})
    assert descriptor_is_picker(descriptor) is True


def test_non_dialog_is_not_picker() -> None:
    descriptor = _descriptor(class_name="Chrome_WidgetWin_1")
    assert descriptor_is_picker(descriptor) is False


def test_rename_error_modal_classified() -> None:
    descriptor = _descriptor(title_has_open=False, title_has_rename=True, child_class_counts={"button": 1}, child_text_keyword_hits=["the file name is not valid"])
    assert descriptor_is_known_error_modal(descriptor) is True
    assert descriptor_is_picker(descriptor) is False


def test_single_picker_detection_passes() -> None:
    detection = classify_descriptors([_descriptor()])
    assert detection.status == "PASS_PICKER_DETECTED"
    assert detection.picker_detected is True
    assert detection.picker_count == 1
    assert detection.ambiguous is False
    assert detection.safety_flags["file_path_written"] is False
    assert detection.safety_flags["chatgpt_submit_performed"] is False


def test_multiple_pickers_block_as_ambiguous() -> None:
    detection = classify_descriptors([_descriptor(handle=1), _descriptor(handle=2)])
    assert detection.status == "BLOCKED_AMBIGUOUS_PICKERS"
    assert detection.picker_detected is True
    assert detection.picker_count == 2
    assert detection.ambiguous is True


def test_error_modal_without_picker_is_detected() -> None:
    detection = classify_descriptors([_descriptor(title_has_open=False, title_has_rename=True, child_class_counts={"button": 1})])
    assert detection.status == "PASS_ERROR_MODAL_DETECTED"
    assert detection.error_modal_detected is True
    assert detection.picker_detected is False


def test_no_picker_status_is_safe() -> None:
    detection = classify_descriptors([])
    assert detection.status == "PASS_NO_PICKER"
    assert detection.safety_flags == default_safety_flags()


def test_write_detection_evidence(tmp_path) -> None:
    detection = classify_descriptors([_descriptor()])
    json_path, txt_path = write_detection_evidence(detection, tmp_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_PICKER_DETECTED"
    assert payload["safety_flags"]["file_selected"] is False
    assert payload["safety_flags"]["open_button_pressed"] is False
    text = txt_path.read_text(encoding="utf-8")
    assert "PATCHOPS CHATGPT UPLOADER FILE PICKER DETECTION" in text
    assert "FileSelected           : false" in text


def test_detector_script_runs_without_picker_requirement(tmp_path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_detect_picker_live.py"),
            "--repo-root",
            str(PROJECT_ROOT),
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
    assert "PATCHOPS_UPLOADER_PICKER_DETECT_STATUS:" in result.stdout
    assert "FILE_PATH_WRITTEN: false" in result.stdout
    assert "FILE_SELECTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
