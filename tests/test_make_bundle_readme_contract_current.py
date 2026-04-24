from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from patchops.bundles.authoring import create_starter_bundle

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "patchops.cli", *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_create_starter_bundle_readme_mentions_maintained_authoring_workflow(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "starter_bundle",
        patch_name="patch_demo_bundle",
        target_project="trader",
        target_project_root=r"C:\dev\trader",
        wrapper_project_root=r"C:\dev\patchops",
        recommended_profile="trader",
        mode="apply",
    )

    text = result.readme_path.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "patchops starter bundle" in lowered
    assert "launcher generation rule" in lowered
    assert "do not hand-author the saved root launcher" in lowered
    assert "py -m patchops.cli make-bundle <bundle-root> --mode apply" in lowered
    assert "py -m patchops.cli check-bundle <bundle-root>" in lowered
    assert "bundle_mode" in lowered
    assert "proof" in lowered


def test_make_bundle_cli_writes_maintained_readme_text(tmp_path: Path) -> None:
    bundle_root = tmp_path / "starter_bundle"

    completed = _run_cli(
        "make-bundle",
        str(bundle_root),
        "--mode",
        "verify",
        "--patch-name",
        "patch_demo_bundle",
        "--target-project",
        "trader",
        "--target-root",
        r"C:\dev\trader",
        "--profile",
        "trader",
        "--wrapper-root",
        r"C:\dev\patchops",
    )
    assert completed.returncode == 0, completed.stderr

    readme_path = bundle_root / "README.txt"
    assert readme_path.exists()
    text = readme_path.read_text(encoding="utf-8").lower()

    assert "mode       : verify" in text
    assert "launcher generation rule" in text
    assert "do not hand-author the saved root launcher" in text
    assert "py -m patchops.cli make-bundle <bundle-root> --mode verify" in text
    assert "proof" in text
