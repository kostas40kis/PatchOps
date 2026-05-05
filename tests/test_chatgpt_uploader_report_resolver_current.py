from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from patchops.chatgpt_uploader.report_resolver import (
    resolve_report,
    render_text_summary,
    write_resolver_outputs,
)


def test_resolve_explicit_report_path_records_byte_exact_metadata(tmp_path: Path) -> None:
    report = tmp_path / "patchops_report.txt"
    data = b"PATCHOPS RUN SUMMARY\nResult             : PASS\n"
    report.write_bytes(data)

    result = resolve_report(report_path=report)

    assert result.result == "PASS"
    assert result.resolver_mode == "explicit_path"
    assert result.report_path_provided is True
    assert result.report_dir_provided is False
    assert result.report_exists is True
    assert result.report_is_file is True
    assert result.report_size_bytes == len(data)
    assert result.report_sha256 == hashlib.sha256(data).hexdigest()
    assert result.report_name == "patchops_report.txt"
    assert result.failure_layer == ""
    assert result.error == ""
    assert result.webdriver_used is False
    assert result.selenium_used is False
    assert result.file_upload_attempted is False
    assert result.chatgpt_submit_performed is False


def test_resolve_latest_report_in_dir_uses_mtime_and_prefix(tmp_path: Path) -> None:
    older = tmp_path / "u0_03_report_older.txt"
    newer = tmp_path / "u0_03_report_newer.txt"
    ignored = tmp_path / "other_report.txt"
    older.write_text("older", encoding="utf-8")
    ignored.write_text("ignored", encoding="utf-8")
    time.sleep(0.02)
    newer.write_text("newer", encoding="utf-8")

    result = resolve_report(report_dir=tmp_path, prefix="u0_03_report_")

    assert result.result == "PASS"
    assert result.resolver_mode == "latest_in_dir"
    assert result.latest_selected is True
    assert result.report_name == "u0_03_report_newer.txt"
    assert result.candidate_count == 2
    assert result.candidate_names == ("u0_03_report_newer.txt", "u0_03_report_older.txt")


def test_missing_explicit_report_path_is_blocked_not_exception(tmp_path: Path) -> None:
    result = resolve_report(report_path=tmp_path / "missing.txt")

    assert result.result == "BLOCKED"
    assert result.resolver_mode == "explicit_path"
    assert result.report_exists is False
    assert result.failure_layer == "report_resolver"
    assert "does not exist" in result.error
    assert result.file_upload_attempted is False
    assert result.chatgpt_submit_performed is False


def test_directory_used_as_report_path_is_blocked(tmp_path: Path) -> None:
    result = resolve_report(report_path=tmp_path)

    assert result.result == "BLOCKED"
    assert result.report_exists is True
    assert result.report_is_file is False
    assert result.report_name == tmp_path.name
    assert "not a file" in result.error


def test_write_resolver_outputs_writes_json_and_text(tmp_path: Path) -> None:
    report = tmp_path / "canonical.txt"
    report.write_text("PATCHOPS RUN SUMMARY\nExitCode           : 0\nResult             : PASS\n", encoding="utf-8")
    result = resolve_report(report_path=report)
    outputs = write_resolver_outputs(result, tmp_path / "out")

    json_path = Path(outputs["json_path"])
    txt_path = Path(outputs["txt_path"])
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    summary = txt_path.read_text(encoding="utf-8")

    assert payload["result"] == "PASS"
    assert payload["report_name"] == "canonical.txt"
    assert "PATCHOPS CHATGPT UPLOADER REPORT RESOLVER" in summary
    assert "file_upload_attempted     : false" in summary
    assert "chatgpt_submit_performed  : false" in summary


def test_no_input_is_blocked_with_safety_flags_false() -> None:
    result = resolve_report()
    summary = render_text_summary(result)

    assert result.result == "BLOCKED"
    assert result.resolver_mode == "none"
    assert result.webdriver_used is False
    assert result.selenium_used is False
    assert result.browser_dom_automation_used is False
    assert "No report path or report directory" in result.error
    assert "selenium_used             : false" in summary
