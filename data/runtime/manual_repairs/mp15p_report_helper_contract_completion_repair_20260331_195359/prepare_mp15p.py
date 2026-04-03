from __future__ import annotations

import json
import textwrap
from pathlib import Path
import sys


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15p.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"
    inner_report_dir = working_root / "inner_reports"

    command_sections_text = textwrap.dedent(
        '''
        from __future__ import annotations

        from dataclasses import dataclass
        from pathlib import Path
        from typing import Callable

        from patchops.models import CommandResult


        SectionRule = Callable[[str], str]


        @dataclass(slots=True)
        class ReportCommandSection:
            section_label: str
            command_name: str
            command_text: str
            working_directory: Path
            exit_code: int
            stdout_text: str
            stderr_text: str
            classification: str | None = None

            @property
            def cwd_text(self) -> str:
                return str(self.working_directory)

            @property
            def exit_text(self) -> str:
                return str(self.exit_code)


        @dataclass(slots=True)
        class ReportCommandOutputSection:
            title: str
            results: list[CommandResult]
            rule: SectionRule

            @property
            def command_name(self) -> str:
                return self.results[0].name if self.results else ""

            @property
            def stdout_text(self) -> str:
                return self.results[0].stdout if self.results else ""

            @property
            def stderr_text(self) -> str:
                return self.results[0].stderr if self.results else ""


        def build_report_command_section(
            result: CommandResult,
            section_label: str = "VALIDATION COMMANDS",
            classification: str | None = None,
        ) -> ReportCommandSection:
            return ReportCommandSection(
                section_label=section_label,
                command_name=result.name,
                command_text=result.display_command,
                working_directory=result.working_directory,
                exit_code=result.exit_code,
                stdout_text=result.stdout,
                stderr_text=result.stderr,
                classification=classification,
            )


        def build_report_command_sections(
            results: list[CommandResult],
            section_label: str = "VALIDATION COMMANDS",
            classifications: dict[str, str] | None = None,
        ) -> list[ReportCommandSection]:
            mapping = classifications or {}
            return [
                build_report_command_section(
                    result,
                    section_label=section_label,
                    classification=mapping.get(result.name),
                )
                for result in results
            ]


        def build_report_command_output_section(
            result: CommandResult,
            title: str = "FULL OUTPUT",
            rule: SectionRule | None = None,
        ) -> ReportCommandOutputSection:
            return ReportCommandOutputSection(title=title, results=[result], rule=rule or (lambda value: value))


        def render_report_command_output_section(*args):
            if len(args) == 1:
                section = args[0]
                lines = [
                    f"[{section.command_name}][stdout]",
                    section.stdout_text if section.stdout_text else "",
                    f"[{section.command_name}][stderr]",
                    section.stderr_text if section.stderr_text else "",
                ]
                return "\n".join(lines)

            if len(args) == 3:
                title, results, rule = args
                lines = [rule(title)]
                if not results:
                    lines.append("(none)")
                    return "\n".join(lines)
                for result in results:
                    lines.append(render_report_command_output_section(build_report_command_output_section(result, title=title, rule=rule)))
                return "\n".join(lines)

            raise TypeError("render_report_command_output_section expects either (section) or (title, results, rule).")
        '''
    ).strip() + "\n"

    sections_text = textwrap.dedent(
        '''
        from __future__ import annotations

        from dataclasses import asdict
        from pathlib import Path

        from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord
        from patchops.reporting.command_sections import (
            ReportCommandOutputSection,
            build_report_command_section,
            build_report_command_sections,
            render_report_command_output_section,
        )
        from patchops.workflows.wrapper_retry import (
            WRAPPER_ONLY_RETRY_KIND,
            build_wrapper_only_retry_state,
            get_active_wrapper_only_retry_reason,
            render_wrapper_only_retry_report_lines,
        )


        def _rule(title: str) -> str:
            return f"\n{title}\n{'-' * len(title)}"


        def display_path(value: Path | None) -> str:
            if value is None:
                return "(none)"
            return str(value)


        def header_section(result: WorkflowResult) -> str:
            return "\n".join(
                [
                    f"PATCHOPS {result.mode.upper()}",
                    f"Patch Name           : {result.manifest.patch_name}",
                    f"Manifest Path        : {display_path(result.manifest_path)}",
                    f"Workspace Root       : {display_path(result.workspace_root)}",
                    f"Wrapper Project Root : {display_path(result.wrapper_project_root)}",
                    f"Target Project Root  : {display_path(result.target_project_root)}",
                    f"Active Profile       : {result.resolved_profile.name}",
                    f"Runtime Path         : {display_path(result.runtime_path)}",
                    f"Backup Root          : {display_path(result.backup_root)}",
                    f"Report Path          : {display_path(result.report_path)}",
                    f"Manifest Version     : {result.manifest.manifest_version}",
                ]
            )


        def wrapper_only_retry_section(result: WorkflowResult) -> str:
            if result.mode != WRAPPER_ONLY_RETRY_KIND:
                return ""

            retry_reason = get_active_wrapper_only_retry_reason()
            state = None
            for builder in (
                lambda: build_wrapper_only_retry_state(
                    manifest=result.manifest,
                    target_project_root=result.target_project_root,
                    retry_reason=retry_reason,
                ),
                lambda: build_wrapper_only_retry_state(result.manifest, result.target_project_root, retry_reason),
                lambda: build_wrapper_only_retry_state(result.manifest, result.target_project_root),
            ):
                try:
                    state = builder()
                    break
                except TypeError:
                    continue
            if state is None:
                raise RuntimeError("Unable to build wrapper-only retry state from current helper signatures.")

            lines = list(render_wrapper_only_retry_report_lines(state))
            if retry_reason:
                joined = "\n".join(lines)
                if retry_reason.strip() not in joined:
                    lines.append(f"Retry Reason : {retry_reason.strip()}")
            return "\n".join(lines)


        def target_files_section(paths: list[Path]) -> str:
            lines = [_rule("TARGET FILES")]
            if not paths:
                lines.append("(none)")
            else:
                lines.extend(str(path) for path in paths)
            return "\n".join(lines)


        def backup_section(records: list[BackupRecord]) -> str:
            lines = [_rule("BACKUP")]
            if not records:
                lines.append("(none)")
                return "\n".join(lines)
            for record in records:
                if record.existed and record.destination is not None:
                    lines.append(f"BACKUP : {record.source} -> {record.destination}")
                else:
                    lines.append(f"MISSING: {record.source}")
            return "\n".join(lines)


        def write_section(records: list[WriteRecord]) -> str:
            lines = [_rule("WRITING FILES")]
            if not records:
                lines.append("(none)")
            else:
                for record in records:
                    lines.append(f"WROTE : {record.path}")
            return "\n".join(lines)


        def command_group_section(title: str, results: list[CommandResult]) -> str:
            lines = [_rule(title)]
            if not results:
                lines.append("(none)")
                return "\n".join(lines)
            for section in build_report_command_sections(results, section_label=title):
                lines.append(f"NAME    : {section.command_name}")
                lines.append(f"COMMAND : {section.command_text}")
                lines.append(f"CWD     : {section.cwd_text}")
                lines.append(f"EXIT    : {section.exit_text}")
                if section.classification:
                    lines.append(f"CLASS   : {section.classification}")
            return "\n".join(lines)


        def full_output_section(results: list[CommandResult], title: str) -> str:
            lines = [_rule(title)]
            if not results:
                lines.append("(none)")
                return "\n".join(lines)
            for result in results:
                section = ReportCommandOutputSection(title=title, results=[result], rule=_rule)
                rendered = render_report_command_output_section(section)
                if isinstance(rendered, str):
                    lines.append(rendered)
                else:
                    lines.extend(str(item) for item in rendered)
            return "\n".join(lines)


        def failure_section(result: WorkflowResult) -> str:
            lines = [_rule("FAILURE DETAILS")]
            if result.failure is None:
                lines.append("(none)")
                return "\n".join(lines)
            payload = asdict(result.failure)
            category = payload.get("category")
            category_value = category.get("value") if isinstance(category, dict) else category
            lines.append(f"Category : {category_value}")
            lines.append(f"Message  : {payload.get('message', '')}")
            details = payload.get("details")
            if details:
                lines.append(f"Details  : {details}")
            return "\n".join(lines)
        '''
    ).strip() + "\n"

    write_text(content_root / "patchops" / "reporting" / "command_sections.py", command_sections_text)
    write_text(content_root / "patchops" / "reporting" / "sections.py", sections_text)

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
        "patch_name": "mp15p_report_helper_contract_completion_repair",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace("\\", "/"),
        "backup_files": [
            "patchops\\reporting\\command_sections.py",
            "patchops\\reporting\\sections.py",
        ],
        "files_to_write": [
            {
                "path": "patchops\\reporting\\command_sections.py",
                "content_path": "content/patchops/reporting/command_sections.py",
                "encoding": "utf-8",
            },
            {
                "path": "patchops\\reporting\\sections.py",
                "content_path": "content/patchops/reporting/sections.py",
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "report_helper_contract_pytest",
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
            "report_dir": str(inner_report_dir).replace("\\", "/"),
            "report_name_prefix": "mp15p_report_helper_contract_completion_repair",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper", "contract_completion"],
        "notes": "Narrow MP15 repair. Complete the command-section model and wrapper-only retry contract while preserving the monkeypatchable single-section FULL OUTPUT path.",
    }
    write_text(working_root / "patch_manifest.json", json.dumps(manifest, indent=2) + "\n")

    prepare_lines = [
        "decision=mp15p_report_helper_contract_completion_repair",
        f"command_sections_path={wrapper_root / 'patchops' / 'reporting' / 'command_sections.py'}",
        f"sections_path={wrapper_root / 'patchops' / 'reporting' / 'sections.py'}",
        f"manifest_path={working_root / 'patch_manifest.json'}",
        "rationale=Complete the remaining MP15 contracts: command section fields, output helper string rendering, and wrapper-only retry compatibility.",
        f"validation_targets={';'.join(validation_targets)}",
    ]
    write_text(working_root / "prepare_result.txt", "\n".join(prepare_lines) + "\n")
    print(str(working_root / "patch_manifest.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())