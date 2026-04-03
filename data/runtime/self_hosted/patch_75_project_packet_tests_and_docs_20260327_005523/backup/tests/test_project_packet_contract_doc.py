from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_project_packet_contract_doc_contains_required_contract_sections() -> None:
    content = _read("docs/project_packet_contract.md")

    required_fragments = [
        "Project packet contract",
        "docs/projects/",
        "Required structure for every project packet",
        "Purpose of the target project",
        "Target root",
        "Expected runtime",
        "Selected profile",
        "What must remain outside PatchOps",
        "Recommended example manifests",
        "Patch classes expected for this target",
        "Development phases",
        "Validation strategy",
        "Report expectations",
        "Current state",
        "Latest passed patch",
        "Latest attempted patch",
        "Blockers",
        "Next recommended action",
        "Stable layer versus mutable layer",
        "How a future LLM should use a project packet",
    ]

    for fragment in required_fragments:
        assert fragment in content, f"Missing contract fragment: {fragment}"


def test_project_packet_contract_doc_preserves_core_architecture_rules() -> None:
    content = _read("docs/project_packet_contract.md")

    required_rules = [
        "PatchOps remains project-agnostic",
        "PowerShell remains thin",
        "Python owns reusable packet logic",
        "One canonical report per run remains the rule",
        "Profiles remain the executable abstraction",
        "Handoff remains the continuation surface",
        "Prefer additive change over redesign",
    ]

    for rule in required_rules:
        assert rule in content, f"Missing architecture rule: {rule}"
