from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    build_report_command_section,
    render_report_command_output_section,
)
from patchops.reporting.sections import command_group_section, full_output_section


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDITED_TESTS = [
    PROJECT_ROOT / "tests" / "test_reporting_output_helper_current.py",
    PROJECT_ROOT / "tests" / "test_reporting_command_sections_current.py",
    PROJECT_ROOT / "tests" / "test_report_path_current.py",
]


def _result(*, working_directory: Path, stdout: str, stderr: str) -> CommandResult:
    return CommandResult(
        name="path_audit",
        program="py",
        args=["-m", "pytest", "-q", "tests/test_reporting.py"],
        working_directory=working_directory,
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        display_command=f'py -m pytest -q tests/test_reporting.py --report-path "{working_directory / "rendered_report.txt"}"',
        phase="validation",
    )


def test_rendered_output_labels_ignore_report_word_in_environment_specific_paths() -> None:
    working_directory = Path("C:/tmp/test_report_line_case")
    result = _result(
        working_directory=working_directory,
        stdout=str(working_directory / "stdout_report_capture.txt"),
        stderr=str(working_directory / "stderr_report_capture.txt"),
    )

    section = build_report_command_section(result, section_label="FULL OUTPUT")
    rendered = render_report_command_output_section(section)

    assert rendered[0] == "[path_audit][stdout]"
    assert rendered[2] == "[path_audit][stderr]"
    assert "test_report_line_case" not in rendered[0]
    assert "test_report_line_case" not in rendered[2]
    assert "test_report_line_case" in rendered[1]
    assert "test_report_line_case" in rendered[3]


def test_command_group_section_preserves_semantic_contract_with_report_named_paths() -> None:
    working_directory = Path("C:/tmp/test_report_line_case")
    result = _result(
        working_directory=working_directory,
        stdout="captured stdout",
        stderr="captured stderr",
    )

    text = command_group_section("VALIDATION COMMANDS", [result])

    assert "VALIDATION COMMANDS" in text
    assert "NAME    : path_audit" in text
    assert f"COMMAND : {result.display_command}" in text
    assert f"CWD     : {working_directory}" in text
    assert "EXIT    : 0" in text


def test_full_output_section_keeps_labels_stable_when_output_contains_report_word() -> None:
    working_directory = Path("C:/tmp/test_report_line_case")
    result = _result(
        working_directory=working_directory,
        stdout=str(working_directory / "nested_report_stdout.txt"),
        stderr=str(working_directory / "nested_report_stderr.txt"),
    )

    text = full_output_section([result], "FULL OUTPUT")

    assert text.startswith("FULL OUTPUT")
    assert "[path_audit][stdout]" in text
    assert "[path_audit][stderr]" in text
    assert "nested_report_stdout.txt" in text
    assert "nested_report_stderr.txt" in text


def test_current_reporting_tests_avoid_known_negative_report_word_assertions() -> None:
    forbidden_fragments = [
        'assert "report" not in',
        "assert 'report' not in",
    ]

    for path in AUDITED_TESTS:
        assert path.exists(), f"expected audited test file missing: {path}"
        lowered = path.read_text(encoding="utf-8").lower()
        for fragment in forbidden_fragments:
            assert fragment not in lowered, f"{path.name} still contains brittle path-dependent assertion fragment: {fragment}"
