from __future__ import annotations

import json
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


def test_create_starter_bundle_emits_canonical_staged_authoring_meta_and_manifest(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "starter_bundle",
        patch_name="patch_demo_bundle",
        target_project="trader",
        target_project_root=r"C:\dev\trader",
        wrapper_project_root=r"C:\dev\patchops",
        recommended_profile="trader",
        mode="apply",
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    bundle_meta = json.loads(result.bundle_meta_path.read_text(encoding="utf-8"))

    assert manifest["profile"] == "trader"
    assert manifest["active_profile"] == "trader"
    assert manifest["mode"] == "apply"
    assert manifest["target_root"] == r"C:\dev\trader"
    assert manifest["target_project_root"] == r"C:\dev\trader"
    assert manifest["target_repo_root"] == r"C:\dev\trader"
    assert manifest["wrapper_root"] == r"C:\dev\patchops"
    assert manifest["wrapper_project_root"] == r"C:\dev\patchops"

    assert bundle_meta["bundle_contract"] == "canonical_staged_authoring"
    assert bundle_meta["staged_authoring_contract"] is True
    assert bundle_meta["launcher"] == "run_with_patchops.ps1"
    assert bundle_meta["manifest"] == "manifest.json"
    assert bundle_meta["content_root"] == "content"
    assert bundle_meta["profile"] == "trader"
    assert bundle_meta["active_profile"] == "trader"
    assert bundle_meta["mode"] == "apply"
    assert bundle_meta["target_repo_root"] == r"C:\dev\trader"
    assert bundle_meta["wrapper_repo_root"] == r"C:\dev\patchops"


def test_create_starter_bundle_launcher_passes_check_launcher_cli(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "starter_bundle",
        patch_name="patch_demo_bundle",
        target_project="trader",
        target_project_root=r"C:\dev\trader",
        wrapper_project_root=r"C:\dev\patchops",
        recommended_profile="trader",
        mode="apply",
    )

    completed = _run_cli("check-launcher", str(result.launcher_path))
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["exists"] is True
    assert payload["ok"] is True


def test_create_starter_bundle_launcher_uses_safe_python_owned_shape(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "starter_bundle",
        patch_name="patch_demo_bundle",
        target_project="trader",
        target_project_root=r"C:\dev\trader",
        wrapper_project_root=r"C:\dev\patchops",
        recommended_profile="trader",
        mode="apply",
    )

    text = result.launcher_path.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "convertfrom-json" not in lowered
    assert "convertto-json" not in lowered
    assert "tempmanifestpath" not in lowered
    assert "py -m patchops.cli check $manifestpath" in lowered
    assert "py -m patchops.cli inspect $manifestpath" in lowered
    assert "py -m patchops.cli plan $manifestpath" in lowered
    assert "py -m patchops.cli apply $manifestpath" in lowered
