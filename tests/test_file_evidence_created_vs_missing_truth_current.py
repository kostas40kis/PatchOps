from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.reporting import renderer


def test_file_evidence_renders_created_not_missing_when_missing_backup_was_written(tmp_path: Path) -> None:
    target = tmp_path / "docs" / "created.md"

    result = SimpleNamespace(
        backup_records=[
            SimpleNamespace(source_path=target, backup_path=None, missing=True),
        ],
        write_records=[
            SimpleNamespace(target_path=target, content_source="content/docs/created.md"),
        ],
    )

    lines = renderer._patchops_c1e_build_file_evidence_lines(result)

    assert f"CREATED: {target}" in lines
    assert f"WROTE : {target} (content/docs/created.md)" in lines
    assert f"MISSING: {target}" not in lines


def test_file_evidence_still_renders_missing_when_no_write_record_matches(tmp_path: Path) -> None:
    missing_target = tmp_path / "docs" / "never_written.md"
    written_target = tmp_path / "docs" / "different.md"

    result = SimpleNamespace(
        backup_records=[
            SimpleNamespace(source_path=missing_target, backup_path=None, missing=True),
        ],
        write_records=[
            SimpleNamespace(target_path=written_target),
        ],
    )

    lines = renderer._patchops_c1e_build_file_evidence_lines(result)

    assert f"MISSING: {missing_target}" in lines
    assert f"CREATED: {missing_target}" not in lines
    assert f"WROTE : {written_target}" in lines


def test_file_evidence_created_match_normalizes_windows_and_path_spellings() -> None:
    result = SimpleNamespace(
        backup_records=[
            SimpleNamespace(target_path="C:\\dev\\patchops\\docs\\created.md", existed=False),
        ],
        write_records=[
            SimpleNamespace(destination_path="C:/dev/patchops/docs/created.md"),
        ],
    )

    lines = renderer._patchops_c1e_build_file_evidence_lines(result)

    assert "CREATED: C:\\dev\\patchops\\docs\\created.md" in lines
    assert "MISSING: C:\\dev\\patchops\\docs\\created.md" not in lines
