from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import render_command_output_section
from patchops.reporting.sections import full_output_section



def _result(name: str, stdout: str, stderr: str) -> CommandResult:
    return CommandResult(
        name=name,
        program="python",
        args=["-c", "pass"],
        working_directory=Path("."),
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        display_command="python -c pass",
        phase="validation",
    )



def test_render_command_output_section_renders_named_stdout_and_stderr_blocks() -> None:
    rendered = render_command_output_section(
        "FULL OUTPUT",
        [_result("alpha", "hello\n", "warn\n")],
        lambda title: f"\n{title}\n{'-' * len(title)}",
    )

    assert "FULL OUTPUT" in rendered
    assert "[alpha][stdout]" in rendered
    assert "hello" in rendered
    assert "[alpha][stderr]" in rendered
    assert "warn" in rendered



def test_render_command_output_section_renders_none_when_no_results() -> None:
    rendered = render_command_output_section(
        "AUDIT OUTPUT",
        [],
        lambda title: f"\n{title}\n{'-' * len(title)}",
    )

    assert "AUDIT OUTPUT" in rendered
    assert "(none)" in rendered



def test_full_output_section_uses_helper_shape_for_additional_workflow_path() -> None:
    rendered = full_output_section([_result("beta", "", "")], "SMOKE OUTPUT")

    assert "SMOKE OUTPUT" in rendered
    assert "[beta][stdout]" in rendered
    assert "[beta][stderr]" in rendered



def test_full_output_section_renders_none_for_empty_results() -> None:
    rendered = full_output_section([], "ARCHIVE OUTPUT")

    assert "ARCHIVE OUTPUT" in rendered
    assert "(none)" in rendered
