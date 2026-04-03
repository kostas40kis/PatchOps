from pathlib import Path

from patchops.initial_milestone_gate import (
    REQUIRED_ARCHITECTURE_SENTINELS,
    REQUIRED_INITIAL_MILESTONE_TESTS,
    build_initial_milestone_gate,
    initial_milestone_gate_as_dict,
    initial_milestone_is_complete,
    render_initial_milestone_gate_lines,
)
from patchops.readiness import (
    REQUIRED_INITIAL_MILESTONE_DOCS,
    REQUIRED_INITIAL_MILESTONE_EXAMPLES,
    REQUIRED_INITIAL_MILESTONE_PROFILES,
    REQUIRED_INITIAL_MILESTONE_WORKFLOWS,
)


def test_initial_milestone_gate_is_complete_when_everything_exists(tmp_path: Path) -> None:
    for relative in (
        *REQUIRED_INITIAL_MILESTONE_DOCS,
        *REQUIRED_INITIAL_MILESTONE_EXAMPLES,
        *REQUIRED_INITIAL_MILESTONE_WORKFLOWS,
        *REQUIRED_INITIAL_MILESTONE_TESTS,
        *REQUIRED_ARCHITECTURE_SENTINELS,
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok", encoding="utf-8")

    gate = build_initial_milestone_gate(
        tmp_path,
        available_profiles=REQUIRED_INITIAL_MILESTONE_PROFILES,
        core_tests_green=True,
    )

    assert gate.status == "complete"
    assert initial_milestone_is_complete(gate) is True
    assert gate.issues == ()


def test_initial_milestone_gate_is_not_ready_when_tests_or_architecture_are_missing(tmp_path: Path) -> None:
    gate = build_initial_milestone_gate(
        tmp_path,
        available_profiles=("trader",),
        core_tests_green=False,
    )

    assert gate.status == "not_ready"
    assert gate.tests_ok is False
    assert gate.architecture_ok is False
    assert "missing required tests" in gate.issues
    assert "major architecture drift detected" in gate.issues


def test_initial_milestone_gate_lines_are_human_readable() -> None:
    gate = build_initial_milestone_gate(
        Path('.'),
        available_profiles=(),
        core_tests_green=False,
    )
    lines = render_initial_milestone_gate_lines(gate)

    assert "Surface  : final initial milestone gate" in lines
    assert "Status   : not_ready" in lines
    assert any(line.startswith("Readiness:") for line in lines)
    assert any(line.startswith("Tests    :") for line in lines)
    assert any(line.startswith("Arch     :") for line in lines)
    assert any(line.startswith("Core     :") for line in lines)


def test_initial_milestone_gate_as_dict_exposes_required_sets() -> None:
    gate = build_initial_milestone_gate(
        Path('.'),
        available_profiles=("trader",),
        core_tests_green=False,
    )
    payload = initial_milestone_gate_as_dict(gate)

    assert payload["status"] == "not_ready"
    assert isinstance(payload["missing_tests"], tuple)
    assert isinstance(payload["missing_architecture"], tuple)
    assert payload["required_tests"] == REQUIRED_INITIAL_MILESTONE_TESTS
    assert payload["required_architecture_sentinels"] == REQUIRED_ARCHITECTURE_SENTINELS
