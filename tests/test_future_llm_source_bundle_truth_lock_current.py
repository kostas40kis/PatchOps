from pathlib import Path


def test_final_future_llm_source_bundle_avoids_stale_flat_missing_paths() -> None:
    text = Path("handoff/final_future_llm_source_bundle.txt").read_text(encoding="utf-8")

    assert "MISSING : patchops\\reporting.py" not in text
    assert "MISSING : patchops\\failure_classifier.py" not in text



def test_final_future_llm_source_bundle_mentions_current_modular_layout() -> None:
    text = Path("handoff/final_future_llm_source_bundle.txt").read_text(encoding="utf-8")

    assert "patchops\\reporting\\metadata.py" in text
    assert "patchops\\reporting\\sections.py" in text
    assert "patchops\\reporting\\command_sections.py" in text
    assert "patchops\\bundles\\root_launcher_contract.py" in text
    assert "patchops\\bundles\\launcher_heuristics.py" in text
    assert "patchops\\bundles\\shape_validation.py" in text



def test_final_future_llm_source_bundle_states_modular_layout_rule() -> None:
    text = Path("handoff/final_future_llm_source_bundle.txt").read_text(encoding="utf-8")

    assert "durable future-LLM upload artifact" in text
    assert "maintained repo layout is package-oriented" in text
