from pathlib import Path


def test_profile_matrix_mentions_all_stage1_profiles() -> None:
    text = Path("docs/profile_matrix.md").read_text(encoding="utf-8")
    assert "trader" in text
    assert "generic_python" in text
    assert "generic_python_powershell" in text


def test_readme_mentions_generic_python_powershell_examples() -> None:
    text = Path("README.md").read_text(encoding="utf-8")
    assert "Generic Python + PowerShell profile examples" in text
    assert "generic_python_powershell" in text
