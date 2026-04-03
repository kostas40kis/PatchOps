from pathlib import Path

from patchops.files.backups import backup_file, generate_backup_root


def test_generate_backup_root_includes_patch_name(tmp_path: Path):
    root = generate_backup_root(tmp_path, "data/runtime/patch_backups", "My Patch")
    assert "my_patch" in str(root)


def test_backup_file_records_missing_file(tmp_path: Path):
    source = tmp_path / "missing.txt"
    record = backup_file(source, tmp_path, tmp_path / "backups")
    assert record.existed is False
    assert record.destination is None
