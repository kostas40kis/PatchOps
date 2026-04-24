from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.exceptions import ManifestError
from patchops.manifest_loader import load_manifest


def _base_manifest() -> dict[str, object]:
    return {
        "manifest_version": "1",
        "patch_name": "manifest_loader_alias_compatibility",
        "active_profile": "generic_python",
        "target_project_root": None,
        "backup_files": [],
        "file_writes": [{"path": "docs/demo.md", "content": "demo\n"}],
        "validation_commands": [
            {
                "label": "pytest",
                "program": "py",
                "args": ["-m", "pytest", "-q"],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {},
    }


def test_manifest_loader_accepts_legacy_file_writes_alias(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(_base_manifest()), encoding="utf-8")

    manifest = load_manifest(manifest_path)

    assert len(manifest.files_to_write) == 1
    assert manifest.files_to_write[0].path == "docs/demo.md"


def test_manifest_loader_prefers_canonical_args_over_arguments(tmp_path: Path) -> None:
    payload = _base_manifest()
    command = payload["validation_commands"][0]
    command["args"] = ["-m", "pytest", "-q"]
    command["arguments"] = ["-m", "unittest"]

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    manifest = load_manifest(manifest_path)

    assert manifest.validation_commands[0].args == ["-m", "pytest", "-q"]


def test_manifest_loader_rejects_writes_alias_under_hardened_contract(tmp_path: Path) -> None:
    payload = _base_manifest()
    payload.pop("file_writes")
    payload["writes"] = [{"path": "docs/demo.md", "content": "demo\n"}]

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ManifestError, match="files_to_write"):
        load_manifest(manifest_path)
