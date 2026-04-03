from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_project_packet_workflow_distinguishes_onboarding_from_handoff() -> None:
    content = read_text("docs/project_packet_workflow.md")
    lowered = content.lower()

    assert "two-step onboarding" in lowered
    assert "generic patchops orientation" in lowered
    assert "project packet creation and use" in lowered
    assert "handoff/current_handoff.md" in content
    assert "brand-new target project" in lowered


def test_trader_project_packet_contains_required_roots_profile_and_boundaries() -> None:
    content = read_text("docs/projects/trader.md")
    lowered = content.lower()

    assert r"C:\dev\trader" in content
    assert r"C:\dev\patchops" in content
    assert "`trader`" in content or "expected profile" in lowered
    assert "what must remain outside patchops" in lowered
    assert "recommended example manifests" in lowered
    assert "current state" in lowered
