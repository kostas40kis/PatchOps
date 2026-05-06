from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from patchops.chatgpt_uploader.report_resolver import ReportResolutionError, latest_desktop_report, resolve_report, sha256_file, write_resolved_report_evidence

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def test_explicit_report_path_wins_and_hashes(tmp_path) -> None:
    report = tmp_path / "patch_report.txt"
    data = b"PatchOps report body\n"
    report.write_bytes(data)
    resolved = resolve_report(report_path=report)
    assert resolved.path == str(report.resolve())
    assert resolved.name == "patch_report.txt"
    assert resolved.size_bytes == len(data)
    assert resolved.sha256 == hashlib.sha256(data).hexdigest()
    assert resolved.resolution_mode == "explicit_path"
    assert resolved.stable_observation_count >= 2


def test_missing_report_rejected(tmp_path) -> None:
    with pytest.raises(ReportResolutionError):
        resolve_report(report_path=tmp_path / "missing.txt")


def test_empty_report_rejected(tmp_path) -> None:
    report = tmp_path / "empty.txt"
    report.write_bytes(b"")
    with pytest.raises(ReportResolutionError):
        resolve_report(report_path=report)


def test_temporary_report_rejected(tmp_path) -> None:
    report = tmp_path / "report.txt.crdownload"
    report.write_bytes(b"still downloading")
    with pytest.raises(ReportResolutionError):
        resolve_report(report_path=report)


def test_latest_desktop_recovery_is_explicitly_marked(tmp_path) -> None:
    older = tmp_path / "older.txt"
    newer = tmp_path / "newer.txt"
    older.write_text("older\n", encoding="utf-8")
    newer.write_text("newer\n", encoding="utf-8")
    os.utime(older, (1000, 1000))
    os.utime(newer, (2000, 2000))
    latest = latest_desktop_report(desktop_dir=tmp_path, pattern="*.txt")
    assert latest == newer
    resolved = resolve_report(desktop_dir=tmp_path, latest_desktop_recovery=True, pattern="*.txt")
    assert resolved.path == str(newer.resolve())
    assert resolved.resolution_mode == "latest_desktop_recovery"


def test_write_resolved_report_evidence(tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")
    resolved = resolve_report(report_path=report)
    json_path, txt_path = write_resolved_report_evidence(resolved, tmp_path / "evidence")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["resolved_report"]["path"] == str(report.resolve())
    text = txt_path.read_text(encoding="utf-8")
    assert "PATCHOPS CHATGPT UPLOADER REPORT RESOLUTION" in text
    assert resolved.sha256 in text


def test_resolve_report_script_config_free(tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("script body\n", encoding="utf-8")
    evidence_dir = tmp_path / "evidence"
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_resolve_report.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(tmp_path / "missing_target.json"),
            "--report-path",
            str(report),
            "--evidence-dir",
            str(evidence_dir),
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_UPLOADER_REPORT_RESOLUTION_STATUS: PASS" in result.stdout
    assert f"SELECTED_REPORT_PATH: {report.resolve()}" in result.stdout
    assert "FILE_UPLOAD_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
    assert "SELENIUM_USED: false" in result.stdout
