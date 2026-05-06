from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def _safe_queue_payload() -> dict:
    return {
        "status": "PASS",
        "result": "PASS_U2_7E_REPEATABILITY_QUEUE_READY_NO_SEND",
        "queue_item_count": 1,
        "original_queue_item_count": 2,
        "skipped_queue_item_count": 1,
        "multi_upload_allowed": False,
        "item_results": [
            {
                "status": "PASS",
                "result": "PASS_ATTACHMENT_READY_NO_SEND_HARDENED",
                "chatgpt_submit_performed": False,
                "conversation_text_logged": False,
                "selenium_used": False,
                "webdriver_used": False,
                "browser_dom_automation_used": False,
                "picker_enter_pressed": True,
            }
        ],
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
    }


def test_u2_7g_submission_guard_passes_safe_queue_payload() -> None:
    from patchops.chatgpt_uploader.submission_guard import evaluate_submission_blocker

    result = evaluate_submission_blocker(_safe_queue_payload()).to_payload()

    assert result["status"] == "PASS"
    assert result["submission_blocker_passed"] is True
    assert result["violation_count"] == 0
    assert result["chatgpt_submit_performed"] is False


def test_u2_7g_submission_guard_allows_picker_enter_but_blocks_chat_submit() -> None:
    from patchops.chatgpt_uploader.submission_guard import evaluate_submission_blocker

    payload = _safe_queue_payload()
    payload["item_results"][0]["picker_enter_pressed"] = True
    payload["item_results"][0]["chatgpt_submit_performed"] = True

    result = evaluate_submission_blocker(payload).to_payload()

    assert result["status"] == "FAIL_FORBIDDEN_SUBMISSION_SIDE_EFFECT"
    assert result["submission_blocker_passed"] is False
    assert result["violation_count"] == 1
    assert result["first_violation_key"] == "chatgpt_submit_performed"
    assert "item_results" in result["first_violation_path"]


def test_u2_7g_submission_guard_blocks_send_button_clicked() -> None:
    from patchops.chatgpt_uploader.submission_guard import evaluate_submission_blocker

    payload = _safe_queue_payload()
    payload["send_button_clicked"] = True

    result = evaluate_submission_blocker(payload).to_payload()

    assert result["status"] == "FAIL_FORBIDDEN_SUBMISSION_SIDE_EFFECT"
    assert result["first_violation_key"] == "send_button_clicked"


def test_u2_7g_script_passes_safe_source_json(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps(_safe_queue_payload(), indent=2), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_u2_7g_submission_blocker_gate.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--source-json",
            str(source),
            "--evidence-dir",
            str(tmp_path / "evidence"),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_U2_7G_STATUS: PASS" in result.stdout
    assert "SUBMISSION_BLOCKER_PASSED: true" in result.stdout
    assert "VIOLATION_COUNT: 0" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["submission_blocker_passed"] is True
    assert payload["chatgpt_submit_performed"] is False


def test_u2_7g_script_fails_forbidden_source_json(tmp_path: Path) -> None:
    payload = _safe_queue_payload()
    payload["item_results"][0]["submit_button_clicked"] = True

    source = tmp_path / "source_forbidden.json"
    source.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_u2_7g_submission_blocker_gate.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--source-json",
            str(source),
            "--evidence-dir",
            str(tmp_path / "evidence_forbidden"),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 3
    assert "PATCHOPS_U2_7G_STATUS: FAIL_FORBIDDEN_SUBMISSION_SIDE_EFFECT" in result.stdout
    assert "SUBMISSION_BLOCKER_PASSED: false" in result.stdout
    assert "FIRST_VIOLATION_KEY: submit_button_clicked" in result.stdout
