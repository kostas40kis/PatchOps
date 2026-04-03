from pathlib import Path

from patchops.readiness import (
    REQUIRED_INITIAL_MILESTONE_DOCS,
    REQUIRED_INITIAL_MILESTONE_EXAMPLES,
    REQUIRED_INITIAL_MILESTONE_PROFILES,
    REQUIRED_INITIAL_MILESTONE_WORKFLOWS,
    build_initial_milestone_readiness,
    readiness_as_dict,
    readiness_is_green,
    render_initial_milestone_readiness_lines,
)


def test_readiness_surface_is_green_when_all_requirements_are_present(tmp_path: Path) -> None:
    for relative in REQUIRED_INITIAL_MILESTONE_DOCS + REQUIRED_INITIAL_MILESTONE_EXAMPLES + REQUIRED_INITIAL_MILESTONE_WORKFLOWS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok", encoding="utf-8")

    readiness = build_initial_milestone_readiness(
        tmp_path,
        available_profiles=REQUIRED_INITIAL_MILESTONE_PROFILES,
        core_tests_green=True,
    )

    assert readiness.status == "green"
    assert readiness_is_green(readiness) is True
    assert readiness.issues == ()


def test_readiness_surface_is_not_ready_when_docs_examples_profiles_or_workflows_are_missing(tmp_path: Path) -> None:
    readiness = build_initial_milestone_readiness(
        tmp_path,
        available_profiles=("trader",),
        core_tests_green=False,
    )

    assert readiness.status == "not_ready"
    assert readiness.docs_ok is False
    assert readiness.examples_ok is False
    assert readiness.profiles_ok is False
    assert readiness.workflows_ok is False
    assert readiness.core_tests_green is False
    assert "missing required docs" in readiness.issues
    assert "missing required examples" in readiness.issues
    assert "missing required profiles" in readiness.issues
    assert "missing required workflows" in readiness.issues
    assert "core tests are not green" in readiness.issues


def test_readiness_lines_are_human_readable() -> None:
    readiness = build_initial_milestone_readiness(
        Path('.'),
        available_profiles=(),
        core_tests_green=False,
    )
    lines = render_initial_milestone_readiness_lines(readiness)

    assert "Surface  : initial milestone readiness" in lines
    assert "Status   : not_ready" in lines
    assert any(line.startswith("Docs     :") for line in lines)
    assert any(line.startswith("Examples :") for line in lines)
    assert any(line.startswith("Profiles :") for line in lines)
    assert any(line.startswith("Workflows:") for line in lines)
    assert any(line.startswith("Tests    :") for line in lines)


def test_readiness_as_dict_exposes_missing_details() -> None:
    readiness = build_initial_milestone_readiness(
        Path('.'),
        available_profiles=("trader",),
        core_tests_green=False,
    )
    payload = readiness_as_dict(readiness)

    assert payload["status"] == "not_ready"
    assert isinstance(payload["missing_docs"], tuple)
    assert isinstance(payload["missing_examples"], tuple)
    assert isinstance(payload["missing_profiles"], tuple)
    assert isinstance(payload["missing_workflows"], tuple)
