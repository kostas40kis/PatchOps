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
    source_path = None
    if spec.content is not None:
        content = spec.content
    else:
        source_path = resolve_content_path(
            spec,
            manifest_path=manifest_path,
            wrapper_project_root=wrapper_project_root,
        )
        content = source_path.read_text(encoding=spec.encoding)
    mkdir_required = not destination.parent.exists()
    return WritePlan(
        destination=destination,
        content=content,
        encoding=spec.encoding,
        source_path=source_path,
        mkdir_required=mkdir_required,
    )


def write_single_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
    ensure_directory(destination.parent)
    destination.write_text(content, encoding=encoding)
    return WriteRecord(path=destination, encoding=encoding)


def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
    return write_single_file(destination, content, encoding=encoding)
