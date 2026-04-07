from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from patchops import cli


def _write_bundle_zip(
    bundle_path: Path,
    *,
    include_manifest: bool = True,
    include_bundle_meta: bool = True,
    second_root: bool = False,
) -> None:
    root = "sample_bundle"
    with zipfile.ZipFile(bundle_path, "w") as zf:
        if include_manifest:
            zf.writestr(f"{root}/manifest.json", "{}\n")
        if include_bundle_meta:
            zf.writestr(f"{root}/bundle_meta.json", "{}\n")
        zf.writestr(f"{root}/content/example.txt", "hello\n")
        zf.writestr(
            f"{root}/launchers/apply_with_patchops.ps1",
            "& py -m patchops.cli apply manifest.json\n",
        )
        if second_root:
            zf.writestr("other_root/manifest.json", "{}\n")


def test_check_bundle_help_exposes_current_live_args(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["check-bundle", "--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "usage: patchops check-bundle" in text
    assert "bundle_zip_path" in text


def test_check_bundle_returns_clean_payload_for_valid_zip(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bundle_zip = tmp_path / "bundle.zip"
    _write_bundle_zip(bundle_zip)
    exit_code = cli.main(["check-bundle", str(bundle_zip)])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["exists"] is True
    assert payload["path"] == str(bundle_zip.resolve())
    assert payload["top_level_root"] == "sample_bundle"
    assert payload["issue_count"] == 0
    assert payload["issues"] == []


def test_check_bundle_returns_nonzero_for_missing_manifest(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bundle_zip = tmp_path / "bundle_missing_manifest.zip"
    _write_bundle_zip(bundle_zip, include_manifest=False)
    exit_code = cli.main(["check-bundle", str(bundle_zip)])
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    joined = "\n".join(payload["issues"]).lower()
    assert "manifest.json" in joined


def test_check_bundle_returns_nonzero_for_multiple_roots(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bundle_zip = tmp_path / "bundle_multiple_roots.zip"
    _write_bundle_zip(bundle_zip, second_root=True)
    exit_code = cli.main(["check-bundle", str(bundle_zip)])
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["top_level_root"] is None
    assert "top-level root" in payload["issues"][0].lower()
