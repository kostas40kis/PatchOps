from __future__ import annotations

import io
import json
import subprocess
import sys
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

from patchops.bundle_review import check_bundle_payload, cli_check_bundle_main


def _valid_bundle_members(root_name: str = "demo_bundle") -> dict[str, str]:
    return {
        f"{root_name}/manifest.json": '{"patch_name": "demo"}\n',
        f"{root_name}/bundle_meta.json": '{"bundle_schema_version": 1}\n',
        f"{root_name}/content/example.txt": "hello\n",
        f"{root_name}/launchers/apply_with_patchops.ps1": "Write-Host ok\n",
    }


def _write_zip(tmp_path: Path, members: dict[str, str], zip_name: str = "bundle.zip") -> Path:
    zip_path = tmp_path / zip_name
    with zipfile.ZipFile(zip_path, "w") as archive:
        for member_name, content in members.items():
            archive.writestr(member_name, content)
    return zip_path


def test_check_bundle_payload_for_valid_zip_includes_expected_fields(tmp_path: Path) -> None:
    zip_path = _write_zip(tmp_path, _valid_bundle_members())

    payload = check_bundle_payload(zip_path, requested_profile="generic_python")

    assert payload["ok"] is True
    assert payload["source_kind"] == "zip"
    assert payload["root_folder_name"] == "demo_bundle"
    assert payload["manifest_path"] == "demo_bundle/manifest.json"
    assert payload["bundle_meta_path"] == "demo_bundle/bundle_meta.json"
    assert payload["content_root_path"] == "demo_bundle/content"
    assert payload["launcher_paths"] == ["demo_bundle/launchers/apply_with_patchops.ps1"]
    assert payload["requested_profile"] == "generic_python"


def test_cli_check_bundle_main_returns_one_for_missing_manifest(tmp_path: Path) -> None:
    members = _valid_bundle_members()
    del members["demo_bundle/manifest.json"]
    zip_path = _write_zip(tmp_path, members)

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli_check_bundle_main([str(zip_path)])

    payload = json.loads(buffer.getvalue())
    assert exit_code == 1
    assert payload["ok"] is False
    assert any(issue["code"] == "missing_manifest" for issue in payload["issues"])


def test_py_module_cli_check_bundle_command_works_for_valid_zip(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    zip_path = _write_zip(tmp_path, _valid_bundle_members())

    result = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "check-bundle", str(zip_path), "--profile", "generic_python"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["requested_profile"] == "generic_python"
    assert payload["source_kind"] == "zip"


def test_py_module_cli_check_bundle_command_returns_one_for_missing_manifest(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    members = _valid_bundle_members()
    del members["demo_bundle/manifest.json"]
    zip_path = _write_zip(tmp_path, members)

    result = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "check-bundle", str(zip_path)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any(issue["code"] == "missing_manifest" for issue in payload["issues"])