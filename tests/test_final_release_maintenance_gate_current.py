from pathlib import Path


def test_final_release_maintenance_gate_packet_states_validation_first_verdict() -> None:
    text = Path("docs/final_release_maintenance_gate.md").read_text(encoding="utf-8")

    required_phrases = [
        "F6 — final release / maintenance gate",
        "validation-first",
        "explicit maintenance-mode verdict",
        "maintenance mode",
        "maintenance-gate",
        "release-readiness",
        "continuation is mechanical",
        "onboarding is mechanical",
        "one canonical Desktop txt report",
        "do not widen the product",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_final_release_maintenance_gate_packet_points_to_current_verdict_surfaces() -> None:
    text = Path("docs/final_release_maintenance_gate.md").read_text(encoding="utf-8")

    required_paths = [
        "README.md",
        "docs/project_status.md",
        "docs/finalization_master_plan.md",
        "docs/post_publish_snapshot.md",
        "docs/maintenance_freeze_packet.md",
    ]
    for path in required_paths:
        assert path in text
