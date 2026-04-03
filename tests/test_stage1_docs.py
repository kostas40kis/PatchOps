from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_stage1_docs_exist() -> None:
    for relative in [
        "docs/operator_quickstart.md",
        "docs/command_matrix.md",
        "docs/repair_rerun_matrix.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_operator_quickstart_mentions_safe_flow() -> None:
    text = read_text("docs/operator_quickstart.md").lower()
    for token in ["profiles", "doctor", "examples", "template", "check", "inspect", "plan", "apply", "verify"]:
        assert token in text


def test_command_matrix_mentions_launchers() -> None:
    text = read_text("docs/command_matrix.md")
    for token in [
        "Invoke-PatchProfiles.ps1",
        "Invoke-PatchDoctor.ps1",
        "Invoke-PatchExamples.ps1",
        "Invoke-PatchTemplate.ps1",
        "Invoke-PatchCheck.ps1",
    ]:
        assert token in text


def test_repair_rerun_matrix_mentions_wrapper_only_and_verify_only() -> None:
    text = read_text("docs/repair_rerun_matrix.md").lower()
    assert "wrapper-only" in text
    assert "verify-only" in text
