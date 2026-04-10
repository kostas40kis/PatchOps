from pathlib import Path


def test_overview_reflects_current_maintained_surfaces() -> None:
    text = Path("docs/overview.md").read_text(encoding="utf-8")
    assert "run-package" in text
    assert "check-bundle" in text
    assert "bootstrap repair" in text
    assert "GitHub publish" in text
    assert "canonical root launcher shape contract" in text


def test_profile_system_keeps_generic_python_self_hosted_rule() -> None:
    text = Path("docs/profile_system.md").read_text(encoding="utf-8")
    assert "`generic_python`" in text
    assert "Start with the smallest correct profile" in text
    assert "keep the wrapper project-agnostic" in text


def test_manifest_schema_keeps_review_and_report_contracts() -> None:
    text = Path("docs/manifest_schema.md").read_text(encoding="utf-8")
    assert "`check`" in text
    assert "`inspect`" in text
    assert "`plan`" in text
    assert "one canonical Desktop txt report" in text
    assert "manifest remains the execution contract" in text


def test_compatibility_notes_capture_arguments_and_launcher_rules() -> None:
    text = Path("docs/compatibility_notes.md").read_text(encoding="utf-8")
    assert "ProcessStartInfo.ArgumentList" in text
    assert "ProcessStartInfo.Arguments" in text
    assert "param(" in text
    assert "no stray leading character before `param(...)`" in text
    assert "repair the first failing layer only" in text
