from pathlib import Path

from patchops.manifest_loader import load_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_allowed_exit_example_loads_with_expected_codes() -> None:
    manifest = load_manifest(PROJECT_ROOT / "examples" / "generic_allowed_exit_patch.json")
    assert manifest.patch_name == "generic_allowed_exit_example"
    assert len(manifest.validation_commands) == 1
    command = manifest.validation_commands[0]
    assert command.name == "intentional_non_zero_ok"
    assert command.allowed_exit_codes == [0, 3]


def test_examples_doc_mentions_allowed_exit_example() -> None:
    content = (PROJECT_ROOT / "docs" / "examples.md").read_text(encoding="utf-8")
    assert "generic_allowed_exit_patch.json" in content
    assert "allowed_exit_codes" in content


def test_manifest_schema_doc_mentions_allowed_exit_codes() -> None:
    content = (PROJECT_ROOT / "docs" / "manifest_schema.md").read_text(encoding="utf-8")
    assert "allowed_exit_codes" in content
    assert "generic_allowed_exit_patch.json" in content
