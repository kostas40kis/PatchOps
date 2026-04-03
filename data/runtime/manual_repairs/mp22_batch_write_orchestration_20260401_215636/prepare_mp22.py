from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp22_batch_write_orchestration"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_writers_text() -> str:
    return textwrap.dedent(
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
            normalized_content_source: Path | None = None
            inline_content: str | None = None
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
                inline_content = spec.content
                normalized_content_source = None
                content = inline_content
                content_source_type = "content"
            else:
                normalized_content_source = resolve_content_path(
                    spec,
                    manifest_path=manifest_path,
                    wrapper_project_root=wrapper_project_root,
                )
                inline_content = None
                content = normalized_content_source.read_text(encoding=spec.encoding)
                content_source_type = "content_path"
            mkdir_required = not destination.parent.exists()
            return WritePlan(
                destination=destination,
                content=content,
                encoding=spec.encoding,
                source_path=normalized_content_source,
                normalized_content_source=normalized_content_source,
                inline_content=inline_content,
                mkdir_required=mkdir_required,
                content_source_type=content_source_type,
            )


        def write_single_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
            ensure_directory(destination.parent)
            destination.write_text(content, encoding=encoding)
            return WriteRecord(path=destination, encoding=encoding)


        def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
            return write_single_file(destination, content, encoding=encoding)


        def write_files(
            specs: list[FileWriteSpec],
            destination_root: Path,
            manifest_path: Path | None = None,
            wrapper_project_root: Path | None = None,
        ) -> list[WriteRecord]:
            records: list[WriteRecord] = []
            for spec in specs:
                plan = build_write_plan(
                    spec,
                    destination_root,
                    manifest_path=manifest_path,
                    wrapper_project_root=wrapper_project_root,
                )
                records.append(
                    write_single_file(
                        plan.destination,
                        plan.content,
                        encoding=plan.encoding,
                    )
                )
            return records
        """
    ).strip() + "\n"

def build_apply_patch_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        from pathlib import Path

        from patchops.execution.failure_classifier import classify_exception
        from patchops.files.backups import backup_file, generate_backup_root
        from patchops.files.writers import write_files
        from patchops.manifest_loader import load_manifest
        from patchops.models import FailureInfo, WorkflowResult
        from patchops.profiles.base import resolve_profile
        from patchops.reporting.renderer import render_workflow_report
        from patchops.workflows.common import (
            build_report_path,
            default_report_directory,
            execute_command_group,
            infer_workspace_root,
        )


        def _write_workflow_report(report_path: Path, report_text: str) -> None:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                report_path.write_text(report_text, encoding="utf-8")
            except FileNotFoundError:
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(report_text, encoding="utf-8")


        def apply_manifest(manifest_path: str | Path, wrapper_project_root: str | Path | None = None) -> WorkflowResult:
            manifest_path = Path(manifest_path).resolve()
            wrapper_root = Path(wrapper_project_root).resolve() if wrapper_project_root else Path(__file__).resolve().parents[2]
            manifest = load_manifest(manifest_path)
            resolved_profile = resolve_profile(manifest, wrapper_root)
            target_root = Path(manifest.target_project_root) if manifest.target_project_root else resolved_profile.default_target_root
            if target_root is None:
                raise ValueError("No target project root could be resolved from the manifest/profile.")
            runtime_path = resolved_profile.runtime_path if resolved_profile.runtime_path is not None else None
            workspace_root = infer_workspace_root(target_root)

            report_dir = (
                Path(manifest.report_preferences.report_dir)
                if manifest.report_preferences.report_dir
                else default_report_directory()
            )
            report_path = build_report_path(
                manifest.report_preferences.report_name_prefix or resolved_profile.report_prefix,
                manifest.patch_name,
                report_dir,
            )
            backup_root = generate_backup_root(target_root, resolved_profile.backup_root_name, manifest.patch_name)

            backup_records = []
            write_records = []
            validation_results = []
            smoke_results = []
            audit_results = []
            cleanup_results = []
            archive_results = []
            failure: FailureInfo | None = None
            exit_code = 0
            result_label = "PASS"

            try:
                file_paths_to_backup = set(manifest.backup_files)
                file_paths_to_backup.update(item.path for item in manifest.files_to_write)

                for relative_path in sorted(file_paths_to_backup):
                    source = target_root / relative_path
                    backup_records.append(backup_file(source, target_root, backup_root))

                write_records.extend(
                    write_files(
                        manifest.files_to_write,
                        target_root,
                        manifest_path=manifest_path,
                        wrapper_project_root=wrapper_root,
                    )
                )

                for phase_name, commands, sink in [
                    ("validation", manifest.validation_commands, validation_results),
                    ("smoke", manifest.smoke_commands, smoke_results),
                    ("audit", manifest.audit_commands, audit_results),
                    ("cleanup", manifest.cleanup_commands, cleanup_results),
                    ("archive", manifest.archive_commands, archive_results),
                ]:
                    phase_results, command_failure = execute_command_group(
                        commands,
                        runtime_path=runtime_path,
                        working_directory_root=target_root,
                        phase=phase_name,
                    )
                    sink.extend(phase_results)
                    if command_failure is not None:
                        failure = command_failure
                        exit_code = phase_results[-1].exit_code
                        result_label = "FAIL"
                        raise RuntimeError(command_failure.message)
            except Exception as exc:  # noqa: BLE001
                if failure is None:
                    failure = classify_exception(exc)
                    if exit_code == 0:
                        exit_code = 1
                result_label = "FAIL"
            finally:
                workflow_result = WorkflowResult(
                    mode="apply",
                    manifest_path=manifest_path,
                    manifest=manifest,
                    resolved_profile=resolved_profile,
                    workspace_root=workspace_root,
                    wrapper_project_root=wrapper_root,
                    target_project_root=target_root,
                    runtime_path=runtime_path,
                    backup_root=backup_root,
                    report_path=report_path,
                    backup_records=backup_records,
                    write_records=write_records,
                    validation_results=validation_results,
                    smoke_results=smoke_results,
                    audit_results=audit_results,
                    cleanup_results=cleanup_results,
                    archive_results=archive_results,
                    failure=failure,
                    exit_code=exit_code,
                    result_label=result_label,
                )
                report_text = render_workflow_report(workflow_result)
                _write_workflow_report(report_path, report_text)
            return workflow_result
        """
    ).strip() + "\n"

def build_batch_test_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path

        import patchops.files.writers as writers
        import patchops.workflows.apply_patch as apply_patch
        from patchops.models import FileWriteSpec, WriteRecord


        def test_write_files_orchestrates_multiple_specs_through_shared_path(
            tmp_path: Path,
            monkeypatch,
        ) -> None:
            specs = [
                FileWriteSpec(path="docs/a.txt", content="alpha", content_path=None, encoding="utf-8"),
                FileWriteSpec(path="docs/b.txt", content="beta", content_path=None, encoding="utf-8"),
            ]
            plans = [
                writers.WritePlan(
                    destination=tmp_path / "docs" / "a.txt",
                    content="alpha",
                    encoding="utf-8",
                    inline_content="alpha",
                    content_source_type="content",
                ),
                writers.WritePlan(
                    destination=tmp_path / "docs" / "b.txt",
                    content="beta",
                    encoding="utf-8",
                    inline_content="beta",
                    content_source_type="content",
                ),
            ]

            build_calls: list[tuple[str, Path | None, Path | None]] = []
            write_calls: list[tuple[Path, str, str]] = []

            def fake_build_write_plan(spec, destination_root, manifest_path=None, wrapper_project_root=None):
                index = len(build_calls)
                build_calls.append((spec.path, manifest_path, wrapper_project_root))
                return plans[index]

            def fake_write_single_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
                write_calls.append((destination, content, encoding))
                return WriteRecord(path=destination, encoding=encoding)

            monkeypatch.setattr(writers, "build_write_plan", fake_build_write_plan)
            monkeypatch.setattr(writers, "write_single_file", fake_write_single_file)

            records = writers.write_files(
                specs,
                tmp_path,
                manifest_path=tmp_path / "patch_manifest.json",
                wrapper_project_root=tmp_path / "wrapper_root",
            )

            assert [record.path for record in records] == [plan.destination for plan in plans]
            assert build_calls == [
                ("docs/a.txt", tmp_path / "patch_manifest.json", tmp_path / "wrapper_root"),
                ("docs/b.txt", tmp_path / "patch_manifest.json", tmp_path / "wrapper_root"),
            ]
            assert write_calls == [
                (plans[0].destination, "alpha", "utf-8"),
                (plans[1].destination, "beta", "utf-8"),
            ]


        def test_apply_manifest_routes_multi_file_writes_through_batch_helper(
            tmp_path: Path,
            monkeypatch,
        ) -> None:
            wrapper_root = tmp_path / "wrapper"
            target_root = tmp_path / "target"
            report_dir = tmp_path / "reports"
            wrapper_root.mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            manifest_path = wrapper_root / "patch_manifest.json"
            manifest_data = {
                "manifest_version": "1",
                "patch_name": "mp22_apply_batch_write_contract",
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": [
                    {
                        "path": "docs/one.txt",
                        "content": "one",
                        "content_path": None,
                        "encoding": "utf-8",
                    },
                    {
                        "path": "docs/two.txt",
                        "content": "two",
                        "content_path": None,
                        "encoding": "utf-8",
                    },
                ],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": "mp22_apply_batch_write_contract",
                    "write_to_desktop": False,
                },
            }
            manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

            captured: dict[str, object] = {}

            def fake_write_files(specs, destination_root, manifest_path=None, wrapper_project_root=None):
                captured["spec_paths"] = [spec.path for spec in specs]
                captured["destination_root"] = destination_root
                captured["manifest_path"] = manifest_path
                captured["wrapper_project_root"] = wrapper_project_root
                return [
                    WriteRecord(path=destination_root / spec.path, encoding=spec.encoding)
                    for spec in specs
                ]

            monkeypatch.setattr(apply_patch, "write_files", fake_write_files)

            result = apply_patch.apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

            assert result.result_label == "PASS"
            assert captured == {
                "spec_paths": ["docs/one.txt", "docs/two.txt"],
                "destination_root": target_root,
                "manifest_path": manifest_path.resolve(),
                "wrapper_project_root": wrapper_root.resolve(),
            }
            assert [record.path for record in result.write_records] == [
                target_root / "docs/one.txt",
                target_root / "docs/two.txt",
            ]
        """
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    writers_path = wrapper_root / "patchops" / "files" / "writers.py"
    apply_path = wrapper_root / "patchops" / "workflows" / "apply_patch.py"
    batch_test_path = wrapper_root / "tests" / "test_batch_write_orchestration_current.py"

    writers_source = writers_path.read_text(encoding="utf-8")
    apply_source = apply_path.read_text(encoding="utf-8")

    write_files_exists_before = "def write_files(" in writers_source
    apply_uses_write_files_before = "write_files(" in apply_source and "write_records.extend(" in apply_source
    batch_test_exists_before = batch_test_path.exists()

    staged = {
        "patchops/files/writers.py": build_writers_text(),
        "patchops/workflows/apply_patch.py": build_apply_patch_text(),
        "tests/test_batch_write_orchestration_current.py": build_batch_test_text(),
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
            "report_name_prefix": "mp22",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "mp22", "self_hosted"],
        "notes": "Route multi-file writes through the shared write helper and plan model without changing manifest semantics.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    json.loads(manifest_path.read_text(encoding="utf-8"))

    audit = {
        "patch_name": PATCH_NAME,
        "writers_path": str(writers_path),
        "apply_path": str(apply_path),
        "batch_test_path": str(batch_test_path),
        "write_files_exists_before": write_files_exists_before,
        "apply_uses_write_files_before": apply_uses_write_files_before,
        "batch_test_exists_before": batch_test_exists_before,
        "manifest_path": str(manifest_path),
        "staged_files": [str((content_root / path).resolve()) for path in staged.keys()],
    }
    write_text(working_root / "prepare_audit.txt", json.dumps(audit, indent=2) + "\n")

    print(f"Prepared manifest: {manifest_path}")
    print(f"Prepared audit   : {working_root / 'prepare_audit.txt'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())