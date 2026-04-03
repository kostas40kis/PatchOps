from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp21_single_file_writer_helper_retry"

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
        """
    ).strip() + "\n"

def build_single_file_test_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        from pathlib import Path

        import patchops.files.writers as writers
        from patchops.models import WriteRecord


        def test_write_single_file_creates_parent_directory_and_writes_text(tmp_path: Path) -> None:
            destination = tmp_path / "nested" / "notes" / "example.txt"

            record = writers.write_single_file(destination, "hello from helper", encoding="utf-8")

            assert destination.exists()
            assert destination.read_text(encoding="utf-8") == "hello from helper"
            assert record == WriteRecord(path=destination, encoding="utf-8")


        def test_write_text_file_delegates_to_single_file_helper(tmp_path: Path, monkeypatch) -> None:
            destination = tmp_path / "target" / "delegated.txt"
            captured: dict[str, object] = {}
            expected = WriteRecord(path=destination, encoding="utf-8")

            def fake_write_single_file(path: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
                captured["path"] = path
                captured["content"] = content
                captured["encoding"] = encoding
                return expected

            monkeypatch.setattr(writers, "write_single_file", fake_write_single_file)

            result = writers.write_text_file(destination, "delegated payload", encoding="utf-8")

            assert result == expected
            assert captured == {
                "path": destination,
                "content": "delegated payload",
                "encoding": "utf-8",
            }
        """
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    writers_path = wrapper_root / "patchops" / "files" / "writers.py"
    existing_test_path = wrapper_root / "tests" / "test_single_file_writer_current.py"

    writers_source = writers_path.read_text(encoding="utf-8")
    helper_exists_before = "def write_single_file(" in writers_source
    delegates_before = "return write_single_file(destination, content, encoding=encoding)" in writers_source

    writers_text = build_writers_text()
    single_file_test_text = build_single_file_test_text()

    staged = {
        "patchops/files/writers.py": writers_text,
        "tests/test_single_file_writer_current.py": single_file_test_text,
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
            "report_name_prefix": "mp21",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "mp21", "self_hosted"],
        "notes": "Move actual single-file write behavior into one helper and prove write_text_file delegates to it.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    json.loads(manifest_path.read_text(encoding="utf-8"))

    audit = {
        "patch_name": PATCH_NAME,
        "writers_path": str(writers_path),
        "single_file_test_path": str(existing_test_path),
        "write_single_file_exists_before": helper_exists_before,
        "write_text_file_delegates_before": delegates_before,
        "single_file_test_exists_before": existing_test_path.exists(),
        "manifest_path": str(manifest_path),
        "staged_files": [str((content_root / path).resolve()) for path in staged.keys()],
    }
    write_text(working_root / "prepare_audit.txt", json.dumps(audit, indent=2) + "\n")

    print(f"Prepared manifest: {manifest_path}")
    print(f"Prepared audit   : {working_root / 'prepare_audit.txt'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())