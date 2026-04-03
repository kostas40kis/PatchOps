from __future__ import annotations

from pathlib import Path

from patchops.files.paths import ensure_directory
from patchops.models import FileWriteSpec, WriteRecord


def load_content(
    spec: FileWriteSpec,
    manifest_path: Path | None = None,
    wrapper_project_root: Path | None = None,
) -> str:
    if spec.content is not None:
        return spec.content
    if spec.content_path is None:
        raise ValueError(f"No content source defined for {spec.path}")

    content_path = Path(spec.content_path)
    if not content_path.is_absolute():
        candidate_paths: list[Path] = []
        if wrapper_project_root is not None:
            candidate_paths.append(Path(wrapper_project_root) / content_path)
        if manifest_path is not None:
            candidate_paths.append(Path(manifest_path).parent / content_path)

        if candidate_paths:
            for candidate in candidate_paths:
                if candidate.exists():
                    content_path = candidate
                    break
            else:
                content_path = candidate_paths[0]

    return content_path.read_text(encoding=spec.encoding)


def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
    ensure_directory(destination.parent)
    destination.write_text(content, encoding=encoding)
    return WriteRecord(path=destination, encoding=encoding)
