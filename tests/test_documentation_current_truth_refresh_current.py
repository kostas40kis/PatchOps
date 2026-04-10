\
from pathlib import Path


def test_readme_refreshes_current_truth_and_source_bundle_surface() -> None:
    text = Path("README.md").read_text(encoding="utf-8").lower()

    assert "final pre-documentation proof stop" in text
    assert "handoff/final_future_llm_source_bundle.txt" in text
    assert "patchops/reporting/" in text
    assert "patchops/failure_categories.py" in text
    assert "historical patch 29 operator-script attempts should not be treated as the accepted success state on their own" in text


def test_project_status_distinguishes_frontier_and_next_doc_phase() -> None:
    text = Path("docs/project_status.md").read_text(encoding="utf-8").lower()

    assert "green through the final pre-documentation proof stop" in text
    assert "the old patch 29 attempts exposed the seams" in text
    assert "the later recovery patches repaired those seams" in text
    assert "patchops/reporting/" in text
    assert "patchops/failure_categories.py" in text
    assert "documentation discrepancy closure" in text
    assert "packet and handoff refresh" in text


def test_llm_usage_prefers_current_module_layout_and_current_examples() -> None:
    text = Path("docs/llm_usage.md").read_text(encoding="utf-8").lower()

    assert "handoff/final_future_llm_source_bundle.txt" in text
    assert "patchops/reporting/" in text
    assert "patchops/failure_categories.py" in text
    assert "generic_python_powershell_patch.json" in text
    assert "generic_python_powershell_verify_patch.json" in text
    assert "trader_first_doc_patch.json" in text
    assert "trader_first_verify_patch.json" in text
    assert "stale exports that mention missing flat files" in text


def test_operator_quickstart_and_examples_reflect_current_bundle_and_example_story() -> None:
    quickstart = Path("docs/operator_quickstart.md").read_text(encoding="utf-8").lower()
    examples = Path("docs/examples.md").read_text(encoding="utf-8").lower()

    assert "bundle-doctor" in quickstart
    assert "handoff/final_future_llm_source_bundle.txt" in quickstart
    assert "bundle-entry path" in quickstart
    assert "examples/generic_python_powershell_patch.json" in examples
    assert "examples/generic_python_powershell_verify_patch.json" in examples
    assert "examples/bundles/generic_apply_bundle/" in examples
    assert "examples/bundles/generic_verify_bundle/" in examples
