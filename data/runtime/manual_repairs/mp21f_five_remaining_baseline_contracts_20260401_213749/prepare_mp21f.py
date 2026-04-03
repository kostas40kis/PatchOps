from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp21f_five_remaining_baseline_contracts"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    handoff_json_path = wrapper_root / "handoff" / "current_handoff.json"
    next_prompt_path = wrapper_root / "handoff" / "next_prompt.txt"

    handoff_data = json.loads(handoff_json_path.read_text(encoding="utf-8"))
    resume = dict(handoff_data.get("resume", {}))
    if not isinstance(resume.get("next_recommended_mode"), str) or not resume.get("next_recommended_mode"):
        resume["next_recommended_mode"] = "repair_patch"
    if not isinstance(resume.get("mode"), str) or not resume.get("mode"):
        resume["mode"] = handoff_data.get("resume_mode", "maintenance")
    if "must_read_files" not in resume:
        resume["must_read_files"] = handoff_data.get("must_read_files", [])
    if "next_action" not in resume:
        resume["next_action"] = handoff_data.get("next_action")
    handoff_data["resume"] = resume

    next_prompt_text = textwrap.dedent(
        """
        You are resuming the PatchOps project from the current maintained repo state.

        Read these files first:
        1. handoff/current_handoff.md
        2. handoff/current_handoff.json
        3. handoff/latest_report_copy.txt

        [content_path repair stream]
        Keep the content_path repair stream treated as repaired and maintenance-locked unless new contrary repo evidence appears.
        The maintained rule is wrapper project root first, with manifest-local compatibility fallback only when the wrapper-root file is missing.

        Next recommended action: Retry MP21 single-file writer helper only after the baseline stays green.

        Rules:
        - keep PowerShell thin
        - keep reusable logic in Python
        - preserve the one-report evidence contract
        - do not move target-repo business logic into PatchOps
        - do not redesign the architecture unless the handoff explicitly shows a deeper repo-truth problem

        After reading the handoff, briefly restate:
        - current state
        - latest attempted patch
        - failure class
        - next recommended action

        Then produce only the next repair patch or next planned patch.
        """
    ).strip() + "\n"

    writers_text = textwrap.dedent(
        """
        from __future__ import annotations

        from dataclasses import dataclass
        from pathlib import Path

        from patchops.files.paths import ensure_directory
        from patchops.models import FileWriteSpec, WriteRecord


        @dataclass(slots=True)
        class WritePlan:
            destination: Path
            content: str
            encoding: str = "utf-8"
            source_path: Path | None = None
            mkdir_required: bool = False
            content_source_type: str = "content"

            @property
            def path(self) -> Path:
                return self.destination


        def resolve_content_path(
            spec: FileWriteSpec,
            manifest_path: Path | None = None,
            wrapper_project_root: Path | None = None,
        ) -> Path:
            if spec.content_path is None:
                raise ValueError(f"No content source defined for {spec.path}")

            content_path = Path(spec.content_path)
            if content_path.is_absolute():
                return content_path

            candidates: list[Path] = []
            if wrapper_project_root is not None:
                candidates.append(Path(wrapper_project_root) / content_path)
            if manifest_path is not None:
                candidates.append(Path(manifest_path).parent / content_path)

            for candidate in candidates:
                if candidate.exists():
                    return candidate

            if candidates:
                return candidates[0]
            return content_path


        def load_content(
            spec: FileWriteSpec,
            manifest_path: Path | None = None,
            wrapper_project_root: Path | None = None,
        ) -> str:
            if spec.content is not None:
                return spec.content
            source_path = resolve_content_path(
                spec,
                manifest_path=manifest_path,
                wrapper_project_root=wrapper_project_root,
            )
            return source_path.read_text(encoding=spec.encoding)


        def build_write_plan(
            spec: FileWriteSpec,
            destination_root: Path,
            manifest_path: Path | None = None,
            wrapper_project_root: Path | None = None,
        ) -> WritePlan:
            destination_root = Path(destination_root)
            destination = Path(spec.path) if Path(spec.path).is_absolute() else destination_root / spec.path
            if spec.content is not None:
                content = spec.content
                source_path = None
                content_source_type = "content"
            else:
                source_path = resolve_content_path(
                    spec,
                    manifest_path=manifest_path,
                    wrapper_project_root=wrapper_project_root,
                )
                content = source_path.read_text(encoding=spec.encoding)
                content_source_type = "content_path"
            mkdir_required = not destination.parent.exists()
            return WritePlan(
                destination=destination,
                content=content,
                encoding=spec.encoding,
                source_path=source_path,
                mkdir_required=mkdir_required,
                content_source_type=content_source_type,
            )


        def write_single_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
            ensure_directory(destination.parent)
            destination.write_text(content, encoding=encoding)
            return WriteRecord(path=destination, encoding=encoding)


        def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
            return write_single_file(destination, content, encoding=encoding)
        """
    ).strip() + "\n"

    metadata_text = textwrap.dedent(
        """
        from __future__ import annotations

        from dataclasses import dataclass
        from datetime import datetime
        from pathlib import Path

        from patchops.models import WorkflowResult


        @dataclass(slots=True)
        class ReportHeaderMetadata:
            patch_name: str
            timestamp: str | None = None
            workspace_root: Path | None = None
            wrapper_project_root: Path | None = None
            target_project_root: Path | None = None
            active_profile: str | None = None
            runtime_path: Path | None = None
            report_path: Path | None = None
            manifest_path: Path | None = None
            mode: str | None = None
            backup_root: Path | None = None
            manifest_version: str | None = None

            @property
            def manifest_identity(self) -> str | None:
                if self.manifest_path is None:
                    return None
                return str(self.manifest_path)


        def build_report_header_metadata(
            result: WorkflowResult,
            *,
            timestamp: datetime | None = None,
        ) -> ReportHeaderMetadata:
            rendered_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp is not None else None
            return ReportHeaderMetadata(
                patch_name=result.manifest.patch_name,
                timestamp=rendered_timestamp,
                workspace_root=result.workspace_root,
                wrapper_project_root=result.wrapper_project_root,
                target_project_root=result.target_project_root,
                active_profile=result.resolved_profile.name if result.resolved_profile else None,
                runtime_path=result.runtime_path,
                report_path=result.report_path,
                manifest_path=result.manifest_path,
            )


        def _display_path(value: Path | None) -> str:
            if value is None:
                return "(none)"
            return str(value)


        def render_report_header_lines(metadata: ReportHeaderMetadata) -> tuple[str, ...]:
            lines = [
                f"PATCHOPS {(metadata.mode or 'apply').upper()}",
                f"Patch Name           : {metadata.patch_name}",
            ]
            if metadata.timestamp is not None:
                lines.append(f"Timestamp            : {metadata.timestamp}")
            lines.extend(
                [
                    f"Manifest Path        : {_display_path(metadata.manifest_path)}",
                    f"Workspace Root       : {_display_path(metadata.workspace_root)}",
                    f"Wrapper Project Root : {_display_path(metadata.wrapper_project_root)}",
                    f"Target Project Root  : {_display_path(metadata.target_project_root)}",
                    f"Active Profile       : {metadata.active_profile or '(none)'}",
                    f"Runtime Path         : {_display_path(metadata.runtime_path)}",
                    f"Backup Root          : {_display_path(metadata.backup_root)}",
                    f"Report Path          : {_display_path(metadata.report_path)}",
                    f"Manifest Version     : {metadata.manifest_version or '(none)'}",
                ]
            )
            return tuple(lines)


        def render_report_header(
            value: WorkflowResult | ReportHeaderMetadata,
            *,
            timestamp: datetime | None = None,
        ) -> str:
            metadata = value if isinstance(value, ReportHeaderMetadata) else build_report_header_metadata(value, timestamp=timestamp)
            return "\\n".join(render_report_header_lines(metadata))
        """
    ).strip() + "\n"

    reporting_init_text = textwrap.dedent(
        """
        \"\"\"Reporting utilities for PatchOps.\"\"\"

        from patchops.reporting.metadata import (
            ReportHeaderMetadata,
            build_report_header_metadata,
            render_report_header,
            render_report_header_lines,
        )

        __all__ = [
            "ReportHeaderMetadata",
            "build_report_header_metadata",
            "render_report_header",
            "render_report_header_lines",
        ]
        """
    ).strip() + "\n"

    staged = {
        "patchops/files/writers.py": writers_text,
        "patchops/reporting/metadata.py": metadata_text,
        "patchops/reporting/__init__.py": reporting_init_text,
        "handoff/current_handoff.json": json.dumps(handoff_data, indent=2) + "\n",
        "handoff/next_prompt.txt": next_prompt_text,
    }

    files_to_write = []
    for relative_path, content in staged.items():
        staged_path = content_root / relative_path
        write_text(staged_path, content)
        files_to_write.append(
            {
                "path": relative_path,
                "content": None,
                "content_path": str(staged_path.relative_to(working_root)).replace("\\", "/"),
                "encoding": "utf-8",
            }
        )

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root),
        "backup_files": list(staged.keys()),
        "files_to_write": files_to_write,
        "validation_commands": [
            {
                "name": "full-pytest-quiet",
                "program": "py",
                "args": ["-m", "pytest", "-q"],
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
            "report_dir": str((working_root / "inner_reports").resolve()),
            "report_name_prefix": "mp21f",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "baseline_repair", "mp21f", "self_hosted"],
        "notes": "Repair the five remaining baseline contracts before retrying MP21.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    json.loads(manifest_path.read_text(encoding="utf-8"))

    audit = {
        "patch_name": PATCH_NAME,
        "manifest_path": str(manifest_path),
        "manifest_valid_json": True,
        "resume_has_next_recommended_mode_after": bool(handoff_data["resume"].get("next_recommended_mode")),
        "next_prompt_mentions_wrapper_project_root_first_after": "wrapper project root first" in next_prompt_text,
        "write_plan_has_content_source_type_after": "content_source_type" in writers_text,
        "metadata_build_leaves_optional_defaults_after": True,
        "staged_files": [str((content_root / path).resolve()) for path in staged.keys()],
    }
    write_text(working_root / "prepare_audit.txt", json.dumps(audit, indent=2) + "\n")

    print(f"Prepared manifest: {manifest_path}")
    print(f"Prepared audit   : {working_root / 'prepare_audit.txt'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())