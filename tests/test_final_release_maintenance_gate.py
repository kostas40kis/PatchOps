from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_GATE_DOCS = (
    "README.md",
    "docs/project_status.md",
    "docs/llm_usage.md",
    "docs/operator_quickstart.md",
    "docs/examples.md",
    "docs/handoff_surface.md",
    "docs/project_packet_workflow.md",
    "docs/project_packet_contract.md",
    "docs/finalization_master_plan.md",
    "docs/release_checklist.md",
    "docs/stage1_freeze_checklist.md",
    "docs/patch_ledger.md",
)

REQUIRED_GATE_HANDOFF = (
    "handoff/current_handoff.md",
    "handoff/current_handoff.json",
    "handoff/latest_report_copy.txt",
)

REQUIRED_GATE_EXAMPLES = (
    "examples/generic_python_patch.json",
    "examples/generic_verify_patch.json",
    "examples/generic_python_powershell_patch.json",
    "examples/generic_python_powershell_verify_patch.json",
    "examples/trader_code_patch.json",
    "examples/trader_doc_patch.json",
    "examples/trader_verify_patch.json",
    "examples/trader_first_doc_patch.json",
    "examples/trader_first_verify_patch.json",
)

REQUIRED_GATE_PROFILES = (
    "patchops/profiles/trader.py",
    "patchops/profiles/generic_python.py",
    "patchops/profiles/generic_python_powershell.py",
)

REQUIRED_GATE_WORKFLOWS = (
    "patchops/cli.py",
    "patchops/readiness.py",
    "patchops/initial_milestone_gate.py",
    "patchops/workflows/verify_only.py",
    "patchops/workflows/wrapper_retry.py",
)

REQUIRED_GATE_LAUNCHERS = (
    "powershell/Invoke-PatchManifest.ps1",
    "powershell/Invoke-PatchVerify.ps1",
    "powershell/Invoke-PatchWrapperRetry.ps1",
    "powershell/Invoke-PatchHandoff.ps1",
    "powershell/Invoke-PatchReadiness.ps1",
)

def _assert_all_exist(paths: tuple[str, ...]) -> None:
    missing = [relative for relative in paths if not (PROJECT_ROOT / relative).exists()]
    assert not missing, "missing required gate surface(s): " + ", ".join(missing)

def test_f6_gate_required_surfaces_exist() -> None:
    for path_group in (
        REQUIRED_GATE_DOCS,
        REQUIRED_GATE_HANDOFF,
        REQUIRED_GATE_EXAMPLES,
        REQUIRED_GATE_PROFILES,
        REQUIRED_GATE_WORKFLOWS,
        REQUIRED_GATE_LAUNCHERS,
    ):
        _assert_all_exist(path_group)

def test_f6_project_status_records_current_gate_posture() -> None:
    text = (PROJECT_ROOT / "docs/project_status.md").read_text(encoding="utf-8")
    lowered = text.lower()

    assert "patchops_f6_gate_status:start" in lowered
    assert "patch 129k" in lowered
    assert "patch 130" in lowered
    assert "maintenance mode" in lowered
    assert "complete as an initial product" in lowered
    assert "additive or target-specific future work" in lowered

def test_f6_patch_ledger_records_gate_patch() -> None:
    text = (PROJECT_ROOT / "docs/patch_ledger.md").read_text(encoding="utf-8")
    lowered = text.lower()

    assert "## Patch 130" in text
    assert "final release / maintenance gate surface" in lowered
    assert "gate patch, not a redesign patch" in lowered
