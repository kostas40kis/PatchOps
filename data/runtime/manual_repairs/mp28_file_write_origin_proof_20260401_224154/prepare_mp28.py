from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp28_file_write_origin_proof"

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
            file_write_origin: str | None = None


        def build_run_origin_metadata(result: WorkflowResult) -> RunOriginMetadata:
            file_write_origin = "wrapper_owned_write_engine" if result.write_records else None
            return RunOriginMetadata(
                workflow_mode=result.mode,
                manifest_path=result.manifest_path,
                active_profile=result.resolved_profile.name if result.resolved_profile else None,
                resolved_runtime=result.runtime_path,
                wrapper_project_root=result.wrapper_project_root,
                target_project_root=result.target_project_root,
                file_write_origin=file_write_origin,
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
                        f"File Write Origin    : {metadata.run_origin.file_write_origin or '(none)'}",
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

        from patchops.reporting import build_report_header_metadata
        from patchops.workflows.apply_patch import apply_manifest


        def test_run_origin_metadata_marks_wrapper_owned_file_write_engine_when_writes_exist(tmp_path: Path) -> None:
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
                "patch_name": "mp28_file_write_origin_metadata_contract",
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": [
                    {
                        "path": "docs/example.txt",
                        "content": "written by wrapper",
                        "content_path": None,
                        "encoding": "utf-8",
                    }
                ],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": "mp28_file_write_origin_metadata_contract",
                    "write_to_desktop": False,
                },
            }
            manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
            metadata = build_report_header_metadata(result)

            assert result.result_label == "PASS"
            assert metadata.run_origin is not None
            assert metadata.run_origin.file_write_origin == "wrapper_owned_write_engine"


        def test_canonical_report_header_shows_file_write_origin_for_wrapper_writes(tmp_path: Path) -> None:
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
                "patch_name": "mp28_file_write_origin_report_contract",
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": [
                    {
                        "path": "docs/example.txt",
                        "content": "written by wrapper",
                        "content_path": None,
                        "encoding": "utf-8",
                    }
                ],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": "mp28_file_write_origin_report_contract",
                    "write_to_desktop": False,
                },
            }
            manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
            report_text = result.report_path.read_text(encoding="utf-8")

            assert result.result_label == "PASS"
            assert "File Write Origin    : wrapper_owned_write_engine" in report_text
            assert "WROTE : " in report_text
        """
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    metadata_path = wrapper_root / "patchops" / "reporting" / "metadata.py"
    test_path = wrapper_root / "tests" / "test_file_write_origin_proof_current.py"

    metadata_source = metadata_path.read_text(encoding="utf-8")
    file_write_origin_exists_before = "file_write_origin" in metadata_source
    test_exists_before = test_path.exists()

    staged = {
        "patchops/reporting/metadata.py": build_metadata_text(),
        "tests/test_file_write_origin_proof_current.py": build_test_text(),
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
            "report_name_prefix": "mp28",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "mp28", "proof", "self_hosted"],
        "notes": "Prove that the canonical report makes wrapper-engine file writes explicit through the provenance header path.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    json.loads(manifest_path.read_text(encoding="utf-8"))

    audit = {
        "patch_name": PATCH_NAME,
        "metadata_path": str(metadata_path),
        "test_path": str(test_path),
        "file_write_origin_exists_before": file_write_origin_exists_before,
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