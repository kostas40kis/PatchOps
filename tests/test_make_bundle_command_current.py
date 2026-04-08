from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.bundles.shape_validation import validate_bundle_directory


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_make_bundle(bundle_root: Path, *, mode: str = "apply") -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "make-bundle",
            str(bundle_root),
            "--mode",
            mode,
            "--patch-name",
            f"{mode}_starter_bundle",
            "--target-project",
            "patchops",
            "--target-root",
            r"C:\dev\patchops",
            "--wrapper-root",
            r"C:\dev\patchops",
            "--profile",
            "generic_python",
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    return json.loads(result.stdout)


def test_make_bundle_cli_generates_canonical_bundle_root(tmp_path: Path) -> None:
    bundle_root = tmp_path / "generated_apply_bundle"
    payload = _run_make_bundle(bundle_root, mode="apply")

    assert payload["ok"] is True
    assert payload["issue_count"] == 0
    assert bundle_root.exists()
    assert (bundle_root / "manifest.json").is_file()
    assert (bundle_root / "bundle_meta.json").is_file()
    assert (bundle_root / "README.txt").is_file()
    assert (bundle_root / "run_with_patchops.ps1").is_file()
    assert (bundle_root / "content").is_dir()

    manifest = json.loads((bundle_root / "manifest.json").read_text(encoding="utf-8"))
    bundle_meta = json.loads((bundle_root / "bundle_meta.json").read_text(encoding="utf-8"))

    assert manifest["patch_name"] == "apply_starter_bundle"
    assert bundle_meta["patch_name"] == "apply_starter_bundle"
    assert bundle_meta["bundle_mode"] == "apply"
    assert bundle_meta["launcher_path"] == "run_with_patchops.ps1"

    shape = validate_bundle_directory(bundle_root)
    assert shape.ok is True


def test_make_bundle_cli_scaffold_passes_check_bundle_for_directory_root(tmp_path: Path) -> None:
    bundle_root = tmp_path / "generated_check_bundle_root"
    _run_make_bundle(bundle_root, mode="verify")

    result = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "check-bundle", str(bundle_root)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["issue_count"] == 0


def test_make_bundle_cli_supports_proof_mode_metadata(tmp_path: Path) -> None:
    bundle_root = tmp_path / "generated_proof_bundle"
    payload = _run_make_bundle(bundle_root, mode="proof")

    bundle_meta = json.loads((bundle_root / "bundle_meta.json").read_text(encoding="utf-8"))
    launcher_text = (bundle_root / "run_with_patchops.ps1").read_text(encoding="utf-8")

    assert payload["bundle_mode"] == "proof"
    assert bundle_meta["bundle_mode"] == "proof"
    assert "py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot" in launcher_text
    assert "py -m patchops.cli apply $manifestPath" not in launcher_text
    assert "py -m patchops.cli verify $manifestPath" not in launcher_text
