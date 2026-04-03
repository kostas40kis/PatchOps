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


def find_baseline_file(wrapper_root: Path, relative_path: str) -> Path:
    patch_backups_root = wrapper_root / "data" / "runtime" / "patch_backups"
    preferred_prefixes = [
        "mp15a_report_helper_additional_workflow_path_repair_",
        "mp14a_required_vs_tolerated_contract_repair_",
    ]
    candidates: list[Path] = []

    if patch_backups_root.exists():
        for child in sorted(patch_backups_root.iterdir()):
            if not child.is_dir():
                continue
            for prefix in preferred_prefixes:
                if child.name.startswith(prefix):
                    candidate = child / Path(relative_path)
                    if candidate.exists():
                        return candidate
            candidate = child / Path(relative_path)
            if candidate.exists():
                candidates.append(candidate)

    if candidates:
        return sorted(candidates)[-1]

    raise RuntimeError(f"Could not find baseline backup for {relative_path}.")


def ensure_import(text: str, import_line: str) -> str:
    if import_line in text:
        return text
    lines = text.splitlines()
    insert_at = 0
    for index, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = index + 1
    lines.insert(insert_at, import_line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def replace_function(text: str, function_name: str, replacement: str) -> str:
    pattern = re.compile(
        rf"^def {re.escape(function_name)}\([^\n]*\):\n(?:^[ \t].*\n|^\n)*",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"Could not locate function {function_name}.")
    return text[:match.start()] + replacement + text[match.end():]


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15k.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    sections_rel = "patchops/reporting/sections.py"
    command_sections_rel = "patchops/reporting/command_sections.py"
    test_rel = "tests/test_reporting_output_helper_current.py"

    sections_baseline = find_baseline_file(wrapper_root, sections_rel)
    command_sections_baseline = find_baseline_file(wrapper_root, command_sections_rel)

    sections_text = read_text(sections_baseline)
    command_sections_text = read_text(command_sections_baseline)

    command_sections_text = ensure_import(command_sections_text, "from dataclasses import dataclass")
    command_sections_text = ensure_import(command_sections_text, "from typing import Callable")
    command_sections_text = ensure_import(command_sections_text, "from patchops.models import CommandResult")

    helper_markers = [
        "\n@dataclass\nclass ReportCommandOutputSection:",
        "\ndef build_report_command_section(",
        "\ndef render_command_output_section(",
        "\ndef render_report_command_output_section(",
    ]
    starts = [command_sections_text.find(marker) for marker in helper_markers if command_sections_text.find(marker) != -1]
    if starts:
        command_sections_text = command_sections_text[: min(starts)].rstrip() + "\n\n"

    helper_block = '''
@dataclass
class ReportCommandOutputSection:
    title: str
    results: list[CommandResult]
    rule: Callable[[str], str]

    @property
    def command_name(self) -> str:
        if self.results:
            return str(self.results[0].name)
        return "(none)"


def _report_command_display(result: CommandResult) -> str:
    display = getattr(result, "display_command", None)
    if display:
        return str(display)
    program = str(getattr(result, "program", ""))
    args = [str(item) for item in (getattr(result, "args", None) or [])]
    return " ".join([program, *args]).strip()


def build_report_command_section(result: CommandResult) -> tuple[str, ...]:
    return (
        f"NAME    : {result.name}",
        f"COMMAND : {_report_command_display(result)}",
        f"CWD     : {result.working_directory}",
        f"EXIT    : {result.exit_code}",
    )


def render_command_output_section(title: str, results: list[CommandResult], rule: Callable[[str], str]) -> str:
    lines: list[str] = [rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)

    for result in results:
        lines.append(f"[{result.name}][stdout]")
        stdout = str(getattr(result, "stdout", "") or "").rstrip("\\n")
        lines.append(stdout)
        lines.append("")
        lines.append(f"[{result.name}][stderr]")
        stderr = str(getattr(result, "stderr", "") or "").rstrip("\\n")
        lines.append(stderr)
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()
    return "\\n".join(lines)


def render_report_command_output_section(*args):
    if len(args) == 1:
        section = args[0]
        return render_command_output_section(section.title, list(section.results), section.rule)
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(str(title), list(results), rule)
    raise TypeError("render_report_command_output_section expects either 1 section object or 3 legacy arguments.")
'''.strip()

    command_sections_text = command_sections_text.rstrip() + "\n\n" + helper_block + "\n"

    sections_text = ensure_import(
        sections_text,
        "from patchops.reporting.command_sections import ReportCommandOutputSection, build_report_command_section, render_report_command_output_section",
    )

    if "def command_group_section(" not in sections_text:
        sections_text = sections_text.rstrip() + '''

def command_group_section(title: str, results: list[CommandResult]) -> str:
    lines = [title, "-" * len(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        lines.extend(build_report_command_section(result))
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return "\\n".join(lines)
'''

    full_output_replacement = '''
def full_output_section(results: list[CommandResult], title: str) -> str:
    section = ReportCommandOutputSection(title=title, results=results, rule=_rule)
    rendered = render_report_command_output_section(section)
    if rendered is None:
        return ""
    if isinstance(rendered, tuple):
        return "\\n".join(str(part) for part in rendered)
    return str(rendered)
'''.lstrip()
    sections_text = replace_function(sections_text, "full_output_section", full_output_replacement)

    test_text = '''from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    render_command_output_section,
    render_report_command_output_section,
)


def _result(name: str, stdout: str, stderr: str) -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest", "-q", "tests/test_reporting.py"],
        working_directory=Path("."),
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        display_command="py -m pytest -q tests/test_reporting.py",
        phase="validation",
    )


def test_report_output_helper_alias_matches_base_helper() -> None:
    result = _result("alpha", "hello\\n", "warn\\n")
    rule = lambda title: f"\\n{title}\\n{'-' * len(title)}"

    base = render_command_output_section("FULL OUTPUT", [result], rule)
    alias = render_report_command_output_section("FULL OUTPUT", [result], rule)

    assert alias == base
    assert "[alpha][stdout]" in alias
    assert "[alpha][stderr]" in alias


def test_report_output_section_object_exposes_command_name() -> None:
    result = _result("beta", "one\\n", "")
    section = ReportCommandOutputSection(
        title="FULL OUTPUT",
        results=[result],
        rule=lambda title: f"\\n{title}\\n{'-' * len(title)}",
    )

    assert section.command_name == "beta"
    rendered = render_report_command_output_section(section)
    assert "[beta][stdout]" in rendered
    assert "[beta][stderr]" in rendered
'''
    write_text(working_root / "content" / "patchops" / "reporting" / "sections.py", sections_text)
    write_text(working_root / "content" / "patchops" / "reporting" / "command_sections.py", command_sections_text)
    write_text(working_root / "content" / "tests" / "test_reporting_output_helper_current.py", test_text)

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
        "patch_name": "mp15k_report_helper_baseline_restore_and_minimal_path",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root),
        "backup_files": [sections_rel.replace("/", "\\\\"), command_sections_rel.replace("/", "\\\\"), test_rel.replace("/", "\\\\")],
        "files_to_write": [
            {"path": sections_rel.replace("/", "\\\\"), "content_path": "content/patchops/reporting/sections.py", "encoding": "utf-8"},
            {"path": command_sections_rel.replace("/", "\\\\"), "content_path": "content/patchops/reporting/command_sections.py", "encoding": "utf-8"},
            {"path": test_rel.replace("/", "\\\\"), "content_path": "content/tests/test_reporting_output_helper_current.py", "encoding": "utf-8"},
        ],
        "validation_commands": [{"name": "report_helper_minimal_pytest", "program": "python", "args": ["-m", "pytest", "-q", *validation_targets], "working_directory": ".", "use_profile_runtime": False, "allowed_exit_codes": [0]}],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {"report_dir": str((working_root / "inner_reports")), "report_name_prefix": "mp15k_report_helper_baseline_restore_and_minimal_path", "write_to_desktop": False},
        "tags": ["maintenance", "pythonization", "mp15", "report_helper", "baseline_restore"],
        "notes": "Restore baseline reporting surfaces from backup, then apply the narrow MP15 helper path with preserved exports and dual helper call compatibility.",
    }
    write_text(working_root / "patch_manifest.json", json.dumps(manifest, indent=2) + "\n")

    prepare_lines = [
        "decision=mp15k_report_helper_baseline_restore_and_minimal_path",
        f"sections_baseline={sections_baseline}",
        f"command_sections_baseline={command_sections_baseline}",
        f"manifest_path={working_root / 'patch_manifest.json'}",
        "rationale=Restore a known-good reporting baseline first, then apply the smallest helper change that preserves renderer imports and both helper call shapes.",
        "validation_targets=" + ";".join(validation_targets),
    ]
    write_text(working_root / "prepare_result.txt", "\n".join(prepare_lines) + "\n")
    print(str(working_root / "patch_manifest.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())