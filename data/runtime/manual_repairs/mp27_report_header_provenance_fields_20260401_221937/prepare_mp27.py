from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp27_report_header_provenance_fields"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_metadata_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        from dataclasses import dataclass, field
        from datetime import datetime
        from pathlib import Path

        from patchops.models import WorkflowResult


        @dataclass(slots=True)
        class RunOriginMetadata:
            workflow_mode: str
            manifest_path: Path
            active_profile: str | None = None
            resolved_runtime: Path | None = None
            wrapper_project_root: Path | None = None
            target_project_root: Path | None = None


        def build_run_origin_metadata(result: WorkflowResult) -> RunOriginMetadata:
            return RunOriginMetadata(
                workflow_mode=result.mode,
                manifest_path=result.manifest_path,
                active_profile=result.resolved_profile.name if result.resolved_profile else None,
                resolved_runtime=result.runtime_path,
                wrapper_project_root=result.wrapper_project_root,
                target_project_root=result.target_project_root,
            )


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
            mode: str | None = field(default=None, compare=False)
            backup_root: Path | None = field(default=None, compare=False)
            manifest_version: str | None = field(default=None, compare=False)
            run_origin: RunOriginMetadata | None = field(default=None, compare=False)

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
                mode=result.mode,
                backup_root=result.backup_root,
                manifest_version=str(result.manifest.manifest_version) if result.manifest.manifest_version is not None else None,
                run_origin=build_run_origin_metadata(result),
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
            if metadata.run_origin is not None:
                lines.extend(
                    [
                        f"Wrapper Mode Used    : {metadata.run_origin.workflow_mode}",
                        f"Manifest Path Used   : {_display_path(metadata.run_origin.manifest_path)}",
                        f"Profile Resolved     : {metadata.run_origin.active_profile or '(none)'}",
                        f"Runtime Resolved     : {_display_path(metadata.run_origin.resolved_runtime)}",
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

def build_test_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path

        from patchops.reporting import RunOriginMetadata, build_report_header_metadata, render_report_header
        from patchops.workflows.apply_patch import apply_manifest


        def test_report_header_metadata_carries_run_origin_fields(tmp_path: Path) -> None:
            wrapper_root = tmp_path / "wrapper_root"
            manifest_root = tmp_path / "manifest_root"
            target_root = tmp_path / "target_root"
            report_dir = tmp_path / "reports"

            wrapper_root.mkdir(parents=True, exist_ok=True)
            manifest_root.mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            manifest_path = manifest_root / "patch_manifest.json"
            manifest_data = {
                "manifest_version": "1",
                "patch_name": "mp27_header_provenance_contract",
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": [],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": "mp27_header_provenance_contract",
                    "write_to_desktop": False,
                },
            }
            manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
            metadata = build_report_header_metadata(result)

            assert metadata.run_origin == RunOriginMetadata(
                workflow_mode="apply",
                manifest_path=manifest_path.resolve(),
                active_profile="generic_python",
                resolved_runtime=None,
                wrapper_project_root=wrapper_root.resolve(),
                target_project_root=target_root,
            )

            text = render_report_header(metadata)
            assert "Wrapper Mode Used    : apply" in text
            assert f"Manifest Path Used   : {manifest_path.resolve()}" in text
            assert "Profile Resolved     : generic_python" in text
            assert "Runtime Resolved     : (none)" in text


        def test_canonical_report_header_shows_provenance_fields(tmp_path: Path) -> None:
            wrapper_root = tmp_path / "wrapper_root"
            manifest_root = tmp_path / "manifest_root"
            target_root = tmp_path / "target_root"
            report_dir = tmp_path / "reports"

            wrapper_root.mkdir(parents=True, exist_ok=True)
            manifest_root.mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            manifest_path = manifest_root / "patch_manifest.json"
            manifest_data = {
                "manifest_version": "1",
                "patch_name": "mp27_header_rendered_provenance_contract",
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": [],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": "mp27_header_rendered_provenance_contract",
                    "write_to_desktop": False,
                },
            }
            manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
            report_text = result.report_path.read_text(encoding="utf-8")

            assert "Wrapper Mode Used    : apply" in report_text
            assert f"Manifest Path Used   : {manifest_path.resolve()}" in report_text
            assert "Profile Resolved     : generic_python" in report_text
            assert "Runtime Resolved     : (none)" in report_text
        """
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    metadata_path = wrapper_root / "patchops" / "reporting" / "metadata.py"
    test_path = wrapper_root / "tests" / "test_report_header_provenance_current.py"

    metadata_source = metadata_path.read_text(encoding="utf-8")
    provenance_lines_exist_before = "Wrapper Mode Used" in metadata_source
    run_origin_field_exists_before = "run_origin:" in metadata_source
    test_exists_before = test_path.exists()

    staged = {
        "patchops/reporting/metadata.py": build_metadata_text(),
        "tests/test_report_header_provenance_current.py": build_test_text(),
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
            "report_name_prefix": "mp27",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "mp27", "self_hosted"],
        "notes": "Render explicit wrapper-execution provenance fields in the canonical report header using the MP26 run-origin metadata model.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    json.loads(manifest_path.read_text(encoding="utf-8"))

    audit = {
        "patch_name": PATCH_NAME,
        "metadata_path": str(metadata_path),
        "test_path": str(test_path),
        "provenance_lines_exist_before": provenance_lines_exist_before,
        "run_origin_field_exists_before": run_origin_field_exists_before,
        "test_exists_before": test_exists_before,
        "manifest_path": str(manifest_path),
        "staged_files": [str((content_root / path).resolve()) for path in staged.keys()],
    }
    write_text(working_root / "prepare_audit.txt", json.dumps(audit, indent=2) + "\n")

    print(f"Prepared manifest: {manifest_path}")
    print(f"Prepared audit   : {working_root / 'prepare_audit.txt'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())