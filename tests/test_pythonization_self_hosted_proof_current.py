from pathlib import Path


def test_pythonization_self_hosted_proof_note_present() -> None:
    text = Path("docs/project_status.md").read_text(encoding="utf-8")
    assert 'Pythonization self-hosted proof is now exercised through PatchOps itself.' in text
    assert 'This proof uses check, inspect, plan, and apply against PatchOps itself while keeping the repo changes narrow and maintenance-facing.' in text
