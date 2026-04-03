from pathlib import Path

from patchops.files.writers import write_text_file


def test_write_text_file_creates_parent_dirs(tmp_path: Path):
    destination = tmp_path / "nested" / "a.txt"
    record = write_text_file(destination, "hello")
    assert destination.read_text(encoding="utf-8") == "hello"
    assert record.path == destination
