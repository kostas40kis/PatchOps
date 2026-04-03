from __future__ import annotations

import json
import sys
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15n.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    target_rel = Path("patchops") / "reporting" / "command_sections.py"
    target_path = wrapper_root / target_rel
    if not target_path.exists():
        raise RuntimeError(f"Expected command_sections.py at {target_path}")

    replacement = '''from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from patchops.models import CommandResult


@dataclass(frozen=True)
class ReportCommandOutputSection:
    command_name: str
    display_command: str
    working_directory: str
    exit_code: int
    stdout: str
    stderr: str


def build_report_command_section(result: CommandResult) -> ReportCommandOutputSection:
    return ReportCommandOutputSection(
        command_name=result.name,
        display_command=result.display_command,
        working_directory=str(result.working_directory) if isinstance(result.working_directory, Path) else str(result.working_directory),
        exit_code=int(result.exit_code),
        stdout=result.stdout if result.stdout else "",
        stderr=result.stderr if result.stderr else "",
    )


def build_report_command_sections(results: list[CommandResult]) -> list[ReportCommandOutputSection]:
    return [build_report_command_section(result) for result in results]


def _render_section_tuple(section: object) -> tuple[str, str, str, str]:
    command_name = str(getattr(section, "command_name"))
    stdout = getattr(section, "stdout", "") or ""
    stderr = getattr(section, "stderr", "") or ""
    return (
        f"[{command_name}][stdout]",
        str(stdout),
        f"[{command_name}][stderr]",
        str(stderr),
    )


def render_command_output_section(
    title: str,
    results: list[CommandResult],
    rule: Callable[[str], str],
) -> str:
    lines = [rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for section in build_report_command_sections(results):
        lines.extend(_render_section_tuple(section))
    return "\\n".join(lines)


def render_report_command_output_section(*args):
    if len(args) == 1:
        return _render_section_tuple(args[0])
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(str(title), list(results), rule)
    raise TypeError(
        "render_report_command_output_section expected either (section) or (title, results, rule)."
    )


__all__ = [
    "ReportCommandOutputSection",
    "build_report_command_section",
    "build_report_command_sections",
    "render_command_output_section",
    "render_report_command_output_section",
]
'''

    content_target = working_root / "content" / target_rel
    write_text(content_target, replacement)

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
        "patch_name": "mp15n_report_command_sections_plural_restore",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace("\\", "/"),
        "backup_files": [str(target_rel).replace("\\", "\\\\")],
        "files_to_write": [
            {
                "path": str(target_rel).replace("\\", "\\\\"),
                "content_path": "content/patchops/reporting/command_sections.py",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "report_command_sections_pytest",
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
            "report_dir": str((working_root / "inner_reports")).replace("\\", "/"),
            "report_name_prefix": "mp15n_report_command_sections_plural_restore",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper", "plural_restore"],
        "notes": "Narrow MP15 repair. Restore build_report_command_sections while preserving the existing dual-signature output helper contract.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")

    lines = [
        "decision=mp15n_report_command_sections_plural_restore",
        f"target_path={target_path}",
        f"manifest_path={manifest_path}",
        "validation_targets=" + "; ".join(validation_targets),
        "rationale=Restore build_report_command_sections while preserving build_report_command_section and the single-section monkeypatch path.",
    ]
    write_text(working_root / "prepare_result.txt", "\n".join(lines) + "\n")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())