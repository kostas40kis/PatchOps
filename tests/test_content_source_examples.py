from pathlib import Path

from patchops.manifest_loader import load_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_content_path_example_loads_with_external_content_reference() -> None:
    manifest = load_manifest(PROJECT_ROOT / "examples" / "generic_content_path_patch.json")
    assert manifest.patch_name == "generic_content_path_example"
    assert len(manifest.files_to_write) == 1

    entry = manifest.files_to_write[0]
    assert entry.path == "CONTENT_PATH_EXAMPLE.txt"
    assert entry.content is None
    assert entry.content_path == "examples/content/generic_content_path_note.txt"
    assert entry.encoding == "utf-8"


def test_examples_doc_mentions_content_path_example() -> None:
    content = (PROJECT_ROOT / "docs" / "examples.md").read_text(encoding="utf-8")
    assert "generic_content_path_patch.json" in content
    assert "generic_content_path_note.txt" in content


def test_manifest_schema_doc_mentions_content_path_guidance() -> None:
    content = (PROJECT_ROOT / "docs" / "manifest_schema.md").read_text(encoding="utf-8")
    assert "content_path" in content
    assert "files_to_write entries" in content


def test_manifest_schema_doc_states_wrapper_relative_content_path_rule() -> None:
    content = (PROJECT_ROOT / "docs" / "manifest_schema.md").read_text(encoding="utf-8")
    assert "wrapper-relative paths from the wrapper project root" in content
    assert "falls back to manifest-local resolution" in content
    assert "compatibility fallback rather than the primary contract" in content


def test_examples_doc_states_content_path_resolution_rule() -> None:
    content = (PROJECT_ROOT / "docs" / "examples.md").read_text(encoding="utf-8")
    assert "## content_path resolution rule" in content
    assert "wrapper-relative paths from the wrapper project root" in content
    assert "falls back to manifest-local resolution" in content
    assert "compatibility fallback, not the primary authoring rule" in content
