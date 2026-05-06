from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.report_parser import (
    parse_report_file,
    parse_report_text,
    render_text_summary,
    main as parser_main,
)


PASS_REPORT = """PATCHOPS RUN-PACKAGE OUTER REPORT
---------------------------------
Result              : PASS
Exit Code           : 0
ExitCode            : 0
Failure Category    :
FailureCategory     :
Outer Report Path   : C:\\Users\\kostas\\Desktop\\example.txt

STDOUT
------
PATCHOPS RUN SUMMARY
--------------------
Mode               : apply
Patch Name         : u0_03a_chatgpt_uploader_report_resolver_manifest_repair
ExitCode           : 0
Result             : PASS
"""


FAIL_MANIFEST_REPORT = """PATCHOPS RUN-PACKAGE OUTER REPORT
---------------------------------
Result              : FAIL
Exit Code           : 1
Failure Category    : wrapper_failure
Outer Report Path   : C:\\Users\\kostas\\Desktop\\patchops_run_package_20260505_155329.txt

STDERR
------
Traceback (most recent call last):
  File "C:\\dev\\patchops\\patchops\\cli.py", line 1540, in <module>
    raise SystemExit(main())
patchops.exceptions.ManifestError: Manifest field 'writes' is not recognized by this manifest loader; use 'files_to_write'.
"""


PYTEST_FAIL_REPORT = """PATCHOPS RUN SUMMARY
--------------------
Patch Name         : sample_patch
ExitCode           : 1
Result             : FAIL

COMMAND : pytest_sample
ExitCode : 1

STDERR
------
E   AssertionError: expected READY but got BLOCKED
"""


def test_parse_pass_report_extracts_result_exit_and_patch_name() -> None:
    parsed = parse_report_text(PASS_REPORT)

    assert parsed.ok is True
    assert parsed.result == "PASS"
    assert parsed.exit_code == 0
    assert parsed.patch_name == "u0_03a_chatgpt_uploader_report_resolver_manifest_repair"
    assert parsed.failure_layer == "none"


def test_parse_manifest_error_classifies_manifest_validation_and_error() -> None:
    parsed = parse_report_text(FAIL_MANIFEST_REPORT)

    assert parsed.ok is False
    assert parsed.result == "FAIL"
    assert parsed.exit_code == 1
    assert parsed.failure_category == "wrapper_failure"
    assert parsed.failure_layer == "manifest_validation"
    assert parsed.primary_error_type == "ManifestError"
    assert "files_to_write" in parsed.primary_error_message
    assert parsed.primary_error_file.endswith("patchops\\cli.py")
    assert parsed.primary_error_line == 1540


def test_parse_failing_command_from_command_section() -> None:
    parsed = parse_report_text(PYTEST_FAIL_REPORT)

    assert parsed.first_failing_command == "pytest_sample"
    assert parsed.failure_layer == "target_validation"
    assert parsed.primary_error_type == "AssertionError"


def test_parse_report_file_uses_path_when_report_path_missing(tmp_path: Path) -> None:
    path = tmp_path / "report.txt"
    path.write_text("Result : PASS\nExitCode : 0\n", encoding="utf-8")

    parsed = parse_report_file(path)

    assert parsed.ok is True
    assert parsed.report_path == str(path)
    assert parsed.source_path == str(path)


def test_json_payload_is_stable() -> None:
    payload = parse_report_text(FAIL_MANIFEST_REPORT).to_payload()

    assert payload["ok"] is False
    assert payload["result"] == "FAIL"
    assert payload["primary_error"]["type"] == "ManifestError"
    assert "warnings" in payload


def test_text_summary_contains_compact_fields() -> None:
    summary = render_text_summary(parse_report_text(PASS_REPORT))

    assert "PATCHOPS REPORT PARSE SUMMARY" in summary
    assert "Result              : PASS" in summary
    assert "FailureLayer        : none" in summary


def test_cli_json_and_strict_modes(tmp_path: Path, capsys) -> None:
    report = tmp_path / "report.txt"
    report.write_text(PASS_REPORT, encoding="utf-8")

    code = parser_main(["--report", str(report), "--json", "--strict"])

    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["ok"] is True
    assert payload["result"] == "PASS"


def test_cli_strict_fails_for_failed_report(tmp_path: Path, capsys) -> None:
    report = tmp_path / "report.txt"
    report.write_text(FAIL_MANIFEST_REPORT, encoding="utf-8")

    code = parser_main(["--report", str(report), "--strict"])

    captured = capsys.readouterr()
    assert code == 1
    assert "Result              : FAIL" in captured.out


def test_smoke_script_runs_by_path_from_repo_root(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_u0_04_chatgpt_uploader_report_parser.py"
    output_dir = tmp_path / "script_smoke"

    completed = subprocess.run(
        [sys.executable, str(script), "--output-dir", str(output_dir)],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["result"] == "PASS"
    assert (output_dir / "u0_04_report_parse_summary.json").exists()
