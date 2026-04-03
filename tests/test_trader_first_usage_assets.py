from pathlib import Path
from patchops.manifest_loader import load_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_trader_first_usage_docs_exist() -> None:
    assert (PROJECT_ROOT / "docs" / "trader_manifest_authoring_checklist.md").exists()
    assert (PROJECT_ROOT / "docs" / "trader_safe_first_patch_types.md").exists()


def test_trader_first_starter_manifests_exist_and_load() -> None:
    doc_manifest = load_manifest(PROJECT_ROOT / "examples" / "trader_first_doc_patch.json")
    verify_manifest = load_manifest(PROJECT_ROOT / "examples" / "trader_first_verify_patch.json")

    assert doc_manifest.active_profile == "trader"
    assert verify_manifest.active_profile == "trader"
    assert doc_manifest.patch_name == "trader_first_doc_patch"
    assert verify_manifest.patch_name == "trader_first_verify_patch"


def test_trader_first_usage_guide_mentions_starters() -> None:
    content = (PROJECT_ROOT / "docs" / "trader_first_usage.md").read_text(encoding="utf-8")
    assert "trader_first_doc_patch.json" in content
    assert "trader_first_verify_patch.json" in content
