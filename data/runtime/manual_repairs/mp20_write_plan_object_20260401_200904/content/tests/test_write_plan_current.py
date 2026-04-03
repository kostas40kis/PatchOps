from __future__ import annotations

from pathlib import Path

from patchops.files.writers import WritePlan, build_write_plan, load_content
from patchops.models import FileWriteSpec



def test_build_write_plan_for_inline_content_resolves_destination_and_encoding(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    spec = FileWriteSpec(path="docs/example.md", content="hello", content_path=None, encoding="utf-8")

    plan = build_write_plan(spec, target_root)

    assert isinstance(plan, WritePlan)
    assert plan.destination == target_root / "docs" / "example.md"
    assert plan.content_source_type == "content"
    assert plan.encoding == "utf-8"
    assert plan.normalized_content_source is None
    assert plan.inline_content == "hello"
    assert plan.mkdir_required is True



def test_build_write_plan_for_content_path_normalizes_relative_source_against_manifest(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    manifest_root = tmp_path / "patch"
    manifest_root.mkdir(parents=True, exist_ok=True)
    content_path = manifest_root / "content" / "docs" / "example.md"
    content_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_text("hello from file", encoding="utf-8")
    manifest_path = manifest_root / "patch_manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")
    spec = FileWriteSpec(path="docs/out.md", content=None, content_path="content/docs/example.md", encoding="utf-8")

    plan = build_write_plan(spec, target_root, manifest_path)

    assert plan.destination == target_root / "docs" / "out.md"
    assert plan.content_source_type == "content_path"
    assert plan.normalized_content_source == content_path
    assert plan.inline_content is None
    assert plan.mkdir_required is True



def test_build_write_plan_marks_mkdir_requirement_false_when_parent_exists(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    destination_parent = target_root / "docs"
    destination_parent.mkdir(parents=True, exist_ok=True)
    spec = FileWriteSpec(path="docs/example.md", content="hello", content_path=None, encoding="utf-8")

    plan = build_write_plan(spec, target_root)

    assert plan.mkdir_required is False



def test_load_content_preserves_inline_content_contract() -> None:
    spec = FileWriteSpec(path="docs/example.md", content="inline hello", content_path=None, encoding="utf-8")

    assert load_content(spec) == "inline hello"



def test_load_content_reads_from_manifest_relative_content_path(tmp_path: Path) -> None:
    manifest_root = tmp_path / "patch"
    manifest_root.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_root / "patch_manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")
    content_path = manifest_root / "content" / "docs" / "example.md"
    content_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_text("file hello", encoding="utf-8")
    spec = FileWriteSpec(path="docs/example.md", content=None, content_path="content/docs/example.md", encoding="utf-8")

    assert load_content(spec, manifest_path) == "file hello"