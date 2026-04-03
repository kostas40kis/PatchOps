from pathlib import Path

from patchops.manifest_loader import load_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_smoke_audit_example_loads_with_expected_groups() -> None:
    manifest = load_manifest(PROJECT_ROOT / "examples" / "generic_smoke_audit_patch.json")
    assert manifest.patch_name == "generic_smoke_audit_example"
    assert len(manifest.validation_commands) == 1
    assert len(manifest.smoke_commands) == 1
    assert len(manifest.audit_commands) == 1
    assert len(manifest.cleanup_commands) == 0
    assert len(manifest.archive_commands) == 0


def test_cleanup_archive_example_loads_with_expected_groups() -> None:
    manifest = load_manifest(PROJECT_ROOT / "examples" / "generic_cleanup_archive_patch.json")
    assert manifest.patch_name == "generic_cleanup_archive_example"
    assert len(manifest.validation_commands) == 1
    assert len(manifest.smoke_commands) == 0
    assert len(manifest.audit_commands) == 0
    assert len(manifest.cleanup_commands) == 1
    assert len(manifest.archive_commands) == 1


def test_manifest_schema_doc_mentions_new_command_group_examples() -> None:
    content = (PROJECT_ROOT / "docs" / "manifest_schema.md").read_text(encoding="utf-8")
    assert "generic_smoke_audit_patch.json" in content
    assert "generic_cleanup_archive_patch.json" in content
