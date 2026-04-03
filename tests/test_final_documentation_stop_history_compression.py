from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOC_MARKERS = {
    "README.md": "PATCHOPS_F7_FINAL_DOC_STOP_README:START",
    "docs/project_status.md": "PATCHOPS_F7_FINAL_DOC_STOP_STATUS:START",
    "docs/llm_usage.md": "PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:START",
    "docs/operator_quickstart.md": "PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:START",
    "docs/examples.md": "PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:START",
    "docs/handoff_surface.md": "PATCHOPS_F7_FINAL_DOC_STOP_HANDOFF:START",
    "docs/project_packet_workflow.md": "PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:START",
    "docs/project_packet_contract.md": "PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:START",
    "docs/finalization_master_plan.md": "PATCHOPS_F7_FINAL_DOC_STOP_FINALIZATION_PLAN:START",
}

def test_f7_doc_stop_markers_exist() -> None:
    for relative_path, marker in DOC_MARKERS.items():
        text = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        assert marker in text, f"missing F7 marker in {relative_path}"

def test_f7_reading_order_and_boundary_language_is_present() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8").lower()
    llm_usage = (PROJECT_ROOT / "docs/llm_usage.md").read_text(encoding="utf-8").lower()
    operator = (PROJECT_ROOT / "docs/operator_quickstart.md").read_text(encoding="utf-8").lower()
    project_status = (PROJECT_ROOT / "docs/project_status.md").read_text(encoding="utf-8").lower()
    packet_workflow = (PROJECT_ROOT / "docs/project_packet_workflow.md").read_text(encoding="utf-8").lower()
    packet_contract = (PROJECT_ROOT / "docs/project_packet_contract.md").read_text(encoding="utf-8").lower()
    handoff_surface = (PROJECT_ROOT / "docs/handoff_surface.md").read_text(encoding="utf-8").lower()
    examples = (PROJECT_ROOT / "docs/examples.md").read_text(encoding="utf-8").lower()
    patch_ledger = (PROJECT_ROOT / "docs/patch_ledger.md").read_text(encoding="utf-8").lower()
    finalization_plan = (PROJECT_ROOT / "docs/finalization_master_plan.md").read_text(encoding="utf-8").lower()

    assert "handoff/current_handoff.md" in readme
    assert "brand-new target project" in readme
    assert "historical anchors" in readme
    assert "target-specific extension work" in readme

    assert "generic onboarding packet" in llm_usage
    assert "handoff/current_handoff.json" in llm_usage

    assert "path a - continue already-running patchops work" in operator
    assert "path b - start a brand-new target project" in operator

    assert "finished as an initial product" in project_status
    assert "optional future work" in project_status
    assert "target-specific extension work" in project_status

    assert "use the project-packet workflow only for brand-new target projects" in packet_workflow
    assert "start from the handoff bundle instead" in packet_workflow

    assert "stable layer" in packet_contract
    assert "mutable layer" in packet_contract
    assert "does not replace" in packet_contract

    assert "maintained continuation surface for already-running patchops work" in handoff_surface
    assert "does not replace" in handoff_surface

    assert "generic_python_powershell_patch.json" in examples
    assert "trader_first_verify_patch.json" in examples

    assert "## patch 131" in patch_ledger
    assert "history-compression patch" in patch_ledger

    assert "f6 has already passed" in finalization_plan
    assert "history disappears" in finalization_plan

def test_f7_final_docs_preserve_start_here_distinction() -> None:
    llm_usage = (PROJECT_ROOT / "docs/llm_usage.md").read_text(encoding="utf-8").lower()
    operator = (PROJECT_ROOT / "docs/operator_quickstart.md").read_text(encoding="utf-8").lower()

    assert "if patchops work is already in progress" in llm_usage
    assert "if you are starting a brand-new target project" in llm_usage
    assert "already-running patchops work" in operator
    assert "brand-new target project" in operator
