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
            return f"
{title}
{'-' * len(title)}"


        def display_path(value: Path | None) -> str:
            if value is None:
                return "(none)"
            return str(value)


        def header_section(result: WorkflowResult) -> str:
            return "
".join(
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
                joined = "
".join(lines)
                if retry_reason.strip() not in joined:
                    lines.append(f"Retry Reason : {retry_reason.strip()}")
            return "
".join(lines)


        def target_files_section(paths: list[Path]) -> str:
            lines = [_rule("TARGET FILES")]
            if not paths:
                lines.append("(none)")
            else:
                lines.extend(str(path) for path in paths)
            return "
".join(lines)


        def backup_section(records: list[BackupRecord]) -> str:
            lines = [_rule("BACKUP")]
            if not records:
                lines.append("(none)")
                return "
".join(lines)
            for record in records:
                if record.existed and record.destination is not None:
                    lines.append(f"BACKUP : {record.source} -> {record.destination}")
                else:
                    lines.append(f"MISSING: {record.source}")
            return "
".join(lines)


        def write_section(records: list[WriteRecord]) -> str:
            lines = [_rule("WRITING FILES")]
            if not records:
                lines.append("(none)")
            else:
                for record in records:
                    lines.append(f"WROTE : {record.path}")
            return "
".join(lines)


        def command_group_section(title: str, results: list[CommandResult]) -> str:
            lines = [_rule(title)]
            if not results:
                lines.append("(none)")
                return "
".join(lines)
            for section in build_report_command_sections(results, section_label=title):
                lines.append(f"NAME    : {section.command_name}")
                lines.append(f"COMMAND : {section.command_text}")
                lines.append(f"CWD     : {section.cwd_text}")
                lines.append(f"EXIT    : {section.exit_text}")
                if section.classification:
                    lines.append(f"CLASS   : {section.classification}")
            return "
".join(lines)


        def full_output_section(results: list[CommandResult], title: str) -> str:
            lines = [_rule(title)]
            if not results:
                lines.append("(none)")
                return "
".join(lines)
            for result in results:
                section = ReportCommandOutputSection(title=title, results=[result], rule=_rule)
                rendered = render_report_command_output_section(section)
                if isinstance(rendered, str):
                    lines.append(rendered)
                else:
                    lines.extend(str(item) for item in rendered)
            return "
".join(lines)


        def failure_section(result: WorkflowResult) -> str:
            lines = [_rule("FAILURE DETAILS")]
            if result.failure is None:
                lines.append("(none)")
                return "
".join(lines)
            payload = asdict(result.failure)
            category = payload.get("category")
            category_value = category.get("value") if isinstance(category, dict) else category
            lines.append(f"Category : {category_value}")
            lines.append(f"Message  : {payload.get('message', '')}")
            details = payload.get("details")
            if details:
                lines.append(f"Details  : {details}")
            return "
".join(lines)
