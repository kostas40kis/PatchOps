from __future__ import annotations

import json
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_function(text: str, function_name: str, replacement: str) -> str:
    marker = f"def {function_name}("
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Could not find function {function_name}.")

    next_candidates: list[int] = []
    for token in ("\ndef ", "\nclass "):
        idx = text.find(token, start + 1)
        if idx >= 0:
            next_candidates.append(idx + 1)

    end = min(next_candidates) if next_candidates else len(text)
    return text[:start] + replacement.rstrip() + "\n\n" + text[end:].lstrip("\n")


def insert_import_after_last_import(text: str, import_line: str) -> str:
    if import_line in text:
        return text

    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15c.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    command_sections_path = wrapper_root / "patchops" / "reporting" / "command_sections.py"
    sections_path = wrapper_root / "patchops" / "reporting" / "sections.py"

    command_sections_text = read_text(command_sections_path)
    sections_text = read_text(sections_path)

    if "def render_command_output_section(" not in command_sections_text:
        raise RuntimeError("Expected render_command_output_section in command_sections.py.")

    if "class ReportCommandOutputSection" not in command_sections_text:
        raise RuntimeError("Expected ReportCommandOutputSection in command_sections.py.")

    command_sections_replacement = """
def render_report_command_output_section(*args):
    if len(args) == 1:
        section = args[0]
        return render_command_output_section(section.title, section.results, section.rule)
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(title, results, rule)
    raise TypeError(
        "render_report_command_output_section() expected 1 or 3 positional arguments."
    )
"""

    if "def render_report_command_output_section(" in command_sections_text:
        updated_command_sections = replace_function(
            command_sections_text,
            "render_report_command_output_section",
            command_sections_replacement,
        )
        alias_added = False
    else:
        updated_command_sections = command_sections_text.rstrip() + "\n\n" + command_sections_replacement.strip() + "\n"
        alias_added = True

    sections_text = insert_import_after_last_import(
        sections_text,
        "from .command_sections import ReportCommandOutputSection, render_report_command_output_section",
    )

    full_output_replacement = """
def full_output_section(results: list[CommandResult], title: str) -> str:
    section = ReportCommandOutputSection(title=title, results=results, rule=_rule)
    return render_report_command_output_section(section)
"""

    updated_sections = replace_function(sections_text, "full_output_section", full_output_replacement)

    write_text(working_root / "content" / "patchops" / "reporting" / "command_sections.py", updated_command_sections)
    write_text(working_root / "content" / "patchops" / "reporting" / "sections.py", updated_sections)

    validation_candidates = [
        Path("tests") / "test_reporting.py",
        Path("tests") / "test_reporting_command_sections_current.py",
        Path("tests") / "test_reporting_output_helper_current.py",
        Path("tests") / "test_summary_integrity_current.py",
        Path("tests") / "test_summary_derivation_lock_current.py",
        Path("tests") / "test_required_vs_tolerated_report_current.py",
        Path("tests") / "test_summary_integrity_workflow_current.py",
    ]
    validation_targets = [str(path).replace("\\\\", "/") for path in validation_candidates if (wrapper_root / path).exists()]

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp15c_report_helper_signature_and_monkeypatch_repair",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root),
        "backup_files": [
            str(Path("patchops") / "reporting" / "command_sections.py"),
            str(Path("patchops") / "reporting" / "sections.py"),
        ],
        "files_to_write": [
            {
                "path": str(Path("patchops") / "reporting" / "command_sections.py"),
                "content_path": str(Path("content") / "patchops" / "reporting" / "command_sections.py"),
                "encoding": "utf-8",
            },
            {
                "path": str(Path("patchops") / "reporting" / "sections.py"),
                "content_path": str(Path("content") / "patchops" / "reporting" / "sections.py"),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "report_helper_signature_pytest",
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
            "report_dir": str((working_root / "inner_reports")),
            "report_name_prefix": "mp15c_report_helper_signature_and_monkeypatch_repair",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper", "signature_repair"],
        "notes": "Narrow MP15 repair. Restore the helper's dual-call signature in command_sections and keep full_output_section monkeypatchable through reporting.sections.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")

    note_lines = [
        "decision=mp15c_report_helper_signature_and_monkeypatch_repair",
        f"command_sections_path={command_sections_path}",
        f"sections_path={sections_path}",
        f"alias_added={str(alias_added).lower()}",
        "rationale=Restore dual-call helper signature and preserve sections-level monkeypatch contract.",
    ]
    for target in validation_targets:
        note_lines.append(f"validation_target={target}")
    write_text(working_root / "prepare_note.txt", "\n".join(note_lines) + "\n")

    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())