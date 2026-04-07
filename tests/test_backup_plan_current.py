from __future__ import annotations

from pathlib import Path

from patchops.files.backups import BackupPlan, backup_file, build_backup_plan, execute_backup_plan


def test_build_backup_plan_preserves_relative_destination(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    source = target_root / "patchops" / "demo" / "sample.txt"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("hello", encoding="utf-8")
    backup_root = tmp_path / "backups"

    plan = build_backup_plan(source, target_root, backup_root)

    assert isinstance(plan, BackupPlan)
    assert plan.source == source
    assert plan.relative_path == Path("patchops/demo/sample.txt")
    assert plan.destination == backup_root / Path("patchops/demo/sample.txt")
    assert plan.existed is True
    assert plan.missing is False


def test_build_backup_plan_marks_missing_file_without_guessing_root(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    source = target_root / "docs" / "missing.md"
    backup_root = tmp_path / "backups"

    plan = build_backup_plan(source, target_root, backup_root)

    assert plan.source == source
    assert plan.relative_path == Path("docs/missing.md")
    assert plan.destination == backup_root / Path("docs/missing.md")
    assert plan.existed is False
    assert plan.missing is True


def test_execute_backup_plan_copies_existing_file(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    source = target_root / "pkg" / "file.txt"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("backup me", encoding="utf-8")
    backup_root = tmp_path / "backups"

    plan = build_backup_plan(source, target_root, backup_root)
    record = execute_backup_plan(plan)

    assert record.existed is True
    assert record.destination == backup_root / Path("pkg/file.txt")
    assert record.destination is not None
    assert record.destination.read_text(encoding="utf-8") == "backup me"


def test_backup_file_preserves_missing_file_contract(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    source = target_root / "pkg" / "missing.txt"
    backup_root = tmp_path / "backups"

    record = backup_file(source, target_root, backup_root)

    assert record.source == source
    assert record.destination is None
    assert record.existed is False
