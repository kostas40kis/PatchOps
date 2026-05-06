from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from patchops.chatgpt_uploader.config import write_target_config
from patchops.chatgpt_uploader.report_resolver import parse_report_path_from_text, resolve_report, sha256_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def _write_report(path: Path, body: str = "PATCHOPS RUN SUMMARY\nResult : PASS\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_explicit_report_path_wins_over_recovery_latest(tmp_path: Path) -> None:
    explicit = _write_report(tmp_path / "explicit.txt", "explicit report\n")
    latest = _write_report(tmp_path / "latest.txt", "latest report\n")
    future = time.time() + 5
    latest_mtime = future
    explicit_mtime = future - 20
    explicit.touch()
    latest.touch()
    import os
    os.utime(explicit, (explicit_mtime, explicit_mtime))
    os.utime(latest, (latest_mtime, latest_mtime))

    result = resolve_report(
        report_path=explicit,
        report_dir=tmp_path,
        recovery_latest=True,
        min_stable_age_seconds=0,
        now=future + 10,
    )

    assert result.ok is True
    assert result.result == "PASS_REPORT_RESOLVED"
    assert result.selection_reason == "explicit_report_path"
    assert result.selected_report_path == str(explicit.resolve())
    assert result.selected_report_sha256 == sha256_file(explicit)


def test_missing_empty_and_still_writing_reports_are_rejected(tmp_path: Path) -> None:
    missing = resolve_report(report_path=tmp_path / "missing.txt", min_stable_age_seconds=0)
    assert missing.ok is False
    assert missing.result == "BLOCKED_REPORT_MISSING"

    empty_path = tmp_path / "empty.txt"
    empty_path.write_text("", encoding="utf-8")
    empty = resolve_report(report_path=empty_path, min_stable_age_seconds=0)
    assert empty.ok is False
    assert empty.result == "BLOCKED_REPORT_EMPTY"

    fresh_path = _write_report(tmp_path / "fresh.txt")
    now = fresh_path.stat().st_mtime + 1
    fresh = resolve_report(report_path=fresh_path, min_stable_age_seconds=3600, now=now)
    assert fresh.ok is False
    assert fresh.result == "BLOCKED_REPORT_STILL_WRITING"


def test_latest_desktop_style_fallback_only_in_recovery_mode(tmp_path: Path) -> None:
    old = _write_report(tmp_path / "patchops_old.txt", "old\n")
    new = _write_report(tmp_path / "patchops_new.txt", "new\n")

    import os
    base = time.time() - 100
    os.utime(old, (base, base))
    os.utime(new, (base + 50, base + 50))

    blocked = resolve_report(report_dir=tmp_path, prefix="patchops_", min_stable_age_seconds=0)
    assert blocked.ok is False
    assert blocked.result == "BLOCKED_REPORT_PATH_REQUIRED"

    selected = resolve_report(
        report_dir=tmp_path,
        prefix="patchops_",
        recovery_latest=True,
        min_stable_age_seconds=0,
        now=base + 100,
    )
    assert selected.ok is True
    assert selected.selection_reason == "latest_report_recovery_fallback"
    assert selected.selected_report_path == str(new.resolve())
    assert selected.candidate_count == 2


def test_parse_report_path_from_patchops_output(tmp_path: Path) -> None:
    report = _write_report(tmp_path / "patchops_report.txt")
    text = f"""
PATCHOPS RUN SUMMARY
--------------------
Report Path        : {report}
ExitCode           : 0
Result             : PASS
"""
    assert parse_report_path_from_text(text) == str(report)

    result = resolve_report(report_output_text=text, min_stable_age_seconds=0)
    assert result.ok is True
    assert result.selection_reason == "parsed_report_path_from_output"
    assert result.selected_report_path == str(report.resolve())


def test_resolve_report_script_writes_evidence_without_upload_or_send(tmp_path: Path) -> None:
    report = _write_report(tmp_path / "patchops_exact.txt")
    config = tmp_path / "target.json"
    evidence_dir = tmp_path / "evidence"
    write_target_config(config, target_url=TARGET_URL, source_patch="test_u2_01")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_uploader_resolve_report.py",
            "--report-path",
            str(report),
            "--config-path",
            str(config),
            "--evidence-dir",
            str(evidence_dir),
            "--min-stable-age-seconds",
            "0",
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["result"] == "PASS_REPORT_RESOLVED_NO_UPLOAD_NO_SEND"
    assert payload["selected_report_path"] == str(report.resolve())

    evidence_payload = json.loads(Path(payload["json"]).read_text(encoding="utf-8"))
    assert evidence_payload["safety_flags"]["selenium_used"] is False
    assert evidence_payload["safety_flags"]["webdriver_used"] is False
    assert evidence_payload["safety_flags"]["browser_dom_automation_used"] is False
    assert evidence_payload["safety_flags"]["file_upload_attempted"] is False
    assert evidence_payload["safety_flags"]["chatgpt_submit_performed"] is False
    assert evidence_payload["details"]["selected_report_sha256"] == sha256_file(report)


def test_u2_01_scripts_do_not_import_selenium_or_webdriver() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "report_resolver.py",
        PROJECT_ROOT / "scripts" / "run_uploader_resolve_report.py",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        assert "import selenium" not in text
        assert "from selenium" not in text
        assert "webdriver.edge" not in text
        assert "webdriver.chrome" not in text