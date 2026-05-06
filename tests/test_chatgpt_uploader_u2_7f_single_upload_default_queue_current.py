from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def _make_reports(tmp_path: Path) -> tuple[Path, Path]:
    report_a = tmp_path / "a.txt"
    report_b = tmp_path / "b.txt"
    report_a.write_text("a\n", encoding="utf-8")
    report_b.write_text("b\n", encoding="utf-8")
    return report_a, report_b


def test_u2_7f_select_queue_items_single_default(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.upload_queue import build_upload_queue, select_queue_items

    report_a, report_b = _make_reports(tmp_path)
    queue = build_upload_queue([report_a, report_b])
    selection = select_queue_items(queue)

    assert selection.original_queue_item_count == 2
    assert selection.queue_item_count == 1
    assert selection.skipped_queue_item_count == 1
    assert selection.multi_upload_allowed is False
    assert selection.items[0].report_path == str(report_a.resolve())


def test_u2_7f_select_queue_items_allows_multi_when_explicit(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.upload_queue import build_upload_queue, select_queue_items

    report_a, report_b = _make_reports(tmp_path)
    queue = build_upload_queue([report_a, report_b])
    selection = select_queue_items(queue, allow_multi_upload=True)

    assert selection.original_queue_item_count == 2
    assert selection.queue_item_count == 2
    assert selection.skipped_queue_item_count == 0
    assert selection.multi_upload_allowed is True


def test_u2_7f_script_defaults_to_one_item_even_with_two_report_paths(tmp_path: Path) -> None:
    report_a, report_b = _make_reports(tmp_path)

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
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "ORIGINAL_QUEUE_ITEM_COUNT: 2" in result.stdout
    assert "QUEUE_ITEM_COUNT: 1" in result.stdout
    assert "SKIPPED_QUEUE_ITEM_COUNT: 1" in result.stdout
    assert "MULTI_UPLOAD_ALLOWED: false" in result.stdout
    assert "PASS_COUNT: 1" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["original_queue_item_count"] == 2
    assert payload["queue_item_count"] == 1
    assert payload["skipped_queue_item_count"] == 1
    assert payload["multi_upload_allowed"] is False
    assert len(payload["queue_items"]) == 1
    assert len(payload["item_results"]) == 1
    assert payload["chatgpt_submit_performed"] is False


def test_u2_7f_script_allows_multi_only_with_explicit_flag(tmp_path: Path) -> None:
    report_a, report_b = _make_reports(tmp_path)

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
    assert "ORIGINAL_QUEUE_ITEM_COUNT: 2" in result.stdout
    assert "QUEUE_ITEM_COUNT: 2" in result.stdout
    assert "SKIPPED_QUEUE_ITEM_COUNT: 0" in result.stdout
    assert "MULTI_UPLOAD_ALLOWED: true" in result.stdout
    assert "PASS_COUNT: 2" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["original_queue_item_count"] == 2
    assert payload["queue_item_count"] == 2
    assert payload["skipped_queue_item_count"] == 0
    assert payload["multi_upload_allowed"] is True
    assert len(payload["queue_items"]) == 2
    assert len(payload["item_results"]) == 2
    assert payload["chatgpt_submit_performed"] is False


def test_u2_7f_script_respects_max_items_with_multi_flag(tmp_path: Path) -> None:
    report_a, report_b = _make_reports(tmp_path)

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
            "--max-items",
            "1",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "QUEUE_ITEM_COUNT: 1" in result.stdout
    assert "SKIPPED_QUEUE_ITEM_COUNT: 1" in result.stdout
    assert "MULTI_UPLOAD_ALLOWED: true" in result.stdout
