from __future__ import annotations

from types import SimpleNamespace

from patchops.reporting import renderer


def test_file_evidence_renders_created_and_write_for_new_target_same_run():
    target = "C:\\dev\\trader\\src\\demo.py"

    result = SimpleNamespace(
        backup_records=[
            SimpleNamespace(
                source_path=target,
                target_path=target,
                backup_path=None,
                missing=True,
            )
        ],
        write_records=[
            SimpleNamespace(
                target_path=target,
            )
        ],
    )

    lines = renderer._patchops_c1e_build_file_evidence_lines(result)

    assert f"CREATED: {target}" in lines
    assert f"WROTE : {target}" in lines


def test_file_evidence_still_renders_missing_when_not_written_same_run():
    target = "C:\\dev\\trader\\src\\missing_only.py"

    result = SimpleNamespace(
        backup_records=[
            SimpleNamespace(
                source_path=target,
                backup_path=None,
                missing=True,
            )
        ],
        write_records=[],
    )

    lines = renderer._patchops_c1e_build_file_evidence_lines(result)

    assert f"MISSING: {target}" in lines
