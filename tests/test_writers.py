from pathlib import Path

from patchops.files.writers import load_content, write_text_file
from patchops.models import FileWriteSpec


def test_write_text_file_creates_parent_dirs(tmp_path: Path):
    destination = tmp_path / "nested" / "a.txt"
    record = write_text_file(destination, "hello")
    assert destination.read_text(encoding="utf-8") == "hello"
    assert record.path == destination


def test_load_content_prefers_wrapper_project_root_for_relative_content_path(tmp_path: Path):
    wrapper_root = tmp_path / "wrapper_root"
    manifest_dir = wrapper_root / "data" / "runtime" / "manual_repairs" / "sample_patch"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_dir / "patch_manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")

    relative_content_path = Path("content/source.txt")

    wrapper_source = wrapper_root / relative_content_path
    wrapper_source.parent.mkdir(parents=True, exist_ok=True)
    wrapper_source.write_text("wrapper-root payload\n", encoding="utf-8")

    manifest_local_source = manifest_dir / relative_content_path
    manifest_local_source.parent.mkdir(parents=True, exist_ok=True)
    manifest_local_source.write_text("manifest-local payload\n", encoding="utf-8")

    spec = FileWriteSpec(
        path="OUTPUT.txt",
        content=None,
        content_path=relative_content_path.as_posix(),
        encoding="utf-8",
    )

    content = load_content(
        spec,
        manifest_path=manifest_path,
        wrapper_project_root=wrapper_root,
    )

    assert content == "wrapper-root payload\n"


def test_load_content_falls_back_to_manifest_local_when_wrapper_root_file_is_missing(tmp_path: Path):
    wrapper_root = tmp_path / "wrapper_root"
    manifest_dir = wrapper_root / "data" / "runtime" / "manual_repairs" / "sample_patch"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_dir / "patch_manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")

    relative_content_path = Path("content/source.txt")
    manifest_local_source = manifest_dir / relative_content_path
    manifest_local_source.parent.mkdir(parents=True, exist_ok=True)
    manifest_local_source.write_text("manifest-local payload\n", encoding="utf-8")

    spec = FileWriteSpec(
        path="OUTPUT.txt",
        content=None,
        content_path=relative_content_path.as_posix(),
        encoding="utf-8",
    )

    content = load_content(
        spec,
        manifest_path=manifest_path,
        wrapper_project_root=wrapper_root,
    )

    assert content == "manifest-local payload\n"
