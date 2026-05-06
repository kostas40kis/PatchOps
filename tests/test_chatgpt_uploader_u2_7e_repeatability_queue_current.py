from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_7e_queue_builds_stable_items(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.upload_queue import build_upload_queue, write_queue_file, read_queue_file

    report_a = tmp_path / "a.txt"
    report_b = tmp_path / "b.txt"
    report_a.write_text("a\n", encoding="utf-8")
    report_b.write_text("b\n", encoding="utf-8")

    queue = build_upload_queue([report_a, report_b])
    assert len(queue) == 2
    assert queue[0].index == 1
    assert queue[0].report_exists is True
    assert queue[0].report_sha256

    queue_file = write_queue_file(queue, tmp_path / "queue.json")
    loaded = read_queue_file(queue_file)

    assert [item.report_path for item in loaded] == [item.report_path for item in queue]


def test_u2_7e_repeatability_classifier_passes_two_successes() -> None:
    from patchops.chatgpt_uploader.upload_queue import classify_repeatability_results

    success = {
        "status": "PASS",
        "result": "PASS_ATTACHMENT_READY_NO_SEND_HARDENED",
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
    }

    summary = classify_repeatability_results([dict(success), dict(success)]).to_payload()

    assert summary["status"] == "PASS"
    assert summary["result"] == "PASS_U2_7E_REPEATABILITY_QUEUE_READY_NO_SEND"
    assert summary["queue_item_count"] == 2
    assert summary["pass_count"] == 2
    assert summary["blocked_count"] == 0
    assert summary["chatgpt_submit_performed"] is False


def test_u2_7e_repeatability_classifier_blocks_first_missing_layer() -> None:
    from patchops.chatgpt_uploader.upload_queue import classify_repeatability_results

    first = {
        "status": "PASS",
        "result": "PASS_ATTACHMENT_READY_NO_SEND_HARDENED",
        "chatgpt_submit_performed": False,
    }
    second = {
        "status": "PASS_OR_BLOCKED",
        "result": "PASS_OR_BLOCKED_ATTACHMENT_READY_HARDENING_FIRST_LAYER_CLASSIFIED",
        "failure_layer": "picker_not_opened",
        "recommended_next_mode": "repair_picker_open_detection_or_focus",
        "chatgpt_submit_performed": False,
    }

    summary = classify_repeatability_results([first, second]).to_payload()

    assert summary["status"] == "PASS_OR_BLOCKED"
    assert summary["first_failure_index"] == 2
    assert summary["first_failure_layer"] == "picker_not_opened"
    assert summary["recommended_next_mode"] == "repair_picker_open_detection_or_focus"


def test_u2_7e_script_simulate_pass_writes_queue_evidence_with_explicit_multi(tmp_path: Path) -> None:
    report_a = tmp_path / "a.txt"
    report_b = tmp_path / "b.txt"
    report_a.write_text("a\n", encoding="utf-8")
    report_b.write_text("b\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_u2_7e_repeatability_queue_gate.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--report-path",
            str(report_a),
            "--report-path",
            str(report_b),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--simulate-pass",
            "--allow-multi-upload",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_U2_7E_STATUS: PASS" in result.stdout
    assert "ORIGINAL_QUEUE_ITEM_COUNT: 2" in result.stdout
    assert "QUEUE_ITEM_COUNT: 2" in result.stdout
    assert "SKIPPED_QUEUE_ITEM_COUNT: 0" in result.stdout
    assert "MULTI_UPLOAD_ALLOWED: true" in result.stdout
    assert "PASS_COUNT: 2" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["queue_item_count"] == 2
    assert payload["multi_upload_allowed"] is True
    assert len(payload["queue_items"]) == 2
    assert len(payload["item_results"]) == 2
    assert payload["chatgpt_submit_performed"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
