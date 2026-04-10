from pathlib import Path

from patchops.bundles.root_launcher_contract import emit_run_with_patchops_launcher


def _first_non_whitespace(text: str) -> str:
    for ch in text:
        if not ch.isspace():
            return ch
    raise AssertionError("launcher text was empty")


def test_root_launcher_starts_with_param_on_first_line() -> None:
    text = emit_run_with_patchops_launcher()
    assert text.startswith("param(\n")
    assert text.splitlines()[0] == "param("
    assert _first_non_whitespace(text) == "p"


def test_root_launcher_has_no_stray_leading_backslash() -> None:
    text = emit_run_with_patchops_launcher()
    assert not text.startswith("\\")
    assert "\n\\\nparam(" not in text


def test_root_launcher_delegates_to_bundle_entry() -> None:
    text = emit_run_with_patchops_launcher()
    assert 'py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot' in text
    assert '$bundleMetaPath = Join-Path $bundleRoot "bundle_meta.json"' in text


def test_root_launcher_shape_doc_mentions_first_line_param_contract() -> None:
    doc = Path("docs/root_launcher_shape_contract.md").read_text(encoding="utf-8")
    assert "must begin with `param(` on the **first line**" in doc
    assert "no stray leading character" in doc
    assert "leading backslash" in doc
