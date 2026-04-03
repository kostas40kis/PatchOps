from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_project_packet_workflow_doc_stays_aligned_with_onboarding_and_handoff() -> None:
    content = _read("docs/project_packet_workflow.md")

    required_fragments = [
        "two-step onboarding workflow",
        "Step 1 — generic PatchOps orientation",
        "Step 2 — project packet creation and use",
        "docs/projects/",
        "brand-new target project",
        "handoff bundle",
        "project packets and handoff",
        "generic docs teach PatchOps",
        "project packets teach one target project",
        "manifests tell PatchOps what to do now",
        "reports prove what happened",
    ]

    for fragment in required_fragments:
        assert fragment in content, f"Missing workflow fragment: {fragment}"


def test_trader_project_packet_contains_required_roots_boundaries_and_examples() -> None:
    content = _read("docs/projects/trader.md")

    required_fragments = [
        "Trader project packet",
        r"C:\dev\trader",
        r"C:\dev\patchops",
        r"C:\dev\trader\.venv\Scripts\python.exe",
        "Expected profile:",
        "`trader`",
        "What must remain outside PatchOps",
        "examples/trader_first_verify_patch.json",
        "examples/trader_first_doc_patch.json",
        "Current state",
        "Latest passed patch",
        "Latest attempted patch",
        "Current blockers",
        "Next recommended action",
        "one canonical report",
    ]

    for fragment in required_fragments:
        assert fragment in content, f"Missing trader packet fragment: {fragment}"
