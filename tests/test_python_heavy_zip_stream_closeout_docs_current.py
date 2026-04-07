from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_native_zip_transition_doc_matches_finished_operator_flow() -> None:
    text = _read("docs/native_zip_transition.md")
    assert "you no longer manually unzip bundles" in text
    assert 'py -m patchops.cli run-package "<bundle.zip>" --wrapper-root "C:\\dev\\patchops"' in text
    assert "read the outer canonical report first" in text
    assert "bundled launchers still need to stay thin and boring" in text
    assert "preflight_bundle_zip(...)" in text


def test_python_heavy_zip_stream_closeout_doc_covers_python_owned_surfaces() -> None:
    text = _read("docs/python_heavy_zip_stream_closeout.md")
    assert "build_patchops_bundle_launcher(...)" in text
    assert "find_common_launcher_mistakes(...)" in text
    assert "preflight_bundle_zip(...)" in text
    assert "classify_bundle_run_failure(...)" in text
    assert "create_starter_bundle(...)" in text
    assert "PowerShell remains a thin boundary" in text
    assert "one canonical Desktop txt report" in text
    assert "still not implemented here" in text


def test_example_bundle_readme_matches_zip_native_stage() -> None:
    text = _read("examples/bundles/example_generic_python_patch_bundle/README.txt")
    assert "create_starter_bundle(...)" in text
    assert "do **not** manually unzip the delivered `.zip`" in text
    assert 'py -m patchops.cli run-package "<bundle.zip>" --wrapper-root "C:\\dev\\patchops"' in text
    assert "let PatchOps extract the bundle and call the bundled launcher" in text


def test_handoff_closeout_summarizes_finished_stream_without_overclaim() -> None:
    text = _read("handoff/python_heavy_zip_stream_closeout.md")
    assert "Patch 19 helper-family proof" in text
    assert "Patch 20 docs/examples/handoff closeout" in text
    assert "Start from the raw zip." in text
    assert "PowerShell remains a thin operator boundary" in text
    assert "not implemented in this closeout" in text
