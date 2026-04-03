from __future__ import annotations

from pathlib import Path

import patchops.files.writers as writers
from patchops.models import WriteRecord


def test_write_single_file_creates_parent_directory_and_writes_text(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "notes" / "example.txt"

    record = writers.write_single_file(destination, "hello from helper", encoding="utf-8")

    assert destination.exists()
    assert destination.read_text(encoding="utf-8") == "hello from helper"
    assert record == WriteRecord(path=destination, encoding="utf-8")


def test_write_text_file_delegates_to_single_file_helper(tmp_path: Path, monkeypatch) -> None:
    destination = tmp_path / "target" / "delegated.txt"
    captured: dict[str, object] = {}
    expected = WriteRecord(path=destination, encoding="utf-8")

    def fake_write_single_file(path: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
        captured["path"] = path
        captured["content"] = content
        captured["encoding"] = encoding
        return expected

    monkeypatch.setattr(writers, "write_single_file", fake_write_single_file)

    result = writers.write_text_file(destination, "delegated payload", encoding="utf-8")

    assert result == expected
    assert captured == {
        "path": destination,
        "content": "delegated payload",
        "encoding": "utf-8",
    }
