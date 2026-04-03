from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
patch_root = Path(sys.argv[2]).resolve()
desktop = Path(sys.argv[3]).resolve()
patch_name = sys.argv[4]
validation_program = sys.argv[5]
validation_args_path = Path(sys.argv[6]).resolve()
validation_args = json.loads(validation_args_path.read_text(encoding="utf-8"))

manifest_schema_path = project_root / "docs/manifest_schema.md"
examples_doc_path = project_root / "docs/examples.md"
content_example_note_path = project_root / "examples/content/generic_content_path_note.txt"
test_content_examples_path = project_root / "tests/test_content_source_examples.py"

manifest_schema_current = manifest_schema_path.read_text(encoding="utf-8")
examples_doc_current = examples_doc_path.read_text(encoding="utf-8")

clarity_block = textwrap.dedent(
    """
    Relative `content_path` values should be authored as wrapper-relative paths from the wrapper project root.

    PatchOps now resolves a relative `content_path` against the wrapper project root first.
    If that wrapper-root candidate does not exist, PatchOps falls back to manifest-local resolution so older nested-manifest flows still work.
    The maintained authoring rule is still wrapper-relative, and the manifest-local behavior should be treated as compatibility fallback rather than the primary contract.
    """
).strip()

if "Relative `content_path` values should be authored as wrapper-relative paths from the wrapper project root." not in manifest_schema_current:
    anchor = (
        "`content_path` should be treated as a maintained authoring surface rather than a legacy edge case.\n"
        "It exists so larger or cleaner payloads can live beside the manifest instead of being embedded inline.\n"
    )
    replacement = anchor + "\n" + clarity_block + "\n"
    if anchor not in manifest_schema_current:
        raise RuntimeError("Could not find manifest_schema.md content_path anchor block.")
    manifest_schema_updated = manifest_schema_current.replace(anchor, replacement, 1)
else:
    manifest_schema_updated = manifest_schema_current

examples_append = textwrap.dedent(
    """

    ## content_path resolution rule

    `examples/generic_content_path_patch.json` demonstrates the maintained `content_path` authoring contract.

    Author relative `content_path` values as wrapper-relative paths from the wrapper project root.

    PatchOps resolves the wrapper-root candidate first. If that file does not exist, PatchOps falls back to manifest-local resolution so older nested-manifest flows still load cleanly. That manifest-local behavior is compatibility fallback, not the primary authoring rule.

    The external payload for the maintained example lives at `examples/content/generic_content_path_note.txt`.
    """
).rstrip() + "\n"

if "## content_path resolution rule" not in examples_doc_current:
    if not examples_doc_current.endswith("\n"):
        examples_doc_current += "\n"
    examples_doc_updated = examples_doc_current + examples_append
else:
    examples_doc_updated = examples_doc_current

content_example_note_updated = (
    "This file is referenced by generic_content_path_patch.json and demonstrates "
    "wrapper-relative content_path authoring from the wrapper project root.\n"
)

test_content_examples_updated = textwrap.dedent(
    """
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
    """
).lstrip()

patch_root.mkdir(parents=True, exist_ok=True)

manifest = {
    "manifest_version": "1",
    "patch_name": patch_name,
    "active_profile": "generic_python",
    "target_project_root": project_root.as_posix(),
    "backup_files": [],
    "files_to_write": [
        {
            "path": "docs/manifest_schema.md",
            "content": manifest_schema_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "docs/examples.md",
            "content": examples_doc_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "examples/content/generic_content_path_note.txt",
            "content": content_example_note_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_content_source_examples.py",
            "content": test_content_examples_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_docs_and_examples",
            "program": validation_program,
            "args": validation_args,
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
        "report_dir": desktop.as_posix(),
        "report_name_prefix": patch_name,
        "write_to_desktop": False,
    },
    "tags": ["content_path", "docs", "examples", "contract_lock"],
    "notes": (
        "Third repair-stream patch. "
        "This patch aligns manifest_schema.md, examples.md, example content, and example-contract tests "
        "with the repaired wrapper-relative content_path behavior and manifest-local fallback."
    ),
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "manifest_path": str(manifest_path),
    "manifest_schema_path": str(manifest_schema_path),
    "examples_doc_path": str(examples_doc_path),
    "content_example_note_path": str(content_example_note_path),
    "test_content_examples_path": str(test_content_examples_path),
}))