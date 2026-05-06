from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.pasteback_builder import (
    PastebackBuildOptions,
    build_pasteback,
    write_pasteback_outputs,
)
from patchops.chatgpt_uploader.report_parser import parse_report_text


PASS_REPORT = """PATCHOPS RUN-PACKAGE OUTER REPORT
---------------------------------
Result              : PASS
Exit Code           : 0
ExitCode            : 0
Failure Category    :
FailureCategory     :
Outer Report Path   : C:\\Users\\kostas\\Desktop\\u0_04b.txt

STDOUT
------
PATCHOPS RUN SUMMARY
--------------------
Mode               : apply
Patch Name         : u0_04b_chatgpt_uploader_report_parser_script_path_repair
ExitCode           : 0
Result             : PASS
"""


FAIL_REPORT = """PATCHOPS RUN-PACKAGE OUTER REPORT
---------------------------------
Result              : FAIL
Exit Code           : 1
Failure Category    : target_content_failure
Outer Report Path   : C:\\Users\\kostas\\Desktop\\u0_04a.txt

STDOUT
------
PATCHOPS RUN SUMMARY
--------------------
Patch Name         : u0_04a_chatgpt_uploader_report_parser_metadata_repair
ExitCode           : 1
Result             : FAIL

COMMAND : pytest_u0_04a_report_parser
ExitCode : 1

STDERR
------
E   AssertionError: expected READY but got BLOCKED
"""


def test_build_pass_pasteback_has_required_markers_and_fields() -> None:
    parsed = parse_report_text(PASS_REPORT)
    message = build_pasteback(parsed)

    assert message.ok is True
    assert message.status == "PASS"
    assert message.text.startswith("PATCHOPS_LLM_PASTEBACK\n")
    assert message.text.endswith("END_PATCHOPS_LLM_PASTEBACK\n")
    assert "Status: PASS" in message.text
    assert "Result: PASS" in message.text
    assert "ExitCode: 0" in message.text
    assert "PatchName: u0_04b_chatgpt_uploader_report_parser_script_path_repair" in message.text
    assert "chatgpt_submit_performed: false" in message.text
    assert "file_upload_attempted: false" in message.text


def test_build_failure_pasteback_reports_failure_layer_and_next_action() -> None:
    parsed = parse_report_text(FAIL_REPORT)
    message = build_pasteback(parsed)

    assert message.ok is False
    assert message.status == "FAIL"
    assert "FailureLayer: target_validation" in message.text
    assert "FirstFailingCommand: pytest_u0_04a_report_parser" in message.text
    assert "Type: AssertionError" in message.text
    assert "Repair the failing target content or test" in message.text


def test_pasteback_payload_is_json_safe() -> None:
    message = build_pasteback(parse_report_text(FAIL_REPORT))
    payload = message.to_payload()

    encoded = json.dumps(payload, sort_keys=True)
    assert "PATCHOPS_LLM_PASTEBACK" in encoded
    assert payload["status"] == "FAIL"
    assert payload["payload"]["safety"]["selenium_used"] == "false"


def test_builder_truncates_long_error_message() -> None:
    long_report = FAIL_REPORT + "\nValueError: " + ("x" * 1000) + "\n"
    message = build_pasteback(
        parse_report_text(long_report),
        options=PastebackBuildOptions(max_field_chars=80, max_total_chars=1200),
    )

    assert len(message.text) <= 1200
    assert message.text.endswith("END_PATCHOPS_LLM_PASTEBACK\n")


def test_write_outputs_creates_text_and_json(tmp_path: Path) -> None:
    message = build_pasteback(parse_report_text(PASS_REPORT))
    outputs = write_pasteback_outputs(message, tmp_path)

    text_path = Path(outputs["text_path"])
    json_path = Path(outputs["json_path"])
    assert text_path.exists()
    assert json_path.exists()
    assert text_path.read_text(encoding="utf-8") == message.text
    assert json.loads(json_path.read_text(encoding="utf-8"))["status"] == "PASS"


def test_smoke_script_runs_by_path_from_repo_root(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = tmp_path / "report.txt"
    report.write_text(PASS_REPORT, encoding="utf-8")
    script = repo_root / "scripts" / "run_u0_05_chatgpt_uploader_pasteback_builder.py"
    output_dir = tmp_path / "script_smoke"

    completed = subprocess.run(
        [sys.executable, str(script), "--report", str(report), "--output-dir", str(output_dir), "--json"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "PASS"
    assert payload["ok"] is True
    assert Path(payload["outputs"]["text_path"]).exists()
