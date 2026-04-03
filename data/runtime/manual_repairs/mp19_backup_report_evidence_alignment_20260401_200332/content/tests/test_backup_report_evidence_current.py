from __future__ import annotations

from pathlib import Path

from patchops.files.backups import (
    BackupExecution,
    build_backup_plan,
    execute_backup,
    render_backup_report_line,
    render_backup_report_lines,
)



def test_render_backup_report_line_for_existing_file_uses_backup_mapping(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    source = target_root / "patchops" / "files" / "backups.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("content", encoding="utf-8")
    backup_root = tmp_path / "backups"

    execution = execute_backup(build_backup_plan(source, target_root, backup_root))

    assert isinstance(execution, BackupExecution)
    assert render_backup_report_line(execution) == (
        f"BACKUP : {source} -> {backup_root / Path('patchops/files/backups.py')}"
    )



def test_render_backup_report_line_for_missing_file_uses_missing_prefix(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    source = target_root / "docs" / "missing.md"
    backup_root = tmp_path / "backups"

    execution = execute_backup(build_backup_plan(source, target_root, backup_root))

    assert render_backup_report_line(execution) == f"MISSING: {source}"



def test_render_backup_report_lines_preserves_execution_order(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    source_a = target_root / "pkg" / "alpha.txt"
    source_a.parent.mkdir(parents=True, exist_ok=True)
    source_a.write_text("alpha", encoding="utf-8")
    source_b = target_root / "pkg" / "missing.txt"
    backup_root = tmp_path / "backups"

    execution_a = execute_backup(build_backup_plan(source_a, target_root, backup_root))
    execution_b = execute_backup(build_backup_plan(source_b, target_root, backup_root))

    lines = render_backup_report_lines([execution_a, execution_b])

    assert lines == [
        f"BACKUP : {source_a} -> {backup_root / Path('pkg/alpha.txt')}",
        f"MISSING: {source_b}",
    ]