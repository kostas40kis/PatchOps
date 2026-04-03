from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_function_block(source: str, function_name: str, replacement: str) -> str:
    pattern = re.compile(rf"(?ms)^def {re.escape(function_name)}\(.*?(?=^def\s+|\Z)")
    updated, count = pattern.subn(replacement.strip() + "\n\n", source, count=1)
    if count != 1:
        raise RuntimeError(f"Could not replace function block for {function_name}.")
    return updated


def ensure_import(source: str) -> str:
    import_line = "from patchops.reporting.command_sections import ReportCommandOutputSection, render_report_command_output_section\n"
    if import_line in source:
        return source
    anchor = "from patchops.workflows.wrapper_retry import (\n"
    idx = source.find(anchor)
    if idx == -1:
        raise RuntimeError("Could not find import anchor in sections.py.")
    end = source.find(")\n", idx)
    if end == -1:
        raise RuntimeError("Could not find wrapper_retry import end in sections.py.")
    end += 2
    return source[:end] + import_line + source[end:]


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15e.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    sections_path = wrapper_root / "patchops" / "reporting" / "sections.py"
    command_sections_path = wrapper_root / "patchops" / "reporting" / "command_sections.py"

    sections_text = read_text(sections_path)

    command_sections_text = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from patchops.models import CommandResult


RuleFunc = Callable[[str], str]


@dataclass(frozen=True)
class ReportCommandOutputSection:
    title: str
    results: Sequence[CommandResult]
    rule: RuleFunc

    @property
    def command_name(self) -> str:
        if self.results:
            return str(self.results[0].name)
        return "(none)"


def _normalize_output_text(value: str) -> list[str]:
    if not value:
        return [""]
    trimmed = value.rstrip("\\n")
    if not trimmed:
        return [""]
    return trimmed.splitlines()


def _body_lines(results: Sequence[CommandResult]) -> list[str]:
    if not results:
        return ["(none)"]

    lines: list[str] = []
    for result in results:
        lines.append(f"[{result.name}][stdout]")
        lines.extend(_normalize_output_text(result.stdout))
        lines.append(f"[{result.name}][stderr]")
        lines.extend(_normalize_output_text(result.stderr))
    return lines


def _header_lines(title: str, rule: RuleFunc) -> list[str]:
    rendered = str(rule(title))
    rendered = rendered.lstrip("\\n")
    if not rendered:
        return [title, "-" * len(title)]
    return rendered.splitlines()


def render_command_output_section(title: str, results: Sequence[CommandResult], rule: RuleFunc) -> str:
    return "\\n".join([*_header_lines(title, rule), *_body_lines(results)])


def render_report_command_output_section(*args):
    if len(args) == 1:
        section = args[0]
        if not isinstance(section, ReportCommandOutputSection):
            raise TypeError("Single-argument report output rendering requires ReportCommandOutputSection.")
        return tuple(_body_lines(section.results))

    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(str(title), results, rule)

    raise TypeError("render_report_command_output_section() expects either (section) or (title, results, rule).")
'''

    full_output_replacement = '''def full_output_section(results: list[CommandResult], title: str) -> str:
    section = ReportCommandOutputSection(title=title, results=results, rule=_rule)
    rendered = render_report_command_output_section(section)
    if isinstance(rendered, str):
        return rendered
    if isinstance(rendered, Iterable) and not isinstance(rendered, (str, bytes)):
        header = str(_rule(title)).lstrip("\\n")
        body = "\\n".join(str(item) for item in rendered)
        if body:
            return "\\n".join([header, body])
        return header
    return str(rendered)'''

    updated_sections = ensure_import(sections_text)
    updated_sections = replace_function_block(updated_sections, "full_output_section", full_output_replacement)

    content_sections_path = working_root / "content" / "patchops" / "reporting" / "sections.py"
    content_command_sections_path = working_root / "content" / "patchops" / "reporting" / "command_sections.py"

    write_text(content_sections_path, updated_sections)
    write_text(content_command_sections_path, command_sections_text)

    validation_targets = [
        "tests/test_reporting.py",
        "tests/test_reporting_command_sections_current.py",
        "tests/test_reporting_output_helper_current.py",
        "tests/test_summary_integrity_current.py",
        "tests/test_summary_derivation_lock_current.py",
        "tests/test_required_vs_tolerated_report_current.py",
        "tests/test_summary_integrity_workflow_current.py",
    ]

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp15e_report_helper_class_alias_repair",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace("\\\\", "/"),
        "backup_files": [
            "patchops/reporting/sections.py",
            "patchops/reporting/command_sections.py",
        ],
        "files_to_write": [
            {
                "path": "patchops/reporting/sections.py",
                "content_path": "content/patchops/reporting/sections.py",
                "encoding": "utf-8",
            },
            {
                "path": "patchops/reporting/command_sections.py",
                "content_path": "content/patchops/reporting/command_sections.py",
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "report_helper_class_alias_pytest",
                "program": "python",
                "args": ["-m", "pytest", "-q", *validation_targets],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str((working_root / "inner_reports")).replace("\\\\", "/"),
            "report_name_prefix": "mp15e_report_helper_class_alias_repair",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper", "class_alias_repair"],
        "notes": "Narrow MP15 repair. Restore a real ReportCommandOutputSection class and a dual-shape report helper that preserves the reporting.sections monkeypatch contract.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\\n")

    prepare_lines = [
        "decision=mp15e_report_helper_class_alias_repair",
        f"sections_path={sections_path}",
        f"command_sections_path={command_sections_path}",
        f"manifest_path={manifest_path}",
        "rationale=Repair MP15 by restoring a real ReportCommandOutputSection class and supporting both helper call shapes without alias confusion.",
        "validation_targets=" + ";".join(validation_targets),
    ]
    write_text(working_root / "prepare_result.txt", "\\n".join(prepare_lines) + "\\n")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())