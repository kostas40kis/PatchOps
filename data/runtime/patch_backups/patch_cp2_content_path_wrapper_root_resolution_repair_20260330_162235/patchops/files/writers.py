from __future__ import annotations

from pathlib import Path

from patchops.files.paths import ensure_directory
from patchops.models import FileWriteSpec, WriteRecord


def load_content(spec: FileWriteSpec, manifest_path: Path | None = None) -> str:
    if spec.content is not None:
        return spec.content
    if spec.content_path is None:
        raise ValueError(f"No content source defined for {spec.path}")
    content_path = Path(spec.content_path)
    if not content_path.is_absolute() and manifest_path is not None:
        content_path = manifest_path.parent / content_path
    return content_path.read_text(encoding=spec.encoding)


def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
    ensure_directory(destination.parent)
    destination.write_text(content, encoding=encoding)
    return WriteRecord(path=destination, encoding=encoding)
