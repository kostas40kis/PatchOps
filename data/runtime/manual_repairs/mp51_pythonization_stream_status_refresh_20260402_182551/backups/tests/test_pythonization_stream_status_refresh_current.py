from pathlib import Path


def test_project_status_records_pythonization_stream_closed() -> None:
    text = Path("docs/project_status.md").read_text(encoding="utf-8")
    assert "Pythonization Stream Status" in text
    assert "closed through MP51" in text
    assert "MP50 proved a real PatchOps-on-PatchOps self-hosted apply path" in text


def test_patch_ledger_mentions_mp51_when_present() -> None:
    path = Path("docs/patch_ledger.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    assert "MP51 â€” Pythonization stream status refresh" in text


def test_handoff_mentions_closed_stream_when_present() -> None:
    path = Path("handoff/current_handoff.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    assert "Pythonization Stream Refresh" in text
    assert "closed through MP51" in text


def test_next_prompt_mentions_closed_stream_when_present() -> None:
    path = Path("handoff/next_prompt.txt")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    assert "Pythonization stream note:" in text
    assert "MP42 through MP51" in text
