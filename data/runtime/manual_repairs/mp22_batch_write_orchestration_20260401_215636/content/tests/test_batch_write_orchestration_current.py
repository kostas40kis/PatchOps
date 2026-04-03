from __future__ import annotations

import json
from pathlib import Path

import patchops.files.writers as writers
import patchops.workflows.apply_patch as apply_patch
from patchops.models import FileWriteSpec, WriteRecord


def test_write_files_orchestrates_multiple_specs_through_shared_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    specs = [
        FileWriteSpec(path="docs/a.txt", content="alpha", content_path=None, encoding="utf-8"),
        FileWriteSpec(path="docs/b.txt", content="beta", content_path=None, encoding="utf-8"),
    ]
    plans = [
        writers.WritePlan(
            destination=tmp_path / "docs" / "a.txt",
            content="alpha",
            encoding="utf-8",
            inline_content="alpha",
            content_source_type="content",
        ),
        writers.WritePlan(
            destination=tmp_path / "docs" / "b.txt",
            content="beta",
            encoding="utf-8",
            inline_content="beta",
            content_source_type="content",
        ),
    ]

    build_calls: list[tuple[str, Path | None, Path | None]] = []
    write_calls: list[tuple[Path, str, str]] = []

    def fake_build_write_plan(spec, destination_root, manifest_path=None, wrapper_project_root=None):
        index = len(build_calls)
        build_calls.append((spec.path, manifest_path, wrapper_project_root))
        return plans[index]

    def fake_write_single_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
        write_calls.append((destination, content, encoding))
        return WriteRecord(path=destination, encoding=encoding)

    monkeypatch.setattr(writers, "build_write_plan", fake_build_write_plan)
    monkeypatch.setattr(writers, "write_single_file", fake_write_single_file)

    records = writers.write_files(
        specs,
        tmp_path,
        manifest_path=tmp_path / "patch_manifest.json",
        wrapper_project_root=tmp_path / "wrapper_root",
    )

    assert [record.path for record in records] == [plan.destination for plan in plans]
    assert build_calls == [
        ("docs/a.txt", tmp_path / "patch_manifest.json", tmp_path / "wrapper_root"),
        ("docs/b.txt", tmp_path / "patch_manifest.json", tmp_path / "wrapper_root"),
    ]
    assert write_calls == [
        (plans[0].destination, "alpha", "utf-8"),
        (plans[1].destination, "beta", "utf-8"),
    ]


def test_apply_manifest_routes_multi_file_writes_through_batch_helper(
    tmp_path: Path,
    monkeypatch,
) -> None:
    wrapper_root = tmp_path / "wrapper"
    target_root = tmp_path / "target"
    report_dir = tmp_path / "reports"
    wrapper_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = wrapper_root / "patch_manifest.json"
    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp22_apply_batch_write_contract",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "docs/one.txt",
                "content": "one",
                "content_path": None,
                "encoding": "utf-8",
            },
            {
                "path": "docs/two.txt",
                "content": "two",
                "content_path": None,
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir),
            "report_name_prefix": "mp22_apply_batch_write_contract",
            "write_to_desktop": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_write_files(specs, destination_root, manifest_path=None, wrapper_project_root=None):
        captured["spec_paths"] = [spec.path for spec in specs]
        captured["destination_root"] = destination_root
        captured["manifest_path"] = manifest_path
        captured["wrapper_project_root"] = wrapper_project_root
        return [
            WriteRecord(path=destination_root / spec.path, encoding=spec.encoding)
            for spec in specs
        ]

    monkeypatch.setattr(apply_patch, "write_files", fake_write_files)

    result = apply_patch.apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "PASS"
    assert captured == {
        "spec_paths": ["docs/one.txt", "docs/two.txt"],
        "destination_root": target_root,
        "manifest_path": manifest_path.resolve(),
        "wrapper_project_root": wrapper_root.resolve(),
    }
    assert [record.path for record in result.write_records] == [
        target_root / "docs/one.txt",
        target_root / "docs/two.txt",
    ]
