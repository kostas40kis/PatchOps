from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_llm_usage_mentions_self_hosted_patch_authoring_notes() -> None:
    content = (PROJECT_ROOT / "docs" / "llm_usage.md").read_text(encoding="utf-8")
    assert "## Self-hosted patch authoring notes for Windows PowerShell / ISE" in content
    assert "write the patch manifest as compact JSON" in content
    assert "do not add a trailing newline to the patch manifest" in content
    assert "validate the manifest immediately with `json.load(...)`" in content
    assert "ProcessStartInfo.Arguments" in content
    assert "ArgumentList" in content


def test_compatibility_notes_mentions_self_hosted_manifest_authoring_pattern() -> None:
    content = (PROJECT_ROOT / "docs" / "compatibility_notes.md").read_text(encoding="utf-8")
    assert "## Self-hosted manifest-authoring compatibility note" in content
    assert "PowerShell ISE" in content
    assert "avoid relying on `ProcessStartInfo.ArgumentList`" in content
    assert "compact JSON" in content
    assert "no trailing newline" in content
    assert "immediate `json.load(...)` validation" in content
