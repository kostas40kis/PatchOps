from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8").lower()


def test_bundle_docs_describe_python_owned_root_launcher_emission() -> None:
    standard_text = _read("docs/zip_bundle_standard.md")
    template_text = _read("docs/bundle_authoring_template.md")

    required_standard = [
        "emit_root_bundle_launcher",
        "create_starter_bundle",
        "do not hand-author the saved root launcher",
        "top-level `param(...)` script-file form",
        "run_with_patchops.ps1",
        "metadata-driven mode",
    ]
    missing_standard = [phrase for phrase in required_standard if phrase not in standard_text]
    assert not missing_standard, f"zip bundle standard doc is missing required phrases: {missing_standard}"

    required_template = [
        "emit_root_bundle_launcher",
        "create_starter_bundle",
        "saved root launcher",
        "top-level `param(...)` script-file form",
        "keep inline `& { ... }` wrapping",
        "metadata-driven",
    ]
    missing_template = [phrase for phrase in required_template if phrase not in template_text]
    assert not missing_template, f"bundle authoring template doc is missing required phrases: {missing_template}"
