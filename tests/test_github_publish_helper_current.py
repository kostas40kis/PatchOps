from pathlib import Path


def test_github_publish_helper_contains_windows_powershell_compat_and_safety_guards() -> None:
    script = Path("powershell/Push-PatchOpsToGitHub.ps1").read_text(encoding="utf-8")

    assert "Convert-ToWindowsArgumentString" in script
    assert "$psi.Arguments = Convert-ToWindowsArgumentString -Args $Args" in script
    assert "ArgumentList" not in script
    assert "index.lock" in script
    assert "remote', 'get-url', 'origin'" in script
    assert "data/runtime/" in script
    assert "'main'" in script
    assert "https://github.com/kostas40kis/PatchOps.git" in script


def test_github_publish_helper_stages_the_maintained_repo_surfaces() -> None:
    script = Path("powershell/Push-PatchOpsToGitHub.ps1").read_text(encoding="utf-8")

    for expected in [
        "'README.md'",
        "'pyproject.toml'",
        "'docs'",
        "'examples'",
        "'handoff'",
        "'llm'",
        "'onboarding'",
        "'patchops'",
        "'powershell'",
        "'tests'",
    ]:
        assert expected in script


def test_operator_quickstart_mentions_manual_github_publish_helper() -> None:
    quickstart = Path("docs/operator_quickstart.md").read_text(encoding="utf-8")

    assert "Push-PatchOpsToGitHub.ps1" in quickstart
    assert "manual" in quickstart
    assert "not" in quickstart and "automatic" in quickstart
    assert "ProcessStartInfo.Arguments" in quickstart
