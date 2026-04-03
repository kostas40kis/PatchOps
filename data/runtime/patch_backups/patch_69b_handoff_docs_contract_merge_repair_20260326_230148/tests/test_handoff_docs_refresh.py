from pathlib import Path


def test_readme_points_to_handoff_first_takeover() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "Read these files in this order:" in text
    assert "1. `handoff/current_handoff.md`" in text
    assert "2. `handoff/current_handoff.json`" in text
    assert "3. `handoff/latest_report_copy.txt`" in text
    assert "run handoff export" in text
    assert "paste `handoff/next_prompt.txt`" in text


def test_project_status_declares_handoff_first_buildout_completed_through_patch_69() -> None:
    text = Path("docs/project_status.md").read_text(encoding="utf-8")

    assert "Stage 2 and the handoff-first UX buildout has been completed through Patch 69" in text
    assert "Patch 69: documentation stop for handoff-first onboarding" in text
    assert "run one export command" in text
    assert "paste one generated prompt" in text


def test_examples_doc_says_examples_are_not_first_state_reconstruction_surface() -> None:
    text = Path("docs/examples.md").read_text(encoding="utf-8")

    assert "Examples are no longer the first state-reconstruction surface" in text
    assert "1. `handoff/current_handoff.md`" in text
    assert "2. `handoff/current_handoff.json`" in text
    assert "3. `handoff/latest_report_copy.txt`" in text
    assert "Examples help you build the next manifest." in text


def test_handoff_surface_doc_marks_patch_69_documentation_stop() -> None:
    text = Path("docs/handoff_surface.md").read_text(encoding="utf-8")

    assert "Patch 69 is the documentation stop for the handoff-first UX." in text
    assert "`README.md`" in text
    assert "`docs/project_status.md`" in text
    assert "`docs/examples.md`" in text
    assert "Future onboarding should now start from the handoff artifact" in text


def test_llm_usage_doc_still_points_to_handoff_first() -> None:
    text = Path("docs/llm_usage.md").read_text(encoding="utf-8")

    assert "This file is the orientation page for future coding LLMs." in text
    assert "It is not the main state-reconstruction surface anymore." in text
    assert "1. `handoff/current_handoff.md`" in text
    assert "2. `handoff/current_handoff.json`" in text
    assert "3. `handoff/latest_report_copy.txt`" in text