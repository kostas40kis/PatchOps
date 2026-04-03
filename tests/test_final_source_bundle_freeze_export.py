from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_f8_final_source_bundle_exists() -> None:
    bundle_path = PROJECT_ROOT / "handoff/final_future_llm_source_bundle.txt"
    assert bundle_path.exists(), "missing final future-LLM source bundle"

def test_f8_final_source_bundle_mentions_preferred_artifact_and_key_surfaces() -> None:
    text = (PROJECT_ROOT / "handoff/final_future_llm_source_bundle.txt").read_text(encoding="utf-8").lower()

    assert "preferred history-compression artifact" in text
    assert "docs/project_status.md" in text
    assert "handoff/current_handoff.md" in text
    assert "handoff/current_handoff.json" in text
    assert "handoff/latest_report_copy.txt" in text
    assert "docs/finalization_master_plan.md" in text
    assert "docs/project_packet_workflow.md" in text
    assert "docs/project_packet_contract.md" in text
    assert "docs/projects/trader.md" in text
    assert "examples/generic_python_powershell_patch.json" in text
    assert "examples/trader_first_verify_patch.json" in text

def test_f8_docs_name_the_final_bundle_explicitly() -> None:
    project_status = (PROJECT_ROOT / "docs/project_status.md").read_text(encoding="utf-8").lower()
    llm_usage = (PROJECT_ROOT / "docs/llm_usage.md").read_text(encoding="utf-8").lower()
    handoff_surface = (PROJECT_ROOT / "docs/handoff_surface.md").read_text(encoding="utf-8").lower()
    finalization = (PROJECT_ROOT / "docs/finalization_master_plan.md").read_text(encoding="utf-8").lower()
    patch_ledger = (PROJECT_ROOT / "docs/patch_ledger.md").read_text(encoding="utf-8").lower()

    assert "handoff/final_future_llm_source_bundle.txt" in project_status
    assert "handoff/final_future_llm_source_bundle.txt" in llm_usage
    assert "handoff/final_future_llm_source_bundle.txt" in handoff_surface
    assert "handoff/final_future_llm_source_bundle.txt" in finalization
    assert "## patch 132" in patch_ledger
    assert "freeze-export patch" in patch_ledger
