from __future__ import annotations

from pathlib import Path

from patchops.files.writers import write_single_file, write_text_file
from patchops.models import WriteRecord


def test_write_single_file_creates_parent_directories_and_writes_utf8_without_bom(tmp_path):
    destination = tmp_path / "nested" / "folder" / "note.txt"
    content = "hello â€“ ÎšÎ±Î»Î·Î¼Î­ÏÎ±"

    record = write_single_file(destination, content, encoding="utf-8")

    assert isinstance(record, WriteRecord)
    assert record.path == destination
    assert record.encoding == "utf-8"
    assert destination.read_text(encoding="utf-8") == content
    assert destination.read_bytes() == content.encode("utf-8")


def test_write_text_file_delegates_to_single_file_writer(monkeypatch, tmp_path):
    destination = tmp_path / "delegated.txt"
    expected = WriteRecord(path=destination, encoding="utf-8")
    calls = []

    def fake_write_single_file(inner_destination: Path, inner_content: str, encoding: str = "utf-8") -> WriteRecord:
        calls.append((inner_destination, inner_content, encoding))
        return expected

    monkeypatch.setattr("patchops.files.writers.write_single_file", fake_write_single_file)

    result = write_text_file(destination, "payload", encoding="utf-8")

    assert result is expected
    assert calls == [(destination, "payload", "utf-8")]
