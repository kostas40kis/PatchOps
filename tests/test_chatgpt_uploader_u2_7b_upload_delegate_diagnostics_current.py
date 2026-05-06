from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_7b_delegate_diagnostic_classifies_attachment_not_visible() -> None:
    from patchops.chatgpt_uploader.upload_delegate_diagnostics import classify_delegate_output

    diagnostic = classify_delegate_output(
        delegate_attempted=True,
        delegate_exit_code=0,
        stdout="\n".join([
            "BROWSER_PICKER_OPENED: true",
            "PATH_TYPED: true",
            "ENTER_PRESSED_ONCE: true",
            "FILE_UPLOAD_ATTEMPTED: true",
            "ATTACHMENT_VISIBLE: false",
            "CHATGPT_SUBMIT_PERFORMED: false",
            "SELENIUM_USED: false",
            "WEBDRIVER_USED: false",
            "BROWSER_DOM_AUTOMATION_USED: false",
        ]),
        stderr="",
    ).to_payload()

    assert diagnostic["delegate_attempted"] is True
    assert diagnostic["delegate_exit_zero"] is True
    assert diagnostic["browser_picker_opened"] is True
    assert diagnostic["path_typed"] is True
    assert diagnostic["enter_pressed_once"] is True
    assert diagnostic["file_upload_attempted"] is True
    assert diagnostic["attachment_visible"] is False
    assert diagnostic["failure_layer"] == "attachment_not_visible"
    assert diagnostic["recommended_next_mode"] == "patch_attachment_verifier_detection_or_wait"


def test_u2_7b_delegate_diagnostic_classifies_picker_not_opened() -> None:
    from patchops.chatgpt_uploader.upload_delegate_diagnostics import classify_delegate_output

    diagnostic = classify_delegate_output(
        delegate_attempted=True,
        delegate_exit_code=0,
        stdout="\n".join([
            "FILE_UPLOAD_ATTEMPTED: true",
            "CHATGPT_SUBMIT_PERFORMED: false",
            "SELENIUM_USED: false",
            "WEBDRIVER_USED: false",
            "BROWSER_DOM_AUTOMATION_USED: false",
        ]),
        stderr="",
    ).to_payload()

    assert diagnostic["failure_layer"] == "picker_not_opened"
    assert diagnostic["classification"] == "upload_delegate_did_not_open_picker"


def test_u2_7b_script_simulated_delegate_output_writes_layered_evidence(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, write_config

    config_path = tmp_path / "target.json"
    report_path = tmp_path / "report.txt"
    evidence_dir = tmp_path / "evidence"

    write_config(ChatGPTUploaderConfig.create("https://chatgpt.com/"), config_path)
    report_path.write_text("report body\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_u2_7b_delegate_diagnostic_live.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--report-path",
            str(report_path),
            "--evidence-dir",
            str(evidence_dir),
            "--simulate-existing-target-found",
            "--simulate-delegate-stdout",
            "\n".join([
                "BROWSER_PICKER_OPENED: true",
                "PATH_TYPED: false",
                "FILE_UPLOAD_ATTEMPTED: true",
                "CHATGPT_SUBMIT_PERFORMED: false",
                "SELENIUM_USED: false",
                "WEBDRIVER_USED: false",
                "BROWSER_DOM_AUTOMATION_USED: false",
            ]),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_U2_7B_STATUS: PASS_OR_BLOCKED" in result.stdout
    assert "EXISTING_TARGET_FOCUSED: true" in result.stdout
    assert "DELEGATE_ATTEMPTED: true" in result.stdout
    assert "PATH_TYPED: false" in result.stdout
    assert "FAILURE_LAYER: report_path_not_typed" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["existing_target_focused"] is True
    assert payload["delegate_attempted"] is True
    assert payload["failure_layer"] == "report_path_not_typed"
    assert payload["chatgpt_submit_performed"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
