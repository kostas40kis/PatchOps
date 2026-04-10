from pathlib import Path


def test_post_publish_snapshot_mentions_published_state_and_key_surfaces() -> None:
    text = Path("docs/post_publish_snapshot.md").read_text(encoding="utf-8")

    assert "Patch 25A" in text
    assert "main" in text
    assert "run-package" in text
    assert "check-bundle" in text
    assert "bundle-doctor" in text
    assert "maintenance-gate" in text
    assert "emit-operator-script" in text
    assert "bootstrap-repair" in text
    assert "Push-PatchOpsToGitHub.ps1" in text
    assert "canonical Desktop txt report" in text
