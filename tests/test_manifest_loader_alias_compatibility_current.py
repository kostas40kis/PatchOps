from __future__ import annotations

import json

from patchops.manifest_loader import load_manifest


def _base_manifest() -> dict:
    return {
        "manifest_version": 1,
        "patch_name": "alias_compatibility_current",
        "active_profile": "generic_python",
        "target_project_root": ".",
        "files_to_backup": ["src/demo.py"],
        "file_writes": [
            {
                "path": "src/demo.py",
                "content": "print('demo')\\n",
            }
        ],
        "validation_commands": [
            {
                "name": "alias_validation",
                "program": "python",
                "arguments": ["-m", "unittest", "tests.test_demo"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
    }


def test_manifest_loader_accepts_legacy_bundle_aliases(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(_base_manifest()), encoding="utf-8")

    manifest = load_manifest(manifest_path)

    assert manifest.backup_files == ["src/demo.py"]
    assert len(manifest.files_to_write) == 1
    assert manifest.files_to_write[0].path == "src/demo.py"
    assert manifest.files_to_write[0].content == "print('demo')\\n"
    assert len(manifest.validation_commands) == 1
    assert manifest.validation_commands[0].args == ["-m", "unittest", "tests.test_demo"]


def test_manifest_loader_prefers_canonical_args_over_arguments(tmp_path):
    payload = _base_manifest()
    payload["validation_commands"][0]["args"] = ["-m", "pytest", "-q"]
    payload["validation_commands"][0]["arguments"] = ["-m", "unittest"]

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    manifest = load_manifest(manifest_path)

    assert manifest.validation_commands[0].args == ["-m", "pytest", "-q"]


def test_manifest_loader_accepts_writes_alias(tmp_path):
    payload = _base_manifest()
    payload.pop("file_writes")
    payload["writes"] = [{"path": "docs/demo.md", "content": "demo\\n"}]

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    manifest = load_manifest(manifest_path)

    assert len(manifest.files_to_write) == 1
    assert manifest.files_to_write[0].path == "docs/demo.md"
