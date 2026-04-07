from __future__ import annotations

import json
from pathlib import Path
import zipfile

import pytest

from patchops import cli


def _write_valid_bundle(bundle_zip_path: Path, root: str = "patch_demo_bundle") -> None:
    with zipfile.ZipFile(bundle_zip_path, "w") as zf:
        zf.writestr(f"{root}/manifest.json", "{}\n")
        zf.writestr(f"{root}/bundle_meta.json", "{}\n")
        zf.writestr(f"{root}/README.txt", "demo\n")
        zf.writestr(f"{root}/content/example.txt", "payload\n")
        zf.writestr(f"{root}/launchers/apply_with_patchops.ps1", "Write-Host demo\n")


def test_inspect_bundle_help_exposes_current_live_args(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["inspect-bundle", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops inspect-bundle" in text
    assert "bundle_zip_path" in text


def test_inspect_bundle_returns_clean_payload_for_valid_zip(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bundle_zip_path = tmp_path / "demo_bundle.zip"
    _write_valid_bundle(bundle_zip_path)

    exit_code = cli.main(["inspect-bundle", str(bundle_zip_path)])
    assert exit_code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["exists"] is True
    assert payload["bundle_zip_path"] == str(bundle_zip_path.resolve())
    assert payload["root_folder"] == "patch_demo_bundle"
    assert payload["manifest_path"] == "patch_demo_bundle/manifest.json"
    assert payload["bundle_meta_path"] == "patch_demo_bundle/bundle_meta.json"
    assert payload["readme_path"] == "patch_demo_bundle/README.txt"
    assert payload["content_prefix"] == "patch_demo_bundle/content/"
    assert payload["issue_count"] == 0
    assert payload["issues"] == []
    assert any(item.endswith("apply_with_patchops.ps1") for item in payload["launchers"])


def test_inspect_bundle_returns_nonzero_for_missing_required_root_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bundle_zip_path = tmp_path / "missing_manifest_bundle.zip"
    with zipfile.ZipFile(bundle_zip_path, "w") as zf:
        zf.writestr("patch_demo_bundle/bundle_meta.json", "{}\n")
        zf.writestr("patch_demo_bundle/README.txt", "demo\n")
        zf.writestr("patch_demo_bundle/content/example.txt", "payload\n")
        zf.writestr("patch_demo_bundle/launchers/apply_with_patchops.ps1", "Write-Host demo\n")

    exit_code = cli.main(["inspect-bundle", str(bundle_zip_path)])
    assert exit_code == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["issue_count"] >= 1
    assert any("manifest.json" in issue for issue in payload["issues"])


def test_inspect_bundle_returns_nonzero_for_multiple_roots(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bundle_zip_path = tmp_path / "multi_root_bundle.zip"
    with zipfile.ZipFile(bundle_zip_path, "w") as zf:
        zf.writestr("root_one/manifest.json", "{}\n")
        zf.writestr("root_two/bundle_meta.json", "{}\n")

    exit_code = cli.main(["inspect-bundle", str(bundle_zip_path)])
    assert exit_code == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["issue_count"] >= 1
    joined = "\n".join(payload["issues"]).lower()
    assert "top-level root" in joined or "exactly one" in joined
