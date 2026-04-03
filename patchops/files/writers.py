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
