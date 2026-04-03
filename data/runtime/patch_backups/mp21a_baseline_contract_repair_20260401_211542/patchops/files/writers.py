from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from patchops.files.paths import ensure_directory
from patchops.models import FileWriteSpec, WriteRecord


@dataclass(frozen=True)
class WritePlan:
    destination: Path
    content_source_type: str
    encoding: str
    normalized_content_source: Path | None
    inline_content: str | None
    mkdir_required: bool


def _resolve_content_source_path(spec: FileWriteSpec, manifest_path: Path | None = None) -> Path:
    if spec.content_path is None:
        raise ValueError(f"No content source defined for {spec.path}")
    content_path = Path(spec.content_path)
    if not content_path.is_absolute() and manifest_path is not None:
        content_path = manifest_path.parent / content_path
    return content_path



def build_write_plan(
    spec: FileWriteSpec,
    target_project_root: Path,
    manifest_path: Path | None = None,
) -> WritePlan:
    destination = target_project_root / Path(spec.path)
    mkdir_required = not destination.parent.exists()

    if spec.content is not None:
        return WritePlan(
            destination=destination,
            content_source_type="content",
            encoding=spec.encoding,
            normalized_content_source=None,
            inline_content=spec.content,
            mkdir_required=mkdir_required,
        )

    return WritePlan(
        destination=destination,
        content_source_type="content_path",
        encoding=spec.encoding,
        normalized_content_source=_resolve_content_source_path(spec, manifest_path),
        inline_content=None,
        mkdir_required=mkdir_required,
    )



def load_content(spec: FileWriteSpec, manifest_path: Path | None = None) -> str:
    if spec.content is not None:
        return spec.content
    content_path = _resolve_content_source_path(spec, manifest_path)
    return content_path.read_text(encoding=spec.encoding)



def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
    ensure_directory(destination.parent)
    destination.write_text(content, encoding=encoding)
    return WriteRecord(path=destination, encoding=encoding)