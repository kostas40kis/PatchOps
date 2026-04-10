from pathlib import Path


def _read(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_readme_mentions_recovery_frontier_and_truth_rules() -> None:
    text = _read("README.md")
    assert "post-Patch-29 recovery stream is now green through the accepted recovery frontier regression gate" in text
    assert "treat any outer PASS with fatal stderr and no detected inner report as a failure" in text
    assert "setup-windows-env" in text
    assert "emit-operator-script" in text


def test_operator_quickstart_mentions_preflight_and_smoke_proof() -> None:
    text = _read("docs/operator_quickstart.md")
    assert "PatchOps validates bundle shape and metadata before launcher execution" in text
    assert "generated-helper syntax gate" in text
    assert "emitted `patchops-entry-ps1` forwarding is locked by live proof against the repo" in text


def test_project_status_preserves_patch_29_historical_clarification() -> None:
    text = _read("docs/project_status.md")
    assert "Do not describe the old Patch 29 operator-script wave as accepted" in text
    assert "green recovery frontier" in text
    assert "documentation refresh and then narrow doc-contract locking" in text


def test_llm_usage_keeps_code_first_docs_last_and_canonical_truth() -> None:
    text = _read("docs/llm_usage.md")
    assert "Treat the canonical report as the truth surface for each run" in text
    assert "Use code-first / docs-last discipline" in text
    assert "legacy launcher compatibility still exists for bare transport/demo bundles where appropriate" in text
