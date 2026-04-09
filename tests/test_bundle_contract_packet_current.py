from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_bundle_contract_packet_exists_and_is_llm_facing() -> None:
    text = _read("docs/bundle_contract_packet.md")
    assert "LLM-facing" in text or "LLM facing" in text
    assert "fresh LLM should be able to author a correct bundle using only this packet" in text


def test_bundle_contract_packet_defines_exact_bundle_tree_and_launcher_rule() -> None:
    text = _read("docs/bundle_contract_packet.md")
    required = [
        "Exact bundle tree",
        "manifest.json",
        "bundle_meta.json",
        "README.txt",
        "run_with_patchops.ps1",
        "content/",
        "Exact launcher rule",
        "top-level `param(...)` script-file form",
        "Do not hand-author the saved root launcher; emit it from Python.",
        "bundle-entry",
    ]
    for phrase in required:
        assert phrase in text


def test_bundle_contract_packet_defines_exact_metadata_fields_and_commands() -> None:
    text = _read("docs/bundle_contract_packet.md")
    metadata_fields = [
        "schema_version",
        "patch_name",
        "bundle_mode",
        "recommended_profile",
        "target_project",
        "target_project_root",
        "manifest_path",
        "content_root",
        "launcher_path",
    ]
    for phrase in metadata_fields:
        assert f"`{phrase}`" in text

    commands = [
        "make-bundle",
        "check-bundle",
        "inspect-bundle",
        "plan-bundle",
        "bundle-doctor",
        "build-bundle",
        "run-package",
        "continue patch by patch from evidence",
    ]
    for phrase in commands:
        assert phrase in text


def test_bundle_contract_packet_includes_good_and_bad_examples_and_what_not_to_do() -> None:
    text = _read("docs/bundle_contract_packet.md")
    required = [
        "What not to do",
        "Do not create multiple launcher variants",
        "Do not manually invent zip layout by hand.",
        "Do not skip `bundle-doctor`",
        "One good example",
        "good_example_bundle/",
        '"launcher_path": "run_with_patchops.ps1"',
        "One bad example",
        "bad_example_bundle/",
        "apply_with_patchops.ps1",
        "verify_with_patchops.ps1",
    ]
    for phrase in required:
        assert phrase in text
