from __future__ import annotations

import json
import sys
from pathlib import Path


PATCH_NAME = "mp11_command_section_renderer_cleanup"


def write_utf8(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def as_repo_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_mp11.py <repo_root> <work_root>")

    repo_root = Path(sys.argv[1]).resolve()
    work_root = Path(sys.argv[2]).resolve()
    content_root = work_root / "content"
    inner_reports = work_root / "inner_reports"
    inner_reports.mkdir(parents=True, exist_ok=True)

    command_sections_path = repo_root / "patchops" / "reporting" / "command_sections.py"
    sections_path = repo_root / "patchops" / "reporting" / "sections.py"
    tests_path = repo_root / "tests" / "test_reporting_command_sections_current.py"

    required_paths = (command_sections_path, sections_path, tests_path)
    for path in required_paths:
        if not path.exists():
            raise RuntimeError(f"Required repo file missing: {path}")

    command_sections_text = command_sections_path.read_text(encoding="utf-8")
    sections_text = sections_path.read_text(encoding="utf-8")
    tests_text = tests_path.read_text(encoding="utf-8")

    helper_block = """def render_report_command_output_section(
    section: ReportCommandSection,
) -> tuple[str, ...]:
    return (
        f"[{section.command_name}][stdout]",
        section.stdout if section.stdout else "",
        f"[{section.command_name}][stderr]",
        section.stderr if section.stderr else "",
    )
"""

    if "def render_report_command_output_section(" not in command_sections_text:
        command_sections_text = command_sections_text.rstrip() + "


" + helper_block + "
"

    single_import = "from patchops.reporting.command_sections import build_report_command_sections
"
    block_import = """from patchops.reporting.command_sections import (
    build_report_command_sections,
    render_report_command_output_section,
)
"""
    if "render_report_command_output_section" not in sections_text:
        if single_import not in sections_text:
            raise RuntimeError("Could not locate command_sections import in sections.py.")
        sections_text = sections_text.replace(single_import, block_import, 1)

    old_output = """def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    sections = build_report_command_sections(results, section_label=title)
    for section in sections:
        lines.append(f"[{section.command_name}][stdout]")
        lines.append(section.stdout if section.stdout else "")
        lines.append(f"[{section.command_name}][stderr]")
        lines.append(section.stderr if section.stderr else "")
    return "\n".join(lines)
"""
    new_output = """def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    sections = build_report_command_sections(results, section_label=title)
    for section in sections:
        lines.extend(render_report_command_output_section(section))
    return "\n".join(lines)
"""
    if old_output not in sections_text:
        raise RuntimeError("Could not locate MP10 full_output_section block in sections.py.")
    sections_text = sections_text.replace(old_output, new_output, 1)

    old_test_import = """from patchops.reporting.command_sections import (
    build_report_command_section,
    build_report_command_sections,
)
from patchops.reporting.sections import command_group_section, full_output_section
"""
    new_test_import = """from patchops.reporting.command_sections import (
    build_report_command_section,
    build_report_command_sections,
    render_report_command_output_section,
)
import patchops.reporting.sections as reporting_sections
from patchops.reporting.sections import command_group_section, full_output_section
"""
    if "render_report_command_output_section" not in tests_text:
        if old_test_import not in tests_text:
            raise RuntimeError("Could not locate command_sections import block in tests/test_reporting_command_sections_current.py.")
        tests_text = tests_text.replace(old_test_import, new_test_import, 1)

    helper_test_block = """

def test_render_report_command_output_section_preserves_visible_shape():
    result = _command_result(stdout="captured stdout", stderr="captured stderr")

    section = build_report_command_section(result, section_label="FULL OUTPUT")
    lines = render_report_command_output_section(section)

    assert lines == (
        "[reporting_contracts][stdout]",
        "captured stdout",
        "[reporting_contracts][stderr]",
        "captured stderr",
    )


def test_full_output_section_uses_shared_output_renderer(monkeypatch):
    result = _command_result(stdout="captured stdout", stderr="captured stderr")
    seen: list[str] = []

    def fake_renderer(section):
        seen.append(section.command_name)
        return (
            "[patched][stdout]",
            "patched stdout",
            "[patched][stderr]",
            "patched stderr",
        )

    monkeypatch.setattr(reporting_sections, "render_report_command_output_section", fake_renderer)

    text = reporting_sections.full_output_section([result], "FULL OUTPUT")

    assert seen == ["reporting_contracts"]
    assert "[patched][stdout]" in text
    assert "patched stdout" in text
    assert "[patched][stderr]" in text
    assert "patched stderr" in text
"""
    if "def test_render_report_command_output_section_preserves_visible_shape" not in tests_text:
        tests_text = tests_text.rstrip() + "

" + helper_test_block.strip() + "
"

    command_sections_content_path = content_root / "patchops" / "reporting" / "command_sections.py"
    sections_content_path = content_root / "patchops" / "reporting" / "sections.py"
    tests_content_path = content_root / "tests" / "test_reporting_command_sections_current.py"

    write_utf8(command_sections_content_path, command_sections_text)
    write_utf8(sections_content_path, sections_text)
    write_utf8(tests_content_path, tests_text)

    selected_tests = [
        "tests/test_reporting.py",
        "tests/test_reporting_command_sections_current.py",
        "tests/test_summary_integrity_current.py",
    ]
    workflow_summary_test = repo_root / "tests" / "test_summary_integrity_workflow_current.py"
    if workflow_summary_test.exists():
        selected_tests.append("tests/test_summary_integrity_workflow_current.py")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(repo_root).replace("\", "/"),
        "backup_files": [
            "patchops/reporting/command_sections.py",
            "patchops/reporting/sections.py",
            "tests/test_reporting_command_sections_current.py",
        ],
        "files_to_write": [
            {
                "path": "patchops/reporting/command_sections.py",
                "content_path": as_repo_relative(command_sections_content_path, work_root),
                "encoding": "utf-8",
            },
            {
                "path": "patchops/reporting/sections.py",
                "content_path": as_repo_relative(sections_content_path, work_root),
                "encoding": "utf-8",
            },
            {
                "path": "tests/test_reporting_command_sections_current.py",
                "content_path": as_repo_relative(tests_content_path, work_root),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "command_section_renderer_contracts",
                "program": "py",
                "args": ["-m", "pytest", "-q", *selected_tests],
                "working_directory": ".",
            }
        ],
        "report_preferences": {
            "report_name_prefix": "mp11",
            "report_dir": str(inner_reports.resolve()).replace("\", "/"),
        },
        "tags": [
            "self_hosted",
            "pythonization",
            "mp11",
            "command_section_renderer_cleanup",
            "reporting",
        ],
        "notes": "MP11: render the current full command output section from the shared command-section renderer helper without changing visible report shape.",
    }

    manifest_path = work_root / "patch_manifest.json"
    write_utf8(manifest_path, json.dumps(manifest, indent=2) + "
")

    print(f"INFO: staged_command_sections={command_sections_content_path}")
    print(f"INFO: staged_sections={sections_content_path}")
    print(f"INFO: staged_tests={tests_content_path}")
    print(f"INFO: selected_tests={selected_tests}")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
