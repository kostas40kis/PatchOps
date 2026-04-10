from pathlib import Path


def test_bundle_workflow_docs_refresh_preserve_exact_bundle_tree_and_commands() -> None:
    zip_standard = Path("docs/zip_bundle_standard.md").read_text(encoding="utf-8")
    authoring = Path("docs/bundle_authoring_template.md").read_text(encoding="utf-8")
    packet = Path("docs/bundle_contract_packet.md").read_text(encoding="utf-8")

    for text in (zip_standard, packet):
        assert "run_with_patchops.ps1" in text
        assert "check-bundle" in text
        assert "inspect-bundle" in text
        assert "plan-bundle" in text
        assert "bundle-doctor" in text
        assert "build-bundle" in text
        assert "run-package" in text

    assert "content/" in zip_standard
    assert "content/" in packet
    assert "compatibility shim" in zip_standard
    assert "compatibility shim" in packet
    assert "stray leading `/` or `\\` characters" in zip_standard
    assert "stray leading `/` or `\\` characters" in packet

    assert "Generate the bundle from Python when possible." in authoring
    assert "bundle-entry" in authoring
    assert "single saved root launcher" in authoring
    assert "canonical Desktop txt report" in authoring
