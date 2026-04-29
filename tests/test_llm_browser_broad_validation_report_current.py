from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.llm_browser import commands
from patchops.llm_browser.broad_validation_report import (
    parse_broad_validation_report_file,
    parse_broad_validation_report_text,
    render_broad_validation_report_summary,
)


SAMPLE_PASS_REPORT = """
========================================================================================================================
PATCHOPS LLM-BROWSER BROAD VALIDATION
========================================================================================================================
Started    : 2026-04-29T23:10:00
RepoRoot   : C:\\dev\\patchops
ReportPath : C:\\Users\\kostas\\Desktop\\patchops_reports\\patchops_llm_browser_broad_validation_20260429_231000.txt
ReportFolder : C:\\Users\\kostas\\Desktop\\patchops_reports
PointerPath  : C:\\Users\\kostas\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt

========================================================================================================================
COMMAND: git status
========================================================================================================================
CWD       : C:\\dev\\patchops
Command   : git status --short --branch
Timeout   : 120s
TimedOut  : False
ExitCode  : 0
--- STDOUT ---
## main...origin/main

--- STDERR ---


========================================================================================================================
COMMAND: full pytest
========================================================================================================================
CWD       : C:\\dev\\patchops
Command   : C:\\dev\\patchops\\.venv\\Scripts\\python.exe -m pytest -q
Timeout   : 1800s
TimedOut  : False
ExitCode  : 0
--- STDOUT ---
10 passed

--- STDERR ---


========================================================================================================================
SUMMARY
========================================================================================================================
Result     : PASS
ExitCode   : 0
Mode       : EXECUTED

Commands captured : 2
ReportPath        : C:\\Users\\kostas\\Desktop\\patchops_reports\\patchops_llm_browser_broad_validation_20260429_231000.txt
ReportFolder      : C:\\Users\\kostas\\Desktop\\patchops_reports
PointerPath       : C:\\Users\\kostas\\Desktop\\patchops_latest_llm_browser_broad_validation_report.txt
""".strip()


SAMPLE_FAIL_REPORT = SAMPLE_PASS_REPORT.replace("Result     : PASS", "Result     : FAIL").replace(
    "ExitCode   : 0\nMode       : EXECUTED",
    "ExitCode   : 1\nMode       : EXECUTED\n\nFailures:\n- full pytest: exit code 1",
).replace("ExitCode  : 0\n--- STDOUT ---\n10 passed", "ExitCode  : 1\n--- STDOUT ---\n1 failed")


def test_parse_broad_validation_report_text_pass() -> None:
    report = parse_broad_validation_report_text(SAMPLE_PASS_REPORT)

    assert report.ok is True
    assert report.result == "PASS"
    assert report.exit_code == "0"
    assert report.mode == "EXECUTED"
    assert report.command_count_reported == 2
    assert len(report.commands) == 2
    assert report.commands[0].label == "git status"
    assert report.commands[0].ok is True
    assert report.commands[1].label == "full pytest"
    assert report.failed_commands == ()
    assert report.timed_out_commands == ()


def test_parse_broad_validation_report_text_fail() -> None:
    report = parse_broad_validation_report_text(SAMPLE_FAIL_REPORT)

    assert report.ok is False
    assert report.result == "FAIL"
    assert report.exit_code == "1"
    assert report.failures == ("full pytest: exit code 1",)
    assert len(report.failed_commands) == 1
    assert report.failed_commands[0].label == "full pytest"


def test_parse_broad_validation_report_file_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "report.txt"
    path.write_text(SAMPLE_PASS_REPORT, encoding="utf-8")

    report = parse_broad_validation_report_file(path)

    assert report.path == path
    assert report.ok is True
    assert report.to_payload()["command_count_parsed"] == 2


def test_render_broad_validation_report_summary() -> None:
    report = parse_broad_validation_report_text(SAMPLE_FAIL_REPORT)
    text = render_broad_validation_report_summary(report)

    assert "Broad validation report summary" in text
    assert "Result     : FAIL" in text
    assert "Failed     : 1" in text
    assert "full pytest: exit=1" in text


def test_broad_report_cli_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "report.txt"
    path.write_text(SAMPLE_PASS_REPORT, encoding="utf-8")

    code = commands.main(["broad-report", "--path", str(path), "--json"])

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["result"] == "PASS"
    assert payload["command_count_parsed"] == 2


def test_broad_report_cli_strict_returns_nonzero_for_failed_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "report.txt"
    path.write_text(SAMPLE_FAIL_REPORT, encoding="utf-8")

    code = commands.main(["broad-report", "--path", str(path), "--json", "--strict"])

    payload = json.loads(capsys.readouterr().out)

    assert code == 1
    assert payload["ok"] is False
    assert payload["failed_command_count"] == 1


def test_broad_report_help_has_no_live_or_send_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["broad-report", "--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "broad-report" in out
    assert "--path" in out
    assert "--json" in out
    assert "--strict" in out
    assert "--auto-send" not in out
    assert "--allow-send" not in out
    assert "--live" not in out


def test_llm_browser_help_includes_broad_report(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "broad-report" in out
    assert "checkpoint" in out
    assert "release-gate" in out
