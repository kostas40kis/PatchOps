from __future__ import annotations

import json
from pathlib import Path
import textwrap
import sys

PATCH_NAME = "mp21c_direct_boot_repair"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def patch_apply_text(source: str) -> str:
    old = "content = load_content(spec, manifest_path=manifest_path)"
    new = "content = load_content(spec, manifest_path=manifest_path, wrapper_project_root=wrapper_root)"
    if new in source:
        return source
    if old in source:
        return source.replace(old, new)
    raise RuntimeError("Could not find load_content call to repair in apply_patch.py")

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    writers_path = wrapper_root / "patchops" / "files" / "writers.py"
    apply_path = wrapper_root / "patchops" / "workflows" / "apply_patch.py"
    metadata_path = wrapper_root / "patchops" / "reporting" / "metadata.py"
    reporting_init_path = wrapper_root / "patchops" / "reporting" / "__init__.py"

    writers_source = writers_path.read_text(encoding="utf-8")
    apply_source = apply_path.read_text(encoding="utf-8")
    metadata_source = metadata_path.read_text(encoding="utf-8")
    reporting_init_source = reporting_init_path.read_text(encoding="utf-8")

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

            @property
            def path(self) -> Path:
                return self.destination


        def resolve_content_path(
            spec: FileWriteSpec,
            *,
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
            destination: Path,
            *,
            manifest_path: Path | None = None,
            wrapper_project_root: Path | None = None,
        ) -> WritePlan:
            content = load_content(
                spec,
                manifest_path=manifest_path,
                wrapper_project_root=wrapper_project_root,
            )
            return WritePlan(destination=destination, content=content, encoding=spec.encoding)


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
            mode: str
            patch_name: str
            timestamp: datetime | None
            manifest_path: Path | None
            workspace_root: Path | None
            wrapper_project_root: Path | None
            target_project_root: Path | None
            active_profile: str | None
            runtime_path: Path | None
            backup_root: Path | None
            report_path: Path | None
            manifest_version: str | None


        def build_report_header_metadata(
            result: WorkflowResult,
            *,
            timestamp: datetime | None = None,
        ) -> ReportHeaderMetadata:
            return ReportHeaderMetadata(
                mode=result.mode,
                patch_name=result.manifest.patch_name,
                timestamp=timestamp,
                manifest_path=result.manifest_path,
                workspace_root=result.workspace_root,
                wrapper_project_root=result.wrapper_project_root,
                target_project_root=result.target_project_root,
                active_profile=result.resolved_profile.name if result.resolved_profile else None,
                runtime_path=result.runtime_path,
                backup_root=result.backup_root,
                report_path=result.report_path,
                manifest_version=result.manifest.manifest_version,
            )


        def _display_path(value: Path | None) -> str:
            if value is None:
                return "(none)"
            return str(value)


        def render_report_header_lines(metadata: ReportHeaderMetadata) -> tuple[str, ...]:
            lines = [
                f"PATCHOPS {metadata.mode.upper()}",
                f"Patch Name           : {metadata.patch_name}",
            ]
            if metadata.timestamp is not None:
                lines.append(f"Timestamp            : {metadata.timestamp:%Y-%m-%d %H:%M:%S}")
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

    write_text(content_root / "patchops" / "files" / "writers.py", writers_text)
    write_text(content_root / "patchops" / "workflows" / "apply_patch.py", patch_apply_text(apply_source))
    write_text(content_root / "patchops" / "reporting" / "metadata.py", metadata_text)
    write_text(content_root / "patchops" / "reporting" / "__init__.py", reporting_init_text)

    audit = {
        "patch_name": PATCH_NAME,
        "writers_path": str(writers_path),
        "apply_path": str(apply_path),
        "metadata_path": str(metadata_path),
        "reporting_init_path": str(reporting_init_path),
        "broken_writeplan_import_before": "from patchops.models import FileWriteSpec, WritePlan, WriteRecord" in writers_source,
        "wrapper_root_apply_fix_present_before": "wrapper_project_root=wrapper_root" in apply_source,
        "metadata_has_render_report_header_before": "def render_report_header(" in metadata_source,
        "reporting_init_exports_render_report_header_before": "render_report_header" in reporting_init_source,
        "staged_files": [
            str((content_root / "patchops" / "files" / "writers.py").resolve()),
            str((content_root / "patchops" / "workflows" / "apply_patch.py").resolve()),
            str((content_root / "patchops" / "reporting" / "metadata.py").resolve()),
            str((content_root / "patchops" / "reporting" / "__init__.py").resolve()),
        ],
    }
    write_text(working_root / "prepare_audit.txt", json.dumps(audit, indent=2) + "\n")
    print(f"Prepared audit   : {working_root / 'prepare_audit.txt'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())