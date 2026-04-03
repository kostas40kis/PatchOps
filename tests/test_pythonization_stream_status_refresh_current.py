from pathlib import Path


def _read(repo_root: Path, relative_path: str) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8")


def test_project_status_marks_pythonization_stream_complete():
    repo_root = Path(__file__).resolve().parents[1]
    text = _read(repo_root, "docs/project_status.md")
    assert "## Pythonization stream status" in text
    assert "complete through MP51" in text
    assert "self-hosted PatchOps-on-PatchOps proof run" in text
    assert "did not widen PowerShell into a second workflow engine" in text


def test_patch_ledger_mentions_mp51_if_present():
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "docs/patch_ledger.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    assert "MP51" in text
    assert "Pythonization stream" in text


def test_handoff_surfaces_mark_stream_complete_if_present():
    repo_root = Path(__file__).resolve().parents[1]
    handoff_path = repo_root / "handoff/current_handoff.md"
    if handoff_path.exists():
        handoff_text = handoff_path.read_text(encoding="utf-8")
        assert "Pythonization stream: complete through MP51." in handoff_text

    prompt_path = repo_root / "handoff/next_prompt.txt"
    if prompt_path.exists():
        prompt_text = prompt_path.read_text(encoding="utf-8")
        assert prompt_text.startswith("Pythonization stream: complete through MP51.")
